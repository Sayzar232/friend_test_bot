from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    waiting_for_answer = State()
    waiting_for_text_answer = State()
    waiting_for_friend_answer = State()
    waiting_for_broadcast_message = State()
    waiting_for_url_button_broadcast = State()