# Library Booking System
## Complete System Documentation

---

# Table of Contents

1. [Problem, Overview and Requirements (SRS)](#1-problem-overview-and-requirements-srs)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Database Schema](#4-database-schema)
5. [Backend Implementation](#5-backend-implementation)
6. [Frontend Implementation](#6-frontend-implementation)
7. [AI Agent System](#7-ai-agent-system)
8. [API Reference](#8-api-reference)
9. [Setup and Configuration](#9-setup-and-configuration)
10. [Testing](#10-testing)
11. [Deployment](#11-deployment)

---

# 1. Problem, Overview and Requirements (SRS)

## 1.1 Problem Statement

Many libraries—physical and hybrid—still rely on fragmented, manual, or semi-digital processes for managing book catalogs, handling purchases for paid copies or digital assets, and coordinating the booking of shared facilities (study rooms, conference rooms, equipment). This creates friction for patrons and staff:

- **Patrons struggle** to search catalogs, buy copies, or reserve study spaces in one unified place
- **Staff must manually** check availability, reconcile payments, and handle repeated clarifying questions
- **Decision-making and user experience degrade** when information (availability, stock, pricing, past interactions) is scattered
- **No convenient, auditable way** for an intelligent assistant to help users using natural language while preserving safety and traceability

**Problem Statement:** Build a single, auditable, user-friendly system that unifies catalog management, facility/resource booking, transactions, and an AI assistant that can (safely) assist and automate user requests while preserving clear audit trails and business rules.

## 1.2 System Overview (Purpose & Scope)

### Purpose

The Library Booking System is a web-based application that lets users search and purchase books, reserve library resources (rooms, seats, equipment), manage a virtual balance, view transaction history, and interact with an AI assistant that can understand natural-language requests and either answer or orchestrate actions (search, purchase, book) on the user's behalf. The system serves library patrons, library staff/admins, and auditors.

### Primary Goals

1. Provide fast, consistent REST APIs and a minimal, accessible frontend for patrons and admins
2. Ensure financial and booking operations are atomic and auditable
3. Offer an AI-powered conversational interface (receptionist + specialist agents) to simplify user workflows and automate repetitive tasks
4. Log AI decisions and actions for compliance and review

### Scope

**In-Scope:**
- User sign-up, login, role-based access (user/admin)
- Book catalog: list, search, detail, purchase, inventory management
- Resource catalog: list resources, check availability, create/cancel bookings, capacity & features
- Virtual balance management and transaction records
- AI agent system (receptionist + book/resource officers) that can classify intent, call backend tools, and produce audit logs
- Frontend SPA (Vite + React TypeScript) implementing core flows: auth, book and resource browsing, booking/purchase flows, my bookings, and an AI chat panel
- Seed data for demo/testing and a mock mode for offline agent testing

**Out of Scope:**
- External payment gateway integration (system uses virtual balance)
- Multi-tenant library installations (single installation per deployment)
- Advanced analytics dashboards (future enhancement)
- Production-ready CI/CD and container orchestration (deployment docs optional)

### Primary Stakeholders

- **Library patrons / students** - End users
- **Library administrators** - Manage books/resources, view logs
- **Developers & DevOps** - Deploy & maintain system
- **Auditors / compliance officers** - Review AI and financial logs

## 1.3 System Features Overview

### Core Functionality

**User Authentication**
- JWT-based authentication with role-based access control
- Secure password hashing using bcrypt
- Token expiration and refresh mechanisms

**Book Management**
- Search and browse books from the catalog
- Purchase books with stock and balance validation
- Admin capabilities for CRUD operations on books

**Resource Booking**
- Reserve conference rooms, study spaces, and equipment
- Real-time availability checking
- Automatic cost calculation based on duration and hourly rates

**Balance System**
- Virtual wallet for purchases and bookings
- Transaction history with full audit trail
- Add balance functionality (demo mode)

**AI-Powered Assistant**
- Natural language interface for user interactions
- Intent classification and smart routing
- Specialized agents for books and resources
- Complete audit logging of all AI interactions

## 1.4 Functional Requirements

### Authentication & User Management

**FR-001 — Sign Up**
Users can register with name, email, password. New user default balance = $100 (configurable).

**FR-002 — Login**
Users obtain a JWT on successful login.

**FR-003 — Profile**
Users can view their profile and balance (GET /api/auth/me).

**FR-004 — Role-based Access**
Admin-only endpoints protected (create/update/delete books/resources).

### Book Catalog & Purchases

**FR-010 — List/Search Books**
Users can list books and search by title, author, ISBN, and category (GET /api/books with query params).

**FR-011 — Book Details**
Users can fetch full book details (GET /api/books/{id}).

**FR-012 — Purchase Book**
Authenticated users can purchase a book (POST /api/books/{id}/purchase) with quantity. System:
- Validates stock and user balance
- Atomically decrements stock and deducts balance
- Creates a transaction record (status, amount, currency)
- Returns transaction ID and updated balance

**FR-013 — Admin Book Management**
Admins can create, update, delete books.

### Resource Catalog & Bookings

**FR-020 — List Resources**
Users can list resources (rooms, seats, equipment) with optional filters e.g., min_capacity.

**FR-021 — Resource Details**
Get resource metadata (features, open/close hours, hourly_rate).

**FR-022 — Check Availability**
Query availability for a specific time range OR get available slots for a specific date (GET /api/resources/{id}/availability).

**FR-023 — Create Booking**
Authenticated users can create bookings (POST /api/bookings) with:
- Validation: start < end, duration <= 8 hours, lead time >= 15 minutes
- Availability check: no overlapping confirmed bookings
- Cost calc: hours × hourly_rate
- Atomic deduction of user balance and creation of booking + transaction
- Return booking ID and details

**FR-024 — List & Cancel Bookings**
Users can list their bookings and cancel if within policy (cancel ≥1 hour before start); admins can cancel any booking.

**FR-025 — Admin Resource Management**
Admins can create/update/delete resources.

### Transactions & Balance

**FR-030 — Transaction Records**
All purchases/bookings create a transactions record storing user, amount, related book_id or booking_id, currency, status, and timestamp.

**FR-031 — Add Balance**
Endpoint to add funds to user balance (in demo mode; payment gateway out of scope).

### AI Agent System

**FR-040 — Agent Chat Endpoint**
Single endpoint for AI: POST /api/agent/chat that accepts a message and returns structured output: intent, parsed_details, human-readable response, and audit_id.

**FR-041 — Receptionist Classification**
The receptionist classifies into book, resources, or normal_question and extracts parsed_details.

**FR-042 — Specialist Agents**
Book Officer and Resources Officer run workflows using available tools (list_books, get_book, purchase_book, get_resource, check_resource_availability, create_booking, etc.). Agents must request confirmation before performing state-changing actions (purchase, booking).

**FR-043 — Audit Logging**
Every agent decision and action must be logged to ai_audit_logs with agent type, input_text, detected intent, actions_taken (JSON), meta, and timestamp.

### API & Frontend

**FR-050 — REST API**
Backend exposes documented endpoints (Swagger/OpenAPI).

**FR-051 — Frontend Flows**
Frontend SPA implements: auth, books list/detail/purchase, resources list/detail/booking, my-bookings, AI chat side panel.

**FR-052 — Error Reporting**
API returns structured errors; frontend displays 400 validation messages and 409 conflicts clearly.

## 1.5 Non-Functional Requirements

**NFR-001 — Security**
JWT tokens for authentication; hashed passwords (bcrypt). Protect admin endpoints. Sanitize inputs.

**NFR-002 — Auditability**
All financial and AI agent actions logged in transactions and ai_audit_logs.

**NFR-003 — Atomicity & Consistency**
Use DB transactions for balance deduction + booking/purchase creation to prevent race conditions and ensure data integrity.

**NFR-004 — Timezones**
Store all timestamps in UTC. Frontend converts and displays local time for users.

**NFR-005 — Performance**
API should handle typical library traffic; endpoints should respond < 300ms for simple GETs under normal load (hardware dependent).

**NFR-006 — Availability**
System should be designed for high availability in production (recommendations: run behind load balancer, use stable DB).

**NFR-007 — Maintainability**
Clear modular structure: models, schemas, crud, api, agents. Provide seed and test scripts.

**NFR-008 — Usability & Accessibility**
Frontend should be keyboard-accessible, responsive, with clear error messages and minimal UI.

**NFR-009 — Privacy**
Do not expose user-sensitive info; store minimal PII and secure tokens.

## 1.6 System Constraints & Assumptions

**Constraints:**
- Payment integration with external processors is out of scope; system uses an internal balance system for demo purposes
- Local dev uses SQLite by default; production should use PostgreSQL for concurrency/scale

**Assumptions:**
- Users provide datetimes in ISO 8601 (with timezone or Z) from frontend; backend will normalize to UTC
- Agents may use external LLMs (Gemini / CrewAI) — API keys and quotas must be configured in environment variables
- Admins will seed initial catalog or use the provided seed script

---

# 2. System Architecture

## 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     FastAPI Backend                      │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │   Auth   │  │  Books   │  │Resources│  │ AI Agent│ │
│  │  Routes  │  │  Routes  │  │ Routes  │  │ Routes  │ │
│  └─────┬────┘  └─────┬────┘  └─────┬───┘  └────┬────┘ │
│        │             │              │            │      │
│  ┌─────┴─────────────┴──────────────┴────────────┴───┐ │
│  │              Business Logic Layer                  │ │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────────┐ │ │
│  │  │   CRUD   │  │  Booking │  │   CrewAI Agents │ │ │
│  │  │Operations│  │  Logic   │  │   ┌───────────┐ │ │ │
│  │  └──────────┘  └──────────┘  │   │Receptionist│ │ │ │
│  │                               │   ├───────────┤ │ │ │
│  │                               │   │  Books    │ │ │ │
│  │                               │   ├───────────┤ │ │ │
│  │                               │   │ Resources │ │ │ │
│  │                               │   └───────────┘ │ │ │
│  │                               └─────────────────┘ │ │
│  └────────────────┬───────────────────────────────────┘ │
│                   │                                      │
│  ┌────────────────┴───────────────────────────────────┐ │
│  │         SQLModel / SQLAlchemy ORM                   │ │
│  └────────────────┬───────────────────────────────────┘ │
└───────────────────┼─────────────────────────────────────┘
                    │
          ┌─────────┴─────────┐
          │ PostgreSQL/SQLite │
          └───────────────────┘
```

## 2.2 Component Interactions

### User Request Flow

```
User → Frontend → API Gateway → Auth Middleware → Route Handler
                                      ↓
                                Business Logic
                                      ↓
                                 CRUD Layer
                                      ↓
                                  Database
```

### AI Agent Flow

```
User Message → Agent Endpoint → Receptionist Agent
                                      ↓
                            Intent Classification
                                      ↓
                    ┌─────────────────┼─────────────────┐
                    ↓                 ↓                 ↓
            Normal Question    Books Officer    Resources Officer
                    ↓                 ↓                 ↓
            Direct Response      Tool Calls        Tool Calls
                    ↓                 ↓                 ↓
                    └─────────────────┴─────────────────┘
                                      ↓
                              Response + Audit Log
```

---

# 3. Technology Stack

## 3.1 Backend Technologies

### Core Framework
- **FastAPI 0.109+** - Modern, fast web framework with automatic API documentation
- **Python 3.10+** - Primary programming language
- **Uvicorn** - ASGI server for running FastAPI applications

### Database & ORM
- **SQLModel 0.0.14** - SQL databases in Python with type checking
- **SQLAlchemy** - Database toolkit and ORM (underlying SQLModel)
- **PostgreSQL** - Production database (recommended)
- **SQLite** - Development database (default)

### AI & Agents
- **CrewAI 0.11+** - Framework for orchestrating autonomous AI agents
- **Google Gemini API** - Large Language Model for agent intelligence
- **LangChain Tools** - Tool framework for agent capabilities

### Security
- **python-jose** - JWT token generation and validation
- **passlib[bcrypt]** - Password hashing and verification
- **python-multipart** - Form data parsing

### Utilities
- **Pydantic 2.5+** - Data validation and settings management
- **python-dotenv** - Environment variable management

## 3.2 Frontend Technologies

### Core Framework
- **React 18.2** - UI library for building interactive interfaces
- **TypeScript 5.2** - Static typing for JavaScript
- **Vite** - Fast build tool and development server

### Routing & HTTP
- **React Router DOM 6.23** - Client-side routing
- **Axios 1.7** - HTTP client for API communication

### Styling
- **Tailwind CSS 3.4** - Utility-first CSS framework
- **PostCSS** - CSS transformations
- **Autoprefixer** - Automatic vendor prefixes

### Content Rendering
- **ReactMarkdown** - Markdown rendering in React
- **Remark-Gfm** - GitHub Flavored Markdown support

### State Management
- **React Context API** - Global state management
  - AuthContext for authentication
  - AIActionContext for agent interactions

---

# 4. Database Schema

## 4.1 Entity Relationship Diagram

```
┌─────────────┐
│    users    │
│─────────────│
│ id (PK)     │
│ name        │
│ email       │◄─────────┐
│ password_hash│          │
│ role        │          │
│ balance     │          │
│ created_at  │          │
└──────┬──────┘          │
       │                 │
       │ 1:N             │ 1:N
       │                 │
       ├─────────────────┼────────────┐
       │                 │            │
       ▼                 ▼            ▼
┌─────────────┐   ┌─────────────┐   ┌──────────────┐
│  bookings   │   │transactions │   │ai_audit_logs │
│─────────────│   │─────────────│   │──────────────│
│ id (PK)     │   │ id (PK)     │   │ id (PK)      │
│ resource_id │◄──│ booking_id  │   │ agent_type   │
│ user_id (FK)│   │ book_id     │   │ input_text   │
│ start_datetime  │ user_id (FK)│   │ detected_intent│
│ end_datetime│   │ amount      │   │ actions_taken│
│ status      │   │ currency    │   │ metadata     │
│ notes       │   │ status      │   │ timestamp    │
│ created_at  │   │ created_at  │   └──────────────┘
└──────┬──────┘   └──────┬──────┘
       │                 │
       │ N:1             │ N:1
       │                 │
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│  resources  │   │    books    │
│─────────────│   │─────────────│
│ id (PK)     │   │ id (PK)     │
│ name        │   │ title       │
│ type        │   │ author      │
│ capacity    │   │ isbn        │
│ hourly_rate │   │ category    │
│ open_hour   │   │ description │
│ close_hour  │   │ price       │
│ features    │   │ stock_count │
│ created_at  │   │ digital_url │
└─────────────┘   │ created_at  │
                  └─────────────┘
```

## 4.2 Table Definitions

### users

Stores user accounts with authentication credentials and balance.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing user ID |
| name | VARCHAR | NOT NULL | User's full name |
| email | VARCHAR | UNIQUE, NOT NULL, INDEX | Email address (used for login) |
| password_hash | VARCHAR | NOT NULL | Bcrypt-hashed password |
| role | VARCHAR | DEFAULT 'user' | User role: 'user' or 'admin' |
| balance | FLOAT | DEFAULT 100.0 | Virtual wallet balance (USD) |
| created_at | TIMESTAMP | DEFAULT NOW | Account creation timestamp (UTC) |

**Indexes:**
- `ix_users_email` on `email`

### books

Catalog of available books with pricing and inventory.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing book ID |
| title | VARCHAR | NOT NULL, INDEX | Book title |
| author | VARCHAR | NOT NULL, INDEX | Book author(s) |
| isbn | VARCHAR | UNIQUE, NOT NULL, INDEX | ISBN number |
| category | VARCHAR | NOT NULL, INDEX | Book category/genre |
| description | TEXT | NULLABLE | Book description |
| price | FLOAT | DEFAULT 25.0 | Price in USD |
| stock_count | INTEGER | DEFAULT 0 | Available copies |
| digital_url | VARCHAR | NULLABLE | URL to digital version |
| created_at | TIMESTAMP | DEFAULT NOW | Record creation timestamp (UTC) |

**Indexes:**
- `ix_books_title` on `title`
- `ix_books_author` on `author`
- `ix_books_isbn` on `isbn`
- `ix_books_category` on `category`

### resources

Bookable library facilities and equipment.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing resource ID |
| name | VARCHAR | NOT NULL, INDEX | Resource name |
| type | ENUM | NOT NULL | Type: 'room', 'seat', 'equipment' |
| capacity | INTEGER | NOT NULL | Maximum capacity/occupancy |
| hourly_rate | FLOAT | DEFAULT 10.0 | Rental price per hour (USD) |
| open_hour | VARCHAR | DEFAULT '09:00' | Opening time (HH:MM format) |
| close_hour | VARCHAR | DEFAULT '21:00' | Closing time (HH:MM format) |
| features | TEXT | NULLABLE | JSON string of features |
| created_at | TIMESTAMP | DEFAULT NOW | Record creation timestamp (UTC) |

**Resource Types:**
- `room` - Conference rooms, study rooms
- `seat` - Individual reading desks, laptop stations
- `equipment` - 3D printers, projectors, etc.

### bookings

Resource reservations made by users.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing booking ID |
| resource_id | INTEGER | FOREIGN KEY, NOT NULL, INDEX | Reference to resources.id |
| user_id | INTEGER | FOREIGN KEY, NOT NULL, INDEX | Reference to users.id |
| start_datetime | TIMESTAMP | NOT NULL, INDEX | Booking start time (UTC) |
| end_datetime | TIMESTAMP | NOT NULL, INDEX | Booking end time (UTC) |
| status | ENUM | DEFAULT 'confirmed' | Status: 'confirmed', 'cancelled' |
| notes | TEXT | NULLABLE | Optional booking notes |
| created_at | TIMESTAMP | DEFAULT NOW | Booking creation timestamp (UTC) |

**Business Rules:**
- No overlapping bookings for same resource
- Maximum duration: 8 hours
- Minimum lead time: 15 minutes
- Cost = (hours) × (resource.hourly_rate)
- Deducted from user balance on creation

### transactions

Financial transaction records for purchases and payments.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing transaction ID |
| user_id | INTEGER | FOREIGN KEY, NOT NULL, INDEX | Reference to users.id |
| booking_id | INTEGER | FOREIGN KEY, NULLABLE | Reference to bookings.id (if booking payment) |
| book_id | INTEGER | FOREIGN KEY, NULLABLE | Reference to books.id (if book purchase) |
| amount | FLOAT | NOT NULL | Transaction amount (USD) |
| currency | VARCHAR | DEFAULT 'USD' | Currency code |
| status | ENUM | NOT NULL | Status: 'completed', 'failed', 'refunded' |
| created_at | TIMESTAMP | DEFAULT NOW | Transaction timestamp (UTC) |

**Transaction Types:**
- Book purchase: `book_id` is set, `booking_id` is NULL
- Booking payment: `booking_id` is set, `book_id` is NULL

### ai_audit_logs

Audit trail of AI agent interactions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-incrementing log ID |
| agent_type | VARCHAR | NOT NULL, INDEX | Agent: 'receptionist', 'book_officer', 'resources_officer' |
| input_text | TEXT | NOT NULL | User's input message |
| detected_intent | VARCHAR | NOT NULL | Classified intent |
| actions_taken | TEXT | NOT NULL | JSON string of actions performed |
| metadata | TEXT | NULLABLE | Additional JSON metadata |
| timestamp | TIMESTAMP | DEFAULT NOW, INDEX | Log timestamp (UTC) |

---

# 5. Backend Implementation

## 5.1 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Configuration management
│   ├── database.py             # Database setup
│   ├── deps.py                 # Dependency injection
│   │
│   ├── models/                 # SQLModel database models
│   │   ├── user.py
│   │   ├── book.py
│   │   ├── resource.py
│   │   ├── booking.py
│   │   ├── transaction.py
│   │   └── ai_audit_log.py
│   │
│   ├── schemas/                # Pydantic validation schemas
│   │   ├── user.py
│   │   ├── book.py
│   │   ├── resource.py
│   │   └── booking.py
│   │
│   ├── crud/                   # Database operations
│   │   ├── user.py
│   │   ├── book.py
│   │   ├── resource.py
│   │   ├── booking.py
│   │   ├── transaction.py
│   │   └── ai_audit_log.py
│   │
│   ├── core/                   # Core utilities
│   │   └── security.py
│   │
│   ├── api/                    # API routes
│   │   ├── router.py
│   │   ├── auth.py
│   │   ├── books.py
│   │   ├── resources.py
│   │   ├── bookings.py
│   │   └── agent.py
│   │
│   ├── agents/                 # CrewAI agent system
│   │   ├── models.py
│   │   ├── tools.py
│   │   ├── crews.py
│   │   └── config/
│   │       ├── agents.yaml
│   │       └── tasks.yaml
│   │
│   ├── seed/
│   │   └── seed_data.py
│   │
│   └── tests/
│       ├── test_auth.py
│       ├── test_booking.py
│       ├── test_purchase.py
│       └── test_books_resources.py
│
├── requirements.txt
├── .env.example
└── README.md
```

## 5.2 Core Components

### Configuration (config.py)

Manages all application settings using Pydantic BaseSettings:

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    GOOGLE_API_KEY: str
    VECTORSTORE_DIR: str = "./app/vectorstore/db"
```

### Database (database.py)

Sets up SQLModel engine and session management:

```python
engine = create_engine(settings.DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session
```

### Security (core/security.py)

Handles password hashing and JWT token operations:

```python
def hash_password(password: str) -> str
def verify_password(plain: str, hashed: str) -> bool
def create_access_token(data: dict) -> str
def decode_access_token(token: str) -> dict
```

## 5.3 API Endpoints Summary

### Authentication (`/api/auth`)
- `POST /signup` - Register new user
- `POST /login` - Get JWT token
- `GET /me` - Get current user
- `POST /add-balance` - Add funds

### Books (`/api/books`)
- `GET /` - List/search books
- `GET /{id}` - Get book details
- `POST /{id}/purchase` - Buy books
- `POST /` - Create book (admin)
- `PUT /{id}` - Update book (admin)
- `DELETE /{id}` - Delete book (admin)

### Resources (`/api/resources`)
- `GET /` - List resources
- `GET /{id}` - Get resource details
- `GET /{id}/availability` - Check availability
- `POST /` - Create resource (admin)
- `PUT /{id}` - Update resource (admin)
- `DELETE /{id}` - Delete resource (admin)

### Bookings (`/api/bookings`)
- `POST /` - Create booking
- `GET /` - List user's bookings
- `DELETE /{id}` - Cancel booking

### AI Agent (`/api/agent`)
- `POST /chat` - Chat with AI assistant

---

# 6. Frontend Implementation

## 6.1 Project Structure

```
frontend/src/
├── api/                # API communication layer
│   ├── ai.ts
│   ├── auth.ts
│   ├── axiosInstance.ts
│   ├── bookings.ts
│   ├── books.ts
│   └── resources.ts
├── components/         # Reusable React components
│   ├── AgentChat.tsx
│   ├── Layout.tsx
│   └── Modal.tsx
├── context/            # Global state management
│   ├── AIActionContext.tsx
│   └── AuthContext.tsx
├── pages/              # Top-level route components
│   ├── Books.tsx
│   ├── Home.tsx
│   ├── Login.tsx
│   ├── MyBookings.tsx
│   └── ResourceDetail.tsx
├── styles/
│   └── index.css
├── types.ts            # TypeScript type definitions
├── utils/
│   └── dateUtils.ts
└── main.tsx            # Application entry point
```

## 6.2 Core Features

### Authentication Flow

1. **Registration & Login**: Users register or login through dedicated pages
2. **JWT Token Management**: Tokens stored in localStorage
3. **Authenticated Requests**: Axios interceptor auto-attaches Bearer token
4. **Global Error Handling**: 401 responses trigger automatic logout and redirect
5. **Protected Routes**: AuthContext checks authentication before rendering protected pages

### State Management

**AuthContext**: Manages user authentication state globally
- Checks for token on app load
- Fetches current user data from `/api/auth/me`
- Provides login/logout functions

**AIActionContext**: Bridges AI chat and application UI
- Captures parsed_details from AI responses
- Provides "suggestions" to pre-fill forms
- Creates seamless AI-driven workflows

### AI Assistant (AgentChat.tsx)

Core features:
- Natural language query input
- Structured JSON response rendering
- Markdown support for conversational text
- Formatted data displays (books, resources)
- Actionable suggestions with "Apply" buttons
- Automatic balance updates on transactions

### Date & Time Handling

All datetime operations follow strict UTC policies:

```typescript
// Parse UTC strings from backend
parseUTCDate(utcString: string): Date

// Format for display in user's local timezone
formatToLocalDateTime(date: Date): string
formatToLocalTime(date: Date): string
```

### Admin Functionality

- Role-based UI rendering (`currentUser.role === 'admin'`)
- CRUD operations via modal interfaces
- Separate admin controls for books and resources

---

# 7. AI Agent System

## 7.1 Architecture Overview

Three-crew agentic system using CrewAI:

```
User Message
    ↓
Receptionist Agent (Intent Classifier)
    ↓
├─→ Normal Question → Direct Response
├─→ Book Intent → Books Officer Crew
└─→ Resource Intent → Resources Officer Crew
    ↓
Response + Audit Log
```

## 7.2 Receptionist Crew

**Purpose:** Classify user intent and extract relevant parameters

**Output Model:**
```python
class ReceptionistOutput(BaseModel):
    intent: Literal["normal_question", "book", "resources"]
    confidence: float
    parsed_details: Optional[Dict[str, Any]]
    clarify: Optional[str]
```

**Intent Classification Rules:**

**"book"** - Route to Books Officer for:
- Searching, browsing catalog, finding titles/authors
- Book information (price, description, availability, stock)
- Purchasing books
- Book categories, genres, recommendations
- Digital book access

**"resources"** - Route to Resources Officer for:
- Booking/reserving facilities (conference rooms, study rooms, desks)
- Equipment rental (3D printers, laptops, projectors)
- Checking availability of spaces or time slots
- Viewing existing bookings or reservations
- Canceling or modifying bookings
- Information about room capacity, features, or pricing

**"normal_question"** - Handle directly for:
- Library hours, opening times, closing times
- General policies, membership rules, library cards
- Directions, location information
- Contact information, how to reach staff

## 7.3 Books Officer Crew

**Tools Available:**

| Tool | Purpose | Arguments | Returns |
|------|---------|-----------|---------|
| `list_books` | Search and list books | q, category, page, limit | JSON array of books |
| `get_book` | Get detailed book info | book_id | JSON book object |
| `purchase_book` | Purchase books | user_id, book_id, quantity | Transaction result |

**Workflow:**
1. Parse user request and extracted details from receptionist
2. Search/retrieve book information using list_books or get_book
3. For purchases:
   - Verify book exists and has sufficient stock
   - Check user's balance is adequate
   - Show price and get explicit confirmation
   - Execute purchase_book
4. Log all actions to AI_Audit_Log
5. Return friendly, detailed response

**Example Conversation:**
```
User: "I want to buy Clean Code"

Books Officer:
1. Calls list_books(q="Clean Code")
2. Finds book: Clean Code by Robert C. Martin - $42.99, 6 in stock
3. Responds: "I found Clean Code by Robert C. Martin for $42.99. 
   We have 6 copies in stock. Would you like to purchase it?"
4. User confirms
5. Calls purchase_book(user_id=1, book_id=1, quantity=1)
6. Responds: "Purchase successful! Clean Code ($42.99) has been 
   charged to your account. Remaining balance: $57.01. 
   Transaction ID: #1001"
```

## 7.4 Resources Officer Crew

**Tools Available:**

| Tool | Purpose | Arguments | Returns |
|------|---------|-----------|---------|
| `list_resources` | List available resources | min_capacity, page, limit | JSON array of resources |
| `get_resource` | Get resource details | resource_id | JSON resource object |
| `check_resource_availability` | Check time slot | resource_id, start, end | Availability result |
| `create_booking` | Make a reservation | user_id, resource_id, start, end, notes | Booking object |
| `list_user_bookings` | View user bookings | user_id, include_past | JSON array of bookings |
| `cancel_booking` | Cancel a booking | user_id, booking_id | Cancellation result |

**Booking Workflow:**
1. Get resource details using get_resource (for hourly_rate)
2. Check availability using check_resource_availability
3. Calculate cost: `hours × hourly_rate`
4. Show calculation to user and get confirmation
5. Create booking using create_booking
6. Return confirmation with booking ID and cost breakdown

**Example Conversation:**
```
User: "Book Conference Room A tomorrow 2pm to 4pm"

Resources Officer:
1. Calls get_resource(1) - Conference Room A ($15/hour)
2. Calls check_resource_availability(1, "2025-10-07T14:00:00Z", 
                                        "2025-10-07T16:00:00Z")
3. Available! Calculates: 2 hours × $15/hour = $30
4. Responds: "Conference Room A is available tomorrow 2:00-4:00 PM. 
   Cost: 2 hours × $15/hour = $30. Confirm booking?"
5. User confirms
6. Calls create_booking(user_id=1, resource_id=1, ...)
7. Responds: "✓ Booking confirmed! Conference Room A reserved for 
   Oct 7, 2:00-4:00 PM. Cost: $30 deducted. Remaining balance: $70. 
   Booking ID: #12"
```

## 7.5 Configuration Files

### agents.yaml

Defines each agent with role, goal, and backstory:

**Receptionist Agent:**
- **Role**: Intent classifier and router
- **Goal**: Accurately classify user intent
- **Backstory**: Includes categorization rules and examples

**Books Officer Agent:**
- **Role**: Book search and purchase specialist
- **Goal**: Help users find and purchase books
- **Backstory**: Lists all book-related tools and workflows

**Resources Officer Agent:**
- **Role**: Facility booking specialist
- **Goal**: Manage resource reservations
- **Backstory**: Lists all resource/booking tools and procedures

### tasks.yaml

Defines tasks with:
- **description**: Detailed instructions and workflows
- **expected_output**: Format and content requirements
- **agent**: Which agent performs the task

## 7.6 Mock Mode for Testing

Tools include `MOCK_MODE` flag (default: `True`) for offline testing:

**Mock Data Includes:**
- 3 sample books (Clean Code, The Pragmatic Programmer, 1984)
- 3 sample resources (Conference Room A, Study Room 101, Reading Desk #5)
- Mock user balance: $100.00
- Empty bookings list (populated during tests)

**To switch to real database:**
```python
# In app/agents/tools.py
MOCK_MODE = False
```

## 7.7 Audit Logging

All agent interactions logged to `AI_Audit_Log` table with:
- `agent_type`: "receptionist", "book_officer", or "resources_officer"
- `input_text`: User's message (truncated to 500 chars)
- `detected_intent`: Classified intent
- `actions_taken`: JSON string of actions performed
- `metadata`: Optional additional metadata
- `timestamp`: UTC timestamp

---

# 8. API Reference

## 8.1 Authentication Endpoints

### POST /api/auth/signup

Register a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "balance": 100.0,
  "created_at": "2025-10-08T10:00:00Z"
}
```

### POST /api/auth/login

Authenticate and receive JWT token.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "balance": 100.0
  }
}
```

### GET /api/auth/me

Get current authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "user",
  "balance": 100.0,
  "created_at": "2025-10-08T10:00:00Z"
}
```

### POST /api/auth/add-balance

Add funds to user balance.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "amount": 50.0
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "balance": 150.0,
  "message": "Balance updated successfully"
}
```

## 8.2 Books Endpoints

### GET /api/books

List and search books.

**Query Parameters:**
- `q` (optional): Search query (title, author, ISBN)
- `category` (optional): Filter by category
- `page` (optional, default: 1): Page number
- `limit` (optional, default: 20): Items per page

**Example:**
```
GET /api/books?q=clean+code&category=Technology&page=1&limit=10
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Clean Code",
      "author": "Robert C. Martin",
      "isbn": "978-0132350884",
      "category": "Technology",
      "description": "A Handbook of Agile Software Craftsmanship",
      "price": 42.99,
      "stock_count": 6,
      "digital_url": null,
      "created_at": "2025-10-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 10
}
```

### GET /api/books/{id}

Get detailed information about a specific book.

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "Clean Code",
  "author": "Robert C. Martin",
  "isbn": "978-0132350884",
  "category": "Technology",
  "description": "A Handbook of Agile Software Craftsmanship",
  "price": 42.99,
  "stock_count": 6,
  "digital_url": null,
  "created_at": "2025-10-01T00:00:00Z"
}
```

### POST /api/books/{id}/purchase

Purchase a book.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "quantity": 1
}
```

**Response (200 OK):**
```json
{
  "transaction": {
    "id": 101,
    "book_id": 1,
    "amount": 42.99,
    "currency": "USD",
    "status": "completed",
    "created_at": "2025-10-08T10:30:00Z"
  },
  "book_title": "Clean Code",
  "remaining_balance": 57.01,
  "message": "Purchase successful"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid quantity or insufficient stock
- `402 Payment Required`: Insufficient balance
- `404 Not Found`: Book not found

### POST /api/books (Admin Only)

Create a new book.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "title": "Design Patterns",
  "author": "Gang of Four",
  "isbn": "978-0201633610",
  "category": "Technology",
  "description": "Elements of Reusable Object-Oriented Software",
  "price": 54.99,
  "stock_count": 10,
  "digital_url": null
}
```

**Response (201 Created):**
```json
{
  "id": 9,
  "title": "Design Patterns",
  "author": "Gang of Four",
  "isbn": "978-0201633610",
  "category": "Technology",
  "description": "Elements of Reusable Object-Oriented Software",
  "price": 54.99,
  "stock_count": 10,
  "digital_url": null,
  "created_at": "2025-10-08T11:00:00Z"
}
```

### PUT /api/books/{id} (Admin Only)

Update an existing book.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "price": 49.99,
  "stock_count": 15
}
```

**Response (200 OK):**
```json
{
  "id": 9,
  "title": "Design Patterns",
  "price": 49.99,
  "stock_count": 15,
  "message": "Book updated successfully"
}
```

### DELETE /api/books/{id} (Admin Only)

Delete a book.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "message": "Book deleted successfully"
}
```

## 8.3 Resources Endpoints

### GET /api/resources

List available resources.

**Query Parameters:**
- `min_capacity` (optional): Minimum capacity filter
- `type` (optional): Filter by type (room, seat, equipment)
- `page` (optional, default: 1): Page number
- `limit` (optional, default: 20): Items per page

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "name": "Conference Room A",
      "type": "room",
      "capacity": 12,
      "hourly_rate": 15.0,
      "open_hour": "09:00",
      "close_hour": "21:00",
      "features": "{\"projector\": true, \"whiteboard\": true}",
      "created_at": "2025-10-01T00:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20
}
```

### GET /api/resources/{id}

Get detailed resource information.

**Response (200 OK):**
```json
{
  "id": 1,
  "name": "Conference Room A",
  "type": "room",
  "capacity": 12,
  "hourly_rate": 15.0,
  "open_hour": "09:00",
  "close_hour": "21:00",
  "features": "{\"projector\": true, \"whiteboard\": true}",
  "created_at": "2025-10-01T00:00:00Z"
}
```

### GET /api/resources/{id}/availability

Check resource availability for a time range.

**Query Parameters:**
- `start` (required): Start datetime (ISO 8601 format)
- `end` (required): End datetime (ISO 8601 format)

**Example:**
```
GET /api/resources/1/availability?start=2025-10-09T10:00:00Z&end=2025-10-09T12:00:00Z
```

**Response (200 OK):**
```json
{
  "available": true,
  "resource_id": 1,
  "start": "2025-10-09T10:00:00Z",
  "end": "2025-10-09T12:00:00Z",
  "conflicting_bookings": []
}
```

**If unavailable:**
```json
{
  "available": false,
  "resource_id": 1,
  "start": "2025-10-09T10:00:00Z",
  "end": "2025-10-09T12:00:00Z",
  "conflicting_bookings": [
    {
      "id": 15,
      "start_datetime": "2025-10-09T09:00:00Z",
      "end_datetime": "2025-10-09T11:00:00Z"
    }
  ]
}
```

### POST /api/resources (Admin Only)

Create a new resource.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "name": "Study Room 102",
  "type": "room",
  "capacity": 4,
  "hourly_rate": 8.0,
  "open_hour": "09:00",
  "close_hour": "21:00",
  "features": "{\"whiteboard\": true}"
}
```

**Response (201 Created):**
```json
{
  "id": 6,
  "name": "Study Room 102",
  "type": "room",
  "capacity": 4,
  "hourly_rate": 8.0,
  "open_hour": "09:00",
  "close_hour": "21:00",
  "features": "{\"whiteboard\": true}",
  "created_at": "2025-10-08T12:00:00Z"
}
```

## 8.4 Bookings Endpoints

### POST /api/bookings

Create a new booking.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "resource_id": 1,
  "start_datetime": "2025-10-09T10:00:00Z",
  "end_datetime": "2025-10-09T12:00:00Z",
  "notes": "Team meeting"
}
```

**Response (201 Created):**
```json
{
  "booking": {
    "id": 25,
    "resource_id": 1,
    "user_id": 1,
    "start_datetime": "2025-10-09T10:00:00Z",
    "end_datetime": "2025-10-09T12:00:00Z",
    "status": "confirmed",
    "notes": "Team meeting",
    "created_at": "2025-10-08T12:30:00Z"
  },
  "transaction": {
    "id": 150,
    "booking_id": 25,
    "amount": 30.0,
    "currency": "USD",
    "status": "completed"
  },
  "resource_name": "Conference Room A",
  "total_cost": 30.0,
  "remaining_balance": 70.0,
  "message": "Booking confirmed"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid datetime range or duration
- `402 Payment Required`: Insufficient balance
- `404 Not Found`: Resource not found
- `409 Conflict`: Time slot not available

### GET /api/bookings

List user's bookings.

**Headers:**
```
Authorization: Bearer <token>
```

**Query Parameters:**
- `include_past` (optional, default: false): Include past bookings
- `page` (optional, default: 1): Page number
- `limit` (optional, default: 20): Items per page

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": 25,
      "resource_id": 1,
      "resource_name": "Conference Room A",
      "user_id": 1,
      "start_datetime": "2025-10-09T10:00:00Z",
      "end_datetime": "2025-10-09T12:00:00Z",
      "status": "confirmed",
      "notes": "Team meeting",
      "created_at": "2025-10-08T12:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20
}
```

### DELETE /api/bookings/{id}

Cancel a booking.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "message": "Booking cancelled successfully",
  "refund_amount": 30.0,
  "new_balance": 100.0
}
```

**Error Responses:**
- `400 Bad Request`: Cannot cancel within 1 hour of start time
- `403 Forbidden`: Not authorized to cancel this booking
- `404 Not Found`: Booking not found

## 8.5 AI Agent Endpoint

### POST /api/agent/chat

Chat with the AI assistant.

**Headers:**
```
Authorization: Bearer <token>
```

**Request Body:**
```json
{
  "message": "I want to buy Clean Code"
}
```

**Response (200 OK):**
```json
{
  "response": "I found Clean Code by Robert C. Martin for $42.99. We have 6 copies in stock. Would you like to purchase it?",
  "user_id": 1,
  "intent": "book",
  "parsed_details": {
    "book_title": "Clean Code",
    "action": "purchase"
  },
  "audit_id": 501
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or missing token
- `500 Internal Server Error`: Agent processing error

---

# 9. Setup and Configuration

## 9.1 Prerequisites

- Python 3.10 or higher
- Node.js 16 or higher
- npm or yarn package manager
- Google API Key (for Gemini AI)
- PostgreSQL (production) or SQLite (development)

## 9.2 Backend Setup

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create `.env` file in backend directory:

```bash
# Database
DATABASE_URL=sqlite:///./library.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/library_db

# JWT Configuration
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# AI Services
GOOGLE_API_KEY=your-google-api-key-here
CREWAI_API_KEY=your-crewai-key-optional
OPENAI_API_KEY=your-openai-key-optional

# Vector Store
VECTORSTORE_DIR=./app/vectorstore/db

# Frontend URL (for CORS)
VITE_API_URL=http://localhost:8000
```

### 5. Initialize Database

```bash
# Run seed script to create tables and demo data
python -m app.seed.seed_data
```

This creates:
- Admin user: `admin@example.com` / `adminpass` ($1,000 balance)
- Demo user: `demo@example.com` / `demopass` ($100 balance)
- 8 sample books
- 5 sample resources

### 6. Run Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

Access points:
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 9.3 Frontend Setup

### 1. Navigate to Frontend

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment

Create `.env` file in frontend directory:

```bash
VITE_API_URL=http://localhost:8000
```

### 4. Run Development Server

```bash
npm run dev
```

Access the application at: http://localhost:3000

## 9.4 Environment Variables Reference

### Backend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | - | Database connection string |
| JWT_SECRET | Yes | - | Secret key for JWT signing |
| JWT_ALGORITHM | No | HS256 | JWT algorithm |
| ACCESS_TOKEN_EXPIRE_MINUTES | No | 10080 | Token expiration (7 days) |
| GOOGLE_API_KEY | Yes | - | Google Gemini API key |
| CREWAI_API_KEY | No | - | CrewAI API key (optional) |
| OPENAI_API_KEY | No | - | OpenAI API key (optional) |
| VECTORSTORE_DIR | No | ./app/vectorstore/db | Vector store directory |

### Frontend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| VITE_API_URL | Yes | - | Backend API base URL |

---

# 10. Testing

## 10.1 Backend Testing

### Run Agent Tests (Offline Mode)

Test AI agents with mock data:

```bash
cd backend
python test_agents.py
```

This tests:
1. Intent classification with various messages
2. Book search and purchase flows
3. Resource listing and booking flows

### Run Unit Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest app/tests/test_auth.py -v

# Run with coverage
pytest --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Test API Endpoints

```bash
# Get authentication token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@example.com","password":"demopass"}'

# Use token in subsequent requests
curl -X GET http://localhost:8000/api/books \
  -H "Authorization: Bearer <your-token-here>"

# Test agent chat
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Authorization: Bearer <your-token-here>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me available books"}'
```

## 10.2 Frontend Testing

### Manual Testing Checklist

**Authentication:**
- [ ] User can register new account
- [ ] User can login with credentials
- [ ] Invalid credentials show error
- [ ] Protected routes redirect to login
- [ ] Logout clears session

**Books:**
- [ ] Books list displays correctly
- [ ] Search filters books
- [ ] Book details page shows full information
- [ ] Purchase flow works with balance check
- [ ] Admin can create/edit/delete books

**Resources:**
- [ ] Resources list displays correctly
- [ ] Resource details show availability
- [ ] Booking form validates dates
- [ ] Booking calculates cost correctly
- [ ] Admin can create/edit/delete resources

**Bookings:**
- [ ] User can view their bookings
- [ ] Upcoming bookings show correctly
- [ ] Cancel booking works and refunds balance
- [ ] Past bookings display when toggled

**AI Assistant:**
- [ ] Chat interface accepts messages
- [ ] AI responses display correctly
- [ ] Suggestions can be applied to forms
- [ ] Balance updates after AI-driven purchases
- [ ] Conversation history maintained

## 10.3 Mock Mode Configuration

For offline agent testing, configure mock mode:

```python
# In app/agents/tools.py
MOCK_MODE = True  # Use mock data (default)
MOCK_MODE = False # Use real database
```

Mock data includes:
- 3 sample books
- 3 sample resources
- Mock user with $100 balance
- Empty bookings list

---

# 11 Monitoring and Maintenance

## 11.1 Logging

1. **Application Logs:**
```python
# In app/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

2. **Access Logs:**
- Enable Uvicorn access logs
- Monitor API endpoint usage
- Track response times

3. **Error Tracking:**
- Integrate Sentry or similar service
- Monitor exception rates
- Alert on critical errors

### Database Maintenance

```sql
-- Regular maintenance tasks
VACUUM ANALYZE;

-- Check table sizes
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Review slow queries
SELECT * FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;
```

### Backup Strategy

```bash
# Daily database backups
pg_dump library_db > backup_$(date +%Y%m%d).sql

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U library_user library_db | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete
```

### Health Checks

**Backend Health Endpoint:**
```python
# Add to app/main.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected"
    }
```

**Monitoring Script:**
```bash
#!/bin/bash
# Monitor application health
while true; do
    STATUS=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)
    if [ $STATUS -ne 200 ]; then
        echo "Alert: Backend is down! Status: $STATUS"
        # Send alert (email, Slack, etc.)
    fi
    sleep 60
done
```

## 11.2 Scaling Strategies

### Horizontal Scaling

1. **Load Balancer Configuration:**
```nginx
# Nginx load balancer
upstream backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

2. **Database Read Replicas:**
- Configure PostgreSQL replication
- Route read queries to replicas
- Write queries to primary database

3. **Session Management:**
- Use Redis for distributed session storage
- Enable sticky sessions in load balancer
- Implement stateless authentication (JWT)

### Vertical Scaling

1. **Database:**
- Increase PostgreSQL shared_buffers
- Adjust work_mem for complex queries
- Tune max_connections based on load

2. **Application:**
- Increase Uvicorn worker count
- Allocate more CPU/RAM to containers
- Optimize Python code for performance

### Caching Strategy

```python
# Redis caching for frequently accessed data
from redis import Redis
from functools import wraps

redis_client = Redis(host='redis', port=6379, decode_responses=True)

def cache_result(expire=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expire, json.dumps(result))
            return result
        return wrapper
    return decorator

# Example usage
@cache_result(expire=600)
async def get_popular_books(limit: int = 10):
    # Implementation
    pass
```

## 11.3 Security Best Practices

### API Security

1. **HTTPS Only:**
```python
# Force HTTPS in production
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

2. **CORS Configuration:**
```python
# Strict CORS in production
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Specific domains only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

3. **Rate Limiting:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(request: Request):
    # Implementation
    pass
```

### Database Security

1. **Parameterized Queries:**
```python
# Always use SQLModel/SQLAlchemy - automatic protection
# NEVER concatenate user input into SQL
```

2. **Least Privilege:**
```sql
-- Create application user with limited privileges
CREATE USER library_app WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE library_db TO library_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO library_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO library_app;
```

3. **Encryption:**
- Enable SSL/TLS for database connections
- Encrypt sensitive data at rest
- Use PostgreSQL pgcrypto for column-level encryption

### Application Security

1. **Input Validation:**
```python
# Pydantic models provide automatic validation
from pydantic import BaseModel, validator, constr

class BookCreate(BaseModel):
    title: constr(min_length=1, max_length=200)
    price: float
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
```

2. **SQL Injection Prevention:**
- Use ORM (SQLModel/SQLAlchemy)
- Never build raw SQL from user input
- Validate and sanitize all inputs

3. **XSS Prevention:**
- Frontend: React automatically escapes content
- Backend: Validate and sanitize user inputs
- Use Content-Security-Policy headers

---

# 12. Appendices

## 12.1 Demo Users

**Admin Account:**
- Email: `admin@example.com`
- Password: `adminpass`
- Balance: $1,000.00
- Role: admin

**Demo User:**
- Email: `demo@example.com`
- Password: `demopass`
- Balance: $100.00
- Role: user

## 12.2 Sample Books Data

| ID | Title | Author | Category | Price | Stock |
|----|-------|--------|----------|-------|-------|
| 1 | Clean Code | Robert C. Martin | Technology | $42.99 | 6 |
| 2 | The Pragmatic Programmer | Andrew Hunt | Technology | $39.99 | 4 |
| 3 | 1984 | George Orwell | Fiction | $15.99 | 4 |
| 4 | To Kill a Mockingbird | Harper Lee | Fiction | $14.99 | 5 |
| 5 | Sapiens | Yuval Noah Harari | History | $22.99 | 7 |
| 6 | Atomic Habits | James Clear | Self-Help | $18.99 | 8 |
| 7 | The Great Gatsby | F. Scott Fitzgerald | Fiction | $12.99 | 6 |
| 8 | Educated | Tara Westover | Biography | $19.99 | 5 |

## 12.3 Sample Resources Data

| ID | Name | Type | Capacity | Rate/Hour | Hours |
|----|------|------|----------|-----------|-------|
| 1 | Conference Room A | room | 12 | $15.00 | 09:00-21:00 |
| 2 | Study Room 101 | room | 4 | $8.00 | 09:00-21:00 |
| 3 | Reading Desk #5 | seat | 1 | $2.00 | 09:00-21:00 |
| 4 | 3D Printer Station | equipment | 1 | $10.00 | 09:00-18:00 |
| 5 | Laptop Checkout | equipment | 1 | $5.00 | 09:00-21:00 |

## 12.4 Common Error Codes

| Code | Meaning | Common Causes | Resolution |
|------|---------|---------------|------------|
| 400 | Bad Request | Invalid input, validation failure | Check request body format |
| 401 | Unauthorized | Missing/invalid token | Login again to get new token |
| 402 | Payment Required | Insufficient balance | Add funds to account |
| 403 | Forbidden | Insufficient permissions | Admin action required |
| 404 | Not Found | Resource doesn't exist | Verify ID/endpoint |
| 409 | Conflict | Booking overlap, stock issue | Check availability first |
| 422 | Unprocessable Entity | Schema validation failed | Review request schema |
| 500 | Internal Server Error | Server/database issue | Check logs, contact admin |

## 12.5 API Response Formats

### Success Response
```json
{
  "data": { /* response data */ },
  "message": "Operation successful",
  "timestamp": "2025-10-08T12:00:00Z"
}
```

### Error Response
```json
{
  "detail": "Error message",
  "error_code": "INSUFFICIENT_BALANCE",
  "timestamp": "2025-10-08T12:00:00Z"
}
```

### Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## 12.6 Database Queries Reference

### Common Queries

**Get user's transaction history:**
```sql
SELECT t.*, b.title as book_title, r.name as resource_name
FROM transactions t
LEFT JOIN books b ON t.book_id = b.id
LEFT JOIN bookings bk ON t.booking_id = bk.id
LEFT JOIN resources r ON bk.resource_id = r.id
WHERE t.user_id = ?
ORDER BY t.created_at DESC;
```

**Check resource availability:**
```sql
SELECT COUNT(*) FROM bookings
WHERE resource_id = ?
  AND status = 'confirmed'
  AND NOT (end_datetime <= ? OR start_datetime >= ?);
```

**Get popular books:**
```sql
SELECT b.*, COUNT(t.id) as purchase_count
FROM books b
LEFT JOIN transactions t ON b.id = t.book_id
WHERE t.created_at >= NOW() - INTERVAL '30 days'
GROUP BY b.id
ORDER BY purchase_count DESC
LIMIT 10;
```

**Revenue report:**
```sql
SELECT 
  DATE(created_at) as date,
  COUNT(*) as transaction_count,
  SUM(amount) as total_revenue
FROM transactions
WHERE status = 'completed'
  AND created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

## 12.7 Troubleshooting Guide

### Backend Issues

**Problem: Database connection error**
```
Solution:
1. Check DATABASE_URL in .env
2. Verify database server is running
3. Check network connectivity
4. Verify credentials
```

**Problem: JWT token invalid**
```
Solution:
1. Check JWT_SECRET is consistent
2. Verify token hasn't expired
3. Clear localStorage and login again
4. Check token format (Bearer <token>)
```

**Problem: AI agent not responding**
```
Solution:
1. Verify GOOGLE_API_KEY is set
2. Check API quota limits
3. Review agent logs in ai_audit_logs table
4. Test with MOCK_MODE=True first
```

### Frontend Issues

**Problem: API calls failing**
```
Solution:
1. Check VITE_API_URL in .env
2. Verify backend is running
3. Check browser console for CORS errors
4. Verify authentication token
```

**Problem: Dates displaying incorrectly**
```
Solution:
1. Ensure using parseUTCDate() for backend dates
2. Check browser timezone settings
3. Verify datetime format from API
```

**Problem: Balance not updating**
```
Solution:
1. Refresh page to fetch latest data
2. Check transaction was successful
3. Review browser console for errors
4. Verify API response includes updated balance
```

## 12.8 Performance Optimization Tips

### Backend Optimization

1. **Database Indexing:**
```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_bookings_user_start ON bookings(user_id, start_datetime);
CREATE INDEX idx_transactions_user_created ON transactions(user_id, created_at DESC);
CREATE INDEX idx_books_category_price ON books(category, price);
```

2. **Query Optimization:**
```python
# Use select_related to reduce queries
from sqlmodel import select

stmt = select(Booking).join(Resource).where(Booking.user_id == user_id)
bookings = session.exec(stmt).all()
```

3. **Connection Pooling:**
```python
# In database.py
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)
```

### Frontend Optimization

1. **Code Splitting:**
```typescript
// Lazy load route components
const Books = lazy(() => import('./pages/Books'));
const Resources = lazy(() => import('./pages/Resources'));

<Suspense fallback={<Loading />}>
  <Routes>
    <Route path="/books" element={<Books />} />
  </Routes>
</Suspense>
```

2. **API Response Caching:**
```typescript
// Cache API responses
const useBooks = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const cached = localStorage.getItem('books_cache');
    const cacheTime = localStorage.getItem('books_cache_time');
    
    if (cached && cacheTime && Date.now() - parseInt(cacheTime) < 300000) {
      setBooks(JSON.parse(cached));
      setLoading(false);
      return;
    }
    
    fetchBooks().then(data => {
      setBooks(data);
      localStorage.setItem('books_cache', JSON.stringify(data));
      localStorage.setItem('books_cache_time', Date.now().toString());
      setLoading(false);
    });
  }, []);
  
  return { books, loading };
};
```

3. **Debounce Search:**
```typescript
// Debounce search input
import { debounce } from 'lodash';

const debouncedSearch = useMemo(
  () => debounce((query: string) => {
    searchBooks(query);
  }, 300),
  []
);
```

## 12.9 Glossary

**Agent**: An AI component that performs specific tasks using tools and reasoning

**Atomic Operation**: A database operation that either completes fully or not at all

**Audit Log**: A record of actions taken in the system for compliance and review

**Balance**: Virtual currency amount in a user's account

**Booking**: A reservation of a resource for a specific time period

**CRUD**: Create, Read, Update, Delete - basic database operations

**Intent**: The classified purpose of a user's message (book, resources, normal_question)

**JWT**: JSON Web Token - a secure method of transmitting authentication data

**Mock Mode**: Testing mode using in-memory data instead of database

**ORM**: Object-Relational Mapping - translates between database and code objects

**Resource**: A bookable facility or equipment item in the library

**SPA**: Single-Page Application - web app that loads once and updates dynamically

**Transaction**: A record of a financial operation (purchase or booking payment)

**UTC**: Coordinated Universal Time - timezone-independent time standard

## 12.10 Additional Resources

### Documentation Links

- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **SQLModel**: https://sqlmodel.tiangolo.com/
- **CrewAI**: https://docs.crewai.com/
- **Tailwind CSS**: https://tailwindcss.com/docs

### Community Support

- **GitHub Issues**: Report bugs and feature requests
- **Stack Overflow**: Tag questions with relevant technology tags
- **Discord/Slack**: Join community channels for real-time help

### License

This project is provided as-is for educational and commercial use. Refer to the LICENSE file in the repository for full details.

### Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request with clear description

### Changelog

**Version 1.0.0 (October 2025)**
- Initial release
- Core authentication and authorization
- Book catalog and purchase system
- Resource booking system
- AI agent integration with three-crew architecture
- Frontend SPA with React and TypeScript
- Complete documentation 

---

# End of Documentation

For the latest updates and additional information, please visit the project repository or contact the development team.

**Last Updated**: October 8, 2025
**Document Version**: 1.0.0