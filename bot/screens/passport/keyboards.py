from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup
from .filters import PassportCallbackData

def get_passport_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Заполнить по ИНН",
        callback_data=PassportCallbackData(action="fill_by_inn").pack()
    )
    builder.button(
        text="Подробнее",
        callback_data=PassportCallbackData(action="more_info").pack()
    )
    builder.button(
        text="Назад",
        callback_data=PassportCallbackData(action="back").pack()
    )
    
    builder.adjust(1)

    return builder.as_markup()