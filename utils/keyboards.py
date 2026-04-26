from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

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

answer_1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🤖 Автоматизации труда", callback_data="answer_1_автоматизации труда")],
    [InlineKeyboardButton(text="🔮 Будущего", callback_data="answer_1_будущее")],
    [InlineKeyboardButton(text="💔 Потерять близких", callback_data="answer_1_потерять близких")],
    [InlineKeyboardButton(text="😔 Одиночество", callback_data="answer_1_одиночество")],
    [InlineKeyboardButton(text="💀 Смерти", callback_data="answer_1_смерть")]
])

# 😊 В чём для тебя счастье?
answer_2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👨‍👩‍👧‍👦 Близкие и семья", callback_data="answer_2_близкие и семья")],
    [InlineKeyboardButton(text="🧘 Свобода", callback_data="answer_2_свобода")],
    [InlineKeyboardButton(text="🎯 Самореализация", callback_data="answer_2_самореализация")],
    [InlineKeyboardButton(text="💰 Деньги", callback_data="answer_2_деньги")]
])

# 🦸‍♂️ Если бы у тебя была суперспособность, то какая?
answer_3 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🦅 Летать", callback_data="answer_3_летать")],
    [InlineKeyboardButton(text="👻 Невидимость", callback_data="answer_3_невидимость")],
    [InlineKeyboardButton(text="🧠 Читать мысли", callback_data="answer_3_читать мысли")],
    [InlineKeyboardButton(text="🛸 Телепортация", callback_data="answer_3_телепортация")],
    [InlineKeyboardButton(text="🕒 Остановка времени", callback_data="answer_3_остановка времени")]
])

# 💸 Куда бы ты потратил(а) миллион прямо сейчас?
answer_4 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏠 Жильё/недвижимость", callback_data="answer_4_жильё/недвижимость")],
    [InlineKeyboardButton(text="📈 Инвестиции", callback_data="answer_4_инвестиции")],
    [InlineKeyboardButton(text="❤️ Благотворительность", callback_data="answer_4_благотворительность")],
    [InlineKeyboardButton(text="🛍 Покупки", callback_data="answer_4_покупки")],
    [InlineKeyboardButton(text="🚀 Бизнес", callback_data="answer_4_бизнес")]
])

# 😤 Что тебя раздражает сильнее всего?
answer_5 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🙄 Ложь и лицемерие", callback_data="answer_5_ложь и лицемерие")],
    [InlineKeyboardButton(text="🕒 Опоздания и игнор", callback_data="answer_5_опоздания и игнор")],
    [InlineKeyboardButton(text="🤐 Несправедливость", callback_data="answer_5_несправедливость")],
    [InlineKeyboardButton(text="📣 Шум и суета", callback_data="answer_5_шум и суета")]
])

# 🏃 Ты занимаешься спортом?
answer_6 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да", callback_data="answer_6_да")],
    [InlineKeyboardButton(text="❌ Нет", callback_data="answer_6_нет")],
    [InlineKeyboardButton(text="💪 Хочу начать", callback_data="answer_6_хочу начать")]
])

# 🎨 Ты больше логик или творческий человек?
answer_7 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🧠 Логик", callback_data="answer_7_логик")],
    [InlineKeyboardButton(text="🎨 Творческий", callback_data="answer_7_творческий")]
])

# 🧑‍🤝‍🧑 Ты интроверт или экстраверт?
answer_8 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏠 Интроверт", callback_data="answer_8_интроверт")],
    [InlineKeyboardButton(text="🎉 Экстраверт", callback_data="answer_8_экстраверт")],
    [InlineKeyboardButton(text="⚖️ Амбиверт", callback_data="answer_8_амбиверт")]
])

# 💑 Ты сейчас в отношениях?
answer_9 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❤️ Да", callback_data="answer_9_да")],
    [InlineKeyboardButton(text="❌ Нет", callback_data="answer_9_нет")]
])

# 🎲 Ты любишь риск или стабильность?
answer_10 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎲 Риск", callback_data="answer_10_риск")],
    [InlineKeyboardButton(text="🧱 Стабильность", callback_data="answer_10_стабильность")],
    [InlineKeyboardButton(text="⚖️ Баланс", callback_data="answer_10_баланс")]
])

# 🌴 Что для тебя идеальный отпуск?
answer_11 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏖 Море и пляж", callback_data="answer_11_море и пляж")],
    [InlineKeyboardButton(text="🏔 Горы и природа", callback_data="answer_11_горы и природа")],
    [InlineKeyboardButton(text="🏙️ Новые города", callback_data="answer_11_новые города")],
    [InlineKeyboardButton(text="🛋️ Дома и никуда", callback_data="answer_11_дома")]
])

# 📱 iOS или Android: за что ты готов(а) спорить до хрипоты?
answer_12 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🍎 iOS", callback_data="answer_12_iOS")],
    [InlineKeyboardButton(text="🤖 Android", callback_data="answer_12_android")],
    [InlineKeyboardButton(text="🤝 Оба норм", callback_data="answer_12_оба норм")]
])

# 🎬 Любимый жанр фильмов или сериалов?
answer_13 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="😂 Комедия", callback_data="answer_13_комедия")],
    [InlineKeyboardButton(text="🔫 Экшн", callback_data="answer_13_экшн")],
    [InlineKeyboardButton(text="🚀 Фантастика", callback_data="answer_13_фантастика")],
    [InlineKeyboardButton(text="👻 Хоррор", callback_data="answer_13_хоррор")],
    [InlineKeyboardButton(text="💘 Романтика", callback_data="answer_13_романтика")]
])

# 🧠 Ты скорее умный(ая) или везучий(ая)?
answer_14 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🧠 Умный(ая)", callback_data="answer_14_умный")],
    [InlineKeyboardButton(text="🍀 Везучий(ая)", callback_data="answer_14_везучий")],
    [InlineKeyboardButton(text="💀 Не умный и не везучий", callback_data="answer_14_не умный и не везучий")],
])

# 🍕 Твоя любимая еда?
answer_15 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🍕 Пицца/фастфуд", callback_data="answer_15_пицца/фастфуд")],
    [InlineKeyboardButton(text="🍣 Суши/азиатская", callback_data="answer_15_суши/азиатская")],
    [InlineKeyboardButton(text="🥩 Мясо/стейки", callback_data="answer_15_мясо/стейки")],
    [InlineKeyboardButton(text="🥗 Здоровая", callback_data="answer_15_здоровая")],
    [InlineKeyboardButton(text="🍰 Сладкое", callback_data="answer_15_сладкое")],
])

admin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
    [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
    [InlineKeyboardButton(text="📈 Рост пользователей", callback_data="admin_growth_chart")],
    [InlineKeyboardButton(text="👥 Последние 100 пользователей", callback_data="admin_100_users")]
])

def get_question_keyboard(question_number: int) -> InlineKeyboardMarkup | None:
    """Возвращает клавиатуру для вопроса по номеру."""
    keyboards = {
        1: answer_1,
        2: answer_2,
        3: answer_3,
        4: answer_4,
        5: answer_5,
        6: answer_6,
        7: answer_7,
        8: answer_8,
        9: answer_9,
        10: answer_10,
        11: answer_11,
        12: answer_12,
        13: answer_13,
        14: answer_14,
        15: answer_15,
    }
    return keyboards.get(question_number)


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
    original_kb = get_question_keyboard(question_number)
    if not original_kb:
        return None
    
    new_inline_keyboard = []
    for row in original_kb.inline_keyboard:
        new_row = []
        for btn in row:
            if btn.callback_data and btn.callback_data.startswith("answer_"):
                new_cb = btn.callback_data.replace("answer_", "grp_ans_", 1)
                new_row.append(InlineKeyboardButton(text=btn.text, callback_data=new_cb))
            else:
                new_row.append(btn)
        new_inline_keyboard.append(new_row)
        
    return InlineKeyboardMarkup(inline_keyboard=new_inline_keyboard)
