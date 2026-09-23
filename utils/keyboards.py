from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from .answers import get_answers

best_users_passed_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Посмотреть ответы на тест", callback_data="test_answers_show")]
])

menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📝 Создать мой тест", callback_data="menu_create_test")],
    [InlineKeyboardButton(text="ℹ Результаты тестов", callback_data="menu_info")],
    [InlineKeyboardButton(text="⁉ Помощь", callback_data="menu_help")]
])

start_quetions_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔥 Начать тест!", callback_data="start_questions_start")],
    [InlineKeyboardButton(text="Назад", callback_data="start_questions_back")]
])

new_user_start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔥 Начать тест!", callback_data="start_questions_start")]
])

back_to_menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="start_questions_back")]
])

friend_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🚀 Пройти тест друга", callback_data="friend_questions_start")],
    [InlineKeyboardButton(text="Отмена", callback_data="friend_questions_cancel")]
])

accept_test_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Подтвердить", callback_data="accept_test_accept")],
    [InlineKeyboardButton(text="Отменить", callback_data="accept_test_cancel")]
])

admin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
    [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
    [InlineKeyboardButton(text="📈 Рост пользователей", callback_data="admin_growth_chart")],
    [InlineKeyboardButton(text="👥 Последние 100 пользователей", callback_data="admin_100_users")]
])

def get_question_keyboard(question_number: int) -> InlineKeyboardMarkup | None:
    """Собирает клавиатуру с вариантами ответов для вопроса по номеру."""
    answers = get_answers(question_number)
    if answers is None:
        return None

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=callback_data)]
        for callback_data, text in answers.items()
    ])


def get_send_link_kb(link: str) -> InlineKeyboardMarkup:
    """Клавиатура для отправки ссылки другу"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поделиться тестом", switch_inline_query=f"Насколько хорошо ты меня знаешь?\n\n{link}")],
        [InlineKeyboardButton(text="Назад в меню", callback_data="menu_info")]
    ])


def get_create_test_reminder_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать тест", callback_data="menu_create_test")]
    ])


def get_share_reminder_kb(link: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поделиться", switch_inline_query=f"Насколько хорошо ты меня знаешь?\n\n{link}")]
    ])


def get_group_start_kb(target_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать тест", callback_data=f"grp_start_{target_id}")],
        [InlineKeyboardButton(text="Отмена", callback_data="grp_cancel")]
    ])


def get_group_question_keyboard(question_number: int) -> InlineKeyboardMarkup | None:
    """Клавиатура ответов для теста в группе (callback_data с префиксом grp_ans_)."""
    answers = get_answers(question_number)
    if answers is None:
        return None

    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=callback_data.replace("answer_", "grp_ans_", 1))]
        for callback_data, text in answers.items()
    ])


def get_url_button_kb(url: str, button_text: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button_text, url=url)]
    ])