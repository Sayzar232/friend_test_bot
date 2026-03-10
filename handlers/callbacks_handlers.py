from html import escape

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.database import get_user_data
from utils.keyboards import *
from utils.questions import QUESTIONS, QUESTIONS_FOR_FRIEND
from utils.states import Form

router = Router()


def get_test_str(test_answers):
    if not test_answers:
        return None

    answers_str = ""
    for i, answer in enumerate(test_answers, 1):
        answers_str += f"<b>{i}. {QUESTIONS[i - 1]}</b>\n{answer}\n"
    return answers_str


def normalize_results_entries(legacy_scores: dict, meta_entries: list | None):
    if meta_entries:
        normalized = []
        for entry in meta_entries:
            if not isinstance(entry, dict):
                continue
            normalized.append(
                {
                    "user_id": entry.get("user_id"),
                    "username": entry.get("username"),
                    "full_name": entry.get("full_name"),
                    "score": entry.get("score", 0),
                }
            )
        return normalized

    normalized = []
    for raw_name, score in (legacy_scores or {}).items():
        raw_name = str(raw_name or "")
        clean_name = raw_name.lstrip("@")
        user_id = int(clean_name) if clean_name.isdigit() else None
        normalized.append(
            {
                "user_id": user_id,
                "username": None if user_id else clean_name,
                "full_name": None,
                "score": score,
            }
        )
    return normalized


def format_user_link(user_id: int | None, username: str | None, full_name: str | None) -> str:
    if username:
        label = f"@{str(username).lstrip('@')}"
    elif full_name:
        label = full_name
    elif user_id is not None:
        label = str(user_id)
    else:
        label = "пользователь"

    safe_label = escape(label)
    if user_id is None:
        return safe_label
    return f'<a href="tg://user?id={user_id}">{safe_label}</a>'


def build_results_block(entries: list[dict], empty_text: str) -> str:
    if not entries:
        return empty_text

    sorted_users = sorted(entries, key=lambda item: item.get("score", 0), reverse=True)
    return "\n".join(
        f"{index}. {format_user_link(item.get('user_id'), item.get('username'), item.get('full_name'))} - <b>{item.get('score', 0)}/15</b>"
        for index, item in enumerate(sorted_users, 1)
    )


def build_compatibility_block(other_test_entries: list[dict]) -> str:
    if not other_test_entries:
        return "Пока недостаточно данных для расчета совместимости."

    sorted_users = sorted(other_test_entries, key=lambda item: item.get("score", 0), reverse=True)
    return "\n".join(
        f"{format_user_link(item.get('user_id'), item.get('username'), item.get('full_name'))} - <b>{round((item.get('score', 0) / 15) * 100)}%</b>"
        for item in sorted_users
    )


def build_info_text(user_info: dict, full_name: str, user_id: int) -> str:
    best_users_entries = normalize_results_entries(
        user_info.get("best_users_passed") or {},
        user_info.get("best_users_passed_meta"),
    )
    other_test_entries = normalize_results_entries(
        user_info.get("other_test_users") or {},
        user_info.get("other_test_users_meta"),
    )

    best_results_str = build_results_block(best_users_entries, "Пока никто не прошел твой тест.")
    other_results_str = build_results_block(other_test_entries, "Ты пока не проходил тесты друзей.")
    compatibility_str = build_compatibility_block(other_test_entries)
    link_text = user_info.get("ref_link") if user_info.get("test_answers") else "Будет доступна после создания теста."

    return (
        "<b>Твой профиль</b>\n\n"
        f"<b>Имя:</b> <code>{full_name}</code>\n"
        f"<b>ID:</b> <code>{user_id}</code>\n\n"
        f"<b>Пройденных тестов:</b> {user_info.get('other_test_passed') or 0}\n"
        f"<b>Людей, которые прошли твой тест:</b> {user_info.get('num_users_passed') or 0}\n\n"
        f"<b>Твоя ссылка на тест:</b>\n{link_text}\n\n"
        "<b>Лучшие результаты по твоему тесту:</b>\n\n"
        f"{best_results_str}\n\n"
        "<b>Твои результаты в тестах друзей:</b>\n\n"
        f"{other_results_str}\n\n"
        "<b>Совместимость с друзьями:</b>\n\n"
        f"{compatibility_str}"
    )


@router.callback_query(F.data.startswith("menu_"))
async def handle_menu(callback: CallbackQuery):
    await callback.answer()

    data = callback.data.replace("menu_", "")

    if data == "create_test":
        await callback.message.edit_text(
            "<b>Создавай или изменяй свой тест!</b>\n\n"
            "Буду отправлять вопросы по одному. Отвечай честно.",
            reply_markup=start_quetions_kb,
        )
    elif data == "info":
        user_info = await get_user_data(callback.from_user.id)
        if not user_info:
            user_info = {
                "best_users_passed": {},
                "best_users_passed_meta": [],
                "other_test_users": {},
                "other_test_users_meta": [],
                "test_answers": [],
                "other_test_passed": 0,
                "num_users_passed": 0,
                "ref_link": "",
            }

        await callback.message.answer(
            text=build_info_text(user_info, callback.from_user.full_name, callback.from_user.id),
            reply_markup=best_users_passed_kb,
        )
    elif data == "help":
        help_text = (
            "<b>ℹ️ Как пользоваться ботом?</b>\n\n"
            "Этот бот позволяет вам создать свой собственный тест и поделиться им с друзьями, чтобы узнать, насколько хорошо они вас знают!\n\n"
            "<b>📋 Пошаговая инструкция:</b>\n\n"
            "1. <b>Создайте тест:</b> Нажмите \"Создать/изменить тест\" в главном меню или используйте команду <code>/edit_test</code> и ответьте на вопросы.\n"
            "2. <b>Получите ссылку:</b> Ваша персональная ссылка для друзей будет доступна в профиле (<code>/profile</code>).\n"
            "3. <b>Отправьте друзьям:</b> 📤 Поделитесь ссылкой с друзьями.\n"
            "4. <b>Следите за результатами:</b> Вы получите уведомление, когда кто-то пройдет ваш тест. Лучшие результаты можно посмотреть в профиле.\n\n"
            "<b>🤖 Доступные команды:</b>\n\n"
            "<code>/start</code> - 🚀 Запустить бота и получить свою персональную ссылку.\n"
            "<code>/profile</code> - 👤 Посмотреть свой профиль, статистику и ссылку на тест.\n"
            "<code>/edit_test</code> - ✏️ Создать или изменить свои ответы на тест.\n"
            "<code>/show_answers</code> - 👀 Посмотреть свои текущие ответы на тест."
        )
        await callback.message.edit_text(text=help_text, reply_markup=back_to_menu_kb)


@router.callback_query(F.data == "test_answers_show")
async def handle_show_users_passed(callback: CallbackQuery):
    await callback.answer()

    user_info = await get_user_data(callback.from_user.id)
    if not user_info:
        user_info = {"test_answers": []}

    test_answers = get_test_str(user_info.get("test_answers"))
    if not test_answers:
        await callback.message.answer("<b>У тебя пока нет сохраненных ответов на тест.</b>")
        return

    await callback.message.answer(f"<b>Твои ответы на тест:</b>\n\n{test_answers}")


@router.callback_query(F.data.startswith("start_questions_"))
async def handle_start_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = callback.data.replace("start_questions_", "")

    if data == "start":
        await state.update_data(test_answers=[i for i in range(15)], test_type="create")
        await state.set_state(Form.waiting_for_answer)
        await callback.message.answer(
            "<b>Вопрос 1 из 15</b>\n\n"
            f"{QUESTIONS[0]}",
            reply_markup=get_question_keyboard(1),
        )
    elif data == "back":
        user_data = await get_user_data(callback.from_user.id)
        text = (
            "<b>Главное меню</b>\n\nВыбери, что хочешь сделать дальше."
            if user_data.get("test_answers")
            else "<b>Главное меню</b>\n\nМожешь пользоваться ботом сразу или создать свой тест позже."
        )
        await callback.message.edit_text(text, reply_markup=menu_kb)


@router.callback_query(F.data.startswith("friend_questions_"))
async def handle_friend_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = callback.data.replace("friend_questions_", "")

    if data == "start":
        await state.update_data(test_answers=[i for i in range(15)], test_type="answer")
        await state.set_state(Form.waiting_for_friend_answer)
        await callback.message.edit_text(
            "<b>Вопрос 1 из 15</b>\n\n"
            f"{QUESTIONS_FOR_FRIEND[0]}",
            reply_markup=get_question_keyboard(1),
        )
    elif data == "cancel":
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(
            "<b>Начало отменено.</b>\n\n"
            "Ты можешь вернуться и пройти тест позже."
        )
