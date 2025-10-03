from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from ..schemas.book import BookCreate, BookRead, BookUpdate
from ..crud import book as book_crud
from ..deps import get_db_session, is_admin
from ..models.user import User

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("", response_model=List[BookRead])
def list_books(
        db: Annotated[Session, Depends(get_db_session)],
        q: Optional[str] = Query(None, description="Search in title and author"),
        category: Optional[str] = Query(None, description="Filter by category"),
        page: int = Query(1, ge=1, description="Page number"),
        limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """
    Get list of books with optional search and filtering

    **Query Parameters:**
    - q: Search query (searches title and author, case-insensitive)
    - category: Filter by category
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)

    **Response:** 200 OK
    - Returns array of books
    """
    skip = (page - 1) * limit
    books = book_crud.list_books(
        db=db,
        q=q,
        category=category,
        skip=skip,
        limit=limit
    )
    return books


@router.get("/{book_id}", response_model=BookRead)
def get_book(
        book_id: int,
        db: Annotated[Session, Depends(get_db_session)]
):
    """
    Get a specific book by ID

    **Response:** 200 OK
    - Returns book details

    **Errors:**
    - 404: Book not found
    """
    book = book_crud.get_book(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book


@router.post("", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(
        book_data: BookCreate,
        db: Annotated[Session, Depends(get_db_session)],
        admin: Annotated[User, Depends(is_admin)]
):
    """
    Create a new book (Admin only)

    **Headers:**
    - Authorization: Bearer {admin_token}

    **Request Body:**
    - title: Book title
    - author: Book author
    - isbn: ISBN number (unique)
    - category: Book category
    - description: Optional description
    - digital_url: Optional URL to digital version
    - stock_count: Number of copies (default: 0)

    **Response:** 201 Created
    - Returns created book

    **Errors:**
    - 401: Not authenticated
    - 403: Not authorized (not admin)
    """
    book = book_crud.create_book(db, book_data)
    return book


@router.put("/{book_id}", response_model=BookRead)
def update_book(
        book_id: int,
        book_data: BookUpdate,
        db: Annotated[Session, Depends(get_db_session)],
        admin: Annotated[User, Depends(is_admin)]
):
    """
    Update a book (Admin only)

    **Headers:**
    - Authorization: Bearer {admin_token}

    **Request Body:**
    - Any book fields to update (all optional)

    **Response:** 200 OK
    - Returns updated book

    **Errors:**
    - 401: Not authenticated
    - 403: Not authorized (not admin)
    - 404: Book not found
    """
    book = book_crud.update_book(db, book_id, book_data)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
        book_id: int,
        db: Annotated[Session, Depends(get_db_session)],
        admin: Annotated[User, Depends(is_admin)]
):
    """
    Delete a book (Admin only)

    **Headers:**
    - Authorization: Bearer {admin_token}

    **Response:** 204 No Content

    **Errors:**
    - 401: Not authenticated
    - 403: Not authorized (not admin)
    - 404: Book not found
    """
    deleted = book_crud.delete_book(db, book_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return None