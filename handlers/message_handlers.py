from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from handlers.answers_callbacks_handlers import (
    build_feedback_question_text,
    build_question_text,
    ensure_correct_answers,
)
from utils.keyboards import get_question_keyboard
from utils.questions import QUESTIONS, QUESTIONS_FOR_FRIEND
from utils.states import Form

router = Router()


def validate_birth_year(answer: str) -> str | None:
    if len(answer) == 4 and answer.isdigit():
        return None
    return "Скорее всего, ты не родился в этом году. Введи год рождения в формате из 4 цифр, например: 2006."


def validate_height(answer: str) -> str | None:
    if not answer.isdigit():
        return "Пожалуйста, введи рост цифрами, без лишних символов."

    if 40 <= int(answer) <= 260:
        return None

    return "Пожалуйста, введи свой реальный рост в сантиметрах."


def validate_text_answer(answer_number: int, answer: str) -> str | None:
    validators = {
        3: validate_height,
        4: validate_birth_year,
    }
    validator = validators.get(answer_number)
    if validator is None:
        return None
    return validator(answer)


def get_question_bank(test_type: str) -> list[str]:
    return QUESTIONS if test_type == "create" else QUESTIONS_FOR_FRIEND


async def build_next_message_text(
    state: FSMContext,
    state_data: dict,
    *,
    test_type: str,
    user_answer: str,
    answer_number: int,
    next_question_number: int,
    next_question_text: str,
) -> str:
    if test_type != "answer":
        return build_question_text(next_question_number, next_question_text)

    correct_answers = await ensure_correct_answers(state, state_data)
    correct_answer = correct_answers[answer_number - 1] if len(correct_answers) >= answer_number else ""
    return build_feedback_question_text(
        user_answer,
        correct_answer,
        next_question_number,
        next_question_text,
    )


async def set_next_text_flow_state(state: FSMContext, next_question_number: int, test_type: str) -> None:
    await state.update_data(answer_num=next_question_number)

    keyboard = get_question_keyboard(next_question_number)
    if keyboard is None:
        await state.set_state(Form.waiting_for_text_answer)
        return

    await state.set_state(Form.waiting_for_answer if test_type == "create" else Form.waiting_for_friend_answer)


@router.message(Form.waiting_for_text_answer, F.text)
async def handle_user_answers(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    answer_number = int(state_data.get("answer_num"))
    test_answers = state_data.get("test_answers") or []
    test_type = state_data.get("test_type")
    user_answer = message.text.strip()

    validation_error = validate_text_answer(answer_number, user_answer)
    if validation_error:
        await message.answer(
            text=validation_error,
            reply_markup=get_question_keyboard(answer_number),
        )
        return

    test_answers[answer_number - 1] = user_answer
    next_question_number = answer_number + 1
    question_bank = get_question_bank(test_type)
    next_question_text = question_bank[answer_number]
    next_message_text = await build_next_message_text(
        state,
        state_data,
        test_type=test_type,
        user_answer=user_answer,
        answer_number=answer_number,
        next_question_number=next_question_number,
        next_question_text=next_question_text,
    )

    await set_next_text_flow_state(state, next_question_number, test_type)
    await message.answer(
        text=next_message_text,
        reply_markup=get_question_keyboard(next_question_number),
    )
    await state.update_data(test_answers=test_answers)
