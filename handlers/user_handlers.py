from datetime import datetime

from aiogram import Bot, Router, types
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link, decode_payload

from database.database import add_user, get_user_data
from handlers.callbacks_handlers import get_test_str
from settings import ADMIN_ID
from utils.keyboards import (
    best_users_passed_kb,
    friend_kb,
    menu_kb,
    new_user_start_kb,
    start_quetions_kb,
)

router = Router()

MIN_FEEDBACK_LENGTH = 10

NEW_USER_PROMPT = (
    "<b>🔥 Кто знает тебя лучше всех?</b> Вторая половинка, лучший друг или мама?\n\n"
    "Всего 15 вопросов отделяют тебя от ответа. Создай свой личный тест, отправь ссылку друзьям и смотри, как они потеют, пытаясь угадать твои секреты! 😈\n\n"
    "<i>Жми кнопку ниже и давай узнаем правду! 👇</i>"
)


async def prompt_create_test(message: types.Message):
    await message.answer(NEW_USER_PROMPT, reply_markup=new_user_start_kb)


def build_start_message(link: str | None) -> str:
    if link:
        return (
            f"<b>👋 Привет!</b>\n\n"
            "Создай тест о себе и проверь, насколько хорошо тебя знают друзья.\n\n"
            "<b>🔗 Твоя персональная ссылка на тест:</b>\n"
            f"<code>{link}</code>\n\n"
            "🔁 <u>Отправь её друзьям и узнай, кто из них лучше всех!</u>"
        )

    return (
        "<b>🔥 Кто знает тебя лучше всех?</b> Вторая половинка, лучший друг или мама?\n\n"
        "Я помогу тебе создать тест о себе и проверить это.\n\n"
        "Ты еще не создал тест, жми кнопку «Создать тест» ниже 👇\n"
    )


def build_profile_text(user_info: dict, full_name: str, user_id: int) -> str:
    answers_text = get_test_str(user_info.get("test_answers")) or "Ты пока не создавал свои ответы на тест."
    link_text = (
        user_info.get("ref_link")
        if user_info.get("test_answers")
        else "Будет доступна после создания теста."
    )

    return (
        "<b>👤 Твой профиль</b>\n\n"
        f"<b>Имя:</b> <code>{full_name}</code>\n"
        f"<b>ID:</b> <code>{user_id}</code>\n\n"
        f"<b>📝 Пройденных тестов:</b> {user_info.get('other_test_passed') or 0}\n"
        f"<b>👥 Людей, которые прошли твой тест:</b> {user_info.get('num_users_passed') or 0}\n\n"
        f"<b>🔗 Твоя ссылка на тест:</b>\n{link_text}\n\n"
        "<b>📚 Твои ответы на тест:</b>\n\n"
        f"{answers_text}"
    )


async def ensure_user_exists(message: types.Message, bot: Bot) -> tuple[str, dict]:
    start_link = await create_start_link(bot, str(message.from_user.id), encode=True)
    current_date = datetime.now().date()

    await add_user(
        message.from_user.id,
        start_link,
        message.from_user.full_name,
        message.from_user.username,
        current_date,
    )
    user_data = await get_user_data(message.from_user.id)
    return start_link, user_data


async def show_start_menu(message: types.Message, link: str | None) -> None:
    await message.answer(build_start_message(link), reply_markup=menu_kb)


async def handle_repeated_friend_test_attempt(message: types.Message) -> None:
    await message.answer(
        "<b>🔄 Ты уже проходил этот тест.</b>\n\n"
        "Каждый пользователь может пройти тест только один раз."
    )


async def handle_empty_friend_test(message: types.Message) -> None:
    await message.answer(
        "<b>⚠️ У этого пользователя пока нет заполненного теста.</b>\n\n"
        "Когда он создаст ответы, ссылка начнет работать."
    )


async def handle_self_test_attempt(message: types.Message) -> None:
    await message.answer(
        "❌ <b>Нельзя проходить свой же тест.</b>\n\n"
        "Но ты можешь отправить ссылку друзьям и посмотреть их результаты."
    )


async def handle_friend_test_entry(message: types.Message, state: FSMContext, friend_id: int) -> None:
    await message.answer(
        "<b>🚨 Вызов принят!</b>\n\n"
        "Твой друг считает, что ты его знаешь. Давай проверим, так ли это на самом деле!\n\n"
        "Ответишь на 15 вопросов без ошибок — получишь респект и звание лучшего друга. Ошибешься — ну... будет повод пообщаться! 😅\n\n"
        "<i>Жми «Пройти тест друга», если не боишься! 👇</i>",
        reply_markup=friend_kb,
    )
    await state.update_data(test_id=friend_id)


async def handle_invalid_deep_link(message: types.Message) -> None:
    await message.answer(
        "⚠️ <b>Неверная или устаревшая персональная ссылка.</b>\n\n"
        "Попробуй получить новую через <code>/start</code> или открыть профиль <code>/profile</code>.",
        reply_markup=menu_kb,
    )


async def process_start_payload(message: types.Message, state: FSMContext, payload: str) -> None:
    if payload == str(message.from_user.id):
        await handle_self_test_attempt(message)
        return

    friend_id = int(payload)
    friend_data = await get_user_data(friend_id) or {"test_answers": []}
    users_cant_again = friend_data.get("users_cant_again") or []

    if message.from_user.id in users_cant_again:
        await handle_repeated_friend_test_attempt(message)
        return

    if not friend_data.get("test_answers"):
        await handle_empty_friend_test(message)
        return

    await handle_friend_test_entry(message, state, friend_id)


def extract_feedback_text(message_text: str | None) -> str:
    if not message_text:
        return ""
    return message_text.partition(" ")[2].strip()


def build_feedback_admin_message(message: types.Message, feedback_text: str) -> str:
    username = message.from_user.username or "без_username"
    return f"📩 <b>Новое сообщение от пользователя</b> @{username}:\n\n{feedback_text}"


@router.message(CommandStart())
async def handle_start(message: types.Message, bot: Bot, command: CommandObject, state: FSMContext):
    link, user_data = await ensure_user_exists(message, bot)
    await show_start_menu(message, link if user_data.get("test_answers") else None)

    if not command or not command.args:
        return

    try:
        payload = decode_payload(command.args)
        await process_start_payload(message, state, payload)
    except Exception:
        await handle_invalid_deep_link(message)


@router.message(Command("profile"))
async def handle_profile(message: types.Message):
    user_info = await get_user_data(message.from_user.id) or {}
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
    user_data = await get_user_data(message.from_user.id) or {}
    answers_text = get_test_str(user_data.get("test_answers"))

    await message.answer(
        "<b>📚 Вот твои текущие ответы на тест:</b>\n\n"
        f"{answers_text if answers_text else 'Пока нет сохранённых ответов.'}"
    )


@router.message(Command("feedback"))
async def handle_feedback(message: types.Message, bot: Bot):
    feedback_text = extract_feedback_text(message.text)

    if len(feedback_text) <= MIN_FEEDBACK_LENGTH:
        await message.answer(
            "ℹ️ <b>Сообщение слишком короткое.</b>\n\n"
            "Опиши идею, вопрос или проблему немного подробнее."
        )
        return

    await bot.send_message(
        chat_id=ADMIN_ID,
        text=build_feedback_admin_message(message, feedback_text),
    )
    await message.answer(
        "<b>✅ Спасибо за обратную связь!</b>\n\n"
        "Твоё сообщение отправлено администратору."
    )
