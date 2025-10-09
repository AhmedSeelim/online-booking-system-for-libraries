"""
API endpoint for agent chat interactions
"""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.deps import get_current_user
from app.models.user import User
from app.agents import create_agent_system

router = APIRouter(prefix="/agent", tags=["AI Agent"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    user_id: int


@router.post("/chat", response_model=ChatResponse)
def chat_with_agent(
        request: ChatRequest,
        current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Chat with the AI agent system

    **Headers:**
    - Authorization: Bearer {token}

    **Request Body:**
    ```json
    {
        "message": "I want to buy Clean Code book"
    }
    ```

    **Behavior:**
    - Message is analyzed by receptionist agent to classify intent
    - Based on intent, routed to appropriate specialist crew:
      - Books Officer for book-related requests
      - Resources Officer for booking-related requests
      - Direct response for general questions
    - All interactions are logged to AI_Audit_Log

    **Response:** 200 OK
    ```json
    {
        "response": "I found Clean Code by Robert C. Martin...",
        "user_id": 1
    }
    ```

    **Errors:**
    - 401: Not authenticated
    - 500: Agent processing error
    """
    try:
        # Create agent system for this user
        agent_system = create_agent_system(user_id=current_user.id)

        # Process the message through the agent system
        response = agent_system.process_message(request.message)

        return ChatResponse(
            response=response,
            user_id=current_user.id
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing agent request: {str(e)}"
        )