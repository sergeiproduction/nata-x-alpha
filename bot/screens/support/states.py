from aiogram.fsm.state import State, StatesGroup

class SupportScreen(StatesGroup):
    waiting_for_message = State()