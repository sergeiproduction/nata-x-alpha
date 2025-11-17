from aiogram.utils.keyboard import InlineKeyboardBuilder

from .filters import ServiceCallback


def services_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="Разработка сайта", callback_data=ServiceCallback(action="web"))
    builder.button(text="Отчет под ключ", callback_data=ServiceCallback(action="report"))
    builder.button(text="Назад", callback_data=ServiceCallback(action="back"))
    builder.adjust(1, 1, 1)
    return builder.as_markup()