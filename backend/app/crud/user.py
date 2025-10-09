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

    # Create new user with hashed password and default balance
    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        balance=100.0  # Starting balance
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


def add_balance(db: Session, user_id: int, amount: float) -> User:
    """
    Add money to user's balance

    Args:
        db: Database session
        user_id: User ID
        amount: Amount to add (must be positive)

    Returns:
        Updated User object

    Raises:
        HTTPException 404: User not found
        HTTPException 400: Invalid amount
    """
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive"
        )

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.balance += amount
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def deduct_balance(db: Session, user_id: int, amount: float) -> User:
    """
    Deduct money from user's balance

    Args:
        db: Database session
        user_id: User ID
        amount: Amount to deduct

    Returns:
        Updated User object

    Raises:
        HTTPException 404: User not found
        HTTPException 400: Insufficient balance
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.balance < amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient balance. Current balance: ${user.balance:.2f}, Required: ${amount:.2f}"
        )

    user.balance -= amount
    db.add(user)
    db.flush()  # Flush but don't commit yet (caller may be in transaction)
    return user