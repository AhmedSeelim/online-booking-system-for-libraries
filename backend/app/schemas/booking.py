from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..models.booking import BookingStatus


class BookingCreate(BaseModel):
    resource_id: int
    start_datetime: datetime
    end_datetime: datetime
    notes: Optional[str] = None


class BookingRead(BaseModel):
    id: int
    resource_id: int
    user_id: int
    start_datetime: datetime
    end_datetime: datetime
    status: BookingStatus
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True