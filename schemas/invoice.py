from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
from datetime import datetime

class InvoiceCreate(BaseModel):
    user_id: int
    amount: Decimal

class InvoiceUpdate(BaseModel):
    is_payed: Optional[bool] = None

class InvoiceResponse(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    created_at: datetime
    is_payed: bool

    class Config:
        from_attributes = True