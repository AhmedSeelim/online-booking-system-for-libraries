from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from ..models.resource import ResourceType


class ResourceCreate(BaseModel):
    name: str
    type: ResourceType
    capacity: int
    features: Optional[str] = None
    open_hour: str = "09:00"
    close_hour: str = "21:00"
    hourly_rate: float = 10.0


class ResourceRead(BaseModel):
    id: int
    name: str
    type: ResourceType
    capacity: int
    features: Optional[str] = None
    open_hour: str
    close_hour: str
    hourly_rate: float
    created_at: datetime

    class Config:
        from_attributes = True


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[ResourceType] = None
    capacity: Optional[int] = None
    features: Optional[str] = None
    open_hour: Optional[str] = None
    close_hour: Optional[str] = None
    hourly_rate: Optional[float] = None