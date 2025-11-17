from aiogram.filters.callback_data import CallbackData

class StartupCallback(CallbackData, prefix="startup"):
    action: str