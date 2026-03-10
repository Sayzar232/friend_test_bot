from datetime import datetime
from html import escape

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.deep_linking import create_start_link

from database.database import *
from utils.keyboards import *
from utils.questions import QUESTIONS, QUESTIONS_FOR_FRIEND
from utils.states import Form

router = Router()


def normalize_answer(answer) -> str:
    return str(answer).strip().lower()


def is_correct_answer(user_answer, correct_answer) -> bool:
    return normalize_answer(user_answer) == normalize_answer(correct_answer)


def get_answer_status_text(user_answer, correct_answer) -> str:
    return "правильно ✅" if is_correct_answer(user_answer, correct_answer) else "неправильно ❌"


def build_answer_feedback_text(user_answer, correct_answer) -> str:
    verdict = "✅ Правильно!" if is_correct_answer(user_answer, correct_answer) else "❌ Неправильно!"
    correct_answer_text = escape(str(correct_answer).strip()) if str(correct_answer).strip() else "—"
    return f"{verdict}\nПравильный ответ: <b>{correct_answer_text}</b>"


def build_question_text(question_number: int, question_text: str) -> str:
    return f"<b>✏️ Вопрос {question_number} из 15</b>\n\n{question_text}"


def build_feedback_question_text(user_answer, correct_answer, question_number: int, question_text: str) -> str:
    return (
        f"{build_answer_feedback_text(user_answer, correct_answer)}\n\n"
        f"{build_question_text(question_number, question_text)}"
    )


def get_test_str(test_answers, correct_answers=None):
    if not test_answers:
        return None

    answers_str = ""
    for i, user_answer in enumerate(test_answers):
        answers_str += f"<b>{i + 1}. {QUESTIONS_FOR_FRIEND[i]}</b>\n"
        if correct_answers:
            correct_answer = correct_answers[i] if i < len(correct_answers) else ""
            correct_answer_text = escape(str(correct_answer).strip()) if str(correct_answer).strip() else "—"
            answers_str += (
                f"{escape(str(user_answer).strip())} - {get_answer_status_text(user_answer, correct_answer)}\n"
                f"Правильный ответ: <b>{correct_answer_text}</b>\n\n"
            )
        else:
            answers_str += f"{escape(str(user_answer).strip())}\n\n"

    return answers_str.rstrip()


async def ensure_correct_answers(state: FSMContext, state_data: dict) -> list:
    correct_answers = state_data.get("correct_answers")
    if correct_answers:
        return correct_answers

    friend_id = state_data.get("test_id")
    if not friend_id:
        return []

    friend_data = await get_user_data(friend_id)
    correct_answers = friend_data.get("test_answers") if friend_data else []
    await state.update_data(correct_answers=correct_answers or [])
    return correct_answers or []


@router.callback_query(Form.waiting_for_friend_answer, F.data.startswith("answer_"))
async def handle_friend_answers(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    state_data = await state.get_data()
    test_answers = state_data.get("test_answers")
    data = callback.data.replace("answer_", "")
    parts = data.split("_", 1)
    num_str = parts[0]
    answer = parts[1] if len(parts) > 1 else ""

    try:
        cur_num = int(num_str)
    except ValueError:
        await callback.answer("Неверный формат ответа.", show_alert=True)
        return

    test_answers[cur_num - 1] = answer
    correct_answers = await ensure_correct_answers(state, state_data)
    correct_answer = correct_answers[cur_num - 1] if len(correct_answers) >= cur_num else ""
    next_num = cur_num + 1

    await state.update_data(test_answers=test_answers, answer_num=next_num)

    if next_num <= 15:
        kb = get_question_keyboard(next_num)
        if kb is None:
            await state.set_state(Form.waiting_for_text_answer)
        else:
            await state.set_state(Form.waiting_for_friend_answer)

        await callback.message.edit_text(
            build_feedback_question_text(answer, correct_answer, next_num, QUESTIONS_FOR_FRIEND[next_num - 1]),
            reply_markup=kb,
        )
        return

    await callback.message.delete()

    friend_id = state_data.get("test_id")
    friend_data = await get_user_data(friend_id)
    user_data = await get_user_data(callback.from_user.id)

    if not friend_data or not user_data:
        await callback.message.answer(
            "⚠️ <b>Произошла ошибка при получении данных.</b>\n\n"
            "Попробуйте позже. Если проблема повторяется, напишите нам через команду <code>/feedback</code>."
        )
        await state.clear()
        return

    num_users_passed = friend_data.get("num_users_passed") or 0
    best_users_passed = friend_data.get("best_users_passed") or {}
    users_cant_again = friend_data.get("users_cant_again") or []
    other_test_passed = user_data.get("other_test_passed") or 0
    ref_link = user_data.get("ref_link")
    user_test_answers = user_data.get("test_answers")
    other_test_users = user_data.get("other_test_users") or {}
    friend_test = friend_data.get("test_answers")

    if not friend_test:
        await callback.message.answer(
            "❌ <b>Владелец этого теста ещё не создал свои ответы.</b>\n\n"
            "Попросите его сначала пройти собственный тест, а затем попробуйте снова."
        )
        await state.clear()
        return

    answers_str = get_test_str(test_answers, friend_test) if test_answers else "Ошибка"
    num_right_answers = sum(
        1 for ind, correct in enumerate(friend_test)
        if is_correct_answer(test_answers[ind], correct)
    )
    best_users_passed.update({callback.from_user.username: num_right_answers})
    other_test_users.update({friend_data.get("username"): num_right_answers})
    users_cant_again.append(callback.from_user.id)

    await callback.message.answer(
        "<b>✅ Тест пройден!</b>\n\n"
        f"Правильных ответов: <b>{num_right_answers}/15</b> 🎯\n\n"
        "<b>Твои ответы:</b>\n\n"
        f"{answers_str}"
    )
    await bot.send_message(
        friend_id,
        "<b>👥 Кто-то прошёл твой тест!</b>\n\n"
        f"Твой друг @{callback.from_user.username} набрал(а) <b>{num_right_answers}/15</b> правильных ответов 🙌\n"
        f"{f'🔗 Хочешь пройти его(её) тест: {ref_link}' if user_test_answers else ''}"
    )
    await state.clear()

    await update_after_test_completion(
        test_id=friend_id,
        num_users_passed=num_users_passed + 1,
        best_users_passed=best_users_passed,
        users_cant_again=users_cant_again,
        user_id=callback.from_user.id,
        other_test_passed=other_test_passed + 1,
        other_test_users=other_test_users,
        score=num_right_answers,
    )


@router.callback_query(Form.waiting_for_answer, F.data.startswith("answer_"))
async def handle_create_answers(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    state_data = await state.get_data()
    test_answers = state_data.get("test_answers")
    data = callback.data.replace("answer_", "")
    parts = data.split("_", 1)
    num_str = parts[0]
    answer = parts[1] if len(parts) > 1 else ""

    try:
        cur_num = int(num_str)
    except ValueError:
        await callback.answer("Неверный формат ответа.", show_alert=True)
        return

    test_answers[cur_num - 1] = answer
    next_num = cur_num + 1

    await state.update_data(test_answers=test_answers, answer_num=next_num)

    if next_num <= 15:
        kb = get_question_keyboard(next_num)
        if kb is None:
            await state.set_state(Form.waiting_for_text_answer)
        else:
            await state.set_state(Form.waiting_for_answer)

        await callback.message.edit_text(
            build_question_text(next_num, QUESTIONS[next_num - 1]),
            reply_markup=kb,
        )
        return

    answers_str = ""
    for i in range(len(test_answers)):
        answers_str += f"<b>{i + 1}. {QUESTIONS[i]}</b>\n{test_answers[i]}\n"

    await callback.message.delete()
    await callback.message.answer(
        "<b>✅ Тест заполнен!</b>\n\n"
        "<b>Вот как он выглядит:</b>\n\n"
        f"{answers_str}",
        reply_markup=accept_test_kb,
    )


@router.callback_query(F.data.startswith("accept_test_"))
async def handle_callbacks_accept_test(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    data = callback.data.replace("accept_test_", "")
    state_data = await state.get_data()
    test_answers = state_data.get("test_answers")

    if data == "accept":
        ref_link = await create_start_link(bot, str(callback.from_user.id), encode=True)
        date = datetime.now().date()
        await add_user(callback.from_user.id, ref_link, callback.from_user.full_name, callback.from_user.username, date)
        await update_after_test_creation(callback.from_user.id, test_answers)
        await callback.message.answer(
            "<b>✅ Тест сохранён!</b>\n\n"
            "Теперь можешь отправлять ссылку друзьям и смотреть, насколько хорошо они тебя знают 🤝",
            reply_markup=get_send_link_kb(ref_link),
        )
    else:
        await callback.message.answer(
            "<b>❌ Сохранение отменено.</b>\n\n"
            "Ты можешь вернуться и создать или изменить тест позже 🙂"
        )

    await callback.message.delete()
    await state.clear()
