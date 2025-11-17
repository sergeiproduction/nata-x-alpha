from pydantic import BaseModel

class UserNotificationCreate(BaseModel):
    user_id: int
    notification_type_id: int
    is_active: bool = True

class UserNotificationUpdate(BaseModel):
    is_active: bool = None

class UserNotificationResponse(BaseModel):
    user_id: int
    notification_type_id: int
    is_active: bool

    class Config:
        from_attributes = True