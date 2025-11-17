from typing import List, Optional
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from bot.screens.startup.filters import StartupCallback
from schemas.checklist import ChecklistResponse
from schemas.user_checklist_item import UserChecklistItemResponse
from .filters import ChecklistCallback, ChecklistItemCallback

async def checklist_keyboard(checklists: List[ChecklistResponse]):
    builder = InlineKeyboardBuilder()

    for checklist in checklists:
        builder.row(
            InlineKeyboardButton(
                text=checklist.name,
                callback_data=ChecklistCallback(id=checklist.id).pack()
            ) 
        )

    builder.row(
        InlineKeyboardButton(
                text="Назад",
                callback_data=StartupCallback(action="back").pack()
            )
    )
    return builder.as_markup()


async def checklist_item_keyboard(
    items_with_progress: List[UserChecklistItemResponse], 
    checklist_id: int
):
    builder = InlineKeyboardBuilder()

    for index, user_item in enumerate(items_with_progress, start=1):
        status_emoji = "🟢" if user_item.is_completed else "🔴"
                
        callback_data = ChecklistItemCallback(
            item_id=user_item.item_id, 
            user_id=user_item.user_id,
            checklist_id=checklist_id
        ).pack()
        
        builder.button(
            text=f"{index} {status_emoji}",
            callback_data=callback_data
        )
  
    # Вычисляем оптимальное количество кнопок в ряду
    num_items = len(items_with_progress)

    # Вычисляем распределение кнопок по строкам
    layout = calculate_keyboard_layout(num_items)

    builder.adjust(*layout)

    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=ChecklistCallback(action="back").pack()
        )        
    )

    return builder.as_markup()

def calculate_keyboard_layout(items: int, max_columns: Optional[int] = None) -> List[int]:
    """
    Вычисляет оптимальное распределение кнопок по строкам клавиатуры.
    
    Args:
        items: Общее количество кнопок
        max_columns: Максимальное количество кнопок в строке (если None, вычисляется автоматически)
    
    Returns:
        Список с количеством кнопок в каждой строке
    """
    if items <= 0:
        return []
    
    # Если указано максимальное количество колонок, используем его
    if max_columns is not None:
        return _layout_with_max_columns(items, max_columns)
    
    # Автоматический подбор оптимального распределения
    return _optimal_layout(items)

def _layout_with_max_columns(items: int, max_columns: int) -> List[int]:
    """Распределение с ограничением по максимальному количеству колонок."""
    if max_columns <= 0:
        return [items]
    
    layout = []
    remaining = items
    
    while remaining > 0:
        if remaining >= max_columns:
            layout.append(max_columns)
            remaining -= max_columns
        else:
            layout.append(remaining)
            remaining = 0
    
    return layout

def _optimal_layout(items: int) -> List[int]:
    """Автоматический подбор оптимального распределения."""
    if items <= 5:
        return [items]
    max_cols = 5
    full_rows = items // max_cols
    remainder = items % max_cols
    
    if remainder == 0:
        return [max_cols] * full_rows
    else:
        total_rows = full_rows + 1
        
        base_items_per_row = items // total_rows
        extra_rows = items % total_rows
        
        layout = []
        
        for _ in range(extra_rows):
            layout.append(base_items_per_row + 1)
        for _ in range(total_rows - extra_rows):
            layout.append(base_items_per_row)
        
        return layout