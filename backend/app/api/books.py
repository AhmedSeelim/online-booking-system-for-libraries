from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from pydantic import BaseModel, Field

from ..schemas.book import BookCreate, BookRead, BookUpdate
from ..crud import book as book_crud
from ..crud import transaction as transaction_crud
from ..deps import get_db_session, is_admin, get_current_user
from ..models.user import User
from ..models.book import Book
from ..models.transaction import TransactionStatus

router = APIRouter(prefix="/books", tags=["Books"])

# Default book price if not specified
DEFAULT_BOOK_PRICE = 25.00


class PurchaseRequest(BaseModel):
    quantity: int = Field(ge=1, description="Number of books to purchase")


class PurchaseResponse(BaseModel):
    transaction_id: int
    book_id: int
    book_title: str
    quantity: int
    amount: float
    currency: str
    status: str

    class Config:
        from_attributes = True


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
    - price: Price in USD (default: 25.00)

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


@router.post("/{book_id}/purchase", response_model=PurchaseResponse)
def purchase_book(
        book_id: int,
        purchase_data: PurchaseRequest,
        db: Annotated[Session, Depends(get_db_session)],
        current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Purchase a book (authenticated users)

    **Headers:**
    - Authorization: Bearer {token}

    **Request Body:**
    ```json
    {
        "quantity": 1
    }
    ```

    **Behavior:**
    - Checks if sufficient stock is available
    - Checks if user has sufficient balance
    - Decrements stock count atomically
    - Deducts total cost from user balance
    - Creates a transaction record

    **Response:** 200 OK
    ```json
    {
        "transaction_id": 1,
        "book_id": 5,
        "book_title": "Clean Code",
        "quantity": 2,
        "amount": 50.00,
        "currency": "USD",
        "status": "completed"
    }
    ```

    **Errors:**
    - 400: Out of stock, insufficient balance, or invalid quantity
    - 401: Not authenticated
    - 404: Book not found
    """
    # Begin transaction for atomic stock check, balance deduction, and transaction creation
    with db.begin_nested():
        # Get book with lock
        book = db.get(Book, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        # Check stock availability
        if book.stock_count < purchase_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Only {book.stock_count} copies available"
            )

        # Calculate total amount
        amount = book.price * purchase_data.quantity

        # Check user balance and deduct (this will raise exception if insufficient)
        from app.crud.user import deduct_balance
        deduct_balance(db, current_user.id, amount)

        # Decrement stock atomically
        book.stock_count -= purchase_data.quantity
        db.add(book)
        db.flush()

    # Create transaction record
    transaction = transaction_crud.create_transaction(
        db=db,
        user_id=current_user.id,
        amount=amount,
        book_id=book_id,
        status=TransactionStatus.completed
    )

    # Commit the transaction
    db.commit()

    return PurchaseResponse(
        transaction_id=transaction.id,
        book_id=book.id,
        book_title=book.title,
        quantity=purchase_data.quantity,
        amount=amount,
        currency=transaction.currency,
        status=transaction.status.value
    )