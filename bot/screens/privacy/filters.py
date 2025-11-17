from aiogram.filters.callback_data import CallbackData

class PrivacyCallback(CallbackData, prefix="privacy"):
    action: str