from sqlmodel import Session, select, and_, or_
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from fastapi import HTTPException, status

from ..models.booking import Booking, BookingStatus
from ..models.resource import Resource
from ..schemas.booking import BookingCreate
from ..crud.user import deduct_balance


def is_resource_available(
        db: Session,
        resource_id: int,
        start: datetime,
        end: datetime
) -> bool:
    """
    Check if a resource is available during the specified time period

    Args:
        db: Database session
        resource_id: Resource ID to check
        start: Start datetime
        end: End datetime

    Returns:
        True if available, False if there are overlapping bookings
    """
    # Query for overlapping confirmed bookings
    # Overlap occurs when NOT (existing.end <= new.start OR existing.start >= new.end)
    statement = select(Booking).where(
        and_(
            Booking.resource_id == resource_id,
            Booking.status == BookingStatus.confirmed,
            or_(
                and_(Booking.start_datetime < end, Booking.end_datetime > start)
            )
        )
    )

    conflicting_bookings = db.exec(statement).first()
    return conflicting_bookings is None


def create_booking_atomic(
        db: Session,
        user_id: int,
        resource_id: int,
        start: datetime,
        end: datetime,
        notes: Optional[str] = None
) -> Booking:
    """
    Create a booking with transactional availability check and payment

    Args:
        db: Database session
        user_id: User ID making the booking
        resource_id: Resource to book
        start: Start datetime
        end: End datetime
        notes: Optional booking notes

    Returns:
        Created Booking object

    Raises:
        HTTPException 409: If resource is not available (conflict)
        HTTPException 400: If insufficient balance
    """
    # Begin explicit transaction
    with db.begin_nested():
        # Get resource to calculate cost
        resource = db.get(Resource, resource_id)
        if not resource:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found"
            )

        # Calculate booking duration in hours
        duration = end - start
        hours = duration.total_seconds() / 3600

        # Calculate total cost
        total_cost = hours * resource.hourly_rate

        # Re-check availability inside transaction to prevent race conditions
        if not is_resource_available(db, resource_id, start, end):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Resource is not available for the selected time period"
            )

        # Deduct balance from user (raises exception if insufficient)
        deduct_balance(db, user_id, total_cost)

        # Create booking
        booking = Booking(
            resource_id=resource_id,
            user_id=user_id,
            start_datetime=start,
            end_datetime=end,
            status=BookingStatus.confirmed,
            notes=notes
        )

        db.add(booking)
        db.flush()  # Flush to get the ID
        db.refresh(booking)

    db.commit()
    return booking


def cancel_booking(
        db: Session,
        booking_id: int,
        user_id: int,
        is_admin: bool = False,
        cancellation_window_hours: int = 1
) -> Booking:
    """
    Cancel a booking with rules enforcement

    Args:
        db: Database session
        booking_id: Booking ID to cancel
        user_id: User requesting cancellation
        is_admin: Whether the user is an admin
        cancellation_window_hours: Hours before booking start that cancellation is allowed

    Returns:
        Updated Booking object

    Raises:
        HTTPException 404: Booking not found
        HTTPException 403: Not authorized to cancel
        HTTPException 400: Too late to cancel (outside cancellation window)
    """
    booking = db.get(Booking, booking_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    # Check if booking is already cancelled
    if booking.status == BookingStatus.cancelled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already cancelled"
        )

    # Check authorization
    if not is_admin and booking.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this booking"
        )

    # Check cancellation window (unless admin)
    if not is_admin:
        now = datetime.now(timezone.utc)
        aware_start_datetime = booking.start_datetime.replace(tzinfo=timezone.utc)
        cancellation_deadline = aware_start_datetime - timedelta(hours=cancellation_window_hours)

        if now > cancellation_deadline:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel booking less than {cancellation_window_hours} hour(s) before start time"
            )

    # Cancel booking
    booking.status = BookingStatus.cancelled
    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking


def get_user_bookings(
        db: Session,
        user_id: int,
        include_past: bool = False
) -> List[Booking]:
    """
    Get user's bookings

    Args:
        db: Database session
        user_id: User ID
        include_past: Whether to include past bookings

    Returns:
        List of Booking objects
    """
    statement = select(Booking).where(Booking.user_id == user_id)

    if not include_past:
        now = datetime.now(timezone.utc)
        statement = statement.where(Booking.end_datetime >= now)

    statement = statement.order_by(Booking.start_datetime)

    bookings = db.exec(statement).all()
    return bookings


def get_booking(db: Session, booking_id: int) -> Optional[Booking]:
    """Get booking by ID"""
    return db.get(Booking, booking_id)