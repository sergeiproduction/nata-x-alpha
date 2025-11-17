from aiogram.utils.keyboard import ReplyKeyboardBuilder

def start_screen():
    builder = ReplyKeyboardBuilder()
    
    builder.button(text="🚀 Студенческий стартап")
    
    builder.button(text="📅 Календарь отчетности")
        
    builder.button(text="💼 Наши услуги")
    
    
    builder.button(text="🧾 Бухгалтерия")
    builder.button(text="👤 Профиль")
    
    
    builder.adjust(1, 1, 1, 2)
    
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)