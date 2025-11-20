from aiogram import Router, types, F, Bot
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.utils.deep_linking import create_start_link, decode_payload
from aiogram.fsm.context import FSMContext

from utils.keyboards import *
from utils.states import Form
from database.database import add_user, get_user_data
from handlers.callbacks_handlers import get_test_str

router = Router()

@router.message(CommandStart())
async def handle_start(message: types.Message, bot: Bot, command: CommandObject, state: FSMContext):
    link = await create_start_link(bot, str(message.from_user.id), encode=True)

    await message.answer(f"Приветствую! Ваша персональная ссылка: {link}", reply_markup=menu_kb)

    if command and command.args:
        try:
            payload = decode_payload(command.args)
            if True:
                user_data = await get_user_data(message.from_user.id)
                users_cant_again = user_data.get("users_cant_again") or []
                if not message.from_user.id in users_cant_again:
                    await message.answer("Приветствую! Вы перешли по чужой персональной ссылке.", reply_markup=friend_kb)
                    await state.update_data(test_id=int(payload))
                else:
                    await message.answer("❌ Вы не можете пройти этот тест заново, так как уже проходили его")
        except:
            await message.answer("Неверная персональная ссылка.", reply_markup=menu_kb)

    await add_user(message.from_user.id, link, message.from_user.full_name, message.from_user.username)

@router.message(Command("profile"))
async def handle_profile(message: types.Message):
    user_info = await get_user_data(message.from_user.id)
    answers_str = get_test_str(user_info.get("test_answers"))

    await message.answer(text=(
        f"<b>Профиль</b>\n\n"
        f"<b>Имя:</b> {message.from_user.full_name}\n"
        f"<b>ID:</b> {message.from_user.id}\n\n"
        f"<b>Пройденных тестов:</b> {user_info.get("other_test_passed")}\n"
        f"<b>Количество людей, которые прошли ваш тест:</b> {user_info.get("num_users_passed")}\n\n"
        f"<b>Ваша ссылка на тест:</b> {user_info.get("ref_link")}\n\n"
        f"<b>Ваши ответы на тест:</b>\n\n"
        f"{answers_str if answers_str else "<b>❌Вы пока не создали ответы</b>"}"
        ),
        reply_markup=best_users_passed_kb
    )

@router.message(Command("edit_test"))
async def handle_edit_test(message: types.Message):
    await message.answer("сейчас тебе будут скидываться вопросы", reply_markup=start_quetions_kb)

@router.message(Command("show_answers"))
async def handle_show_answers(message: types.Message):
    user_data = await get_user_data(message.from_user.id)
    test_answers = user_data.get("test_answers")
    answers_str = get_test_str(test_answers)

    await message.answer(text=f"<b>вот ваши ответы:</b>\n\n{answers_str}")