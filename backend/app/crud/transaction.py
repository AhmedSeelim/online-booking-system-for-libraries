from sqlmodel import Session
from typing import Optional

from ..models.transaction import Transaction, TransactionStatus


def create_transaction(
        db: Session,
        user_id: int,
        amount: float,
        book_id: Optional[int] = None,
        booking_id: Optional[int] = None,
        status: TransactionStatus = TransactionStatus.completed,
        currency: str = "USD"
) -> Transaction:
    """
    Create a transaction record

    Args:
        db: Database session
        user_id: User ID
        amount: Transaction amount
        book_id: Optional book ID for book purchases
        booking_id: Optional booking ID for booking payments
        status: Transaction status (default: completed)
        currency: Currency code (default: USD)

    Returns:
        Created Transaction object
    """
    transaction = Transaction(
        user_id=user_id,
        book_id=book_id,
        booking_id=booking_id,
        amount=amount,
        currency=currency,
        status=status
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction