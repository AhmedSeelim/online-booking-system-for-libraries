"""
CrewAI Tools for agents
Wraps CRUD operations and API functionality
"""
from crewai.tools import BaseTool
from typing import Optional, Type
from pydantic import BaseModel, Field
from datetime import datetime
import json

# Mock mode for offline testing
MOCK_MODE = False

# Mock data stores
mock_books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "isbn": "978-0132350884",
     "category": "Technology", "description": "A handbook of agile software craftsmanship",
     "price": 42.99, "stock_count": 6},
    {"id": 2, "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "isbn": "978-0135957059",
     "category": "Technology", "description": "Your journey to mastery",
     "price": 39.99, "stock_count": 4},
    {"id": 3, "title": "1984", "author": "George Orwell", "isbn": "978-0451524935",
     "category": "Fiction", "description": "A dystopian novel",
     "price": 15.99, "stock_count": 4},
]

mock_resources = [
    {"id": 1, "name": "Conference Room A", "type": "room", "capacity": 12,
     "hourly_rate": 15.0, "open_hour": "08:00", "close_hour": "22:00"},
    {"id": 2, "name": "Study Room 101", "type": "room", "capacity": 4,
     "hourly_rate": 8.0, "open_hour": "09:00", "close_hour": "21:00"},
    {"id": 3, "name": "Reading Desk #5", "type": "seat", "capacity": 1,
     "hourly_rate": 2.0, "open_hour": "07:00", "close_hour": "23:00"},
]

mock_bookings = []
mock_user_balance = 100.0


# Book Tools Input Schemas
class ListBooksInput(BaseModel):
    """Input schema for list_books tool"""
    q: Optional[str] = Field(None, description="Search query for title or author")
    category: Optional[str] = Field(None, description="Filter by category")
    page: int = Field(1, description="Page number")
    limit: int = Field(20, description="Items per page")


class GetBookInput(BaseModel):
    """Input schema for get_book tool"""
    book_id: int = Field(..., description="Book ID")


class PurchaseBookInput(BaseModel):
    """Input schema for purchase_book tool"""
    user_id: int = Field(..., description="User ID making the purchase")
    book_id: int = Field(..., description="Book ID to purchase")
    quantity: int = Field(..., description="Number of copies to purchase")


# Resource Tools Input Schemas
class ListResourcesInput(BaseModel):
    """Input schema for list_resources tool"""
    min_capacity: Optional[int] = Field(None, description="Minimum capacity filter")
    page: int = Field(1, description="Page number")
    limit: int = Field(20, description="Items per page")


class GetResourceInput(BaseModel):
    """Input schema for get_resource tool"""
    resource_id: int = Field(..., description="Resource ID")


class CheckAvailabilityInput(BaseModel):
    """Input schema for check_resource_availability tool"""
    resource_id: int = Field(..., description="Resource ID")
    start: str = Field(..., description="Start datetime in ISO format")
    end: str = Field(..., description="End datetime in ISO format")


class CreateBookingInput(BaseModel):
    """Input schema for create_booking tool"""
    user_id: int = Field(..., description="User ID")
    resource_id: int = Field(..., description="Resource ID")
    start: str = Field(..., description="Start datetime ISO format")
    end: str = Field(..., description="End datetime ISO format")
    notes: Optional[str] = Field(None, description="Optional booking notes")


class ListUserBookingsInput(BaseModel):
    """Input schema for list_user_bookings tool"""
    user_id: int = Field(..., description="User ID")
    include_past: bool = Field(False, description="Include past bookings")


class CancelBookingInput(BaseModel):
    """Input schema for cancel_booking tool"""
    user_id: int = Field(..., description="User ID")
    booking_id: int = Field(..., description="Booking ID to cancel")


# Book Tools
class ListBooksTool(BaseTool):
    name: str = "list_books"
    description: str = (
        "List books in the library catalog with optional search and filtering. "
        "Use this when user wants to: search for books, browse catalog, find books by "
        "author or title, filter by category. "
        "Arguments: q (search query), category (filter), page, limit. "
        "Returns: JSON array of books with id, title, author, price, stock_count."
    )
    args_schema: Type[BaseModel] = ListBooksInput

    def _run(self, q: Optional[str] = None, category: Optional[str] = None,
             page: int = 1, limit: int = 20) -> str:
        if MOCK_MODE:
            results = mock_books
            if q:
                q_lower = q.lower()
                results = [b for b in results if q_lower in b['title'].lower() or q_lower in b['author'].lower()]
            if category:
                results = [b for b in results if b['category'].lower() == category.lower()]
            return json.dumps(results, indent=2)
        else:
            from app.crud import book as book_crud
            from app.database import engine
            from sqlmodel import Session
            with Session(engine) as db:
                books = book_crud.list_books(db, q=q, category=category, skip=(page-1)*limit, limit=limit)
                return json.dumps([b.dict() for b in books], default=str, indent=2)


class GetBookTool(BaseTool):
    name: str = "get_book"
    description: str = (
        "Get detailed information about a specific book by ID. "
        "Use this when: user asks about a specific book, wants to see details before "
        "purchase, or needs to verify availability. "
        "Arguments: book_id (required). "
        "Returns: JSON object with complete book details including stock and pricing."
    )
    args_schema: Type[BaseModel] = GetBookInput

    def _run(self, book_id: int) -> str:
        if MOCK_MODE:
            book = next((b for b in mock_books if b['id'] == book_id), None)
            if book:
                return json.dumps(book, indent=2)
            return json.dumps({"error": "Book not found"})
        else:
            from app.crud import book as book_crud
            from app.database import engine
            from sqlmodel import Session
            with Session(engine) as db:
                book = book_crud.get_book(db, book_id)
                if book:
                    return json.dumps(book.dict(), default=str, indent=2)
                return json.dumps({"error": "Book not found"})


class PurchaseBookTool(BaseTool):
    name: str = "purchase_book"
    description: str = (
        "Purchase one or more copies of a book. Deducts cost from user balance and decrements stock. "
        "Arguments: user_id, book_id, quantity (must be >= 1). "
        "Returns: JSON with transaction details: transaction_id, book_title, quantity, amount, status."
    )
    args_schema: Type[BaseModel] = PurchaseBookInput

    def _run(self, user_id: int, book_id: int, quantity: int) -> str:
        global mock_user_balance

        if MOCK_MODE:
            book = next((b for b in mock_books if b['id'] == book_id), None)
            if not book:
                return json.dumps({"error": "Book not found"})

            if book['stock_count'] < quantity:
                return json.dumps({"error": f"Insufficient stock. Only {book['stock_count']} available"})

            total_cost = book['price'] * quantity
            if mock_user_balance < total_cost:
                return json.dumps({"error": f"Insufficient balance. Need ${total_cost:.2f}, have ${mock_user_balance:.2f}"})

            book['stock_count'] -= quantity
            mock_user_balance -= total_cost

            result = {
                "transaction_id": 1001,
                "book_id": book_id,
                "book_title": book['title'],
                "quantity": quantity,
                "amount": total_cost,
                "currency": "USD",
                "status": "completed",
                "remaining_balance": mock_user_balance
            }
            return json.dumps(result, indent=2)
        else:
            from app.database import engine
            from sqlmodel import Session
            from app.crud.user import deduct_balance
            from app.models.book import Book
            from app.crud.transaction import create_transaction
            from app.models.transaction import TransactionStatus

            with Session(engine) as db:
                with db.begin_nested():
                    book = db.get(Book, book_id)
                    if not book:
                        return json.dumps({"error": "Book not found"})

                    if book.stock_count < quantity:
                        return json.dumps({"error": f"Insufficient stock. Only {book.stock_count} available"})

                    amount = book.price * quantity
                    deduct_balance(db, user_id, amount)
                    book.stock_count -= quantity
                    db.add(book)
                    db.flush()

                transaction = create_transaction(db, user_id, amount, book_id=book_id, status=TransactionStatus.completed)
                db.commit()

                result = {
                    "transaction_id": transaction.id,
                    "book_id": book.id,
                    "book_title": book.title,
                    "quantity": quantity,
                    "amount": amount,
                    "currency": transaction.currency,
                    "status": transaction.status.value
                }
                return json.dumps(result, indent=2)


# Resource Tools
class ListResourcesTool(BaseTool):
    name: str = "list_resources"
    description: str = (
        "List available library resources (rooms, seats, equipment). "
        "Arguments: min_capacity (optional filter), page, limit. "
        "Returns: JSON array with id, name, type, capacity, hourly_rate, open/close hours."
    )
    args_schema: Type[BaseModel] = ListResourcesInput

    def _run(self, min_capacity: Optional[int] = None, page: int = 1, limit: int = 20) -> str:
        if MOCK_MODE:
            results = mock_resources
            if min_capacity is not None:
                results = [r for r in results if r['capacity'] >= min_capacity]
            return json.dumps(results, indent=2)
        else:
            from app.crud import resource as resource_crud
            from app.database import engine
            from sqlmodel import Session
            with Session(engine) as db:
                resources = resource_crud.list_resources(db, min_capacity=min_capacity, skip=(page-1)*limit, limit=limit)
                return json.dumps([r.dict() for r in resources], default=str, indent=2)


class GetResourceTool(BaseTool):
    name: str = "get_resource"
    description: str = "Get detailed information about a specific resource. Arguments: resource_id."
    args_schema: Type[BaseModel] = GetResourceInput

    def _run(self, resource_id: int) -> str:
        if MOCK_MODE:
            resource = next((r for r in mock_resources if r['id'] == resource_id), None)
            if resource:
                return json.dumps(resource, indent=2)
            return json.dumps({"error": "Resource not found"})
        else:
            from app.crud import resource as resource_crud
            from app.database import engine
            from sqlmodel import Session
            with Session(engine) as db:
                resource = resource_crud.get_resource(db, resource_id)
                if resource:
                    return json.dumps(resource.dict(), default=str, indent=2)
                return json.dumps({"error": "Resource not found"})


class CheckAvailabilityTool(BaseTool):
    name: str = "check_resource_availability"
    description: str = (
        "Check if a resource is available for a specific time slot. "
        "Arguments: resource_id, start (ISO datetime), end (ISO datetime). "
        "Returns: JSON with 'available' boolean."
    )
    args_schema: Type[BaseModel] = CheckAvailabilityInput

    def _run(self, resource_id: int, start: str, end: str) -> str:
        if MOCK_MODE:
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))

            for booking in mock_bookings:
                if booking['resource_id'] == resource_id and booking['status'] == 'confirmed':
                    b_start = datetime.fromisoformat(booking['start_datetime'])
                    b_end = datetime.fromisoformat(booking['end_datetime'])
                    if start_dt < b_end and end_dt > b_start:
                        return json.dumps({"available": False, "start": start, "end": end,
                                         "message": "Time slot conflicts with existing booking"})

            return json.dumps({"available": True, "start": start, "end": end})
        else:
            from app.crud import booking as booking_crud
            from app.database import engine
            from sqlmodel import Session
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
            with Session(engine) as db:
                available = booking_crud.is_resource_available(db, resource_id, start_dt, end_dt)
                return json.dumps({"available": available, "start": start, "end": end})


class CreateBookingTool(BaseTool):
    name: str = "create_booking"
    description: str = (
        "Create a new resource booking. Deducts cost from user balance (hours × hourly_rate). "
        "IMPORTANT: Always check availability first and show cost calculation before creating. "
        "Arguments: user_id, resource_id, start (ISO), end (ISO), notes (optional)."
    )
    args_schema: Type[BaseModel] = CreateBookingInput

    def _run(self, user_id: int, resource_id: int, start: str, end: str, notes: Optional[str] = None) -> str:
        global mock_user_balance

        if MOCK_MODE:
            resource = next((r for r in mock_resources if r['id'] == resource_id), None)
            if not resource:
                return json.dumps({"error": "Resource not found"})

            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))

            # Check availability
            for booking in mock_bookings:
                if booking['resource_id'] == resource_id and booking['status'] == 'confirmed':
                    b_start = datetime.fromisoformat(booking['start_datetime'])
                    b_end = datetime.fromisoformat(booking['end_datetime'])
                    if start_dt < b_end and end_dt > b_start:
                        return json.dumps({"error": "Time slot not available", "conflict": True})

            hours = (end_dt - start_dt).total_seconds() / 3600
            total_cost = hours * resource['hourly_rate']

            if mock_user_balance < total_cost:
                return json.dumps({"error": f"Insufficient balance. Need ${total_cost:.2f}, have ${mock_user_balance:.2f}"})

            mock_user_balance -= total_cost
            booking = {
                "id": len(mock_bookings) + 1,
                "resource_id": resource_id,
                "user_id": user_id,
                "start_datetime": start,
                "end_datetime": end,
                "status": "confirmed",
                "notes": notes,
                "cost": total_cost,
                "remaining_balance": mock_user_balance
            }
            mock_bookings.append(booking)
            return json.dumps(booking, indent=2)
        else:
            from app.crud import booking as booking_crud
            from app.database import engine
            from sqlmodel import Session
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
            with Session(engine) as db:
                booking = booking_crud.create_booking_atomic(db, user_id, resource_id, start_dt, end_dt, notes)
                return json.dumps(booking.dict(), default=str, indent=2)


class ListUserBookingsTool(BaseTool):
    name: str = "list_user_bookings"
    description: str = "List a user's bookings. Arguments: user_id, include_past (bool)."
    args_schema: Type[BaseModel] = ListUserBookingsInput

    def _run(self, user_id: int, include_past: bool = False) -> str:
        if MOCK_MODE:
            user_bookings = [b for b in mock_bookings if b['user_id'] == user_id]
            if not include_past:
                now = datetime.now()
                user_bookings = [b for b in user_bookings
                               if datetime.fromisoformat(b['end_datetime'].replace('Z', '+00:00')) >= now]
            return json.dumps(user_bookings, indent=2)
        else:
            from app.crud import booking as booking_crud
            from app.database import engine
            from sqlmodel import Session
            with Session(engine) as db:
                bookings = booking_crud.get_user_bookings(db, user_id, include_past)
                return json.dumps([b.dict() for b in bookings], default=str, indent=2)


class CancelBookingTool(BaseTool):
    name: str = "cancel_booking"
    description: str = (
        "Cancel a booking. Subject to cancellation policy (1 hour before start for regular users). "
        "Arguments: user_id, booking_id."
    )
    args_schema: Type[BaseModel] = CancelBookingInput

    def _run(self, user_id: int, booking_id: int) -> str:
        if MOCK_MODE:
            booking = next((b for b in mock_bookings if b['id'] == booking_id), None)
            if not booking:
                return json.dumps({"error": "Booking not found"})
            if booking['user_id'] != user_id:
                return json.dumps({"error": "Not authorized to cancel this booking"})
            if booking['status'] == 'cancelled':
                return json.dumps({"error": "Booking already cancelled"})

            booking['status'] = 'cancelled'
            return json.dumps({"success": True, "booking": booking}, indent=2)
        else:
            from app.crud import booking as booking_crud
            from app.database import engine
            from sqlmodel import Session
            with Session(engine) as db:
                booking = booking_crud.cancel_booking(db, booking_id, user_id, is_admin=False)
                return json.dumps(booking.dict(), default=str, indent=2)


# Factory functions
def create_book_tools():
    """Create tools for Book Officer"""
    return [ListBooksTool(), GetBookTool(), PurchaseBookTool()]


def create_resource_tools():
    """Create tools for Resources Officer"""
    return [
        ListResourcesTool(),
        GetResourceTool(),
        CheckAvailabilityTool(),
        CreateBookingTool(),
        ListUserBookingsTool(),
        CancelBookingTool()
    ]
