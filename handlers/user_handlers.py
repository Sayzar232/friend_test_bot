from aiogram import Router, types, F, Bot
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.utils.deep_linking import create_start_link, decode_payload
from aiogram.fsm.context import FSMContext

from utils.keyboards import *
from utils.states import Form
from database.database import add_user, get_user_data
from handlers.callbacks_handlers import get_test_str
from settings import ADMIN_ID

from datetime import datetime

router = Router()

@router.message(CommandStart())
async def handle_start(message: types.Message, bot: Bot, command: CommandObject, state: FSMContext):
    link = await create_start_link(bot, str(message.from_user.id), encode=True)
    date = datetime.now().date()

    await message.answer(
        "<b>👋 Привет!</b>\n\n"
        "Я помогу тебе создать увлекательный тест о себе и проверить, насколько хорошо тебя знают друзья 😊\n\n"
        "<b>🔗 Твоя персональная ссылка на тест:</b>\n"
        f"{link}\n\n"
        "Отправь её друзьям и узнай, кто знает тебя лучше всех 🧠✨",
        reply_markup=menu_kb
    )

    if command and command.args:
        try:
            payload = decode_payload(command.args)
            if payload != str(message.from_user.id):
                user_data = await get_user_data(message.from_user.id)
                friend_data = await get_user_data(int(payload))

                # Защита на случай, если в БД ещё нет записи
                if not user_data:
                    user_data = {
                        'users_cant_again': [],
                        'test_answers': [],
                        'other_test_passed': 0,
                    }
                if not friend_data:
                    friend_data = {'test_answers': []}

                users_cant_again = user_data.get("users_cant_again") or []
                check_test_answers = True if friend_data.get("test_answers") else False
                if message.from_user.id in users_cant_again:
                    await message.answer(
                        "❌ <b>Вы уже проходили этот тест.</b>\n\n"
                        "Каждый пользователь может пройти тест друга только один раз, "
                        "чтобы результаты оставались честными и точными 😉"
                    )
                elif not check_test_answers:
                    await message.answer(
                        "⚠️ <b>Этот пользователь еще не создал свой тест.</b>\n\n"
                        "Попросите его сначала создать тест, а затем попробуйте снова 😊"
                    )
                else:
                    await message.answer(
                        "<b>🌟 Ты перешёл по персональной ссылке друга!</b>\n\n"
                        "Сейчас ты сможешь пройти его тест и проверить, насколько хорошо ты его знаешь 😎",
                        reply_markup=friend_kb
                    )
                    await state.update_data(test_id=int(payload))
            else:
                await message.answer(
                    "❌ <b>Нельзя проходить свой же тест.</b>\n\n"
                    "Но ты можешь отправить ссылку друзьям и посмотреть, как хорошо знают тебя они 🤝"
                )
        except:
            await message.answer(
                "⚠️ <b>Неверная или устаревшая персональная ссылка.</b>\n\n"
                "Попробуй снова получить ссылку через команду <code>/start</code> или из профиля <code>/profile</code>.",
                reply_markup=menu_kb
            )

    await add_user(message.from_user.id, link, message.from_user.full_name, message.from_user.username, date)

@router.message(Command("profile"))
async def handle_profile(message: types.Message):
    user_info = await get_user_data(message.from_user.id)
    if not user_info:
        user_info = {
            'other_test_passed': 0,
            'num_users_passed': 0,
            'ref_link': '',
            'test_answers': []
        }
    answers_str = get_test_str(user_info.get("test_answers"))

    await message.answer(
        text=(
            "<b>👤 Твой профиль</b>\n\n"
            f"<b>Имя:</b> {message.from_user.full_name}\n"
            f"<b>ID:</b> {message.from_user.id}\n\n"
            f"<b>📝 Пройденных тестов:</b> {user_info.get('other_test_passed')}\n"
            f"<b>👥 Людей, которые прошли твой тест:</b> {user_info.get('num_users_passed')}\n\n"
            f"<b>🔗 Твоя ссылка на тест:</b>\n{user_info.get('ref_link')}\n\n"
            "<b>📚 Твои ответы на тест:</b>\n\n"
            f"{answers_str if answers_str else '<b>❌ Ты пока не создал свои ответы на тест.</b>\\n\\nНажми «Создать/изменить тест», чтобы заполнить его ✏️'}"
        ),
        reply_markup=best_users_passed_kb
    )

@router.message(Command("edit_test"))
async def handle_edit_test(message: types.Message):
    await message.answer(
        "<b>✏️ Давай создадим или изменим твой тест!</b>\n\n"
        "Сейчас я буду по очереди отправлять тебе вопросы. Отвечай честно — так друзьям будет интереснее проходить тест 😉",
        reply_markup=start_quetions_kb
    )

@router.message(Command("show_answers"))
async def handle_show_answers(message: types.Message):
    user_data = await get_user_data(message.from_user.id)
    if not user_data:
        user_data = {'test_answers': []}
    test_answers = user_data.get("test_answers")
    answers_str = get_test_str(test_answers)

    await message.answer(
        text=(
            "<b>📚 Вот твои текущие ответы на тест:</b>\n\n"
            f"{answers_str if answers_str else '❌ <b>Пока нет сохранённых ответов.</b> Создай или обнови тест через команду <code>/edit_test</code> ✏️'}"
        )
    )

@router.message(Command("feedback"))
async def handle_edit_test(message: types.Message, bot: Bot):
    text = message.text.replace("/feedback", "")

    if len(text) > 10:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 <b>Новое сообщение от пользователя</b> @{message.from_user.username or 'без_username'}:\n\n{text.strip()}"
        )
        await message.answer(
            "✅ <b>Спасибо за обратную связь!</b>\n\n"
            "Твоё сообщение отправлено администратору. Если будет что-то важное — мы обязательно ответим 🙂"
        )
    else:
        await message.answer(
            "ℹ️ <b>Сообщение слишком короткое.</b>\n\n"
            "Постарайся описать свою идею, вопрос или проблему чуть подробнее, чтобы мы могли помочь максимально эффективно 🙌"
        )