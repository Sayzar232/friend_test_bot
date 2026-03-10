from html import escape
from typing import Any

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.database import get_user_data
from utils.keyboards import (
    back_to_menu_kb,
    best_users_passed_kb,
    friend_kb,
    get_question_keyboard,
    menu_kb,
    start_quetions_kb,
)
from utils.questions import QUESTIONS, QUESTIONS_FOR_FRIEND
from utils.states import Form

router = Router()

TOTAL_QUESTIONS = 15


def get_test_str(test_answers: list[Any] | None) -> str | None:
    if not test_answers:
        return None

    return "\n".join(
        f"<b>{index}. {QUESTIONS[index - 1]}</b>\n{answer}"
        for index, answer in enumerate(test_answers, start=1)
    )


def normalize_meta_results_entries(meta_entries: list[Any]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
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


def normalize_legacy_results_entries(legacy_scores: dict | None) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for raw_name, score in (legacy_scores or {}).items():
        clean_name = str(raw_name or "").lstrip("@")
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


def normalize_results_entries(
    legacy_scores: dict | None,
    meta_entries: list[Any] | None,
) -> list[dict[str, Any]]:
    if meta_entries:
        return normalize_meta_results_entries(meta_entries)
    return normalize_legacy_results_entries(legacy_scores)


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


def sort_entries_by_score(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(entries, key=lambda item: item.get("score", 0), reverse=True)


def build_results_block(entries: list[dict[str, Any]], empty_text: str) -> str:
    if not entries:
        return empty_text

    return "\n".join(
        f"{index}. {format_user_link(item.get('user_id'), item.get('username'), item.get('full_name'))} - <b>{item.get('score', 0)}/15</b>"
        for index, item in enumerate(sort_entries_by_score(entries), start=1)
    )


def build_compatibility_block(other_test_entries: list[dict[str, Any]]) -> str:
    if not other_test_entries:
        return "Пока недостаточно данных для расчета совместимости."

    return "\n".join(
        f"{format_user_link(item.get('user_id'), item.get('username'), item.get('full_name'))} - <b>{round((item.get('score', 0) / 15) * 100)}%</b>"
        for item in sort_entries_by_score(other_test_entries)
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

    best_results_text = build_results_block(best_users_entries, "Пока никто не прошел твой тест.")
    other_results_text = build_results_block(other_test_entries, "Ты пока не проходил тесты друзей.")
    compatibility_text = build_compatibility_block(other_test_entries)
    link_text = (
        user_info.get("ref_link")
        if user_info.get("test_answers")
        else "Будет доступна после создания теста."
    )

    return (
        "<b>Твой профиль</b>\n\n"
        f"<b>Имя:</b> <code>{full_name}</code>\n"
        f"<b>ID:</b> <code>{user_id}</code>\n\n"
        f"<b>Пройденных тестов:</b> {user_info.get('other_test_passed') or 0}\n"
        f"<b>Людей, которые прошли твой тест:</b> {user_info.get('num_users_passed') or 0}\n\n"
        f"<b>Твоя ссылка на тест:</b>\n{link_text}\n\n"
        "<b>Лучшие результаты по твоему тесту:</b>\n\n"
        f"{best_results_text}\n\n"
        "<b>Твои результаты в тестах друзей:</b>\n\n"
        f"{other_results_text}\n\n"
        "<b>Совместимость с друзьями:</b>\n\n"
        f"{compatibility_text}"
    )


def build_help_text() -> str:
    return (
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


def build_default_user_info() -> dict[str, Any]:
    return {
        "best_users_passed": {},
        "best_users_passed_meta": [],
        "other_test_users": {},
        "other_test_users_meta": [],
        "test_answers": [],
        "other_test_passed": 0,
        "num_users_passed": 0,
        "ref_link": "",
    }


def build_main_menu_text(user_has_test: bool) -> str:
    if user_has_test:
        return "<b>Главное меню</b>\n\nВыбери, что хочешь сделать дальше."
    return "<b>Главное меню</b>\n\nМожешь пользоваться ботом сразу или создать свой тест позже."


async def start_questionnaire(
    callback: CallbackQuery,
    state: FSMContext,
    *,
    test_type: str,
    question_text: str,
    next_state,
    edit_current_message: bool,
) -> None:
    await state.update_data(
        test_answers=list(range(TOTAL_QUESTIONS)),
        test_type=test_type,
        answer_num=1,
    )
    await state.set_state(next_state)

    answer_method = callback.message.edit_text if edit_current_message else callback.message.answer
    await answer_method(
        f"<b>Вопрос 1 из {TOTAL_QUESTIONS}</b>\n\n{question_text}",
        reply_markup=get_question_keyboard(1),
    )


@router.callback_query(F.data.startswith("menu_"))
async def handle_menu(callback: CallbackQuery):
    await callback.answer()

    action = callback.data.removeprefix("menu_")

    if action == "create_test":
        await callback.message.edit_text(
            "<b>Создавай или изменяй свой тест!</b>\n\n"
            "Буду отправлять вопросы по одному. Отвечай честно.",
            reply_markup=start_quetions_kb,
        )
        return

    if action == "info":
        user_info = await get_user_data(callback.from_user.id) or build_default_user_info()
        await callback.message.answer(
            text=build_info_text(user_info, callback.from_user.full_name, callback.from_user.id),
            reply_markup=best_users_passed_kb,
        )
        return

    if action == "help":
        await callback.message.edit_text(build_help_text(), reply_markup=back_to_menu_kb)


@router.callback_query(F.data == "test_answers_show")
async def handle_show_users_passed(callback: CallbackQuery):
    await callback.answer()

    user_info = await get_user_data(callback.from_user.id) or {"test_answers": []}
    test_answers = get_test_str(user_info.get("test_answers"))
    if not test_answers:
        await callback.message.answer("<b>У тебя пока нет сохраненных ответов на тест.</b>")
        return

    await callback.message.answer(f"<b>Твои ответы на тест:</b>\n\n{test_answers}")


@router.callback_query(F.data.startswith("start_questions_"))
async def handle_start_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    action = callback.data.removeprefix("start_questions_")

    if action == "start":
        await start_questionnaire(
            callback,
            state,
            test_type="create",
            question_text=QUESTIONS[0],
            next_state=Form.waiting_for_answer,
            edit_current_message=False,
        )
        return

    if action == "back":
        user_data = await get_user_data(callback.from_user.id) or {"test_answers": []}
        await callback.message.edit_text(
            build_main_menu_text(bool(user_data.get("test_answers"))),
            reply_markup=menu_kb,
        )


@router.callback_query(F.data.startswith("friend_questions_"))
async def handle_friend_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    action = callback.data.removeprefix("friend_questions_")

    if action == "start":
        await start_questionnaire(
            callback,
            state,
            test_type="answer",
            question_text=QUESTIONS_FOR_FRIEND[0],
            next_state=Form.waiting_for_friend_answer,
            edit_current_message=True,
        )
        return

    if action == "cancel":
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(
            "<b>Начало отменено.</b>\n\n"
            "Ты можешь вернуться и пройти тест позже."
        )
