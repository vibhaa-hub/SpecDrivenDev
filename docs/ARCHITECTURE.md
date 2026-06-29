# Daily Expense App — Architecture & Feature Reference

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          BROWSER / CLIENT                           │
│                                                                     │
│   React 18 SPA  ·  Vite 8  ·  Tailwind CSS v4  ·  React Router    │
│   localhost:5173 / 5174                                             │
│                                                                     │
│   Pages: Login · Signup · Dashboard · Transactions · Categories    │
│           Tags · Savings Goals · Budgets                           │
└───────────────────────────┬─────────────────────────────────────────┘
                            │  HTTP / JSON  (Axios + JWT Bearer token)
                            │  CORS: allow_origins=[localhost:5173/5174]
┌───────────────────────────▼─────────────────────────────────────────┐
│                        FASTAPI BACKEND                              │
│                        localhost:8000                               │
│                                                                     │
│  Routers (/api/v1/*)                                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │   auth   │ │transactions│ │categories│ │   tags   │             │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │ budgets  │ │  goals   │ │analytics │ │recurring │              │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                            │
│  │ import   │ │portability│ │notifications│                         │
│  └──────────┘ └──────────┘ └──────────┘                            │
│                                                                     │
│  Middleware: CORSMiddleware · LoggingMiddleware (X-Trace-ID)        │
│  Metrics:   /metrics  (Prometheus via prometheus_fastapi_           │
│                         instrumentator)                             │
│  Health:    /actuator/health                                        │
└──────────┬──────────────────────────┬────────────────────────────── ┘
           │  SQLAlchemy ORM          │  Optional Services
    ┌──────▼──────┐          ┌────────▼────────┐  ┌────────────────┐
    │  SQLite     │          │  Redis           │  │  MinIO         │
    │  (default)  │          │  Token Blacklist │  │  Receipt Files │
    │  OR         │          │  Celery Broker   │  │  localhost:9000│
    │  PostgreSQL │          │  localhost:6379  │  └────────────────┘
    │  (prod)     │          └─────────────────┘
    └─────────────┘                    │
                              ┌────────▼────────┐
                              │  Celery Worker  │
                              │  + Beat Scheduler│
                              │  (midnight UTC) │
                              └─────────────────┘
```

---

## Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Frontend Framework** | React | 18 | SPA component model |
| **Frontend Build** | Vite | 8 | Dev server + bundler |
| **Styling** | Tailwind CSS | v4 | Utility-first CSS via `@tailwindcss/vite` plugin |
| **HTTP Client** | Axios | — | API calls + auto token attachment + 401 refresh |
| **Routing** | React Router | v6 | Client-side page navigation + `ProtectedRoute` |
| **Charts** | Recharts | — | PieChart (category breakdown) + LineChart (trends) |
| **Backend Framework** | FastAPI | — | REST API, OpenAPI docs auto-generated |
| **ORM** | SQLAlchemy | — | Database models + queries |
| **Migrations** | Alembic | — | Schema versioning |
| **Validation** | Pydantic v2 | — | Request/response schemas |
| **Auth** | python-jose (JWT) | — | HS256 tokens — 15 min access, 7 day refresh |
| **Password Hashing** | passlib + bcrypt 3.2.2 | — | Secure password storage |
| **Task Queue** | Celery + Redis | — | Async & scheduled jobs |
| **Object Storage** | MinIO | — | Receipt image uploads (S3-compatible) |
| **Metrics** | prometheus_fastapi_instrumentator | — | Exposes `/metrics` in Prometheus format |
| **Logging** | Python logging + custom middleware | — | Structured logs with `X-Trace-ID` on every request |
| **Database (dev)** | SQLite | — | Zero-setup local file `expense_db.db` |
| **Database (prod)** | PostgreSQL | — | Required for analytics (`date_trunc`) |
| **Email (dev)** | Mailpit | — | Local SMTP trap on port 1025, UI on 8025 |
| **Infrastructure** | Docker Compose | — | Postgres + Redis + MinIO + Mailpit |
| **Testing** | pytest + httpx | — | Unit + integration tests |

---

## Features & Implementation

### 1. Authentication & Security
**Technology: FastAPI · python-jose · passlib/bcrypt · Redis**

```
User ──POST /auth/register──► Create user (is_active=False by default)
     ──POST /auth/login──────► Verify password → issue JWT pair
     ──POST /auth/logout─────► Blacklist access token in Redis (TTL = remaining lifetime)
     ──POST /auth/refresh────► Exchange refresh token → new JWT pair
     ──POST /auth/forgot-password → Generate reset JWT (logged, not emailed yet)
     ──POST /auth/reset-password  → Validate reset token → update hash
```

- Access token: 15-minute expiry (HS256)
- Refresh token: 7-day expiry
- Token blacklist: Redis key with TTL — no cleanup job needed
- All protected routes use `get_current_user_email` dependency

---

### 2. Transactions
**Technology: FastAPI · SQLAlchemy · Pydantic · MinIO**

- CRUD: create, read (paginated + filtered), update, delete
- Fields: amount, date, type (Income/Expense), category, merchant, payment method (Cash/Card/UPI/Net Banking), notes, receipt image, tags, savings goal link
- Receipt upload: file stored in MinIO bucket `receipts`, UUID filename, URL saved on transaction
- Filtering: by date range, category, type, amount range, tags

---

### 3. Categories
**Technology: FastAPI · SQLAlchemy**

- User-owned categories + system-default categories (`user_id = NULL` shared across all users)
- Type: Income or Expense
- Seed script: `python -m app.seed` populates default categories

---

### 4. Tags
**Technology: FastAPI · SQLAlchemy (many-to-many)**

- User-owned tags, linked to transactions via `transaction_tags` join table
- A transaction can have multiple tags; a tag can belong to multiple transactions

---

### 5. Budgets
**Technology: FastAPI · SQLAlchemy · Celery**

- Per-category or global (no category) budget
- Periods: Weekly or Monthly
- Rollover: unspent balance carries to next period (via Celery beat task)
- Threshold alerts: auto-creates `Notification` at 80% and 100% spend

```
Transaction saved
      │
      ▼
check_budget_thresholds()
      │
      ├── Find active budgets for user/category
      ├── Sum expenses in current period
      ├── >= 80%? → Create Notification "80% reached"
      └── >= 100%? → Create Notification "Budget exceeded"
```

---

### 6. Savings Goals
**Technology: FastAPI · SQLAlchemy**

- Target amount + current amount tracking
- Transactions can be linked to a goal (increments `current_amount`)
- Progress shown as percentage on the Goals page

---

### 7. Recurring Transactions
**Technology: Celery · Celery Beat · SQLAlchemy**

- Templates define: amount, category, pattern (Daily/Weekly/Monthly/Yearly), start/end date, max occurrences
- Celery beat runs `generate_recurring_transactions` daily at midnight UTC
- Each run: finds templates with `next_occurrence_date <= now`, creates transaction, advances date, deletes expired templates

```
Celery Beat (midnight UTC)
      │
      ▼
generate_recurring_transactions()
      │
      ├── Query RecurringTemplate WHERE next_occurrence_date <= now
      ├── Create Transaction from template
      ├── Advance next_occurrence_date (+ daily/weekly/monthly/yearly)
      └── Delete template if end_date passed or max_occurrences reached
```

---

### 8. Analytics / Dashboard
**Technology: SQLAlchemy · Recharts (frontend)**

> **Note:** `get_spending_trends` uses `func.date_trunc` — PostgreSQL only. All other analytics work on SQLite.

| Endpoint | What it returns |
|---|---|
| `GET /analytics/summary` | This month's total income, total expenses, net savings, savings rate % |
| `GET /analytics/breakdown` | Per-category expense totals this month (for pie chart) |
| `GET /analytics/trends` | Monthly expense totals over last 12 months (for line chart) |
| `GET /analytics/top-categories` | Top 5 spending categories this month |

---

### 9. Data Import (CSV)
**Technology: Python csv module · FastAPI UploadFile**

- Upload a `.csv` file with columns: `amount, date, category, payment_method, description, merchant, goal, tags, notes`
- Resolves categories and goals by name; creates tags if missing
- Returns `{ success, failed, warnings[] }` per-row report

---

### 10. Data Export (Portability)
**Technology: Python zipfile · json · FastAPI StreamingResponse**

- `GET /portability/export` — downloads a `.zip` containing:
  - `profile.json` — user profile
  - `transactions.json` — all transactions
  - `categories.json` — user categories
  - `tags.json` — user tags
  - `savings_goals.json` — goals
  - `budgets.json` — budgets

---

### 11. Notifications
**Technology: FastAPI · SQLAlchemy**

- Created automatically by budget threshold checks
- `GET /notifications` — list all; `PATCH /notifications/{id}/read` — mark read

---

### 12. Observability
**Technology: prometheus_fastapi_instrumentator · Python logging**

- Every HTTP response gets a unique `X-Trace-ID` header (via `LoggingMiddleware`)
- `/metrics` exposes Prometheus counters and histograms for request count, latency, status codes
- `/actuator/health` returns `{"status": "ok"}`

---

## Database Schema (Key Relationships)

```
users
  │
  ├──► categories (user_id nullable — NULL = system default)
  ├──► tags
  ├──► budgets ──────────────────► categories (optional)
  ├──► savings_goals
  ├──► notifications
  ├──► recurring_templates ──────► categories
  │
  └──► transactions
            │
            ├──► categories
            ├──► savings_goals (optional)
            └──► tags  (via transaction_tags join table)
```

---

## Request Flow

```
Browser
  │
  │  1. Login → store access_token in localStorage
  │
  ▼
Axios interceptor (api/axios.js)
  │  - Attaches: Authorization: Bearer <access_token>
  │  - On 401: attempts POST /auth/refresh → retries original request
  │  - On refresh fail: redirects to /login
  │
  ▼
FastAPI Router
  │
  ├── get_current_user_email() dependency
  │     - Reads Bearer token
  │     - Checks Redis blacklist
  │     - Decodes JWT → returns email
  │
  ├── Service layer (business logic)
  │
  └── SQLAlchemy → SQLite (dev) / PostgreSQL (prod)
```

---

## Local Dev URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 (or 5174 if port taken) |
| Backend API | http://localhost:8000/api/v1/ |
| API Docs (Swagger) | http://localhost:8000/docs |
| Metrics | http://localhost:8000/metrics |
| Health | http://localhost:8000/actuator/health |
| MinIO Console | http://localhost:9001 |
| Mailpit (email) | http://localhost:8025 |
