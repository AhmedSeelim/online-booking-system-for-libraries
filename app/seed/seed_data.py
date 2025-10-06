# backend/app/seed/seed_full.py
from sqlmodel import Session, select
from app.database import engine, create_db_and_tables
from app.models.user import User
from app.models.book import Book
from app.models.resource import Resource, ResourceType
from app.models.booking import Booking, BookingStatus
from app.models.transaction import Transaction, TransactionStatus
from app.core.security import get_password_hash
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from app.models.ai_audit_log import AI_Audit_Log


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def now_utc():
    return datetime.now(timezone.utc)

def resource_is_available(session: Session, resource_id: int, start: datetime, end: datetime) -> bool:
    """Simple overlap check for confirmed bookings."""
    stmt = select(Booking).where(
        Booking.resource_id == resource_id,
        Booking.status == BookingStatus.confirmed,
        Booking.start_datetime < end,
        Booking.end_datetime > start
    )
    existing = session.exec(stmt).first()
    return existing is None

def create_user(session: Session, name: str, email: str, password: str, role: str = "user", balance: float = 100.0) -> User:
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        return existing
    user = User(
        name=name,
        email=email,
        password_hash=get_password_hash(password),
        role=role,
        balance=balance
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def create_book(session: Session, **kwargs) -> Book:
    existing = session.exec(select(Book).where(Book.isbn == kwargs.get("isbn"))).first()
    if existing:
        return existing
    book = Book(**kwargs)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

def create_resource(session: Session, **kwargs) -> Resource:
    existing = session.exec(select(Resource).where(Resource.name == kwargs.get("name"))).first()
    if existing:
        return existing
    resource = Resource(**kwargs)
    session.add(resource)
    session.commit()
    session.refresh(resource)
    return resource

def charge_user_and_create_transaction(session: Session, user: User, amount: float, book_id: Optional[int]=None, booking_id: Optional[int]=None) -> Transaction:
    """Deduct amount from user's balance, create a transaction record. Raises Exception if insufficient balance."""
    if user.balance < amount:
        raise Exception(f"User {user.email} has insufficient balance (${user.balance:.2f}) for amount ${amount:.2f}")
    user.balance -= amount
    session.add(user)
    session.flush()

    tx = Transaction(
        user_id=user.id,
        booking_id=booking_id,
        book_id=book_id,
        amount=amount,
        currency="USD",
        status=TransactionStatus.completed
    )
    session.add(tx)
    session.commit()
    session.refresh(tx)
    session.refresh(user)
    return tx

def create_booking_and_charge(session: Session, user: User, resource: Resource, start: datetime, end: datetime, notes: Optional[str] = None) -> Booking:
    """Check availability, charge user by hours * hourly_rate, create booking and transaction atomically."""
    if start >= end:
        raise ValueError("start must be before end")
    if not resource_is_available(session, resource.id, start, end):
        raise Exception("Resource not available for requested slot")

    duration_hours = (end - start).total_seconds() / 3600.0
    total_cost = round(duration_hours * float(resource.hourly_rate), 2)
    if user.balance < total_cost:
        raise Exception(f"Insufficient balance for user {user.email} to book resource '{resource.name}' (need ${total_cost}, have ${user.balance})")

    # create booking
    booking = Booking(
        resource_id=resource.id,
        user_id=user.id,
        start_datetime=start,
        end_datetime=end,
        status=BookingStatus.confirmed,
        notes=notes
    )
    session.add(booking)
    session.flush()  # get id

    # create transaction & deduct balance
    tx = Transaction(
        user_id=user.id,
        booking_id=booking.id,
        book_id=None,
        amount=total_cost,
        currency="USD",
        status=TransactionStatus.completed
    )
    # deduct balance and commit everything
    user.balance -= total_cost
    session.add(user)
    session.add(tx)
    session.commit()
    session.refresh(booking)
    session.refresh(tx)
    session.refresh(user)
    return booking

def purchase_book_and_create_transaction(session: Session, user: User, book: Book, quantity: int = 1) -> Transaction:
    """Purchase book(s): check stock, decrement, charge user, create transaction."""
    if book.stock_count < quantity:
        raise Exception(f"Book '{book.title}' out of stock (have {book.stock_count}, want {quantity})")
    total_price = round(float(book.price or 0.0) * quantity, 2)
    if user.balance < total_price:
        raise Exception(f"Insufficient balance for user {user.email} to buy book '{book.title}' (need ${total_price}, have ${user.balance})")

    book.stock_count -= quantity
    session.add(book)

    user.balance -= total_price
    session.add(user)

    tx = Transaction(
        user_id=user.id,
        booking_id=None,
        book_id=book.id,
        amount=total_price,
        currency="USD",
        status=TransactionStatus.completed
    )
    session.add(tx)
    session.commit()
    session.refresh(tx)
    session.refresh(book)
    session.refresh(user)
    return tx

import json
from datetime import datetime, timezone

# ---------------------------------------------------------------------
# AI Audit helpers
# ---------------------------------------------------------------------
def create_ai_audit_log(session: Session, agent_type: str, input_text: str,
                        detected_intent: str, actions_taken: dict, meta_data: Optional[dict] = None):
    """
    Create an AI_Audit_Log entry. actions_taken/meta_data should be dicts (will be JSON-dumped).
    """

    row = AI_Audit_Log(
        agent_type=agent_type,
        input_text=input_text,
        detected_intent=detected_intent,
        actions_taken=json.dumps(actions_taken, default=str),
        meta_data=json.dumps(meta_data, default=str) if meta_data is not None else None,
        timestamp=datetime.now(timezone.utc)
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


# ---------------------------------------------------------------------
# Main seeding routine
# ---------------------------------------------------------------------
def seed_database():
    print("Creating DB tables (if not exist)...")
    create_db_and_tables()

    with Session(engine) as session:
        # USERS
        print("Seeding users...")
        admin = create_user(session, "Admin User", "admin@example.com", "adminpass", role="admin", balance=1000.0)
        demo = create_user(session, "Demo User", "demo@example.com", "demopass", role="user", balance=100.0)
        alice = create_user(session, "Alice", "alice@example.com", "alicepass", role="user", balance=150.0)
        bob = create_user(session, "Bob", "bob@example.com", "bobpass", role="user", balance=60.0)
        carol = create_user(session, "Carol", "carol@example.com", "carolpass", role="user", balance=200.0)
        print("Users created:", [u.email for u in (admin, demo, alice, bob, carol)])

        # RESOURCES
        print("Seeding resources...")
        resources = []
        resources.append(create_resource(session,
            name="Conference Room A",
            type=ResourceType.room,
            capacity=12,
            features='{"projector": true, "whiteboard": true}',
            open_hour="08:00",
            close_hour="22:00",
            hourly_rate=15.0
        ))
        resources.append(create_resource(session,
            name="Study Room 101",
            type=ResourceType.room,
            capacity=4,
            features='{"whiteboard": true, "power_outlets": 4}',
            open_hour="09:00",
            close_hour="21:00",
            hourly_rate=8.0
        ))
        resources.append(create_resource(session,
            name="Reading Desk #5",
            type=ResourceType.seat,
            capacity=1,
            features='{"lamp": true, "power_outlet": true}',
            open_hour="07:00",
            close_hour="23:00",
            hourly_rate=2.0
        ))
        print(f"Created {len(resources)} resources")

        # BOOKS
        print("Seeding books...")
        books = []
        books.append(create_book(session,
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
            isbn="978-0743273565",
            category="Fiction",
            description="A classic American novel set in the Jazz Age",
            stock_count=5,
            price=12.99
        ))
        books.append(create_book(session,
            title="Clean Code",
            author="Robert C. Martin",
            isbn="978-0132350884",
            category="Technology",
            description="A handbook of agile software craftsmanship",
            stock_count=6,
            digital_url="https://example.com/clean-code",
            price=42.99
        ))
        books.append(create_book(session,
            title="Sapiens",
            author="Yuval Noah Harari",
            isbn="978-0062316097",
            category="History",
            description="A brief history of humankind",
            stock_count=7,
            price=18.99
        ))
        print(f"Created {len(books)} books")

        # BOOKINGS: create a few bookings in future that don't overlap
        print("Seeding bookings...")
        base = now_utc() + timedelta(days=1)  # start from tomorrow
        bookings_created = []
        try:
            b1 = create_booking_and_charge(session, alice, resources[0],
                start=base.replace(hour=9, minute=0, second=0, microsecond=0),
                end=base.replace(hour=11, minute=0, second=0, microsecond=0),
                notes="Team meeting"
            )
            bookings_created.append(b1)
            b2 = create_booking_and_charge(session, bob, resources[1],
                start=(base + timedelta(days=0)).replace(hour=14, minute=0, second=0, microsecond=0),
                end=(base + timedelta(days=0)).replace(hour=16, minute=0, second=0, microsecond=0),
                notes="Study session"
            )
            bookings_created.append(b2)
            b3 = create_booking_and_charge(session, carol, resources[2],
                start=(base + timedelta(days=0)).replace(hour=18, minute=0, second=0, microsecond=0),
                end=(base + timedelta(days=0)).replace(hour=19, minute=0, second=0, microsecond=0),
                notes="Evening reading"
            )
            bookings_created.append(b3)
        except Exception as e:
            print("Skipping some bookings due to:", e)

        # PURCHASES: create some book purchases
        print("Seeding purchases (transactions)...")
        transactions_created = []
        try:
            tx1 = purchase_book_and_create_transaction(session, demo, books[0], quantity=1)  # demo buys Gatsby
            transactions_created.append(tx1)
            tx2 = purchase_book_and_create_transaction(session, alice, books[1], quantity=1)  # alice buys Clean Code
            transactions_created.append(tx2)
            # Bob tries to buy an expensive book but might have insufficient funds; wrap in try
            try:
                tx3 = purchase_book_and_create_transaction(session, bob, books[1], quantity=1)
                transactions_created.append(tx3)
            except Exception as e:
                print("Could not complete Bob's purchase:", e)
        except Exception as e:
            print("Purchase seeding error:", e)

        # --- seed audit logs for created actions (place after bookings & transactions creation) ---
        print("Seeding a few AI audit logs for demo/debug...")

        try:
            # booking audit (if any booking created)
            if bookings_created:
                b = bookings_created[0]
                create_ai_audit_log(session,
                                    agent_type="booking_agent",
                                    input_text="Book Conference Room A tomorrow 9-11 for team meeting",
                                    detected_intent="booking",
                                    actions_taken={"resource_id": b.resource_id, "booking_id": b.id,
                                                   "status": b.status},
                                    meta_data={"user_id": b.user_id}
                                    )

            # purchase audit (if any tx created)
            if transactions_created:
                tx = transactions_created[0]
                create_ai_audit_log(session,
                                    agent_type="purchase_agent",
                                    input_text=f"Purchase book id={tx.book_id}",
                                    detected_intent="purchase",
                                    actions_taken={"book_id": tx.book_id, "transaction_id": tx.id, "amount": tx.amount},
                                    meta_data={"user_id": tx.user_id}
                                    )

            # sample query audit
            create_ai_audit_log(session,
                                agent_type="query_agent",
                                input_text="Show me latest books about programming",
                                detected_intent="query",
                                actions_taken={"retriever": "tfidf_fallback", "result_count": 2,
                                               "result_ids": [b.id for b in books[:2]]},
                                meta_data=None
                                )

            print("✓ seeded AI_Audit_Log entries")

        except Exception as e:
            print("Warning: could not seed some AI_Audit_Log entries:", e)

        # Final summary & commit ensured by helpers
        print("\nSUMMARY:")
        print(f"  Users: {session.exec(select(User)).count()}")
        print(f"  Resources: {session.exec(select(Resource)).count()}")
        print(f"  Books: {session.exec(select(Book)).count()}")
        print(f"  Bookings created: {len(bookings_created)}")
        print(f"  Transactions created: {len(transactions_created)}")

        # Print users balances
        print("\nUser balances:")
        for u in session.exec(select(User)).all():
            print(f"  {u.email}: ${u.balance:.2f}")

    print("\nDATABASE SEEDED SUCCESSFULLY!")

if __name__ == "__main__":
    seed_database()
