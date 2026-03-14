from datetime import datetime
from html import escape
from typing import Any

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.deep_linking import create_start_link

from database.database import get_user_data, update_after_test_completion, update_after_test_creation
from utils.keyboards import accept_test_kb, get_question_keyboard, get_send_link_kb
from utils.questions import QUESTIONS, QUESTIONS_FOR_FRIEND
from utils.states import Form

router = Router()

TOTAL_QUESTIONS = 15


def normalize_answer(answer: Any) -> str:
    return str(answer).strip().lower()


def is_correct_answer(user_answer: Any, correct_answer: Any) -> bool:
    return normalize_answer(user_answer) == normalize_answer(correct_answer)


def get_answer_status_text(user_answer: Any, correct_answer: Any) -> str:
    return "правильно ✅" if is_correct_answer(user_answer, correct_answer) else "неправильно ❌"


def build_answer_feedback_text(user_answer: Any, correct_answer: Any) -> str:
    verdict = "✅ Правильно!" if is_correct_answer(user_answer, correct_answer) else "❌ Неправильно!"
    correct_answer_text = escape(str(correct_answer).strip()) if str(correct_answer).strip() else "—"
    return f"{verdict}\nПравильный ответ: <b>{correct_answer_text}</b>"


def build_question_text(question_number: int, question_text: str) -> str:
    return f"<b>✏️ Вопрос {question_number} из {TOTAL_QUESTIONS}</b>\n\n{question_text}"


def build_feedback_question_text(
    user_answer: Any,
    correct_answer: Any,
    question_number: int,
    question_text: str,
) -> str:
    return (
        f"{build_answer_feedback_text(user_answer, correct_answer)}\n\n"
        f"{build_question_text(question_number, question_text)}"
    )


def build_test_str(test_answers: list[Any], correct_answers: list[Any] | None = None) -> str | None:
    if not test_answers:
        return None

    lines: list[str] = []
    for index, user_answer in enumerate(test_answers, start=1):
        lines.append(f"<b>{index}. {QUESTIONS_FOR_FRIEND[index - 1]}</b>")
        safe_user_answer = escape(str(user_answer).strip())

        if correct_answers:
            correct_answer = correct_answers[index - 1] if index <= len(correct_answers) else ""
            correct_answer_text = escape(str(correct_answer).strip()) if str(correct_answer).strip() else "—"
            lines.append(
                f"{safe_user_answer} - {get_answer_status_text(user_answer, correct_answer)}\n"
                f"Правильный ответ: <b>{correct_answer_text}</b>"
            )
        else:
            lines.append(safe_user_answer)

        lines.append("")

    return "\n".join(lines).rstrip()


def parse_answer_callback_data(callback_data: str) -> tuple[int | None, str]:
    payload = callback_data.removeprefix("answer_")
    number_raw, _, answer = payload.partition("_")

    try:
        return int(number_raw), answer
    except ValueError:
        return None, answer


def get_answer_by_index(answers: list[Any], answer_number: int) -> Any:
    if len(answers) >= answer_number:
        return answers[answer_number - 1]
    return ""


def build_created_test_preview(test_answers: list[Any]) -> str:
    lines = [
        f"<b>{index}. {QUESTIONS[index - 1]}</b>\n{answer}"
        for index, answer in enumerate(test_answers, start=1)
    ]
    return "\n".join(lines)


def calculate_right_answers(user_answers: list[Any], correct_answers: list[Any]) -> int:
    return sum(
        1
        for index, correct_answer in enumerate(correct_answers)
        if index < len(user_answers) and is_correct_answer(user_answers[index], correct_answer)
    )


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


async def update_state_for_next_question(state: FSMContext, next_question_number: int, form_state) -> None:
    keyboard = get_question_keyboard(next_question_number)
    await state.update_data(answer_num=next_question_number)

    if keyboard is None:
        await state.set_state(Form.waiting_for_text_answer)
        return

    await state.set_state(form_state)


async def ask_next_friend_question(
    callback: CallbackQuery,
    state: FSMContext,
    answer: str,
    correct_answer: Any,
    next_question_number: int,
) -> None:
    await update_state_for_next_question(state, next_question_number, Form.waiting_for_friend_answer)
    await callback.message.edit_text(
        build_feedback_question_text(
            answer,
            correct_answer,
            next_question_number,
            QUESTIONS_FOR_FRIEND[next_question_number - 1],
        ),
        reply_markup=get_question_keyboard(next_question_number),
    )


async def ask_next_create_question(callback: CallbackQuery, state: FSMContext, next_question_number: int) -> None:
    await update_state_for_next_question(state, next_question_number, Form.waiting_for_answer)
    await callback.message.edit_text(
        build_question_text(next_question_number, QUESTIONS[next_question_number - 1]),
        reply_markup=get_question_keyboard(next_question_number),
    )


async def load_friend_test_context(
    callback: CallbackQuery,
    state_data: dict,
) -> tuple[int | None, dict | None, dict | None]:
    friend_id = state_data.get("test_id")
    if not friend_id:
        return None, None, None

    friend_data = await get_user_data(friend_id)
    user_data = await get_user_data(callback.from_user.id)
    return friend_id, friend_data, user_data


def build_completion_payload(
    callback: CallbackQuery,
    friend_data: dict,
    user_data: dict,
    score: int,
) -> dict[str, Any]:
    best_users_passed = friend_data.get("best_users_passed") or {}
    other_test_users = user_data.get("other_test_users") or {}
    users_cant_again = friend_data.get("users_cant_again") or []

    best_users_passed[callback.from_user.username] = score
    other_test_users[friend_data.get("username")] = score
    users_cant_again.append(callback.from_user.id)

    return {
        "num_users_passed": (friend_data.get("num_users_passed") or 0) + 1,
        "best_users_passed": best_users_passed,
        "users_cant_again": users_cant_again,
        "other_test_passed": (user_data.get("other_test_passed") or 0) + 1,
        "other_test_users": other_test_users,
    }


async def notify_test_owner(
    bot: Bot,
    friend_id: int,
    callback: CallbackQuery,
    user_data: dict,
    score: int,
) -> None:
    ref_link = user_data.get("ref_link")
    user_test_answers = user_data.get("test_answers")
    invite_line = f"🔗 Хочешь пройти его(её) тест: {ref_link}" if user_test_answers else ""

    await bot.send_message(
        friend_id,
        "<b>👥 Кто-то прошёл твой тест!</b>\n\n"
        f"Твой друг @{callback.from_user.username} набрал(а) <b>{score}/15</b> правильных ответов 🙌\n"
        f"{invite_line}",
    )


async def finish_friend_test(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    state_data: dict,
    test_answers: list[Any],
) -> None:
    await callback.message.delete()

    friend_id, friend_data, user_data = await load_friend_test_context(callback, state_data)
    if not friend_data or not user_data or friend_id is None:
        await callback.message.answer(
            "⚠️ <b>Произошла ошибка при получении данных.</b>\n\n"
            "Попробуйте позже. Если проблема повторяется, напишите нам через команду <code>/feedback</code>."
        )
        await state.clear()
        return

    friend_test_answers = friend_data.get("test_answers")
    if not friend_test_answers:
        await callback.message.answer(
            "❌ <b>Владелец этого теста ещё не создал свои ответы.</b>\n\n"
            "Попросите его сначала пройти собственный тест, а затем попробуйте снова."
        )
        await state.clear()
        return

    answers_text = build_test_str(test_answers, friend_test_answers) if test_answers else "Ошибка"
    right_answers = calculate_right_answers(test_answers, friend_test_answers)
    completion_payload = build_completion_payload(callback, friend_data, user_data, right_answers)

    await callback.message.answer(
        "<b>✅ Тест пройден!</b>\n\n"
        f"Правильных ответов: <b>{right_answers}/15</b> 🎯\n\n"
        "<b>Твои ответы:</b>\n\n"
        f"{answers_text}"
    )
    await notify_test_owner(bot, friend_id, callback, user_data, right_answers)
    await state.clear()

    await update_after_test_completion(
        test_id=friend_id,
        num_users_passed=completion_payload["num_users_passed"],
        best_users_passed=completion_payload["best_users_passed"],
        users_cant_again=completion_payload["users_cant_again"],
        user_id=callback.from_user.id,
        other_test_passed=completion_payload["other_test_passed"],
        other_test_users=completion_payload["other_test_users"],
        score=right_answers,
    )


async def save_created_test(callback: CallbackQuery, bot: Bot, test_answers: list[Any]) -> None:
    ref_link = await create_start_link(bot, str(callback.from_user.id), encode=True)
    current_date = datetime.now().date()

    await update_after_test_creation(callback.from_user.id, test_answers)
    await callback.message.answer(
        "<b>✅ Тест сохранён!</b>\n\n"
        "Теперь можешь отправлять ссылку друзьям и смотреть, насколько хорошо они тебя знают 🤝",
        reply_markup=get_send_link_kb(ref_link),
    )


@router.callback_query(Form.waiting_for_friend_answer, F.data.startswith("answer_"))
async def handle_friend_answers(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    state_data = await state.get_data()
    test_answers = state_data.get("test_answers") or []
    current_question_number, answer = parse_answer_callback_data(callback.data)

    if current_question_number is None:
        await callback.answer("Неверный формат ответа.", show_alert=True)
        return

    test_answers[current_question_number - 1] = answer
    next_question_number = current_question_number + 1
    correct_answers = await ensure_correct_answers(state, state_data)
    correct_answer = get_answer_by_index(correct_answers, current_question_number)

    await state.update_data(test_answers=test_answers)

    if next_question_number <= TOTAL_QUESTIONS:
        await ask_next_friend_question(
            callback,
            state,
            answer,
            correct_answer,
            next_question_number,
        )
        return

    await finish_friend_test(callback, state, bot, state_data, test_answers)


@router.callback_query(Form.waiting_for_answer, F.data.startswith("answer_"))
async def handle_create_answers(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    state_data = await state.get_data()
    test_answers = state_data.get("test_answers") or []
    current_question_number, answer = parse_answer_callback_data(callback.data)

    if current_question_number is None:
        await callback.answer("Неверный формат ответа.", show_alert=True)
        return

    test_answers[current_question_number - 1] = answer
    next_question_number = current_question_number + 1

    await state.update_data(test_answers=test_answers)

    if next_question_number <= TOTAL_QUESTIONS:
        await ask_next_create_question(callback, state, next_question_number)
        return

    await callback.message.delete()
    await callback.message.answer(
        "<b>✅ Тест заполнен!</b>\n\n"
        "<b>Вот как он выглядит:</b>\n\n"
        f"{build_created_test_preview(test_answers)}",
        reply_markup=accept_test_kb,
    )


@router.callback_query(F.data.startswith("accept_test_"))
async def handle_callbacks_accept_test(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    action = callback.data.removeprefix("accept_test_")
    state_data = await state.get_data()
    test_answers = state_data.get("test_answers") or []

    if action == "accept":
        await save_created_test(callback, bot, test_answers)
    else:
        await callback.message.answer(
            "<b>❌ Сохранение отменено.</b>\n\n"
            "Ты можешь вернуться и создать или изменить тест позже 🙂"
        )

    await callback.message.delete()
    await state.clear()
