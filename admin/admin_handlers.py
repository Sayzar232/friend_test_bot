import logging

from aiogram import Bot, F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.database import (
    get_all_user_ids,
    get_average_test_score,
    get_last_hundred_users,
    get_most_common_answers_per_question,
    get_tests_created_count,
    get_top_tests_by_takers,
    get_total_tests_passed,
    get_user_count,
)
from settings import ADMIN_ID
from utils.keyboards import admin_kb
from utils.states import Form

router = Router()

logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    return str(user_id) == ADMIN_ID


def build_admin_panel_text(user_count: int, total_tests: int) -> str:
    return (
        "Админ панель\n\n"
        f"Количество пользователей: {user_count}\n"
        f"Общее количество пройденных тестов: {total_tests}"
    )


async def get_users_with_results_count() -> int:
    try:
        from database.database import pool

        async with pool.acquire() as connection:
            # Считаем пользователей, которые хотя бы раз проходили чужой тест.
            return await connection.fetchval("SELECT COUNT(DISTINCT taker_id) FROM tests_results;")
    except Exception:
        return 0


def build_common_answers_block(common_answers: dict) -> list[str]:
    if not common_answers:
        return []

    lines = ["", "<b>Частые ответы по вопросам (по созданным тестам):</b>"]
    for question_index in sorted(common_answers.keys()):
        answer, count = common_answers[question_index][0]
        lines.append(f"Вопрос {question_index + 1}: {answer} ({count} раз)")
    return lines


def build_top_tests_block(top_tests: list[dict]) -> list[str]:
    if not top_tests:
        return []

    lines = ["", "<b>Топ тестов по количеству прохождений:</b>"]
    for index, row in enumerate(top_tests, start=1):
        username = row.get("username") or str(row.get("test_id"))
        passed_count = row.get("num_users_passed") or 0
        lines.append(f"{index}. @{username} — {passed_count} прохождений")
    return lines


async def build_stats_text() -> str:
    user_count = await get_user_count()
    total_tests = await get_total_tests_passed()
    tests_created = await get_tests_created_count()
    average_score = await get_average_test_score()
    common_answers = await get_most_common_answers_per_question(top_n=1, max_questions=10)
    top_tests = await get_top_tests_by_takers(limit=5)
    users_with_results = await get_users_with_results_count()

    lines = [
        "<b>Статистика:</b>",
        f"Пользователей: {user_count}",
        f"Пройденных тестов (всего записей): {total_tests}",
        f"Пользователей, создавших тест: {tests_created}",
        f"Средний результат теста: {average_score:.2f}",
    ]
    lines.extend(build_common_answers_block(common_answers))
    lines.extend(build_top_tests_block(top_tests))

    if user_count:
        share_pct = (users_with_results / user_count) * 100
        lines.append(
            f"Пользователей, прошедших хотя бы один тест: {users_with_results} ({share_pct:.1f}%)"
        )

    return "\n".join(lines)


def build_recent_users_text(users: list[str]) -> str:
    if not users:
        return "Произошла ошибка или пользователей нет в базе данных"

    users_block = "\n".join(f"<b>{index}.</b> @{username}" for index, username in enumerate(users, start=1))
    return f"<b>👥 Последние 100 пользователей:</b>\n\n{users_block}"


async def send_broadcast(bot: Bot, user_ids: list[int], text: str) -> int:
    sent_count = 0
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, text)
            sent_count += 1
        except Exception as exc:
            logger.warning("Failed to send broadcast to user %s: %s", user_id, exc)
    return sent_count


@router.message(Command("admin"))
async def handle_admin(message: types.Message):
    if not is_admin(message.from_user.id):
        return

    user_count = await get_user_count()
    total_tests = await get_total_tests_passed()

    await message.answer(
        build_admin_panel_text(user_count, total_tests),
        reply_markup=admin_kb,
    )


@router.callback_query(F.data.startswith("admin_"))
async def handle_admin_actions(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    action = callback.data.removeprefix("admin_")

    if action == "broadcast":
        await callback.message.answer("Введите сообщение для рассылки:")
        await state.set_state(Form.waiting_for_broadcast_message)
        return

    if action == "stats":
        await callback.message.answer(await build_stats_text(), parse_mode="HTML")
        return

    if action == "100_users":
        users = await get_last_hundred_users()
        await callback.message.answer(build_recent_users_text(users))


@router.message(F.text, Form.waiting_for_broadcast_message)
async def handle_broadcast_message(message: types.Message, bot: Bot, state: FSMContext):
    user_ids = await get_all_user_ids()
    sent_count = await send_broadcast(bot, user_ids, message.text)

    await message.answer(f"Рассылка завершена. Отправлено {sent_count} сообщений.")
    await state.clear()
