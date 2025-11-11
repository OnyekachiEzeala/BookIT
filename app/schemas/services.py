from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ServiceBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: int
    duration_minutes: int = Field(..., gt=0)
    is_active: Optional[bool] = True

class ServiceCreate(ServiceBase):
    pass    

class ServiceResponse(ServiceBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class ServiceUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
