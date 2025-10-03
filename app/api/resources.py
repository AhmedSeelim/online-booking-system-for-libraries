from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from ..schemas.resource import ResourceCreate, ResourceRead, ResourceUpdate
from ..crud import resource as resource_crud
from ..deps import get_db_session, is_admin
from ..models.user import User

router = APIRouter(prefix="/resources", tags=["Resources"])


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