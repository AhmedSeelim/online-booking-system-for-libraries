from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Enum as SQLEnum
from datetime import datetime, timezone
from typing import Optional
from enum import Enum


class BookingStatus(str, Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"


class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    id: Optional[int] = Field(default=None, primary_key=True)
    resource_id: int = Field(foreign_key="resources.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    start_datetime: datetime = Field(index=True)
    end_datetime: datetime = Field(index=True)
    status: BookingStatus = Field(
        default=BookingStatus.confirmed,
        sa_column=Column(SQLEnum(BookingStatus))
    )
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))