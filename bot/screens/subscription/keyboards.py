from aiogram.utils.keyboard import InlineKeyboardBuilder

from .filters import PaymentCallback


def change_period():
    builder = InlineKeyboardBuilder()
    
    builder.button(text="1 месяц", callback_data=PaymentCallback(action="buy", month_count=1).pack())
    builder.button(text="3 месяца", callback_data=PaymentCallback(action="buy", month_count=3, discount=0.05).pack())
    builder.button(text="6 месяцев", callback_data=PaymentCallback(action="buy", month_count=6, discount=0.1).pack())
    builder.button(text="12 месяцев", callback_data=PaymentCallback(action="buy", month_count=12, discount=0.2).pack())

    builder.button(text="Назад", callback_data=PaymentCallback(action="back").pack())

    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()



def promocode():
    builder = InlineKeyboardBuilder()
    
    builder.button(text="Отмена", callback_data=PaymentCallback(action="havent_promocode").pack())
    return builder.as_markup()
