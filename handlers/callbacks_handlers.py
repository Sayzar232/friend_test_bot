from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from html import escape

from utils.states import Form
from utils.questions import QUESTIONS, QUESTIONS_FOR_FRIEND
from utils.keyboards import *
from database.database import *

router = Router()

NEW_USER_PROMPT = (
    "<b>👋 Привет!</b>\n\n"
    "Чтобы пользоваться ботом, сначала создай свой тест.\n"
    "Нажми кнопку «Начать тест» ниже."
)


async def ensure_user_has_test(callback: CallbackQuery) -> bool:
    user_data = await get_user_data(callback.from_user.id)
    if user_data.get("test_answers"):
        return True
    await callback.message.answer(NEW_USER_PROMPT, reply_markup=new_user_start_kb)
    return False


def get_test_str(test_answers):
    if test_answers:
        answers_str = ""
        for i in range(len(test_answers)):
            answers_str += f"<b>{i + 1}. {QUESTIONS[i]}</b>\n{test_answers[i]}\n"

        return answers_str
    return None


def normalize_results_entries(legacy_scores: dict, meta_entries: list | None):
    if meta_entries:
        normalized = []
        for entry in meta_entries:
            if not isinstance(entry, dict):
                continue
            normalized.append({
                "user_id": entry.get("user_id"),
                "username": entry.get("username"),
                "full_name": entry.get("full_name"),
                "score": entry.get("score", 0)
            })
        return normalized

    normalized = []
    for raw_name, score in legacy_scores.items():
        raw_name = str(raw_name or "")
        clean_name = raw_name.lstrip("@")
        user_id = int(clean_name) if clean_name.isdigit() else None
        normalized.append({
            "user_id": user_id,
            "username": None if user_id else clean_name,
            "full_name": None,
            "score": score
        })
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


def get_result_key(entry: dict) -> str | None:
    user_id = entry.get("user_id")
    if user_id is not None:
        return f"id:{user_id}"

    username = entry.get("username")
    if username:
        return f"username:{str(username).lower()}"

    full_name = entry.get("full_name")
    if full_name:
        return f"full_name:{str(full_name).lower()}"

    return None

@router.callback_query(F.data.startswith("menu_"))
async def handle_menu(callback: CallbackQuery):
    await callback.answer()

    data = callback.data.replace("menu_", "")

    if data == "create_test":
        await callback.message.edit_text(
            "<b>✏️ Создавай или изменяй свой тест!</b>\n\n"
            "Буду отправлять вопросы по одному. Отвечай честно — результаты будут интереснее 😊",
            reply_markup=start_quetions_kb
        )
    elif data == "info":
        if not await ensure_user_has_test(callback):
            return
        user_info = await get_user_data(callback.from_user.id)
        if not user_info:
            user_info = {
                'best_users_passed': {},
                'other_test_users': {},
                'test_answers': [],
                'other_test_passed': 0,
                'num_users_passed': 0,
                'ref_link': ''
            }
        best_users_entries = normalize_results_entries(
            user_info.get("best_users_passed") or {},
            user_info.get("best_users_passed_meta")
        )
        other_test_entries = normalize_results_entries(
            user_info.get("other_test_users") or {},
            user_info.get("other_test_users_meta")
        )

        if not best_users_entries:
            best_results_str = "Пока никто не прошёл твой тест. Отправь ссылку друзьям 💋"
        else:
            sorted_users = sorted(best_users_entries, key=lambda item: item["score"], reverse=True)
            results_list = [
                f"{i}. {format_user_link(user.get('user_id'), user.get('username'), user.get('full_name'))} - <b>{user.get('score', 0)}/15</b>"
                for i, user in enumerate(sorted_users, 1)
            ]
            best_results_str = '\n'.join(results_list)

        if not other_test_entries:
            best_results_other_str = "Ты пока не прошёл ни один чужой тест. Попробуй пройти тесты друзей 😊"
        else:
            sorted_other_test_passed = sorted(other_test_entries, key=lambda item: item["score"], reverse=True)
            other_results_list = [
                f"{i}. {format_user_link(user.get('user_id'), user.get('username'), user.get('full_name'))} - <b>{user.get('score', 0)}/15</b>"
                for i, user in enumerate(sorted_other_test_passed, 1)
            ]
            best_results_other_str = '\n'.join(other_results_list)

        best_scores_by_key = {}
        best_entry_by_key = {}
        for entry in best_users_entries:
            entry_key = get_result_key(entry)
            if not entry_key:
                continue
            best_scores_by_key[entry_key] = entry.get("score", 0)
            best_entry_by_key[entry_key] = entry

        other_scores_by_key = {}
        other_entry_by_key = {}
        for entry in other_test_entries:
            entry_key = get_result_key(entry)
            if not entry_key:
                continue
            other_scores_by_key[entry_key] = entry.get("score", 0)
            other_entry_by_key[entry_key] = entry

        percent_users = []
        for entry_key in set(best_scores_by_key) & set(other_scores_by_key):
            percent_users.append({
                "user": best_entry_by_key.get(entry_key) or other_entry_by_key.get(entry_key),
                "percent": (best_scores_by_key[entry_key] + other_scores_by_key[entry_key]) / 30 * 100
            })

        if not percent_users:
            percent_users_str = "Пока нет данных. Пройди тесты друзей и дай им пройти твой тест 💫"
        else:
            sorted_percent_users = sorted(percent_users, key=lambda item: item["percent"], reverse=True)
            percent_list = [
                f"{i}. {format_user_link(item['user'].get('user_id'), item['user'].get('username'), item['user'].get('full_name'))} - <b>{round(item['percent'], 1)}%</b>"
                for i, item in enumerate(sorted_percent_users, 1)
            ]
            percent_users_str = '\n'.join(percent_list)

        await callback.message.answer(
            text=(
                "<b>👤 Твой профиль</b>\n\n"
                f"<b>🙋‍♂️ Имя:</b> <code>{callback.from_user.full_name}</code>\n"
                f"<b>🆔 ID:</b> <code>{callback.from_user.id}</code>\n\n"
                f"<b>📝 Пройденных тестов:</b> {user_info.get('other_test_passed')}\n"
                f"<b>👥 Людей, которые прошли твой тест:</b> {user_info.get('num_users_passed')}\n\n"
                f"<b>🔗 Твоя ссылка на тест:</b>\n{user_info.get('ref_link')}\n\n"
                "<b>🏆 Лучшие результаты по твоему тесту:</b>\n\n"
                f"{best_results_str}\n\n"
                "<b>🏆 Твои лучшие результаты в тестах друзей:</b>\n\n"
                f"{best_results_other_str}\n\n"
                "<b>💞 Совместимость с друзьями:</b>\n\n"
                f"{percent_users_str}"
            ),
            reply_markup=best_users_passed_kb
        )
    elif data == "help":
        if not await ensure_user_has_test(callback):
            return
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

    if not await ensure_user_has_test(callback):
        return

    user_info = await get_user_data(callback.from_user.id)
    if not user_info:
        user_info = {'test_answers': []}
    test_answers = get_test_str(user_info.get("test_answers"))

    if not test_answers:
        await callback.message.answer(
            "❌ <b>Ты ещё не создал(а) свои ответы на тест.</b>\n\n"
            "Сначала создай или обнови тест через кнопку «Создать/изменить тест» или команду <code>/edit_test</code> ✏️"
        )
        return

    await callback.message.answer(f"<b>📚 Твои ответы на тест:</b>\n\n{test_answers}")

@router.callback_query(F.data.startswith("start_questions_"))
async def handle_start_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = callback.data.replace("start_questions_", "")

    if data == "start":
        await state.update_data(test_answers=[i for i in range(15)], test_type="create")
        await state.set_state(Form.waiting_for_answer)
        await callback.message.answer(
            "<b>✏️ Вопрос 1 из 15</b>\n\n"
            f"{QUESTIONS[0]}",
            reply_markup=get_question_keyboard(1)
        )
    elif data == "back":
        user_data = await get_user_data(callback.from_user.id)
        if not user_data.get("test_answers"):
            await callback.message.edit_text(NEW_USER_PROMPT, reply_markup=new_user_start_kb)
            return
        await callback.message.edit_text(
            "<b>Главное меню</b>\n\n"
            "Выбери, что хочешь сделать дальше 👇",
            reply_markup=menu_kb
        )
        return

@router.callback_query(F.data.startswith("friend_questions_"))
async def handle_friend_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if not await ensure_user_has_test(callback):
        return

    data = callback.data.replace("friend_questions_", "")

    if data == "start":
        await state.update_data(test_answers=[i for i in range(15)], test_type="answer")
        await state.set_state(Form.waiting_for_friend_answer)
        await callback.message.edit_text(
            "<b>✏️ Вопрос 1 из 15</b>\n\n"
            f"{QUESTIONS_FOR_FRIEND[0]}",
            reply_markup=get_question_keyboard(1)
        )

    elif data == "cancel":
        await state.clear()
        await callback.message.delete()
        await callback.message.answer(
            "<b>❌ Начало отменено.</b>\n\n"
            "Ты можешь вернуться и пройти тест позже 🙂"
        )
        return
