from pydantic import BaseModel

class UserReferralCreate(BaseModel):
    user_id: int
    referrer_id: int

class UserReferralResponse(BaseModel):
    id: int
    user_id: int
    referrer_id: int

    class Config:
        from_attributes = True