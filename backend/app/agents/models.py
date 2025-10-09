"""
Pydantic models for agent outputs and tool responses
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any, List
from datetime import datetime


class ReceptionistOutput(BaseModel):
    """Output model for receptionist agent intent classification"""
    intent: Literal["other_question", "book_question", "resources_question"] = Field(
        description="Classified intent of the user message"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )
    parsed_details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Extracted parameters like book_title, resource_id, dates, etc."
    )
    clarify: Optional[str] = Field(
        default=None,
        description="Clarifying question if more information is needed"
    )


class BookInfo(BaseModel):
    """Book information response"""
    id: int
    title: str
    author: str
    isbn: str
    category: str
    description: Optional[str] = None
    price: float
    stock_count: int
    digital_url: Optional[str] = None


class ResourceInfo(BaseModel):
    """Resource information response"""
    id: int
    name: str
    type: str
    capacity: int
    hourly_rate: float
    open_hour: str
    close_hour: str
    features: Optional[str] = None


class BookingInfo(BaseModel):
    """Booking information response"""
    id: int
    resource_id: int
    user_id: int
    start_datetime: datetime
    end_datetime: datetime
    status: str
    notes: Optional[str] = None


class TransactionResult(BaseModel):
    """Transaction result for purchases"""
    transaction_id: int
    book_id: int
    book_title: str
    quantity: int
    amount: float
    currency: str
    status: str


class AvailabilityResult(BaseModel):
    """Availability check result"""
    available: bool
    start: str
    end: str
    resource_id: int
    message: Optional[str] = None