from pydantic import BaseModel

class UserRoleCreate(BaseModel):
    user_id: int
    role_id: int

class UserRoleResponse(BaseModel):
    id: int
    user_id: int
    role_id: int

    class Config:
        from_attributes = True