from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserSubscriptionBase(BaseModel):
    user_id: int
    tariff_id: int
    starts_at: datetime
    expires_at: datetime
    status: str

class UserSubscriptionCreate(BaseModel):
    user_id: int
    tariff_id: int
    duration_days: Optional[int] = None

class UserSubscriptionResponse(BaseModel):
    id: int
    user_id: int
    tariff_id: int
    tariff_name: Optional[str] = None
    starts_at: datetime
    expires_at: datetime
    status: str
    created_at: datetime
    updated_at: datetime
    days_remaining: Optional[int] = None

    class Config:
        from_attributes = True

class SubscriptionRenew(BaseModel):
    tariff_id: int
    additional_days: Optional[int] = None