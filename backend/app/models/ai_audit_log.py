from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional


class AI_Audit_Log(SQLModel, table=True):
    __tablename__ = "ai_audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    agent_type: str = Field(index=True)
    input_text: str
    detected_intent: str
    actions_taken: str  # JSON string or text
    meta_data: Optional[str] = None  # JSON string
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        index=True
    )