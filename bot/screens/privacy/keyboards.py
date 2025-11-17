from aiogram.utils.keyboard import InlineKeyboardBuilder
from .filters import PrivacyCallback

from config import USER_AGREEMENT, PRIVACY_POLICY


def privacy_keyboard():
    builder = InlineKeyboardBuilder()
    
    builder.button(text="Политика конфиденциальности", url=PRIVACY_POLICY)
    builder.button(text="Пользовательское соглашение", url=USER_AGREEMENT)
    
    builder.button(text="Согласен", callback_data=PrivacyCallback(action="accept"))
    builder.button(text="Отозвать согласие", callback_data=PrivacyCallback(action="revoke"))
    builder.button(text="Главное меню", callback_data=PrivacyCallback(action="main_menu"))
    
    builder.adjust(1, 1, 1, 1)
    return builder.as_markup()