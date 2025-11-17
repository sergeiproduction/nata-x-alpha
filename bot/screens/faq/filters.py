from typing import Optional
from aiogram.filters.callback_data import CallbackData

class FAQCallback(CallbackData, prefix="faq"):
    category_id: Optional[int] = None
    section_id: Optional[int] = None
    item_id: Optional[int] = None
    action: Optional[str] = None