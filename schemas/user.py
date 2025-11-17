from pydantic import BaseModel
from typing import Optional, Union

class UserBase(BaseModel):
    name: str    

class UserCreate(UserBase):
    telegram_id: int

class UserUpdate(BaseModel):
    id: int
    name: Union[str, None] = None
    inn: Optional[str] = None

class UserResponse(UserBase):
    id: int
    telegram_id: Optional[int] = None
    inn: Optional[str] = None

    class Config:
        from_attributes = True


class User(UserResponse):
    is_premium: bool = False