from pydantic import BaseModel

class ChecklistCreate(BaseModel):
    name: str
    description: str = ""
    is_active: bool = True

class ChecklistUpdate(BaseModel):
    name: str = None
    description: str = None
    is_active: bool = None

class ChecklistResponse(BaseModel):
    id: int
    name: str
    description: str
    is_active: bool

    class Config:
        from_attributes = True