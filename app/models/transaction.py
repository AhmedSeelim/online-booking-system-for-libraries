from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Enum as SQLEnum
from datetime import datetime, timezone
from typing import Optional
from enum import Enum


class TransactionStatus(str, Enum):
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    booking_id: Optional[int] = Field(default=None, foreign_key="bookings.id")
    book_id: Optional[int] = Field(default=None, foreign_key="books.id")
    amount: float
    currency: str = Field(default="USD")
    status: TransactionStatus = Field(sa_column=Column(SQLEnum(TransactionStatus)))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))