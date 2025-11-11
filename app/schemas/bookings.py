from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from app.utils.enums import BookingStatus

class BookingBase(BaseModel):
    user_id: str
    service_id: str
    start_time: datetime
    end_time: datetime
    status: BookingStatus = BookingStatus.PENDING

class BookingCreate(BookingBase):
    pass

class BookingResponse(BookingBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class BookingUpdate(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: Optional[BookingStatus]= None