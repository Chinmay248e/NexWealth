# NexWealth — Dark Futuristic Wealth Intelligence & Portfolio Management

NexWealth is an enterprise-grade, dark futuristic personal wealth intelligence and portfolio management platform designed exclusively for the Indian financial ecosystem (**INR / ₹**). Built around a strict, immutable [Data Contract](./NEXWEALTH_DATA_CONTRACT.md), NexWealth delivers unified cashflow tracking, real-time ledger synchronization, investment portfolio analytics, and automated financial health calculations.

---

## 🌟 Features & Implementation Status

### ✅ Live Implemented Modules
- **Authentication & Security:** Secure JWT session authentication, salted bcrypt password hashing, and strict user-scoped request validation.
- **Executive Dashboard:** Real-time KPI cards (Total Income, Total Expenses, Available Savings, Savings Rate), interactive 6-month cashflow bar chart, and expense category donut visualization.
- **Income Streams:** Full CRUD for income records with automatic transaction synchronization into the unified ledger.
- **Categorized Expenses:** Outflow management across 9 financial categories with real-time budget tracking.
- **Unified Financial Ledger:** Consolidated timeline of all debits and credits with category filtering and instant transaction search.
- **Investment Portfolio:** Multi-asset portfolio tracking (Equities, Mutual Funds, Fixed Deposits, Crypto, Gold, Real Estate) with automated total invested, current valuation, unrealized gain/loss, and ROI % calculations.
- **Financial Analytics:** Comprehensive financial health metrics, chronological monthly cashflow aggregation, expense distribution breakdown, and asset class allocation.
- **User Profile Management:** Profile details management, email uniqueness verification, and security overview.
- **Notifications Center:** Real-time financial alerts, unread filtering, and read/delete batch operations.
- **Admin & Data Contract Console:** In-app contract specification viewer, team ownership matrix, and system status audit.

### ⏳ UI Reference & Future Roadmap (Placeholder)
- **Target Savings Goals:** Goal progress tracking and milestone projections.
- **Bank Statement Ingestion:** Automated parser for bank statement ingestion.
- **Encrypted Document Vault:** Secure storage for tax records, PAN/KYC, and financial policies.
- **NexAdvisor AI Copilot:** Neural financial advisor copilot for automated budget optimization.

---

## 🏛️ System Architecture

- **Frontend:** [Next.js 14](https://nextjs.org/) (App Router), React 18, TypeScript, Tailwind CSS, Lucide React, Recharts.
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+), Pydantic v2 schemas, SQLAlchemy 2.0 ORM.
- **Database:** PostgreSQL with [Alembic](https://alembic.sqlalchemy.org/) versioned database migrations.
- **Security:** Cryptographically signed JWT access tokens stored client-side in `sessionStorage` (zero `localStorage` usage), bcrypt password encryption, and zero secret exposure in API responses.
- **Monetary Standard:** Strict Indian Rupee (`INR` / `₹`) formatting via `en-IN` locale across all calculations and visual components.
- **UI/UX Prototype (`sgp/`):** The `sgp/` directory contains the original UI/UX reference design prototype, serving as the visual design baseline for the production Next.js frontend and FastAPI backend.

---

## 📁 Project Structure

```
NexWealth/
├── frontend/                     # Next.js 14+ (App Router) + React + TypeScript + Tailwind CSS
│   ├── app/                      # App Router Page Routes (All Views + Auth)
│   │   ├── login/                # Sign In page
│   │   ├── register/             # Account Registration page
│   │   ├── dashboard/            # Executive Financial Dashboard
│   │   ├── income/               # Cash Inflow Streams
│   │   ├── expenses/             # Categorized Outflows
│   │   ├── transactions/         # Unified Financial Ledger
│   │   ├── investments/          # Investment Portfolio & Assets
│   │   ├── analytics/            # Cashflow & Portfolio Analytics
│   │   ├── notifications/        # Alerts & Notifications Center
│   │   ├── profile/              # User Profile & Security Overview
│   │   ├── admin/                # Admin Console & Data Contract Viewer
│   │   ├── goals/                # Goals Tracker (UI Reference)
│   │   ├── bank-statement/       # Bank Statement Parser (UI Reference)
│   │   ├── documents/            # Encrypted Vault (UI Reference)
│   │   └── ai-advisor/           # NexAdvisor Neural Copilot (UI Reference)
│   ├── components/               # UI components, layouts, charts
│   ├── lib/                      # API client, auth utilities, currency formatters
│   ├── types/                    # TypeScript interfaces aligned with Data Contract
│   ├── .env.local.example        # Frontend environment template
│   └── package.json              # Next.js dependencies & build scripts
│
├── backend/                      # FastAPI (Python 3.10+) REST API
│   ├── app/
│   │   ├── main.py               # FastAPI application entry point & CORS configuration
│   │   ├── core/                 # Config (BaseSettings), Database session, Security (JWT/bcrypt)
│   │   ├── models/               # SQLAlchemy ORM models (User, Income, Expense, Transaction, Investment, Notification)
│   │   ├── schemas/              # Pydantic v2 validation schemas
│   │   ├── api/v1/endpoints/     # Versioned REST endpoints (Auth, Income, Expense, Transaction, Investment, Analytics, Profile, Notification)
│   │   ├── services/             # Core business logic & database calculations
│   │   └── utils/                # Monetary precision helpers
│   ├── alembic/                  # Alembic migration revisions & environment
│   ├── .env.example              # Backend environment variables template
│   └── requirements.txt          # Python dependencies
│
├── database/                     # PostgreSQL Migrations & Seeding
│   ├── migrations/               # Alembic versioned migrations
│   ├── seeds/                    # Seed script for initial development data
│   └── README.md                 # Database setup & migration guide
│
├── NEXWEALTH_DATA_CONTRACT.md     # Single Source of Truth for Data Models, Formulas & Ownership
├── .gitignore                    # Git ignore configuration protecting secrets & build artifacts
└── README.md                     # Project documentation
```

---

## 👥 Team Ownership Matrix

As formalized in [`NEXWEALTH_DATA_CONTRACT.md`](./NEXWEALTH_DATA_CONTRACT.md):

| Team Member | Domain | Assigned Backend & Frontend Modules |
| :--- | :--- | :--- |
| **Person 1** | Cashflow & Auth | `User`, `Authentication`, `Income`, `Expense`, `Transaction`, Dashboard Core Calculations |
| **Person 2** | Goals & Vault | `Goal`, `Document`, `BankStatement`, `AI Advisor` |
| **Person 3** | Portfolio & Controls | `Investment`, `Budget`, `Notification`, `Analytics`, `Profile`, `Admin & Contract` |

---

## ⚙️ Prerequisites

Ensure the following runtimes and services are installed on your machine:

- **Node.js:** `v18.x` or `v20.x` LTS ([Download Node.js](https://nodejs.org/))
- **Python:** `3.10+` ([Download Python](https://www.python.org/))
- **PostgreSQL:** `14+` ([Download PostgreSQL](https://www.postgresql.org/))

---

## 🔐 Environment Configuration

### 1. Backend Environment Setup
Create `backend/.env` from the provided template:

```bash
cd backend
cp .env.example .env
```

Configure your PostgreSQL credentials in `backend/.env`:
```env
PROJECT_NAME=NexWealth API
API_V1_STR=/api/v1
ENVIRONMENT=development
SECRET_KEY=replace-with-a-secure-jwt-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_POSTGRES_PASSWORD
POSTGRES_DB=nexwealth

BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://localhost:5173","http://localhost:5174"]
```

### 2. Frontend Environment Setup
Create `frontend/.env.local` from the provided template:

```bash
cd frontend
cp .env.local.example .env.local
```

Verify the API URL in `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=NexWealth
NEXT_PUBLIC_DEFAULT_CURRENCY=INR
```

> ⚠️ **Important:** `.env` and `.env.local` files contain local settings and must **never** be committed to Git.

---

## 🗄️ Database Setup & Migrations

1. Ensure the PostgreSQL service is running and create the `nexwealth` database:
   ```sql
   CREATE DATABASE nexwealth;
   ```

2. Apply all Alembic schema migrations from the `backend/` directory:
   ```bash
   cd backend
   alembic upgrade head
   ```

3. *(Optional)* Seed initial demo data for local exploration:
   ```bash
   python ../database/seeds/seed.py
   ```
   *Demo Account (Local Development Only):*
   - **Email:** `demo@example.com`
   - **Password:** `Demo@12345`

---

## 🚀 Running the Application

### 1. Start Backend (FastAPI)
From the `backend/` directory:

```bash
# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```

- API Server: `http://localhost:8000`
- Interactive Swagger API Documentation: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

### 2. Start Frontend (Next.js)
From the `frontend/` directory:

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

- Application Web UI: `http://localhost:3000`

### 3. Build Frontend for Production
```bash
cd frontend
npm run build
npm run start
```

---

## 🧪 Testing & Verification

NexWealth maintains a full end-to-end regression test suite covering all API endpoints, cross-user isolation, mathematical precision, and edge cases.

To execute the test suite:
```bash
cd backend
python test_income.py
python test_expense.py
python test_transactions.py
python test_dashboard.py
python test_investments.py
python test_analytics.py
python test_profile.py
python test_notifications.py
```

### Regression Test Suite Status: **100/100 PASSED**
- `test_income.py`: 13/13 PASSED
- `test_expense.py`: 14/14 PASSED
- `test_transactions.py`: 19/19 PASSED
- `test_dashboard.py`: 18/18 PASSED
- `test_investments.py`: 10/10 PASSED
- `test_analytics.py`: 8/8 PASSED
- `test_profile.py`: 8/8 PASSED
- `test_notifications.py`: 10/10 PASSED

---

## 📜 Data Contract Single Source of Truth

The file [`NEXWEALTH_DATA_CONTRACT.md`](./NEXWEALTH_DATA_CONTRACT.md) is the single source of truth for:
1. **Monetary Convention:** Strict INR-only currency (`₹`, `INR`), decimal precision (2 decimal places), and non-negative constraints.
2. **Entity Ownership:** Every financial entity contains a foreign key `userId` extracted exclusively from the cryptographically verified JWT.
3. **Naming Standards:** camelCase JSON field keys, explicit enum values, ISO 8601 UTC timestamps.
4. **Calculations:** Standard formulas for `availableSavings`, `savingsRate`, `totalInvested`, `currentValuation`, `unrealizedGainLoss`, and `overallRoi`.

---

## 🛡️ Security Policies

- **Secret Isolation:** API keys, database passwords, and JWT secrets are loaded strictly from environment variables.
- **Zero Token Exposure:** Tokens and sensitive hashes (`passwordHash`) are excluded from all user-facing responses and profile endpoints.
- **Data Isolation:** All database queries filter strictly by `userId = current_user.id`, ensuring zero cross-tenant data leakage.
- **Client Storage:** JWT tokens are stored exclusively in temporary `sessionStorage` and cleared immediately upon logout.
