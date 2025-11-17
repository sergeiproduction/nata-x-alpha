from pydantic import BaseModel
from datetime import datetime

class CampaignCreate(BaseModel):
    name: str
    description: str
    start_date: datetime
    end_date: datetime

class CampaignUpdate(BaseModel):
    name: str = None
    description: str = None
    start_date: datetime = None
    end_date: datetime = None

class CampaignResponse(BaseModel):
    id: int
    name: str
    description: str
    start_date: datetime
    end_date: datetime

    class Config:
        from_attributes = True