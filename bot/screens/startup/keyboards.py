from aiogram.utils.keyboard import InlineKeyboardBuilder

from .filters import StartupCallback

def startup_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(text="I этап", callback_data=StartupCallback(action="first_stage"))
    builder.button(text="II этап", callback_data=StartupCallback(action="second_stage"))
    
    builder.button(text="FAQ", callback_data=StartupCallback(action="faq"))
    #builder.button(text="Финансы", callback_data=StartupCallback(action="finances"))
    
    builder.button(text="Чек-листы", callback_data=StartupCallback(action="checklists"))
    
    builder.button(text="Назад", callback_data=StartupCallback(action="back"))

    builder.adjust(2, 2, 1, 1)
    
    return builder.as_markup()