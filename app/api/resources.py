from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, and_
from datetime import datetime, timedelta, time, timezone

from ..schemas.resource import ResourceCreate, ResourceRead, ResourceUpdate
from ..crud import resource as resource_crud
from ..crud import booking as booking_crud
from ..deps import get_db_session, is_admin
from ..models.user import User
from ..models.booking import Booking, BookingStatus

router = APIRouter(prefix="/resources", tags=["Resources"])

SLOT_DURATION_MINUTES = 30


@router.get("/{resource_id}/availability")
def check_resource_availability(
        resource_id: int,
        db: Annotated[Session, Depends(get_db_session)],
        start: Optional[str] = Query(None, description="Start datetime ISO format"),
        end: Optional[str] = Query(None, description="End datetime ISO format"),
        date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format")
):
    """
    Check resource availability

    **Query Parameters (two modes):**

    Mode 1 - Check specific time range:
    - start: Start datetime in ISO format (e.g., "2025-10-05T10:00:00Z")
    - end: End datetime in ISO format

    Mode 2 - Get available slots for a date:
    - date: Date in YYYY-MM-DD format (e.g., "2025-10-05")

    **Response for Mode 1:** 200 OK
    ```json
    {
        "available": true,
        "start": "2025-10-05T10:00:00Z",
        "end": "2025-10-05T12:00:00Z"
    }
    ```

    **Response for Mode 2:** 200 OK
    ```json
    {
        "date": "2025-10-05",
        "slots": [
            {
                "start": "2025-10-05T09:00:00Z",
                "end": "2025-10-05T09:30:00Z",
                "available": true
            },
            ...
        ]
    }
    ```

    **Errors:**
    - 400: Invalid parameters
    - 404: Resource not found
    """
    # Check if resource exists
    resource = resource_crud.get_resource(db, resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )

    # Mode 1: Check specific time range
    if start and end:
        try:
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid datetime format. Use ISO format (e.g., 2025-10-05T10:00:00Z)"
            )

        if start_dt >= end_dt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start time must be before end time"
            )

        is_available = booking_crud.is_resource_available(db, resource_id, start_dt, end_dt)

        return {
            "available": is_available,
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat()
        }

    # Mode 2: Get available slots for a date
    elif date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )

        # Parse resource open/close hours
        try:
            open_time = datetime.strptime(resource.open_hour, "%H:%M").time()
            close_time = datetime.strptime(resource.close_hour, "%H:%M").time()
        except ValueError:
            # Default to 9 AM - 9 PM if parsing fails
            open_time = time(9, 0)
            close_time = time(21, 0)

        # Generate slots for the day
        slots = []
        current_dt = datetime.combine(target_date, open_time).replace(tzinfo=timezone.utc)
        end_of_day = datetime.combine(target_date, close_time).replace(tzinfo=timezone.utc)

        slot_delta = timedelta(minutes=SLOT_DURATION_MINUTES)

        while current_dt < end_of_day:
            slot_end = current_dt + slot_delta
            if slot_end > end_of_day:
                break

            is_available = booking_crud.is_resource_available(db, resource_id, current_dt, slot_end)

            slots.append({
                "start": current_dt.isoformat(),
                "end": slot_end.isoformat(),
                "available": is_available
            })

            current_dt = slot_end

        return {
            "date": date,
            "resource_id": resource_id,
            "resource_name": resource.name,
            "slots": slots
        }

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide either (start AND end) or (date) parameters"
        )


@router.get("", response_model=List[ResourceRead])
def list_resources(
        db: Annotated[Session, Depends(get_db_session)],
        min_capacity: Optional[int] = Query(None, description="Minimum capacity filter"),
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    Get list of resources with optional filtering

    **Query Parameters:**
    - min_capacity: Filter resources with at least this capacity
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)

    **Response:** 200 OK
    - Returns array of resources
    """
    skip = (page - 1) * limit
    resources = resource_crud.list_resources(
        db=db,
        min_capacity=min_capacity,
        skip=skip,
        limit=limit
    )
    return resources


@router.get("/{resource_id}", response_model=ResourceRead)
def get_resource(
        resource_id: int,
        db: Annotated[Session, Depends(get_db_session)]
):
    """
    Get a specific resource by ID

    **Response:** 200 OK
    - Returns resource details

    **Errors:**
    - 404: Resource not found
    """
    resource = resource_crud.get_resource(db, resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    return resource


@router.post("", response_model=ResourceRead, status_code=status.HTTP_201_CREATED)
def create_resource(
        resource_data: ResourceCreate,
        db: Annotated[Session, Depends(get_db_session)],
        admin: Annotated[User, Depends(is_admin)]
):
    """
    Create a new resource (Admin only)

    **Headers:**
    - Authorization: Bearer {admin_token}

    **Request Body:**
    - name: Resource name
    - type: Resource type (room, seat, equipment)
    - capacity: Capacity (number of people/units)
    - features: Optional JSON string of features
    - open_hour: Opening time (default: "09:00")
    - close_hour: Closing time (default: "21:00")

    **Response:** 201 Created
    - Returns created resource

    **Errors:**
    - 401: Not authenticated
    - 403: Not authorized (not admin)
    """
    resource = resource_crud.create_resource(db, resource_data)
    return resource


@router.put("/{resource_id}", response_model=ResourceRead)
def update_resource(
        resource_id: int,
        resource_data: ResourceUpdate,
        db: Annotated[Session, Depends(get_db_session)],
        admin: Annotated[User, Depends(is_admin)]
):
    """
    Update a resource (Admin only)

    **Headers:**
    - Authorization: Bearer {admin_token}

    **Request Body:**
    - Any resource fields to update (all optional)

    **Response:** 200 OK
    - Returns updated resource

    **Errors:**
    - 401: Not authenticated
    - 403: Not authorized (not admin)
    - 404: Resource not found
    """
    resource = resource_crud.update_resource(db, resource_id, resource_data)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    return resource


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(
        resource_id: int,
        db: Annotated[Session, Depends(get_db_session)],
        admin: Annotated[User, Depends(is_admin)]
):
    """
    Delete a resource (Admin only)

    **Headers:**
    - Authorization: Bearer {admin_token}

    **Response:** 204 No Content

    **Errors:**
    - 401: Not authenticated
    - 403: Not authorized (not admin)
    - 404: Resource not found
    """
    deleted = resource_crud.delete_resource(db, resource_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found"
        )
    return None