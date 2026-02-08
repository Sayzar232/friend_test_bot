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

send_link_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Отправить ссылку", switch_inline_query="")]
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
    [InlineKeyboardButton(text="🎵 TikTok", callback_data="answer_2_tiktok")],
    [InlineKeyboardButton(text="📺 YouTube", callback_data="answer_2_youtube")],
    [InlineKeyboardButton(text="✈️ Telegram", callback_data="answer_2_telegram")],
    [InlineKeyboardButton(text="📷 Instagram", callback_data="answer_2_instagram")],
    [InlineKeyboardButton(text="📌 Pinterest", callback_data="answer_2_pinterest")],
    [InlineKeyboardButton(text="🌐 VK", callback_data="answer_2_vk")],
    [InlineKeyboardButton(text="🐦 Twitter", callback_data="answer_2_twitter")],
    [InlineKeyboardButton(text="❓ Другое", callback_data="answer_2_другое")],
])

answer_3 = None

# answer_3 = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text="🎵 Поп", callback_data="answer_3_поп")],
#     [InlineKeyboardButton(text="🎸 Рок", callback_data="answer_3_рок")],
#     [InlineKeyboardButton(text="🎤 Хип-хоп", callback_data="answer_3_хип-хоп")],
#     [InlineKeyboardButton(text="🎼 Классика", callback_data="answer_3_классика")],
#     [InlineKeyboardButton(text="🎷 Джаз", callback_data="answer_3_джаз")],
#     [InlineKeyboardButton(text="🤘 Метал", callback_data="answer_3_метал")],
#     [InlineKeyboardButton(text="🎛️ Электроника", callback_data="answer_3_электроника")],
#     [InlineKeyboardButton(text="🎻 Фолк", callback_data="answer_3_фолк")],
#     [InlineKeyboardButton(text="❓ Другое", callback_data="answer_3_другое")]
# ])

answer_4 = None

answer_5 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❄️ Январь", callback_data="answer_5_январь")],
    [InlineKeyboardButton(text="❄️ Февраль", callback_data="answer_5_февраль")],
    [InlineKeyboardButton(text="🌸 Март", callback_data="answer_5_март")],
    [InlineKeyboardButton(text="🌸 Апрель", callback_data="answer_5_апрель")],
    [InlineKeyboardButton(text="🌸 Май", callback_data="answer_5_май")],
    [InlineKeyboardButton(text="☀️ Июнь", callback_data="answer_5_июнь")],
    [InlineKeyboardButton(text="☀️ Июль", callback_data="answer_5_июль")],
    [InlineKeyboardButton(text="☀️ Август", callback_data="answer_5_август")],
    [InlineKeyboardButton(text="🍂 Сентябрь", callback_data="answer_5_сентябрь")],
    [InlineKeyboardButton(text="🍂 Октябрь", callback_data="answer_5_октябрь")],
    [InlineKeyboardButton(text="🍂 Ноябрь", callback_data="answer_5_ноябрь")],
    [InlineKeyboardButton(text="❄️ Декабрь", callback_data="answer_5_декабрь")]
])

answer_6 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🖥️ IT-сфера", callback_data="answer_6_it")],
    [InlineKeyboardButton(text="🩺 Медицина", callback_data="answer_6_медицина")],
    [InlineKeyboardButton(text="🎓 Образование", callback_data="answer_6_образование")],
    [InlineKeyboardButton(text="🎨 Искусство/Творчество", callback_data="answer_6_искусство")],
    [InlineKeyboardButton(text="📈 Бизнес/Финансы", callback_data="answer_6_бизнес")],
    [InlineKeyboardButton(text="🛠️ Инженерия", callback_data="answer_6_инженерия")],
    [InlineKeyboardButton(text="⚖️ Юриспруденция", callback_data="answer_6_юриспруденция")],
    [InlineKeyboardButton(text="📢 Маркетинг/PR", callback_data="answer_6_маркетинг")],
    [InlineKeyboardButton(text="🔬 Наука", callback_data="answer_6_наука")],
    [InlineKeyboardButton(text="🤝 Сфера услуг", callback_data="answer_6_сфера услуг")],
    [InlineKeyboardButton(text="🤔 Еще не решил(а)", callback_data="answer_6_не решил")],
    [InlineKeyboardButton(text="❓ Другое", callback_data="answer_6_другое")]
])

answer_7 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да", callback_data="answer_7_да")],
    [InlineKeyboardButton(text="❌ Нет", callback_data="answer_7_нет")],
    [InlineKeyboardButton(text="⏰ Раньше было", callback_data="answer_7_раньше было")]
])

answer_8 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏠 Интроверт", callback_data="answer_8_интроверт")],
    [InlineKeyboardButton(text="🎉 Экстраверт", callback_data="answer_8_экстраверт")],
    [InlineKeyboardButton(text="⚖️ Амбиверт", callback_data="answer_8_амбиверт")]
])

answer_9 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Да", callback_data="answer_9_да")],
    [InlineKeyboardButton(text="❌ Нет", callback_data="answer_9_нет")],
    [InlineKeyboardButton(text="💔 Раньше было", callback_data="answer_9_раньше было")],
])

answer_10 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🌅 До 7 утра", callback_data="answer_10_до 7 утра")],
    [InlineKeyboardButton(text="🌄 7-9 утра", callback_data="answer_10_7-9 утра")],
    [InlineKeyboardButton(text="☀️ 9-11 утра", callback_data="answer_10_9-11 утра")],
    [InlineKeyboardButton(text="😴 Позже 11", callback_data="answer_10_позже 11")],
    [InlineKeyboardButton(text="🔄 Нет режима", callback_data="answer_10_нет режима")]
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
    [InlineKeyboardButton(text="🖥 ПК", callback_data="answer_15_пк")],
    [InlineKeyboardButton(text="📱 Телефон", callback_data="answer_15_телефон")],
    [InlineKeyboardButton(text="🎮 Консоль", callback_data="answer_15_консоль")],
])

admin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
    [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
    [InlineKeyboardButton(text="👥 Последние 100 пользователей", callback_data="admin_100_users")]
])

def get_question_keyboard(question_number: int) -> InlineKeyboardMarkup | None:
    """Возвращает клавиатуру для вопроса по номеру. Если None - пользователь должен написать ответ."""
    keyboards = {
        1: asnwer_1,
        2: answer_2,
        3: answer_3,
        4: answer_4,  # Год рождения - текстовый ввод
        5: answer_5,  # День рождения - текстовый ввод
        6: answer_6,
        7: answer_7,
        8: answer_8,
        9: answer_9,
        10: answer_10,
        11: answer_11,  # Страна - текстовый ввод
        12: answer_12,
        13: answer_13,
        14: answer_14,
        15: answer_15,
    }
    return keyboards.get(question_number)
