from sqlmodel import Session, select
from fastapi import HTTPException, status
from typing import Optional

from ..models.user import User
from ..schemas.user import UserCreate
from ..core.security import get_password_hash


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user

    Args:
        db: Database session
        user_data: User creation data

    Returns:
        Created User object

    Raises:
        HTTPException 409: If email already exists
    """
    # Check if email already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create new user with hashed password
    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get user by email address

    Args:
        db: Database session
        email: User email

    Returns:
        User object or None if not found
    """
    statement = select(User).where(User.email == email)
    return db.exec(statement).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """
    Get user by ID

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User object or None if not found
    """
    return db.get(User, user_id)