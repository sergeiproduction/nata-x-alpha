from pydantic import BaseModel
from datetime import datetime

class UserPromocodeCreate(BaseModel):
    campaign_id: int
    user_id: int
    name: str

class UserPromocodeUpdate(BaseModel):
    name: str = None

class UserPromocodeResponse(BaseModel):
    id: int
    campaign_id: int
    user_id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True