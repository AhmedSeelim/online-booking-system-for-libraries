from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ..schemas.user import UserCreate, UserRead, UserLogin, AddBalanceRequest
from ..crud.user import create_user, get_user_by_email, add_balance
from ..core.security import verify_password, create_access_token
from ..deps import get_db_session, get_current_user
from ..models.user import User
from ..config import get_settings

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(
        user_data: UserCreate,
        db: Annotated[Session, Depends(get_db_session)]
):
    """
    Register a new user

    **Request Body:**
    - name: User's full name
    - email: Valid email address
    - password: Password (min 6 characters recommended)

    **Response:** 201 Created
    - Returns created user data (without password)
    - User starts with $100.00 balance

    **Errors:**
    - 400: Invalid input data
    - 409: Email already registered
    """
    user = create_user(db, user_data)
    return user


@router.post("/login")
def login(
        login_data: UserLogin,
        db: Annotated[Session, Depends(get_db_session)]
):
    """
    Login and receive access token

    **Request Body:**
    - email: User email
    - password: User password

    **Response:** 200 OK
    ```json
    {
        "access_token": "eyJ...",
        "token_type": "bearer",
        "expires_in_minutes": 10080
    }
    ```

    **Errors:**
    - 401: Invalid credentials
    """
    # Find user by email
    user = get_user_by_email(db, login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
    }


@router.get("/me", response_model=UserRead)
def get_current_user_info(
        current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Get current authenticated user information

    **Headers:**
    - Authorization: Bearer {token}

    **Response:** 200 OK
    - Returns current user data including balance

    **Errors:**
    - 401: Invalid or missing token
    """
    return current_user


@router.post("/add-balance", response_model=UserRead)
def add_user_balance(
        balance_data: AddBalanceRequest,
        db: Annotated[Session, Depends(get_db_session)],
        current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Add money to current user's balance

    **Headers:**
    - Authorization: Bearer {token}

    **Request Body:**
    ```json
    {
        "amount": 50.00
    }
    ```

    **Response:** 200 OK
    - Returns updated user data with new balance

    **Errors:**
    - 400: Invalid amount (must be positive)
    - 401: Not authenticated
    """
    updated_user = add_balance(db, current_user.id, balance_data.amount)
    return updated_user