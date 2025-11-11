from pydantic import BaseModel, Field
from datetime import datetime

class ReviewBase(BaseModel):
    booking_id: str
    rating: int = Field(..., ge=1, le=5, description="Rating between 1 and 5")
    comment: str | None = None

class ReviewCreate(ReviewBase):
    pass    

class ReviewResponse(ReviewBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewUpdate(BaseModel):
    rating: int | None = Field(None, ge=1, le=5, description="Rating between 1 and 5")
    comment: str | None = None