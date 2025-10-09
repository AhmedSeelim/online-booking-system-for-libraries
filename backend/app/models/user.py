from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=False)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: str = Field(default="user")
    balance: float = Field(default=100.0)  # Starting balance of $100
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))