from pydantic import BaseModel

class UserChecklistItemCreate(BaseModel):
    user_id: int
    item_id: int
    is_completed: bool = False

class UserChecklistItemUpdate(BaseModel):
    is_completed: bool = None

class UserChecklistItemResponse(BaseModel):
    user_id: int
    item_id: int
    is_completed: bool

    class Config:
        from_attributes = True