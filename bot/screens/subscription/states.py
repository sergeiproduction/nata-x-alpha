from aiogram.fsm.state import State, StatesGroup

class SubscriptionScreen(StatesGroup):
    promocode = State()