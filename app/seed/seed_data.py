"""
Seed script to populate database with demo data

Usage:
    python -m app.seed.seed_data
"""

from sqlmodel import Session
from ..database import engine, create_db_and_tables
from ..models.user import User
from ..models.book import Book
from ..models.resource import Resource, ResourceType
from ..core.security import get_password_hash


def seed_database():
    """Seed database with demo data"""

    # Create tables
    print("Creating database tables...")
    create_db_and_tables()

    with Session(engine) as session:
        # Create admin user
        admin = User(
            name="Admin User",
            email="admin@example.com",
            password_hash=get_password_hash("adminpass"),
            role="admin"
        )
        session.add(admin)

        # Create demo user
        demo = User(
            name="Demo User",
            email="demo@example.com",
            password_hash=get_password_hash("demopass"),
            role="user"
        )
        session.add(demo)

        print("✓ Created users")

        # Create resources
        resources = [
            Resource(
                name="Conference Room A",
                type=ResourceType.room,
                capacity=12,
                features='{"projector": true, "whiteboard": true, "video_conference": true}',
                open_hour="08:00",
                close_hour="22:00"
            ),
            Resource(
                name="Study Room 101",
                type=ResourceType.room,
                capacity=4,
                features='{"whiteboard": true, "power_outlets": 4}',
                open_hour="09:00",
                close_hour="21:00"
            ),
            Resource(
                name="Reading Desk #5",
                type=ResourceType.seat,
                capacity=1,
                features='{"lamp": true, "power_outlet": true}',
                open_hour="07:00",
                close_hour="23:00"
            ),
            Resource(
                name="Laptop Station #3",
                type=ResourceType.seat,
                capacity=1,
                features='{"monitor": true, "keyboard": true, "mouse": true}',
                open_hour="09:00",
                close_hour="21:00"
            ),
            Resource(
                name="3D Printer",
                type=ResourceType.equipment,
                capacity=1,
                features='{"max_print_size": "30x30x40cm", "materials": ["PLA", "ABS"]}',
                open_hour="10:00",
                close_hour="18:00"
            ),
        ]

        for resource in resources:
            session.add(resource)

        print(f"✓ Created {len(resources)} resources")

        # Create books
        books = [
            Book(
                title="The Great Gatsby",
                author="F. Scott Fitzgerald",
                isbn="978-0743273565",
                category="Fiction",
                description="A classic American novel set in the Jazz Age",
                stock_count=5
            ),
            Book(
                title="To Kill a Mockingbird",
                author="Harper Lee",
                isbn="978-0061120084",
                category="Fiction",
                description="A gripping tale of racial injustice and childhood innocence",
                stock_count=3
            ),
            Book(
                title="1984",
                author="George Orwell",
                isbn="978-0451524935",
                category="Science Fiction",
                description="A dystopian social science fiction novel",
                stock_count=4
            ),
            Book(
                title="Clean Code",
                author="Robert C. Martin",
                isbn="978-0132350884",
                category="Technology",
                description="A handbook of agile software craftsmanship",
                stock_count=6,
                digital_url="https://example.com/clean-code"
            ),
            Book(
                title="The Pragmatic Programmer",
                author="Andrew Hunt and David Thomas",
                isbn="978-0135957059",
                category="Technology",
                description="Your journey to mastery",
                stock_count=4
            ),
            Book(
                title="Sapiens",
                author="Yuval Noah Harari",
                isbn="978-0062316097",
                category="History",
                description="A brief history of humankind",
                stock_count=7
            ),
            Book(
                title="Educated",
                author="Tara Westover",
                isbn="978-0399590504",
                category="Biography",
                description="A memoir about a woman who grows up in a survivalist family",
                stock_count=5
            ),
            Book(
                title="The Design of Everyday Things",
                author="Don Norman",
                isbn="978-0465050659",
                category="Design",
                description="Revised and expanded edition",
                stock_count=3,
                digital_url="https://example.com/design-everyday"
            ),
        ]

        for book in books:
            session.add(book)

        print(f"✓ Created {len(books)} books")

        # Commit all changes
        session.commit()

        print("\n" + "=" * 60)
        print("DATABASE SEEDED SUCCESSFULLY!")
        print("=" * 60)
        print("\nLogin Credentials:")
        print("-" * 60)
        print("Admin Account:")
        print("  Email:    admin@example.com")
        print("  Password: adminpass")
        print("\nDemo User Account:")
        print("  Email:    demo@example.com")
        print("  Password: demopass")
        print("-" * 60)
        print("\nTo start the server:")
        print("  uvicorn app.main:app --reload --port 8000")
        print("\nAPI Documentation:")
        print("  http://localhost:8000/docs")
        print("=" * 60)


if __name__ == "__main__":
    seed_database()