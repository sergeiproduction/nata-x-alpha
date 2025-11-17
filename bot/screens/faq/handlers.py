from typing import Any, Dict
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.screens.faq.filters import FAQCallback

from bot.screens.faq.user_cases import decline_to_dative, find_faq_section_by_question
from bot.screens.startup.keyboards import startup_keyboard
from faq.manager import FaqManager
from faq.iterator import FAQIterator

from faq.schemas import FaqItem
from utils.templates import load_template_text
from .keyboard import build_categories_keyboard, build_navigation_keyboard, build_sections
from neural import processor


faq_router = Router()


@faq_router.callback_query(FAQCallback.filter(F.category_id.is_not(None) & F.section_id.is_(None)))
async def show_category(callback: CallbackQuery, callback_data: FAQCallback):
    manager = FaqManager("./storage/faq.json")
    await manager.load_data()

    categories = await manager.get_categories()
    if callback_data.category_id >= len(categories):
        await callback.answer("Категория не найдена.", show_alert=True)
        return
    
    category_name = categories[callback_data.category_id]

    # Получаем список разделов в категории
    sections = await manager.get_sections_by_category(category_name)

    # Склоняем имя категории в дательный падеж
    category_declined = await decline_to_dative(category_name)
    category_declined = category_declined.capitalize()

    # Рендерим шаблон
    text = await load_template_text(
        template_name="faq_section_list",
        section_type_declined=category_declined,
        sections=sections
    )

    # Показываем список разделов в выбранной категории с помощью шаблона
    await callback.message.edit_text(
        text,
        reply_markup=await build_sections(callback_data.category_id),  # Передаём ID, а не имя
        parse_mode="HTML"
    )
    await callback.answer()


@faq_router.callback_query(FAQCallback.filter(F.section_id.is_not(None) & F.item_id.is_(None)))
async def show_section(callback: CallbackQuery, callback_data: FAQCallback, state: FSMContext):
    manager = FaqManager("./storage/faq.json")
    await manager.load_data()

    categories = await manager.get_categories()
    if callback_data.category_id >= len(categories):
        await callback.answer("Категория не найдена.", show_alert=True)
        return

    category_name = categories[callback_data.category_id]
    sections = await manager.get_sections_by_category(category_name)

    if callback_data.section_id >= len(sections):
        await callback.answer("Раздел не найден.", show_alert=True)
        return

    section_name = sections[callback_data.section_id]

    items = await manager.get_items_by_section(category_name, section_name)

    iterator = FAQIterator(items)

    if not items:
        await callback.message.edit_text("В этом разделе пока нет вопросов.")
        await callback.answer()
        return


    item = None
    if await iterator.has_next():
        item, _ = await iterator.next()

        await state.update_data(iterator=iterator, callback_data=callback_data)

    text = await load_template_text("faq_item", item=item)

    await callback.message.edit_text(
        text,
        reply_markup=await build_navigation_keyboard()
    )
    await callback.answer()


@faq_router.callback_query(FAQCallback.filter(F.action == "next"))
async def next_item(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    iterator: FAQIterator = data.get("iterator")

    if not iterator:
        await callback.answer("Ошибка: сессия истекла.", show_alert=True)
        return

    next_item_data = await iterator.next()

    if next_item_data:
        item, _ = next_item_data
        text = await load_template_text("faq_item", item=item)
        await callback.message.edit_text(
            text,
            reply_markup=await build_navigation_keyboard()
        )
    else:
        await callback.answer("Больше вопросов нет.", show_alert=True)

    await callback.answer()


@faq_router.callback_query(FAQCallback.filter(F.action == "prev"))
async def prev_item(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    iterator: FAQIterator = data.get("iterator")

    if not iterator:
        await callback.answer("Ошибка: сессия истекла.", show_alert=True)
        return

    prev_item_data = await iterator.prev()

    if prev_item_data:
        item, _ = prev_item_data
        text = await load_template_text("faq_item", item=item)
        await callback.message.edit_text(
            text,
            reply_markup=await build_navigation_keyboard()
        )
    else:
        await callback.answer("Это первый вопрос.", show_alert=True)

    await callback.answer()


@faq_router.callback_query(FAQCallback.filter(F.action == "sections"))
async def to_sections(callback: CallbackQuery, state: FSMContext):

    # Пытаемся получить данные из состояния
    data = await state.get_data()
    
    # Проверяем, есть ли в данных category_id (установленный из нейроинтерфейса)
    category_id = data.get("category_id")

    if category_id is not None:
        # Если category_id есть в состоянии, используем его для вызова show_category
        callback_data_mock = type('MockCallbackData', (), {'category_id': category_id})()
        await show_category(callback, callback_data_mock)
    else:
        callback_data_from_state = data.get("callback_data")
        if callback_data_from_state:
            await show_category(callback, callback_data_from_state)
        else:
            await callback.answer("Данные категории не найдены.", show_alert=True)
            return
    
    await state.clear()    
    await callback.answer()


@faq_router.callback_query(FAQCallback.filter(F.action == "back"))
async def back(callback: CallbackQuery):

    text = await load_template_text("faq_menu")
    await callback.message.edit_text(
        text = text,
        reply_markup = await build_categories_keyboard()
    )


@faq_router.callback_query(FAQCallback.filter(F.action == "startup"))
async def startup_screen(callback: CallbackQuery):

    text = await load_template_text("startup_menu")
    await callback.message.edit_text(
        text = text,
        reply_markup = startup_keyboard()
    )
    await callback.answer()


async def find_faq_section_from_neuro(message: Message, search_term: str, state: FSMContext) -> Dict[str, Any]:
    """
    Обработчик для вызова из нейроинтерфейса.
    Принимает поисковый термин и возвращает найденную секцию FAQ.
    """
    result = await find_faq_section_by_question(search_term)

    if not result:
        await message.answer("Вопросы в FAQ по данной тематике не найдены.")
        return

    manager = FaqManager("./storage/faq.json")
    await manager.load_data()

    all_categories = await manager.get_categories()
    category_name = result.get("category")
    
    try:
        category_id = all_categories.index(category_name)
    except ValueError:
        await message.answer("Категория в FAQ не найдена.")
        return

    items = await manager.get_items_by_section(category_name, result.get("section"))
    iterator = FAQIterator(items)

    item: FaqItem = result.get("item")
    
    text = await load_template_text(
        template_name="faq_item",
        item=item
    )
    
    await message.answer(
        text,
        reply_markup=await build_navigation_keyboard(),
        parse_mode="HTML"
    )
    
    await state.update_data(iterator=iterator, category_id=category_id)