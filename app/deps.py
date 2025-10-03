from typing import Generator, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from .database import engine
from .core.security import decode_access_token
from .models.user import User

security = HTTPBearer()


def get_db_session() -> Generator[Session, None, None]:
    """Dependency for getting database session"""
    with Session(engine) as session:
        yield session


async def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
        db: Annotated[Session, Depends(get_db_session)]
) -> User:
    """
    Dependency to get current authenticated user from JWT token

    Returns:
        User object

    Raises:
        HTTPException 401: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def is_admin(
        current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Dependency to check if current user has admin role

    Returns:
        User object if admin

    Raises:
        HTTPException 403: If user is not an admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action"
        )
    return current_user