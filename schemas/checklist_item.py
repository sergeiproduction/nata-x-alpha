from pydantic import BaseModel

class ChecklistItemCreate(BaseModel):
    checklist_id: int
    content: str

class ChecklistItemUpdate(BaseModel):
    content: str = None

class ChecklistItemResponse(BaseModel):
    id: int
    checklist_id: int
    content: str

    class Config:
        from_attributes = True