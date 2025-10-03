from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Enum as SQLEnum
from datetime import datetime, timezone
from typing import Optional
from enum import Enum


class ResourceType(str, Enum):
    room = "room"
    seat = "seat"
    equipment = "equipment"


class Resource(SQLModel, table=True):
    __tablename__ = "resources"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    type: ResourceType = Field(sa_column=Column(SQLEnum(ResourceType)))
    capacity: int
    features: Optional[str] = None  # JSON string or text
    open_hour: str = Field(default="09:00")
    close_hour: str = Field(default="21:00")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))