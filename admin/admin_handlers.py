from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from settings import ADMIN_ID
from database.database import (
    get_all_user_ids,
    get_user_count,
    get_total_tests_passed,
    get_last_hundred_users,
    get_tests_created_count,
    get_average_test_score,
    get_most_common_answers_per_question,
    get_top_tests_by_takers,
)
from utils.keyboards import admin_kb
from utils.states import Form

router = Router()

@router.message(Command("admin"))
async def handle_admin(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID:
        return

    user_count = await get_user_count()
    total_tests = await get_total_tests_passed()

    await message.answer(
        f"Админ панель\n\n"
        f"Количество пользователей: {user_count}\n"
        f"Общее количество пройденных тестов: {total_tests}",
        reply_markup=admin_kb
    )

@router.callback_query(F.data.startswith("admin_"))
async def handle_admin_actions(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = callback.data.replace("admin_", "")

    if data == "broadcast":
        await callback.message.answer("Введите сообщение для рассылки:")
        await state.set_state(Form.waiting_for_broadcast_message)
    elif data == "stats":
        user_count = await get_user_count()
        total_tests = await get_total_tests_passed()
        tests_created = await get_tests_created_count()
        avg_score = await get_average_test_score()
        common_answers = await get_most_common_answers_per_question(top_n=1, max_questions=10)
        top_tests = await get_top_tests_by_takers(limit=5)

        parts = []
        parts.append(f"<b>Статистика:</b>\n")
        parts.append(f"Пользователей: {user_count}")
        parts.append(f"Пройденных тестов (всего записей): {total_tests}")
        parts.append(f"Пользователей, создавших тест: {tests_created}")
        parts.append(f"Средний результат теста: {avg_score:.2f}")

        # Most common answers per question
        if common_answers:
            parts.append('\n<b>Частые ответы по вопросам (по созданным тестам):</b>')
            for qidx in sorted(common_answers.keys()):
                top = common_answers[qidx][0]
                ans, cnt = top
                parts.append(f"Вопрос {qidx + 1}: {ans} ({cnt} раз)")

        # Top tests by number of takers
        if top_tests:
            parts.append('\n<b>Топ тестов по количеству прохождений:</b>')
            for ind, row in enumerate(top_tests):
                uname = row.get('username') or str(row.get('test_id'))
                cnt = row.get('num_users_passed') or 0
                parts.append(f"{ind + 1}. @{uname} — {cnt} прохождений")

        # Additional metric: share of users who ever passed at least one test
        users_with_results = 0
        try:
            # count distinct taker_id
            from database.database import pool
            async with pool.acquire() as connection:
                users_with_results = await connection.fetchval("SELECT COUNT(DISTINCT taker_id) FROM tests_results;")
        except Exception:
            users_with_results = 0

        if user_count:
            share_pct = (users_with_results / user_count) * 100 if user_count else 0
            parts.append(f"Пользователей, прошедших хотя бы один тест: {users_with_results} ({share_pct:.1f}%)")

        await callback.message.answer("\n".join(parts), parse_mode="HTML")
    elif data == "100_users":
        users = await get_last_hundred_users()

        if users:
            users_str_lst = [f"<b>{ind + 1}.</b> @{i}\n" for ind, i in enumerate(users)]
            users_str = "\n".join(users_str_lst)

            await callback.message.answer(f"<b>👥 Последние 100 пользователей:</b>\n\n{users_str}")
        else:
            await callback.message.answer("Произошла ошибка или пользователей нет в базе данных")

@router.message(F.text, Form.waiting_for_broadcast_message)
async def handle_broadcast_message(message: types.Message, bot: Bot, state: FSMContext):
    user_ids = await get_all_user_ids()

    sent_count = 0
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, message.text)
            sent_count += 1
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")

    await message.answer(f"Рассылка завершена. Отправлено {sent_count} сообщений.")
    await state.clear()
