from aiogram.fsm.state import State, StatesGroup

class PassportScreen(StatesGroup):
    inn = State()