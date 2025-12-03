from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from settings import ADMIN_ID
from database.database import get_all_user_ids, get_user_count, get_total_tests_passed, get_last_hundred_users
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

        await callback.message.answer(
            f"Статистика:\n\n"
            f"Пользователей: {user_count}\n"
            f"Пройденных тестов: {total_tests}"
        )
    elif data == "100_users":
        users = await get_last_hundred_users()

        if users:
            users_str_lst = [f"<b>{ind + 1}.</b> @{i}\n" for ind, i in enumerate(users)]
            users_str = "\n".join(users_str_lst)

            await callback.message.answer(f"<b>👥 Первые 100 пользователей:</b>\n\n{users_str}")
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
