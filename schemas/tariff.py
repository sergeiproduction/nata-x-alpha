from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TariffBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    duration_days: int
    features: Optional[str] = None

class TariffCreate(TariffBase):
    pass

class TariffUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    duration_days: Optional[int] = None
    features: Optional[str] = None
    is_active: Optional[bool] = None

class TariffResponse(TariffBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True