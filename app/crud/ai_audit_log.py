"""
CRUD operations for AI Audit Log
"""
from sqlmodel import Session
from typing import Optional
from app.models.ai_audit_log import AI_Audit_Log


def create_audit_log(
        db: Session,
        agent_type: str,
        input_text: str,
        detected_intent: str,
        actions_taken: str,
        metadata: Optional[str] = None
) -> AI_Audit_Log:
    """
    Create an audit log entry for AI agent actions

    Args:
        db: Database session
        agent_type: Type of agent (receptionist, book_officer, resources_officer)
        input_text: User's input message
        detected_intent: Classified intent
        actions_taken: JSON string of actions performed
        metadata: Optional additional metadata as JSON string

    Returns:
        Created AI_Audit_Log object
    """
    log_entry = AI_Audit_Log(
        agent_type=agent_type,
        input_text=input_text,
        detected_intent=detected_intent,
        actions_taken=actions_taken,
        metadata=metadata
    )

    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)

    return log_entry