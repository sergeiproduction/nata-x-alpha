from typing import Optional
from aiogram.filters.callback_data import CallbackData

class PaymentCallback(CallbackData, prefix="payment"):
    action: str
    month_count: Optional[int] = 0
    discount: Optional[float] = 0.0