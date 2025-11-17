from aiogram.utils.keyboard import InlineKeyboardBuilder
from .filters import AccountingCallback

def accounting_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Подробнее", callback_data=AccountingCallback(action="info"))
    builder.button(text="Назад", callback_data=AccountingCallback(action="back"))
    builder.adjust(1, 1)
    return builder.as_markup()


def back():
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data=AccountingCallback(action="back"))
    return builder.as_markup()