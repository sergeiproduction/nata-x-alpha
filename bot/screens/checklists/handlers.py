from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.screens.checklists.keyboards import checklist_item_keyboard, checklist_keyboard
from bot.screens.checklists.user_cases import create_progress_bar
from bot.services.checklist import ChecklistService
from bot.services.checklist_item import ChecklistItemService
from bot.services.checklist_user_item import UserChecklistItemService
from bot.services.user import UserService

from schemas.user_checklist_item import UserChecklistItemUpdate
from utils.templates import load_template_text

from .filters import ChecklistCallback, ChecklistItemCallback


checklist_router = Router()


@checklist_router.callback_query(ChecklistCallback.filter(F.id.is_not(None)))
async def show_checklist_items(
    callback_query: CallbackQuery, 
    callback_data: ChecklistCallback,
    checklist_service: ChecklistService,
    user_checklist_item_service: UserChecklistItemService,
    user_service: UserService,
    checklist_item_service: ChecklistItemService,
):
    """
    Обработчик для просмотра элементов конкретного чек-листа
    """
    checklist_id = callback_data.id
    user_id = callback_query.from_user.id

    user = await user_service.get_user_by_telegram_id(user_id)

    items_with_progress = await user_checklist_item_service.get_user_items_by_checklist(
        user_id=user.id, 
        checklist_id=checklist_id
    )

    checklist = await checklist_service.get_checklist(checklist_id)
    
    if not checklist:
        await callback_query.answer("Чек-лист не найден", show_alert=True)
        return

    # Получаем все элементы чек-листа (для получения их содержимого)
    checklist_items = await checklist_item_service.get_checklist_items(checklist_id)

    # Вычисляем количество выполненных и общее количество
    completed_count = sum(1 for item in items_with_progress if item.is_completed)
    total_count = len(items_with_progress)

    # Вычисляем процент выполнения
    progress_percentage = (completed_count * 100) // total_count if total_count > 0 else 0

    # Создаем прогресс-бар
    progress_bar = create_progress_bar(completed_count, total_count)

    # Загружаем текст шаблона
    message_text = await load_template_text(
        "checklist_view",  # Имя файла шаблона (без .j2)
        checklist=checklist,
        items=checklist_items, # Передаем обогащенные элементы
        progress_percentage=progress_percentage,
        progress_bar=progress_bar
    )

    # Формируем клавиатуру с элементами чек-листа
    keyboard = await checklist_item_keyboard(items_with_progress, checklist_id)
    
    await callback_query.message.edit_text(
        text=message_text,
        reply_markup=keyboard
    )
    
    await callback_query.answer()


@checklist_router.callback_query(ChecklistItemCallback.filter())
async def toggle_checklist_item_status(
    callback_query: CallbackQuery,
    callback_data: ChecklistItemCallback,
    user_service: UserService,
    user_checklist_item_service: UserChecklistItemService,
    checklist_item_service: ChecklistItemService,
    checklist_service: ChecklistService,
):
    """
    Обработчик для переключения статуса выполнения элемента чек-листа
    """
    user_id = callback_query.from_user.id
    item_id = callback_data.item_id
    checklist_id = callback_data.checklist_id

    user = await user_service.get_user_by_telegram_id(user_id)

    current_item = await user_checklist_item_service.get_user_checklist_item(user.id, item_id)
    
    if not current_item:
        await callback_query.answer("Элемент чек-листа не найден", show_alert=True)
        return

    # Переключаем статус
    new_status = not current_item.is_completed
    
    # Обновляем статус элемента
    update_data = UserChecklistItemUpdate(is_completed=new_status)
    updated_item = await user_checklist_item_service.update_user_checklist_item(
        user.id, item_id, update_data
    )

    if not updated_item:
        await callback_query.answer("Ошибка обновления статуса", show_alert=True)
        return

    # Получаем обновленный список элементов для этого чек-листа
    items_with_progress = await user_checklist_item_service.get_user_items_by_checklist(
        user_id=user.id, 
        checklist_id=checklist_id
    )

    # Получаем информацию о чек-листе для заголовка
    checklist = await checklist_service.get_checklist(checklist_id)
    
    if not checklist:
        await callback_query.answer("Чек-лист не найден", show_alert=True)
        return

    # Получаем все элементы чек-листа (для получения их содержимого)
    checklist_items = await checklist_item_service.get_checklist_items(checklist_id)

    # Вычисляем количество выполненных и общее количество
    completed_count = sum(1 for item in items_with_progress if item.is_completed)
    total_count = len(items_with_progress)

    # Вычисляем процент выполнения
    progress_percentage = (completed_count * 100) // total_count if total_count > 0 else 0

    # Создаем прогресс-бар
    progress_bar = create_progress_bar(completed_count, total_count)

    # Загружаем текст шаблона
    message_text = await load_template_text(
        "checklist_view",  # Имя файла шаблона (без .j2)
        checklist=checklist,
        items=checklist_items, # Передаем обогащенные элементы
        progress_percentage=progress_percentage,
        progress_bar=progress_bar
    )

    # Формируем клавиатуру с элементами чек-листа
    keyboard = await checklist_item_keyboard(items_with_progress, checklist_id)
    
    
    await callback_query.message.edit_text(
        text=message_text,
        reply_markup=keyboard
    )
    
    status_text = "выполнен" if new_status else "не выполнен"    
    await callback_query.answer(f"Элемент отмечен как {status_text}", show_alert=False)



@checklist_router.callback_query(ChecklistCallback.filter(F.action == "back"))
async def go_back_to_checklists(
    callback_query: CallbackQuery,
    checklist_service: ChecklistService, checklist_repo,
    session
):
    """
    Обработчик для возврата к списку чек-листов
    """
    
    checklist_service = checklist_service(checklist_repo(session))

    checklists = await checklist_service.get_active_checklists()

    text = await load_template_text("startup_menu")

    await callback_query.message.edit_text(text, reply_markup=await checklist_keyboard(checklists))
    await callback_query.answer()
