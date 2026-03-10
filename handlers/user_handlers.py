from datetime import datetime

from aiogram import Bot, Router, types
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link, decode_payload

from database.database import add_user, get_user_data
from handlers.callbacks_handlers import get_test_str
from settings import ADMIN_ID
from utils.keyboards import *

router = Router()

NEW_USER_PROMPT = (
    "<b>👋 Привет!</b>\n\n"
    "Хочешь узнать, насколько хорошо тебя знают друзья?\n\n"
    "Создай тест про себя и отправь его друзьям, это займет всего пару минут. "
    "Посмотрим, как хорошо они тебя знают.\n\n"
    "<i>Нажми кнопку «Начать тест» ниже 👇</i>."
)


async def prompt_create_test(message: types.Message):
    await message.answer(NEW_USER_PROMPT, reply_markup=new_user_start_kb)


def build_start_message(link: str | None) -> str:
    if link:
        return (
            "<b>👋 Привет!</b>\n\n"
            "Я помогу тебе создать тест о себе и проверить, насколько хорошо тебя знают друзья.\n\n"
            "<b>🔗 Твоя персональная ссылка на тест:</b>\n"
            f"{link}\n\n"
            "Отправь её друзьям и узнай, кто знает тебя лучше всех."
        )

    return (
        "<b>👋 Привет!</b>\n\n"
        "Я помогу тебе создать тест о себе и проверить, насколько хорошо тебя знают друзья.\n\n"
        "Ты еще не создал тест, нажми кнопку «Создать тест» ниже 👇\n"
    )


def build_profile_text(user_info: dict, full_name: str, user_id: int) -> str:
    answers_str = get_test_str(user_info.get("test_answers"))
    link_text = user_info.get("ref_link") if user_info.get("test_answers") else "Будет доступна после создания теста."
    answers_text = answers_str if answers_str else "Ты пока не создавал свои ответы на тест."

    return (
        "<b>👤 Твой профиль</b>\n\n"
        f"<b>Имя:</b> <code>{full_name}</code>\n"
        f"<b>ID:</b> <code>{user_id}</code>\n\n"
        f"<b>📝 Пройденных тестов:</b> {user_info.get('other_test_passed')}\n"
        f"<b>👥 Людей, которые прошли твой тест:</b> {user_info.get('num_users_passed')}\n\n"
        f"<b>🔗 Твоя ссылка на тест:</b>\n{link_text}\n\n"
        "<b>📚 Твои ответы на тест:</b>\n\n"
        f"{answers_text}"
    )


@router.message(CommandStart())
async def handle_start(message: types.Message, bot: Bot, command: CommandObject, state: FSMContext):
    link = await create_start_link(bot, str(message.from_user.id), encode=True)
    date = datetime.now().date()
    await add_user(message.from_user.id, link, message.from_user.full_name, message.from_user.username, date)

    user_data = await get_user_data(message.from_user.id)
    await message.answer(
        build_start_message(link if user_data.get("test_answers") else None),
        reply_markup=menu_kb,
    )

    if command and command.args:
        try:
            payload = decode_payload(command.args)
            if payload != str(message.from_user.id):
                friend_data = await get_user_data(int(payload))
                if not friend_data:
                    friend_data = {"test_answers": []}

                users_cant_again = friend_data.get("users_cant_again") or []
                check_test_answers = bool(friend_data.get("test_answers"))

                if message.from_user.id in users_cant_again:
                    await message.answer(
                        "<b>🔄 Ты уже проходил этот тест.</b>\n\n"
                        "Каждый пользователь может пройти тест только один раз."
                    )
                elif not check_test_answers:
                    await message.answer(
                        "<b>⚠️ У этого пользователя пока нет заполненного теста.</b>\n\n"
                        "Когда он создаст ответы, ссылка начнет работать."
                    )
                else:
                    await message.answer(
                        "<b>🌟 Ты перешёл по ссылке друга!</b>\n\n"
                        "Сейчас можешь пройти его тест и проверить, насколько хорошо ты его знаешь.",
                        reply_markup=friend_kb,
                    )
                    await state.update_data(test_id=int(payload))
            else:
                await message.answer(
                    "❌ <b>Нельзя проходить свой же тест.</b>\n\n"
                    "Но ты можешь отправить ссылку друзьям и посмотреть их результаты."
                )
        except Exception:
            await message.answer(
                "⚠️ <b>Неверная или устаревшая персональная ссылка.</b>\n\n"
                "Попробуй получить новую через <code>/start</code> или открыть профиль <code>/profile</code>.",
                reply_markup=menu_kb,
            )


@router.message(Command("profile"))
async def handle_profile(message: types.Message):
    user_info = await get_user_data(message.from_user.id)
    await message.answer(
        text=build_profile_text(user_info, message.from_user.full_name, message.from_user.id),
        reply_markup=best_users_passed_kb,
    )


@router.message(Command("edit_test"))
async def handle_edit_test(message: types.Message):
    await message.answer(
        "<b>✏️ Создавай или изменяй свой тест!</b>\n\n"
        "Буду отправлять вопросы по одному. Отвечай честно.",
        reply_markup=start_quetions_kb,
    )


@router.message(Command("show_answers"))
async def handle_show_answers(message: types.Message):
    user_data = await get_user_data(message.from_user.id)
    answers_str = get_test_str(user_data.get("test_answers"))

    await message.answer(
        "<b>📚 Вот твои текущие ответы на тест:</b>\n\n"
        f"{answers_str if answers_str else 'Пока нет сохранённых ответов.'}"
    )


@router.message(Command("feedback"))
async def handle_feedback(message: types.Message, bot: Bot):
    text = message.text.replace("/feedback", "")

    if len(text) > 10:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                f"📩 <b>Новое сообщение от пользователя</b> "
                f"@{message.from_user.username or 'без_username'}:\n\n{text.strip()}"
            ),
        )
        await message.answer(
            "<b>✅ Спасибо за обратную связь!</b>\n\n"
            "Твоё сообщение отправлено администратору."
        )
    else:
        await message.answer(
            "ℹ️ <b>Сообщение слишком короткое.</b>\n\n"
            "Опиши идею, вопрос или проблему немного подробнее."
        )
