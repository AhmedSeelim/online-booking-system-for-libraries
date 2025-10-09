# 📚 Library Booking System

A modern, AI-powered library management platform that unifies book catalog management, resource booking, and intelligent assistance through conversational AI agents.

---

## 📁 Complete Project Structure

```
library-booking-system/
│
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── main.py                   # Application entry point
│   │   ├── config.py                 # Configuration (env variables)
│   │   ├── database.py               # Database setup
│   │   ├── deps.py                   # Dependencies (auth, session)
│   │   │
│   │   ├── models/                   # Database Models
│   │   │   ├── user.py               # User model
│   │   │   ├── book.py               # Book model
│   │   │   ├── resource.py           # Resource model
│   │   │   ├── booking.py            # Booking model
│   │   │   ├── transaction.py        # Transaction model
│   │   │   └── ai_audit_log.py       # AI audit log
│   │   │
│   │   ├── schemas/                  # Pydantic Schemas
│   │   │   ├── user.py
│   │   │   ├── book.py
│   │   │   ├── resource.py
│   │   │   └── booking.py
│   │   │
│   │   ├── crud/                     # Database Operations
│   │   │   ├── user.py
│   │   │   ├── book.py
│   │   │   ├── resource.py
│   │   │   ├── booking.py
│   │   │   ├── transaction.py
│   │   │   └── ai_audit_log.py
│   │   │
│   │   ├── core/                     # Core Utilities
│   │   │   └── security.py           # JWT & password hashing
│   │   │
│   │   ├── api/                      # API Routes
│   │   │   ├── router.py             # Main router
│   │   │   ├── auth.py               # Auth endpoints
│   │   │   ├── books.py              # Book endpoints
│   │   │   ├── resources.py          # Resource endpoints
│   │   │   ├── bookings.py           # Booking endpoints
│   │   │   └── agent.py              # AI agent endpoint
│   │   │
│   │   ├── agents/                   # AI Agent System
│   │   │   ├── models.py             # Agent output models
│   │   │   ├── tools.py              # Agent tools
│   │   │   ├── crews.py              # Agent crews
│   │   │   └── config/
│   │   │       ├── agents.yaml       # Agent configs
│   │   │       └── tasks.yaml        # Task definitions
│   │   │
│   │   ├── seed/
│   │   │   └── seed_data.py          # Demo data seeder
│   │   │
│   │   └── tests/                    # Unit tests
│   │
│   ├── requirements.txt              # Python dependencies
│   └── .env.example                # Agent testing script
│
├── frontend/                         # React + TypeScript Frontend
│   ├── src/
│   │   ├── main.tsx                  # App entry point
│   │   │
│   │   ├── api/                      # API Layer
│   │   │   ├── axiosInstance.ts      # Axios config
│   │   │   ├── auth.ts               # Auth API
│   │   │   ├── books.ts              # Books API
│   │   │   ├── resources.ts          # Resources API
│   │   │   ├── bookings.ts           # Bookings API
│   │   │   └── ai.ts                 # AI API
│   │   │
│   │   ├── components/               # React Components
│   │   │   ├── Layout.tsx            # App shell
│   │   │   ├── AgentChat.tsx         # AI chat interface
│   │   │   └── Modal.tsx             # Modal component
│   │   │
│   │   ├── context/                  # State Management
│   │   │   ├── AuthContext.tsx       # Auth state
│   │   │   └── AIActionContext.tsx   # AI suggestions
│   │   │
│   │   ├── pages/                    # Page Components
│   │   │   ├── Home.tsx
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── Books.tsx
│   │   │   ├── Resources.tsx
│   │   │   ├── ResourceDetail.tsx
│   │   │   └── MyBookings.tsx
│   │   │
│   │   ├── types.ts                  # TypeScript types
│   │   ├── utils/
│   │   │   └── dateUtils.ts          # Date utilities
│   │   │
│   │   └── styles/
│   │       └── index.css             # Global styles
│   │
│   ├── package.json                  # Dependencies
│   ├── vite.config.ts                # Vite config
│   ├── tailwind.config.js            # Tailwind config
│   └── tsconfig.node.json              
│
└── docs/                             # Documentation
    ├── DOCUMENTATION.md
    └── AI_tools_usage.md

```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** - Backend runtime
- **Node.js 16+** - Frontend runtime
- **npm or yarn** - Package manager
- **Google API Key** - For Gemini AI (required for agent system)
- **SQLite** (included) or **PostgreSQL** (optional, for production)

### Installation Steps

#### 1️⃣ Clone the Repository

```bash
git clone <repository-url>
cd library-booking-system
```

#### 2️⃣ Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env file with your settings (see Configuration section)
nano .env  # or use your preferred editor
```

#### 3️⃣ Initialize Database with Demo Data

```bash
# Run seed script (creates tables and demo data)
python -m app.seed.seed_data
```

**This creates:**
- **Admin user**: `admin@example.com` / `adminpass` (Balance: $1,000)
- **Demo user**: `demo@example.com` / `demopass` (Balance: $100)
- **8 sample books** (Clean Code, The Pragmatic Programmer, 1984, etc.)
- **5 sample resources** (Conference rooms, study rooms, reading desks, equipment)

#### 4️⃣ Start Backend Server

```bash
# Run development server with auto-reload
uvicorn app.main:app --reload --port 8000
```

Backend will be available at:
- **API Base**: http://localhost:8000
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

#### 5️⃣ Frontend Setup

```bash
# Open new terminal and navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env file (usually just needs backend URL)
nano .env
```

#### 6️⃣ Start Frontend Server

```bash
# Run development server
npm run dev
```

Frontend will be available at: **http://localhost:3000**

---

## ⚙️ Configuration

### Backend Configuration (.env)

Create `backend/.env` file with the following variables:

```bash
# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================
# SQLite (default for development)
DATABASE_URL=sqlite:///./library.db

# PostgreSQL (recommended for production)
# DATABASE_URL=postgresql://username:password@localhost:5432/library_db

# =============================================================================
# JWT AUTHENTICATION
# =============================================================================
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days

# =============================================================================
# AI SERVICES
# =============================================================================
# Google Gemini API (REQUIRED for AI agents)
GOOGLE_API_KEY=your-google-api-key-here

# =============================================================================
# CORS CONFIGURATION
# =============================================================================
# Frontend URL (for CORS)
VITE_API_URL=http://localhost:8000
```

**🔑 How to Get Google API Key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and paste into `.env` file

### Frontend Configuration (.env)

Create `frontend/.env` file:

```bash
# Backend API URL
VITE_API_URL=http://localhost:8000
```

### AI Agent Mock Mode

For offline testing without database calls, configure mock mode:

```python
# In backend/app/agents/tools.py
MOCK_MODE = True   # Use in-memory mock data (default)
MOCK_MODE = False  # Use real database
```

**Mock Mode Includes:**
- 3 sample books (Clean Code, The Pragmatic Programmer, 1984)
- 3 sample resources (Conference Room A, Study Room 101, Reading Desk #5)
- Mock user with $100 balance
- Empty bookings list (populated during tests)

---

## 🎥 Demo

### Video Demonstrations

[![Watch the demo on YouTube](https://img.youtube.com/vi/XCMonQUB6nc/0.jpg)](https://www.youtube.com/watch?v=XCMonQUB6nc)

