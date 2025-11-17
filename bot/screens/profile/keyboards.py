from aiogram.utils.keyboard import InlineKeyboardBuilder

from .filters import ProfileCallback

from bot.screens.subscription.filters import PaymentCallback
from bot.screens.passport.filters import PassportCallbackData

def profile_keyboard(prime_user: bool):
    builder = InlineKeyboardBuilder()
    
    builder.button(text="Моя компания", callback_data=PassportCallbackData(action="my_company").pack())
    """
    if not prime_user:
        builder.button(text="Приобрести премиум", callback_data=PaymentCallback(action="show").pack()) 
    """
    builder.button(text="Назад", callback_data=ProfileCallback(action="back").pack())
    builder.adjust(1,1)
    return builder.as_markup()