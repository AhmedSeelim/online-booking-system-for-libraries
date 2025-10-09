from sqlmodel import Session, select
from typing import Optional, List

from ..models.resource import Resource
from ..schemas.resource import ResourceCreate, ResourceUpdate


def create_resource(db: Session, resource_data: ResourceCreate) -> Resource:
    """Create a new resource"""
    resource = Resource(**resource_data.model_dump())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


def get_resource(db: Session, resource_id: int) -> Optional[Resource]:
    """Get resource by ID"""
    return db.get(Resource, resource_id)


def list_resources(
        db: Session,
        min_capacity: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
) -> List[Resource]:
    """
    List resources with optional filtering

    Args:
        db: Database session
        min_capacity: Minimum capacity filter
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        List of Resource objects
    """
    statement = select(Resource)

    # Filter by minimum capacity
    if min_capacity is not None:
        statement = statement.where(Resource.capacity >= min_capacity)

    # Apply pagination
    statement = statement.offset(skip).limit(limit)

    resources = db.exec(statement).all()
    return resources


def update_resource(
        db: Session,
        resource_id: int,
        resource_data: ResourceUpdate
) -> Optional[Resource]:
    """Update a resource"""
    resource = db.get(Resource, resource_id)
    if not resource:
        return None

    # Update only provided fields
    update_data = resource_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)

    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


def delete_resource(db: Session, resource_id: int) -> bool:
    """Delete a resource"""
    resource = db.get(Resource, resource_id)
    if not resource:
        return False

    db.delete(resource)
    db.commit()
    return True