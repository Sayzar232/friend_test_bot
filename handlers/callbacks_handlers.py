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

@router.callback_query(F.data.startswith("menu_"))
async def handle_menu(callback: CallbackQuery):
    await callback.answer()

    data = callback.data.replace("menu_", "")

    if data == "create_test":
        await callback.message.edit_text("сейчас тебе будут скидываться вопросы", reply_markup=start_quetions_kb)
    elif data == "info":
        user_info = await get_user_data(callback.from_user.id)
        best_users = user_info.get("best_users_passed") or {}
        other_test_passed = user_info.get("other_test_users") or {}

        if not best_users:
            best_results_str = "Пока никто не прошел ваш тест."
        else:
            sorted_users = sorted(best_users.items(), key=lambda item: item[1], reverse=True)
            results_list = [f"{i}. @{username} - <b>{score}/15</b>" for i, (username, score) in enumerate(sorted_users, 1)]
            best_results_str = '\n'.join(results_list)

        if not other_test_passed:
            best_results_other_str = "Вы пока не проходили чужие тесты"
        else:
            sorted_other_test_passed = sorted(other_test_passed.items(), key=lambda item: item[1], reverse=True)
            other_results_list = [f"{i}. @{username} - <b>{score}/15</b>" for i, (username, score) in enumerate(sorted_other_test_passed, 1)]
            best_results_other_str = '\n'.join(other_results_list)

        percent_users_set = set(best_users) & set(other_test_passed)
        percent_users = {i: (best_users[i] + other_test_passed[i]) / 30 * 100 for i in percent_users_set}

        if not percent_users:
            percent_users_str = "Нет данных для расчета совместимости."
        else:
            sorted_percent_users = sorted(percent_users.items(), key=lambda item: item[1], reverse=True)
            percent_list = [f"{i}. @{username} - <b>{round(percent, 1)}%</b>" for i, (username, percent) in enumerate(sorted_percent_users, 1)]
            percent_users_str = '\n'.join(percent_list)

        await callback.message.answer(text=
            f"<b>Профиль</b>\n\n"
            f"<b>Имя:</b> {callback.from_user.full_name}\n"
            f"<b>ID:</b> {callback.from_user.id}\n\n"
            f"<b>Пройденных тестов:</b> {user_info.get("other_test_passed")}\n"
            f"<b>Количество людей, которые прошли ваш тест:</b> {user_info.get("num_users_passed")}\n\n"
            f"<b>Ваша ссылка на тест:</b> {user_info.get("ref_link")}\n\n"
            f"<b>🏆 Ваши лучшие результаты:</b>\n\n"
            f"{best_results_str}\n\n"
            f"<b>🏆 Лучшие результаты ваших друзей:</b>\n\n"
            f"{best_results_other_str}\n\n"
            f"<b>🏆 Лучшая совместимость с друзьями:\n\n</b>"
            f"{percent_users_str}",
            reply_markup=best_users_passed_kb
            )
    elif data == "help":
        help_text = (
            "<b>ℹ️ Как пользоваться ботом?</b>\n\n"
            "Этот бот позволяет вам создать свой собственный тест и поделиться им с друзьями, чтобы узнать, насколько хорошо они вас знают!\n\n"
            "<b>📋 Пошаговая инструкция:</b>\n\n"
            "1. <b>Создайте тест:</b> Нажмите \"Создать/изменить тест\" в главном меню или используйте команду <code>/edit_test</code> и ответьте на вопросы.\n"
            "2. <b>Получите ссылку:</b> Ваша персональная ссылка для друзей будет доступна в профиле (<code>/profile</code>).\n"
            "3. <b>Отправьте друзьям:</b> 📤 Поделитесь ссылкой с друзьями.\n"
            "4. <b>Следите за результатами:</b> Вы получите уведомление, когда кто-то пройдет ваш тест. Лучшие результаты можно посмотреть в профиле.\n\n"
            "<b>🤖 Доступные команды:</b>\n\n"
            "<code>/start</code> - 🚀 Запустить бота и получить свою персональную ссылку.\n"
            "<code>/profile</code> - 👤 Посмотреть свой профиль, статистику и ссылку на тест.\n"
            "<code>/edit_test</code> - ✏️ Создать или изменить свои ответы на тест.\n"
            "<code>/show_answers</code> - 👀 Посмотреть свои текущие ответы на тест."
        )
        await callback.message.edit_text(text=help_text, reply_markup=back_to_menu_kb)

@router.callback_query(F.data == "test_answers_show")
async def handle_show_users_passed(callback: CallbackQuery):
    await callback.answer()

    user_info = await get_user_data(callback.from_user.id)
    test_answers = get_test_str(user_info.get("test_answers"))

    if not test_answers:
        await callback.message.answer("Вы пока не ответили на вопросы теста")
        return

    await callback.message.answer(f"<b>Ответы на тест: </b>\n\n{test_answers}")

@router.callback_query(F.data.startswith("start_questions_"))
async def handle_start_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = callback.data.replace("start_questions_", "")

    if data == "start":
        await state.update_data(test_answers=[i for i in range(15)], test_type="create")
        await state.set_state(Form.waiting_for_answer)
        await callback.message.answer(QUESTIONS[0], reply_markup=get_question_keyboard(1))
    elif data == "back":
        await callback.message.edit_text("Приветствую", reply_markup=menu_kb)
        return

@router.callback_query(F.data.startswith("friend_questions_"))
async def handle_friend_question(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = callback.data.replace("friend_questions_", "")

    if data == "start":
        await state.update_data(test_answers=[i for i in range(15)], test_type="answer")
        await state.set_state(Form.waiting_for_friend_answer)
        await callback.message.edit_text(QUESTIONS[0], reply_markup=get_question_keyboard(1))

    elif data == "cancel":
        await state.clear()
        await callback.message.delete()
        await callback.message.answer("Вы отменили начало теста")
        return