from aiogram.filters.callback_data import CallbackData

class PassportCallbackData(CallbackData, prefix="passport"):
    action: str