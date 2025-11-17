from aiogram.filters.callback_data import CallbackData

class ServiceCallback(CallbackData, prefix="service"):
    action: str