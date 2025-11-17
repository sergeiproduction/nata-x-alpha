from aiogram.filters.callback_data import CallbackData

class AccountingCallback(CallbackData, prefix="account"):
    action: str