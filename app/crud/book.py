from sqlmodel import Session, select, or_
from typing import Optional, List

from ..models.book import Book
from ..schemas.book import BookCreate, BookUpdate


def create_book(db: Session, book_data: BookCreate) -> Book:
    """Create a new book"""
    book = Book(**book_data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def get_book(db: Session, book_id: int) -> Optional[Book]:
    """Get book by ID"""
    return db.get(Book, book_id)


def list_books(
        db: Session,
        q: Optional[str] = None,
        category: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
) -> List[Book]:
    """
    List books with optional search and filtering

    Args:
        db: Database session
        q: Search query (searches title and author, case-insensitive)
        category: Filter by category
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return

    Returns:
        List of Book objects
    """
    statement = select(Book)

    # Search by query (title or author)
    if q:
        search_filter = or_(
            Book.title.ilike(f"%{q}%"),
            Book.author.ilike(f"%{q}%")
        )
        statement = statement.where(search_filter)

    # Filter by category
    if category:
        statement = statement.where(Book.category == category)

    # Apply pagination
    statement = statement.offset(skip).limit(limit)

    books = db.exec(statement).all()
    return books


def update_book(db: Session, book_id: int, book_data: BookUpdate) -> Optional[Book]:
    """Update a book"""
    book = db.get(Book, book_id)
    if not book:
        return None

    # Update only provided fields
    update_data = book_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(book, field, value)

    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id: int) -> bool:
    """Delete a book"""
    book = db.get(Book, book_id)
    if not book:
        return False

    db.delete(book)
    db.commit()
    return True