from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional


class Book(SQLModel, table=True):
    __tablename__ = "books"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    author: str = Field(index=True)
    isbn: Optional[str] = None
    category: str = Field(index=True)
    description: Optional[str] = None
    digital_url: Optional[str] = None
    stock_count: int = Field(default=0)
    price: float = Field(default=25.0)  # Book price in USD
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))