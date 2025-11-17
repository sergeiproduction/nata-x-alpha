from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from faq.manager import FaqManager
from bot.screens.faq.filters import FAQCallback
from bot.screens.checklists.keyboards import calculate_keyboard_layout

async def build_categories_keyboard():
    builder = InlineKeyboardBuilder()
    
    manager = FaqManager("./storage/faq.json")
    await manager.load_data()

    categories = await manager.get_categories()

    for index, cat_name in enumerate(categories):
        builder.button(
            text=cat_name,  # Отображаем имя категории
            callback_data=FAQCallback(category_id=index).pack()  # Передаём ID
        )

    builder.button(text="Назад", callback_data=FAQCallback(action="startup").pack())

    builder.adjust(1)
    return builder.as_markup()


async def build_sections(category_id: int):
    builder = InlineKeyboardBuilder()
    
    manager = FaqManager("./storage/faq.json")
    await manager.load_data()

    categories = await manager.get_categories()
    if category_id >= len(categories):
        raise ValueError("Invalid category ID")

    category_name = categories[category_id]
    sections = await manager.get_sections_by_category(category_name)

    for index, _ in enumerate(sections):
        builder.button(
            text=str(index+1),  # Отображаем имя раздела
            callback_data=FAQCallback(
                category_id=category_id,  # Передаём ID категории
                section_id=index        # Передаём ID раздела
            ).pack()
        )

    layout = calculate_keyboard_layout(len(sections))
    builder.adjust(*layout)

    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=FAQCallback(action="back").pack()
        )
    )

    return builder.as_markup()


async def build_navigation_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="▶️ Следующий вопрос", callback_data=FAQCallback(action="prev").pack())
    builder.button(text="◀️ Предыдущий вопрос", callback_data=FAQCallback(action="next").pack())    
    builder.button(text="📋 К разделам", callback_data=FAQCallback(action="sections").pack())
    builder.adjust(1)
    return builder.as_markup()