# Library Booking System - Backend

FastAPI backend for the library booking system with SQLModel (SQLAlchemy) database models.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Edit `.env` with your actual configuration:
- `DATABASE_URL`: Database connection string (default: SQLite)
- `JWT_SECRET`: Secret key for JWT tokens (change in production!)
- `CREWAI_API_KEY`: Your CrewAI API key
- `OPENAI_API_KEY`: Your OpenAI API key
- Other settings as needed

### 3. Run the Application

Start the development server:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at:
- API Base: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/ping`

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # Database engine and session
│   ├── models/              # SQLModel database models
│   │   ├── user.py
│   │   ├── book.py
│   │   ├── resource.py
│   │   ├── booking.py
│   │   ├── transaction.py
│   │   └── ai_audit_log.py
│   ├── schemas/             # Pydantic schemas for validation
│   │   ├── user.py
│   │   ├── book.py
│   │   ├── resource.py
│   │   └── booking.py
│   └── api/                 # API routes
│       └── router.py
├── requirements.txt
├── .env.example
└── README.md
```

## Database Models

- **User**: User accounts with authentication
- **Book**: Library book catalog
- **Resource**: Bookable resources (rooms, seats, equipment)
- **Booking**: Resource bookings by users
- **Transaction**: Payment/transaction records
- **AI_Audit_Log**: AI agent activity logging

## Development

The database tables are automatically created on application startup. For SQLite, a `library.db` file will be created in the backend directory.

To run tests:

```bash
pytest
```
