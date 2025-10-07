from sqlmodel import Session, select, or_,func
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
    List books with optional search and filtering (case-insensitive).

    - q: case-insensitive substring match on title or author
    - category: case-insensitive exact match (trimmed)
    """
    stmt = select(Book)

    # Search by query (title or author) -> case-insensitive
    if q:
        q_clean = f"%{q.strip().lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Book.title).like(q_clean),
                func.lower(Book.author).like(q_clean)
            )
        )

    # Filter by category (case-insensitive exact match)
    if category:
        cat_clean = category.strip().lower()
        stmt = stmt.where(func.lower(Book.category) == cat_clean)

    # Pagination
    stmt = stmt.offset(skip).limit(limit)

    books = db.exec(stmt).all()
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