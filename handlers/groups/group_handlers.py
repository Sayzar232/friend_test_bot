import re
from aiogram import Bot, F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.database import get_user_data, get_user_id_by_username, update_after_test_completion
from handlers.answers_callbacks_handlers import (
    build_feedback_question_text,
    build_question_text,
    calculate_right_answers,
    get_answer_by_index,
    is_correct_answer,
    notify_test_owner,
    TOTAL_QUESTIONS,
)
from utils.keyboards import get_group_question_keyboard, get_group_start_kb
from utils.questions import QUESTIONS_FOR_FRIEND

router = Router()
router.message.filter(F.chat.type.in_({"group", "supergroup"}))
router.callback_query.filter(F.message.chat.type.in_({"group", "supergroup"}))


def get_friendship_level(score: int) -> str:
    if score <= 5:
        return "Знакомый 😐"
    elif score <= 10:
        return "Товарищ 🙂"
    elif score <= 14:
        return "Хороший друг 🤝"
    else:
        return "Лучший друг 🫂"


@router.message(F.text.regexp(r"^@([A-Za-z0-9_]+)\s+тест$"))
async def handle_group_test_command(message: types.Message, match: re.Match):
    username = match.group(1)
    
    friend_id = await get_user_id_by_username(username)
    if not friend_id:
        await message.answer(f"Пользователь @{username} не найден в базе бота.")
        return
        
    if friend_id == message.from_user.id:
        await message.answer("Ты не можешь проходить свой собственный тест!")
        return
    
    friend_data = await get_user_data(friend_id)
    if not friend_data or not friend_data.get("test_answers"):
        await message.answer(f"У пользователя @{username} еще нет заполненного теста.")
        return
        
    users_cant_again = friend_data.get("users_cant_again") or []
    if message.from_user.id in users_cant_again:
        await message.answer("Ты уже проходил этот тест!")
        return

    await message.answer(
        f"<b>Начать тест на знание @{username}?</b>\n\nВнимание: нажимая «Начать тест», именно ты будешь его проходить.",
        reply_markup=get_group_start_kb(friend_id)
    )


@router.callback_query(F.data == "grp_cancel")
async def handle_grp_cancel(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()


@router.callback_query(F.data.startswith("grp_start_"))
async def handle_grp_start(callback: CallbackQuery, state: FSMContext):
    friend_id_str = callback.data.removeprefix("grp_start_")
    if not friend_id_str.isdigit():
        await callback.answer("Ошибка данных", show_alert=True)
        return
        
    friend_id = int(friend_id_str)
    
    if friend_id == callback.from_user.id:
        await callback.answer("Ты не можешь проходить свой собственный тест!", show_alert=True)
        return

    friend_data = await get_user_data(friend_id)
    if not friend_data or not friend_data.get("test_answers"):
        await callback.answer("У этого пользователя нет заполненного теста.", show_alert=True)
        return
        
    users_cant_again = friend_data.get("users_cant_again") or []
    if callback.from_user.id in users_cant_again:
        await callback.answer("Ты уже проходил этот тест!", show_alert=True)
        return

    # Записываем состояние для пользователя в этой группе
    await state.update_data(
        test_id=friend_id,
        test_answers=[],
        answer_num=1,
        test_message_id=callback.message.message_id
    )
    
    first_question = QUESTIONS_FOR_FRIEND[0]
    await callback.message.edit_text(
        f"Тест проходит: {callback.from_user.mention_html()}\n\n" +
        build_question_text(1, first_question),
        reply_markup=get_group_question_keyboard(1)
    )
    await callback.answer()


def parse_grp_answer_callback_data(callback_data: str) -> tuple[int | None, str]:
    payload = callback_data.removeprefix("grp_ans_")
    number_raw, _, answer = payload.partition("_")

    try:
        return int(number_raw), answer
    except ValueError:
        return None, answer


@router.callback_query(F.data.startswith("grp_ans_"))
async def handle_grp_ans(callback: CallbackQuery, state: FSMContext, bot: Bot):
    state_data = await state.get_data()
    test_message_id = state_data.get("test_message_id")
    
    # Проверка, что нажимает тот, кто начал тест
    if not test_message_id or test_message_id != callback.message.message_id:
        await callback.answer("Это не твой тест!", show_alert=True)
        return
        
    current_question_number, answer = parse_grp_answer_callback_data(callback.data)
    if current_question_number is None:
        await callback.answer("Неверный формат ответа.", show_alert=True)
        return
        
    test_answers = state_data.get("test_answers") or []
    
    # Расширяем массив, если нужно (на всякий случай)
    while len(test_answers) < current_question_number:
        test_answers.append("")
    test_answers[current_question_number - 1] = answer
    
    friend_id = state_data.get("test_id")
    friend_data = await get_user_data(friend_id)
    correct_answers = friend_data.get("test_answers") if friend_data else []
    correct_answer = get_answer_by_index(correct_answers, current_question_number)
    
    # Выводим алерт с правильностью ответа
    is_correct = is_correct_answer(answer, correct_answer)
    status_emoji = "✅ Правильно!" if is_correct else "❌ Неправильно!"
    alert_text = f"{status_emoji}\n\nТвой ответ: {answer}\nПравильный: {correct_answer if correct_answer else '—'}"
    await callback.answer(alert_text, show_alert=True)
    
    next_question_number = current_question_number + 1
    await state.update_data(test_answers=test_answers, answer_num=next_question_number)
    
    if next_question_number <= TOTAL_QUESTIONS:
        # Редактируем сообщение для следующего вопроса
        next_question_text = QUESTIONS_FOR_FRIEND[next_question_number - 1]
        await callback.message.edit_text(
            f"Тест проходит: {callback.from_user.mention_html()}\n\n" +
            build_question_text(next_question_number, next_question_text),
            reply_markup=get_group_question_keyboard(next_question_number)
        )
    else:
        # Тест завершен
        right_answers = calculate_right_answers(test_answers, correct_answers)
        friendship_level = get_friendship_level(right_answers)
        
        user_data = await get_user_data(callback.from_user.id)
        # Если юзера нет в БД бота, то user_data вернет пустую структуру с нулями, это нормально
        
        await callback.message.edit_text(
            f"🎉 {callback.from_user.mention_html()} завершил(а) тест на знание @{friend_data.get('username', friend_id)}!\n\n"
            f"🎯 Результат: <b>{right_answers}/{TOTAL_QUESTIONS}</b> правильных ответов.\n"
            f"Уровень: <b>{friendship_level}</b>"
        )
        await state.clear()
        
        # Обновляем статистику
        best_users_passed = friend_data.get("best_users_passed") or {}
        other_test_users = user_data.get("other_test_users") or {}
        users_cant_again = friend_data.get("users_cant_again") or []
        
        best_users_passed[callback.from_user.username or str(callback.from_user.id)] = right_answers
        other_test_users[friend_data.get("username") or str(friend_id)] = right_answers
        users_cant_again.append(callback.from_user.id)
        
        await update_after_test_completion(
            test_id=friend_id,
            num_users_passed=(friend_data.get("num_users_passed") or 0) + 1,
            best_users_passed=best_users_passed,
            users_cant_again=users_cant_again,
            user_id=callback.from_user.id,
            other_test_passed=(user_data.get("other_test_passed") or 0) + 1,
            other_test_users=other_test_users,
            score=right_answers,
        )
        
        # Уведомляем владельца теста
        await notify_test_owner(bot, friend_id, callback, user_data, right_answers)
