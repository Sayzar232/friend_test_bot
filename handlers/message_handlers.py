from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from handlers.answers_callbacks_handlers import (
    build_feedback_question_text,
    build_question_text,
    ensure_correct_answers,
)
from utils.keyboards import *
from utils.questions import QUESTIONS, QUESTIONS_FOR_FRIEND
from utils.states import Form

router = Router()


@router.message(Form.waiting_for_text_answer, F.text)
async def handle_user_answers(message: types.Message, state: FSMContext):
    data = await state.get_data()
    answer_num = int(data.get("answer_num"))
    test_answers = data.get("test_answers")
    test_type = data.get("test_type")
    user_answer = message.text.strip()

    if answer_num == 4 and len(message.text) != 4:
        await message.answer(
            text="Скорее всего, ты не родился в этом году. Введи год рождения в формате из 4 цифр, например: 2006.",
            reply_markup=get_question_keyboard(answer_num),
        )
        return

    if answer_num == 3:
        if message.text.isdigit():
            if not (40 <= int(message.text) <= 260):
                await message.answer(
                    text="Пожалуйста, введи свой реальный рост в сантиметрах.",
                    reply_markup=get_question_keyboard(answer_num),
                )
                return
        else:
            await message.answer(
                text="Пожалуйста, введи рост цифрами, без лишних символов.",
                reply_markup=get_question_keyboard(answer_num),
            )
            return

    test_answers[answer_num - 1] = user_answer
    next_question_number = answer_num + 1
    next_question = QUESTIONS[answer_num] if test_type == "create" else QUESTIONS_FOR_FRIEND[answer_num]

    if test_type == "answer":
        correct_answers = await ensure_correct_answers(state, data)
        correct_answer = correct_answers[answer_num - 1] if len(correct_answers) >= answer_num else ""
        next_message_text = build_feedback_question_text(
            user_answer,
            correct_answer,
            next_question_number,
            next_question,
        )
    else:
        next_message_text = build_question_text(next_question_number, next_question)

    if not get_question_keyboard(next_question_number):
        await state.update_data(answer_num=next_question_number)
    else:
        await state.set_state(Form.waiting_for_answer if test_type == "create" else Form.waiting_for_friend_answer)

    await message.answer(
        text=next_message_text,
        reply_markup=get_question_keyboard(next_question_number),
    )

    await state.update_data(test_answers=test_answers)
