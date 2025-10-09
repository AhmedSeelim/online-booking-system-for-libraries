from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from datetime import datetime, timedelta, timezone

from ..schemas.booking import BookingCreate, BookingRead
from ..crud import booking as booking_crud
from ..deps import get_db_session, get_current_user, is_admin
from ..models.user import User
from ..models.resource import Resource

router = APIRouter(prefix="/bookings", tags=["Bookings"])

# Configuration constants
MAX_BOOKING_DURATION_HOURS = 8
MIN_LEAD_TIME_MINUTES = 15


@router.post("", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def create_booking(
        booking_data: BookingCreate,
        db: Annotated[Session, Depends(get_db_session)],
        current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Create a new booking (authenticated users)

    **Headers:**
    - Authorization: Bearer {token}

    **Request Body:**
    ```json
    {
        "resource_id": 1,
        "start_datetime": "2025-10-05T10:00:00Z",
        "end_datetime": "2025-10-05T12:00:00Z",
        "notes": "Optional notes"
    }
    ```

    **Validation Rules:**
    - start_datetime must be before end_datetime
    - Duration cannot exceed 8 hours
    - Must book at least 15 minutes in advance
    - Resource must exist
    - Time slot must be available

    **Response:** 201 Created
    - Returns created booking

    **Errors:**
    - 400: Invalid input (validation failed)
    - 401: Not authenticated
    - 404: Resource not found
    - 409: Time slot conflict (resource already booked)
    """
    # Validate start < end
    if booking_data.start_datetime >= booking_data.end_datetime:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start time must be before end time"
        )

    # Validate duration
    duration = booking_data.end_datetime - booking_data.start_datetime
    max_duration = timedelta(hours=MAX_BOOKING_DURATION_HOURS)
    if duration > max_duration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking duration cannot exceed {MAX_BOOKING_DURATION_HOURS} hours"
        )

    # Validate minimum lead time
    now = datetime.now(timezone.utc)
    min_lead = timedelta(minutes=MIN_LEAD_TIME_MINUTES)
    if booking_data.start_datetime < now + min_lead:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking must be made at least {MIN_LEAD_TIME_MINUTES} minutes in advance"
        )

    # Check if resource exists
    resource = db.get(Resource, booking_data.resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    # Create booking atomically with availability check
    booking = booking_crud.create_booking_atomic(
        db=db,
        user_id=current_user.id,
        resource_id=booking_data.resource_id,
        start=booking_data.start_datetime,
        end=booking_data.end_datetime,
        notes=booking_data.notes
    )

    return booking


@router.get("", response_model=List[BookingRead])
def list_user_bookings(
        db: Annotated[Session, Depends(get_db_session)],
        current_user: Annotated[User, Depends(get_current_user)],
        past: bool = Query(False, description="Include past bookings")
):
    """
    Get current user's bookings

    **Headers:**
    - Authorization: Bearer {token}

    **Query Parameters:**
    - past: Include past bookings (default: false, only upcoming)

    **Response:** 200 OK
    - Returns array of user's bookings

    **Errors:**
    - 401: Not authenticated
    """
    bookings = booking_crud.get_user_bookings(
        db=db,
        user_id=current_user.id,
        include_past=past
    )
    return bookings


@router.delete("/{booking_id}", response_model=BookingRead)
def cancel_booking(
        booking_id: int,
        db: Annotated[Session, Depends(get_db_session)],
        current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Cancel a booking

    **Headers:**
    - Authorization: Bearer {token}

    **Cancellation Rules:**
    - Users can cancel their own bookings if more than 1 hour before start time
    - Admins can cancel any booking at any time

    **Response:** 200 OK
    - Returns cancelled booking

    **Errors:**
    - 400: Too late to cancel or already cancelled
    - 401: Not authenticated
    - 403: Not authorized to cancel this booking
    - 404: Booking not found
    """
    is_admin_user = current_user.role == "admin"

    booking = booking_crud.cancel_booking(
        db=db,
        booking_id=booking_id,
        user_id=current_user.id,
        is_admin=is_admin_user,
        cancellation_window_hours=1
    )

    return booking