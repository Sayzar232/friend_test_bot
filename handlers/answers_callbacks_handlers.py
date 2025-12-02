from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from utils.states import Form
from utils.questions import QUESTIONS
from utils.keyboards import *
from database.database import *

router = Router()

def get_test_str(test_answers):
    if test_answers:
        answers_str = ""
        for i in range(len(test_answers)):
            answers_str += f"<b>{i + 1}. {QUESTIONS[i]}</b>\n{test_answers[i]}\n"

        return answers_str
    return None

@router.callback_query(Form.waiting_for_friend_answer, F.data.startswith("answer_"))
async def handle_friend_answers(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()

    state_data = await state.get_data()
    test_answers = state_data.get("test_answers")
    data = callback.data.replace("answer_", "")

    if data[1].isdigit():
        answer_num = data[:2]
        answer = data[3:]
    else:
        answer_num = data[0]
        answer = data[2:]

    test_answers[int(answer_num) - 1] = answer
    await state.update_data(test_answers=test_answers)

    if not int(answer_num) >= 15:
        if not get_question_keyboard(int(answer_num) + 1):
            await state.set_state(Form.waiting_for_text_answer)
            await state.update_data(answer_num=int(answer_num) + 1)

        await callback.message.edit_text(
            text=(
                f"<b>✏️ Вопрос {int(answer_num) + 1} из 15</b>\n\n"
                f"{QUESTIONS[int(answer_num)]}"
            ),
            reply_markup=get_question_keyboard(int(answer_num) + 1)
        )

    else:
        answers_str = get_test_str(test_answers) if test_answers else "Ошибка"

        await callback.message.delete()

        friend_id = state_data.get("test_id")
        friend_data = await get_user_data(friend_id)
        user_data = await get_user_data(callback.from_user.id)

        if not friend_data or not user_data:
            await callback.message.answer(
                "⚠️ <b>Произошла ошибка при получении данных.</b>\n\n"
                "Попробуйте позже. Если проблема повторяется — напишите нам через команду <code>/feedback</code> 🛠"
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
                "Попросите его сначала пройти собственный тест, чтобы результаты были корректными, а затем попробуйте снова 🙂"
            )
            await state.clear()
            return

        num_right_answers = len([1 for ind, i in enumerate(friend_test) if i == test_answers[ind]])
        best_users_passed.update({callback.from_user.username: num_right_answers})
        other_test_users.update({friend_data.get("username"): num_right_answers})
        users_cant_again.append(callback.from_user.id)

        await callback.message.answer(
            "<b>✅ Ты закончил(а) тест!</b>\n\n"
            f"Правильных ответов: <b>{num_right_answers}/15</b> 🎯\n\n"
            "<b>Вот твои ответы:</b>\n\n"
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
            friend_id=friend_id,
            num_users_passed=num_users_passed + 1,
            best_users_passed=best_users_passed,
            users_cant_again=users_cant_again,
            user_id=callback.from_user.id,
            other_test_passed=other_test_passed + 1,
            other_test_users=other_test_users
        )

        return

@router.callback_query(Form.waiting_for_answer, F.data.startswith("answer_"))
async def handle_create_answers(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    state_data = await state.get_data()
    test_answers = state_data.get("test_answers")
    data = callback.data.replace("answer_", "")

    if data[1].isdigit():
        answer_num = data[:2]
        answer = data[3:]
    else:
        answer_num = data[0]
        answer = data[2:]

    test_answers[int(answer_num) - 1] = answer
    await state.update_data(test_answers=test_answers)

    if not int(answer_num) >= 15:
        if not get_question_keyboard(int(answer_num) + 1):
            await state.set_state(Form.waiting_for_text_answer)
            await state.update_data(answer_num=int(answer_num) + 1)

        await callback.message.edit_text(
            text=(
                f"<b>✏️ Вопрос {int(answer_num) + 1} из 15</b>\n\n"
                f"{QUESTIONS[int(answer_num)]}"
            ),
            reply_markup=get_question_keyboard(int(answer_num) + 1)
        )

    else:
        answers_str = ""
        for i in range(len(test_answers)):
            answers_str += f"<b>{i + 1}. {QUESTIONS[i]}</b>\n{test_answers[i]}\n"

        await callback.message.delete()
        await callback.message.answer(
            "<b>✅ Ты заполнил(а) все ответы!</b>\n\n"
            "<b>Вот как выглядит твой тест:</b>\n\n"
            f"{answers_str}",
            reply_markup=accept_test_kb
        )

        return

@router.callback_query(F.data.startswith("accept_test_"))
async def handle_callbacks_accept_test(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = callback.data.replace("accept_test_", "")
    state_data = await state.get_data()
    test_answers = state_data.get("test_answers")

    if data == "accept":
        await update_user_data(callback.from_user.id, test_answers, "tests", "test_answers")
        await update_user_data(callback.from_user.id, [], "tests", "users_cant_again")
        await callback.message.answer(
            "✅ <b>Тест сохранён!</b>\n\n"
            "Теперь можешь отправлять ссылку друзьям и смотреть, насколько хорошо они тебя знают 🤝"
        )
    else:
        await callback.message.answer(
            "❌ <b>Изменение теста отменено.</b>\n\n"
            "Ты всегда можешь вернуться и создать или изменить тест позже 🙂"
        )

    await callback.message.delete()
    await state.clear()