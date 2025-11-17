from pydantic import BaseModel

class NotificationTypeCreate(BaseModel):
    name: str
    description: str
    default_enabled: bool = True
    advance_days: int = 1

class NotificationTypeUpdate(BaseModel):
    name: str = None
    description: str = None
    default_enabled: bool = None
    advance_days: int = None

class NotificationTypeResponse(BaseModel):
    id: int
    name: str
    description: str
    default_enabled: bool
    advance_days: int

    class Config:
        from_attributes = True