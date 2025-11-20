from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

best_users_passed_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Посмотреть ответы на тест", callback_data="test_answers_show")]
])

menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✏ Создать/изменить ответы на тест", callback_data="menu_create_test")],
    [InlineKeyboardButton(text="ℹ Информация о себе и тестах", callback_data="menu_info")],
    [InlineKeyboardButton(text="⁉ Помощь", callback_data="menu_help")]
])

start_quetions_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Начать", callback_data="start_questions_start")],
    [InlineKeyboardButton(text="Назад", callback_data="start_questions_back")]
])

back_to_menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="start_questions_back")]
])

friend_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Начать тест", callback_data="friend_questions_start")],
    [InlineKeyboardButton(text="Отмена", callback_data="friend_questions_cancel")]
])

accept_test_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Подтвердить", callback_data="accept_test_accept")],
    [InlineKeyboardButton(text="Отменить", callback_data="accept_test_cancel")]
])

#Answers keyboards
asnwer_1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔵 Голубой", callback_data="answer_1_голубой")],
    [InlineKeyboardButton(text="🟢 Зеленый", callback_data="answer_1_зеленый")],
    [InlineKeyboardButton(text="🟡 Желтый", callback_data="answer_1_желтый")],
    [InlineKeyboardButton(text="🔴 Красный", callback_data="answer_1_красный")],
    [InlineKeyboardButton(text="🟣 Фиолетовый", callback_data="answer_1_фиолетовый")],
    [InlineKeyboardButton(text="🩷 Розовый", callback_data="answer_1_розовый")],
    [InlineKeyboardButton(text="🔵 Синий", callback_data="answer_1_синий")],
    [InlineKeyboardButton(text="🟠 Оранжевый", callback_data="answer_1_оранжевый")],
    [InlineKeyboardButton(text="⚫ Черный", callback_data="answer_1_черный")],
    [InlineKeyboardButton(text="⚪ Белый", callback_data="answer_1_белый")],
    [InlineKeyboardButton(text="🔘 Серый", callback_data="answer_1_серый")],
    [InlineKeyboardButton(text="❓ Другой", callback_data="answer_1_другой")]
])


answer_2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🥬 Вегетерианец", callback_data="answer_2_вегетерианец")],
    [InlineKeyboardButton(text="🌱 Веган", callback_data="answer_2_веган")],
    [InlineKeyboardButton(text="🥩 Мясоед", callback_data="answer_2_мясоед")],
    [InlineKeyboardButton(text="❓ Другое", callback_data="answer_2_другое")]
])

answer_3 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎵 Поп", callback_data="answer_3_поп")],
    [InlineKeyboardButton(text="🎸 Рок", callback_data="answer_3_рок")],
    [InlineKeyboardButton(text="🎤 Хип-хоп", callback_data="answer_3_хип-хоп")],
    [InlineKeyboardButton(text="🎼 Классика", callback_data="answer_3_классика")],
    [InlineKeyboardButton(text="🎷 Джаз", callback_data="answer_3_джаз")],
    [InlineKeyboardButton(text="🤘 Метал", callback_data="answer_3_метал")],
    [InlineKeyboardButton(text="🎛️ Электроника", callback_data="answer_3_электроника")],
    [InlineKeyboardButton(text="🎻 Фолк", callback_data="answer_3_фолк")],
    [InlineKeyboardButton(text="❓ Другое", callback_data="answer_3_другое")]
])

answer_4 = None

answer_5 = None

answer_6 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⚽ Футбол", callback_data="answer_6_футбол")],
    [InlineKeyboardButton(text="🏀 Баскетбол", callback_data="answer_6_баскетбол")],
    [InlineKeyboardButton(text="🏐 Волейбол", callback_data="answer_6_волейбол")],
    [InlineKeyboardButton(text="🏊 Плавание", callback_data="answer_6_плавание")],
    [InlineKeyboardButton(text="🏃 Бег", callback_data="answer_6_бег")],
    [InlineKeyboardButton(text="🎾 Теннис", callback_data="answer_6_теннис")],
    [InlineKeyboardButton(text="🤸 Гимнастика", callback_data="answer_6_гимнастика")],
    [InlineKeyboardButton(text="🥊 Бокс", callback_data="answer_6_бокс")],
    [InlineKeyboardButton(text="🥋 ММА", callback_data="answer_6_mma")],
    [InlineKeyboardButton(text="🤼 Борьба", callback_data="answer_6_борьба")],
    [InlineKeyboardButton(text="🏸 Теннис", callback_data="answer_6_теннис")],
    [InlineKeyboardButton(text="❌ Нет любимого", callback_data="answer_6_нет_любимого")],
    [InlineKeyboardButton(text="❓ Другое", callback_data="answer_6_другое")]
])

answer_7 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да", callback_data="answer_7_да")],
    [InlineKeyboardButton(text="❌ Нет", callback_data="answer_7_нет")],
    [InlineKeyboardButton(text="⏰ Раньше было", callback_data="answer_7_раньше_было")]
])

answer_8 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏠 Интроверт", callback_data="answer_8_интроверт")],
    [InlineKeyboardButton(text="🎉 Экстраверт", callback_data="answer_8_экстраверт")],
    [InlineKeyboardButton(text="⚖️ Амбиверт", callback_data="answer_8_амбиверт")]
])

answer_9 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🍵 Чай", callback_data="answer_9_чай")],
    [InlineKeyboardButton(text="☕ Кофе", callback_data="answer_9_кофе")],
    [InlineKeyboardButton(text="🍵☕ И то и другое", callback_data="answer_9_и_то_и_другое")],
    [InlineKeyboardButton(text="❌ Ни то ни другое", callback_data="answer_9_ни_то_ни_другое")]
])

answer_10 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🌅 До 7 утра", callback_data="answer_10_до_7")],
    [InlineKeyboardButton(text="🌄 7-9 утра", callback_data="answer_10_7_9")],
    [InlineKeyboardButton(text="☀️ 9-11 утра", callback_data="answer_10_9_11")],
    [InlineKeyboardButton(text="😴 Позже 11", callback_data="answer_10_позже_11")],
    [InlineKeyboardButton(text="🔄 Нет режима", callback_data="answer_10_нет_режима")]
])

answer_11 = None

answer_12 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📱 Apple", callback_data="answer_12_apple")],
    [InlineKeyboardButton(text="📱 Samsung", callback_data="answer_12_samsung")],
    [InlineKeyboardButton(text="📱 Xiaomi", callback_data="answer_12_xiaomi")],
    [InlineKeyboardButton(text="📱 Huawei", callback_data="answer_12_huawei")],
    [InlineKeyboardButton(text="📱 Honor", callback_data="answer_12_honor")],
    [InlineKeyboardButton(text="📱 Realme", callback_data="answer_12_realme")],
    [InlineKeyboardButton(text="📱 Oppo", callback_data="answer_12_oppo")],
    [InlineKeyboardButton(text="📱 Vivo", callback_data="answer_12_vivo")],
    [InlineKeyboardButton(text="📱 Lenovo", callback_data="answer_12_lenovo")],
    [InlineKeyboardButton(text="📱 Tecno", callback_data="answer_12_tecno")],
    [InlineKeyboardButton(text="❓ Другое", callback_data="answer_12_другое")]
])

answer_13 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📚 Чтение", callback_data="answer_13_чтение")],
    [InlineKeyboardButton(text="🏃 Спорт", callback_data="answer_13_спорт")],
    [InlineKeyboardButton(text="✈️ Путешествия", callback_data="answer_13_путешествия")],
    [InlineKeyboardButton(text="🎮 Игры", callback_data="answer_13_игры")],
    [InlineKeyboardButton(text="🎵 Музыка", callback_data="answer_13_музыка")],
    [InlineKeyboardButton(text="🎨 Рисование", callback_data="answer_13_рисование")],
    [InlineKeyboardButton(text="❓ Другое", callback_data="answer_13_другое")]
])

answer_14 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❄️ Зима", callback_data="answer_14_зима")],
    [InlineKeyboardButton(text="🌸 Весна", callback_data="answer_14_весна")],
    [InlineKeyboardButton(text="☀️ Лето", callback_data="answer_14_лето")],
    [InlineKeyboardButton(text="🍂 Осень", callback_data="answer_14_осень")]
])

answer_15 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1️⃣ 1", callback_data="answer_15_1")],
    [InlineKeyboardButton(text="2️⃣ 2", callback_data="answer_15_2")],
    [InlineKeyboardButton(text="3️⃣ 3", callback_data="answer_15_3")],
    [InlineKeyboardButton(text="4️⃣ 4", callback_data="answer_15_4")],
    [InlineKeyboardButton(text="5️⃣+ 5+", callback_data="answer_15_5+")],
    [InlineKeyboardButton(text="❌ Нет лучших друзей", callback_data="answer_15_нет_лучших_друзей")]
])

admin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
    [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")]
])

def get_question_keyboard(question_number: int) -> InlineKeyboardMarkup | None:
    """Возвращает клавиатуру для вопроса по номеру. Если None - пользователь должен написать ответ."""
    keyboards = {
        1: asnwer_1,
        2: answer_2,
        3: answer_3,
        4: None,  # Год рождения - текстовый ввод
        5: None,  # День рождения - текстовый ввод
        6: answer_6,
        7: answer_7,
        8: answer_8,
        9: answer_9,
        10: answer_10,
        11: None,  # Страна - текстовый ввод
        12: answer_12,
        13: answer_13,
        14: answer_14,
        15: answer_15,
    }
    return keyboards.get(question_number)
