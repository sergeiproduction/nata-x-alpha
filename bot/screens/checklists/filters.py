from typing import Optional
from aiogram.filters.callback_data import CallbackData

class ChecklistCallback(CallbackData, prefix="checklist"):
    action: Optional[str] = None
    id: Optional[int] = None


class ChecklistItemCallback(CallbackData, prefix="checklist_item"):
    item_id: int
    user_id: Optional[int] = None
    checklist_id: int
    action: Optional[str] = "toggle"