from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BookCreate(BaseModel):
    title: str
    author: str
    isbn: Optional[str] = None
    category: str
    description: Optional[str] = None
    digital_url: Optional[str] = None
    stock_count: int = 0
    price: float = 25.0


class BookRead(BaseModel):
    id: int
    title: str
    author: str
    isbn: Optional[str] = None
    category: str
    description: Optional[str] = None
    digital_url: Optional[str] = None
    stock_count: int
    price: float
    created_at: datetime

    class Config:
        from_attributes = True


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    isbn: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    digital_url: Optional[str] = None
    stock_count: Optional[int] = None
    price: Optional[float] = None