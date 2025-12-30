from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from utils.states import Form
from utils.keyboards import *
from utils.questions import QUESTIONS

router = Router()


@router.message(Form.waiting_for_text_answer, F.text)
async def handle_user_answers(message: types.Message, state: FSMContext):
    data = await state.get_data()
    answer_num = data.get("answer_num")
    test_answers = data.get("test_answers")
    test_type = data.get("test_type")

    if answer_num == 4 and len(message.text) != 4:
        await message.answer(
            text="Скорее всего ты не родился в этом году, введи год рождения в формате из 4 цифр (например, 2006).",
            reply_markup=get_question_keyboard(int(answer_num))
        )
        return
    if answer_num == 3:
        if message.text.isdigit():
            if not (40 <= int(message.text) <= 260):
                await message.answer(
                    text="Пожалуйста, введи свой реальный рост в сантиметрах",
                    reply_markup=get_question_keyboard(int(answer_num))
                )
                return
        else:
            await message.answer(
                    text="Пожалуйста, введи рост в цифрах, без лишних символов",
                reply_markup=get_question_keyboard(int(answer_num))
                )
            return

    if not get_question_keyboard(int(answer_num) + 1):
        await state.update_data(answer_num=int(answer_num) + 1)
    else:
        await state.set_state(Form.waiting_for_answer if test_type == "create" else Form.waiting_for_friend_answer)

    await message.answer(
        text=(
            f"<b>✏️ Вопрос {int(answer_num) + 1} из 15</b>\n\n"
            f"{QUESTIONS[int(answer_num)]}"
        ),
        reply_markup=get_question_keyboard(int(answer_num) + 1)
    )

    test_answers[answer_num - 1] = message.text.lower()
    await state.update_data(test_answers=test_answers)