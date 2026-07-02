# README.md


## Project Overview

This is a **Daily Expense Application** — a personal finance tracker built as a full-stack monorepo. The backend is a FastAPI + SQLAlchemy REST API; the frontend is a React SPA built with Vite. Infrastructure services (PostgreSQL, Redis, MinIO, Mailpit) are defined in `docker-compose.yml`.

## Commands

### Backend (run from `backend/` directory)

```bash
# Start the API server
uvicorn app.main:app --reload

# Run all tests
pytest

# Run a single test file
pytest tests/test_auth.py

# Run database migrations
alembic upgrade head

# Generate a new migration after model changes
alembic revision --autogenerate -m "description"

# Seed default categories
python -m app.seed

# Start Celery worker (requires Redis)
celery -A app.celery_app worker --loglevel=info

# Start Celery beat scheduler
celery -A app.celery_app beat --loglevel=info
```

### Frontend (run from `frontend/` directory)

```bash
npm install
npm run dev       # Start dev server at http://localhost:5173
npm run build     # Production build
npm run lint      # ESLint
npm run preview   # Preview production build
```

### Infrastructure

```bash
docker-compose up -d   # Start PostgreSQL (5432), Redis, MinIO (9000/9001), Mailpit (8025/1025)
```

## Architecture

### Backend (`backend/app/`)

Layered architecture with clear separation:

- **`main.py`** — FastAPI app entry point; registers all routers under `/api/v1/` and mounts Prometheus metrics at `/metrics`. Health check at `/actuator/health`.
- **`database.py`** — SQLAlchemy engine; defaults to SQLite (`expense_db.db`) locally, switches to PostgreSQL via `DATABASE_URL` env var.
- **`controllers/`** — FastAPI routers (one file per resource). Auth dependency `get_current_user_email` lives in `auth_controller.py` and is imported by all other controllers.
- **`services/`** — Business logic. Notable services:
  - `auth_service.py` — JWT creation/validation (HS256, 15-min access tokens, 7-day refresh tokens)
  - `token_blacklist.py` — Redis-backed token invalidation for logout
  - `minio_service.py` — Receipt image upload/retrieval via MinIO
  - `recurring_service.py` — Generates next occurrences for recurring templates (scheduled via Celery beat at midnight UTC)
  - `analytics_service.py` — Monthly summaries, category breakdowns, spending trends
  - `portability_service.py` — Full data export as a ZIP of JSON files
  - `import_service.py` — Bulk CSV import for transactions
- **`models/`** — SQLAlchemy ORM models. `Transaction` is the central entity, linked to `User`, `Category`, `SavingsGoal`, and `Tag` (many-to-many via `transaction_tags` join table).
- **`schemas/`** — Pydantic request/response models.
- **`repositories/base_repository.py`** — Generic CRUD base class (not used everywhere; controllers often query SQLAlchemy directly).
- **`middleware/logging_middleware.py`** — Adds `X-Trace-ID` header to every response and structured log output with trace context.
- **`celery_app.py`** — Celery configuration with Redis as broker/backend. Beat schedule runs `recurring_service.generate_recurring_transactions` daily.

### Frontend (`frontend/src/`)

- **`api/axios.js`** — Axios instance with base URL `http://localhost:8000/api/v1`. Interceptors auto-attach Bearer tokens and handle 401s by attempting a token refresh before redirecting to `/login`.
- **`context/AuthContext.jsx`** — React context for auth state; tokens are stored in `localStorage`.
- **`App.jsx`** — Router with `ProtectedRoute` wrapper that checks `AuthContext` before rendering. All protected routes are wrapped in `<Layout>`.
- **`pages/`** — One page component per domain (Dashboard, Transactions, Categories, Tags, Goals, Budgets).
- **`components/Layout.jsx`** — Shell shared by all authenticated pages.

### Database Schema

Key relationships:
- `users` → owns `categories`, `tags`, `transactions`, `budgets`, `savings_goals`, `notifications`, `recurring_templates`
- `transactions` → belongs to `category`, optionally linked to `savings_goal`; many-to-many with `tags` via `transaction_tags`
- `categories.user_id` is nullable — `NULL` means a system-default category shared across all users
- `budgets` can be global (no `category_id`) or per-category

### Environment Variables

| Variable | Default | Purpose |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./expense_db.db` | SQLAlchemy connection string |
| `SECRET_KEY` | `super-secret-key-for-dev-only` | JWT signing key |
| `REDIS_URL` | `redis://localhost:6379/0` | Celery broker/backend |
| `REDIS_HOST` / `REDIS_PORT` | `localhost` / `6379` | Token blacklist Redis |
| `MINIO_ENDPOINT` | `localhost:9000` | MinIO for receipt storage |
| `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` | `minioadmin` | MinIO credentials |

### Key Design Decisions

- The backend must be started from the `backend/` directory (or with `backend/` on `sys.path`) because `main.py` explicitly appends it to `sys.path` at startup.
- Token blacklisting uses Redis TTL matching the JWT's remaining lifetime — no cleanup job needed.
- `date_trunc` in `analytics_service.py` is PostgreSQL-specific; these queries will fail on SQLite.
- Receipt bucket name is hardcoded as `"receipts"` in `minio_service.py`.
