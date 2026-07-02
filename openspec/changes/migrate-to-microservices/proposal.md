## Why

The backend is a single FastAPI process ("modular monolith") covering nine distinct business capabilities (auth, categories/tags, transactions, recurring, savings goals, budgets, analytics, reporting, notifications) behind one deployment, one database, and one scaling unit. As usage grows, this couples unrelated capabilities together: a spike in analytics/report generation competes for the same process resources as transaction writes, a bug in one controller can take down the whole API, and every deploy ships all nine capabilities at once even when only one changed. The `services/` layer already reflects clean domain boundaries, making this a natural point to decompose into independently deployable microservices before the codebase grows further and the split becomes harder.

## What Changes

- Decompose `backend/app` into independently deployable services along the existing domain boundaries:
  - **User & Auth Service** (`user-management`) — signup, login, JWT issuance/refresh, password reset, profile, account deletion.
  - **Category & Tag Service** (`categories-tags`) — default/custom categories, tags.
  - **Transaction Service** (`transaction-management`) — expenses, income, receipts (MinIO), CSV import/export, data portability export.
  - **Recurring Service** (`recurring-transactions`) — recurring templates, Celery Beat generation of next occurrences.
  - **Savings Goal Service** (`savings-goals`) — goals, contributions, goal-transaction linking.
  - **Budget Service** (`budgeting-engine`) — budgets, rollover, threshold checks.
  - **Insights Service** (`dashboard-analytics` + `reporting-service`) — dashboard summaries, trends, PDF/CSV report generation.
  - **Notification Service** (`notification-service`) — in-app notification center, email digests, alert dispatch.
- Introduce an **API Gateway** as the single entry point the frontend talks to at `/api/v1/*`, replacing direct calls into the monolith. The gateway forwards requests to the owning service and preserves the current public API contract so the frontend requires no functional changes beyond its base URL.
- **BREAKING**: Each service gets its own database/schema. Cross-domain data access that today happens via direct SQLAlchemy joins (e.g., a transaction query joining `categories`, budget threshold checks reading `transactions`) must move to synchronous service-to-service API calls or asynchronous events — no more shared database.
- Introduce inter-service communication:
  - Synchronous REST calls for request/response lookups a service needs from another (e.g., Transaction Service validating a `category_id` with the Category Service).
  - Asynchronous events (via Redis, reusing the existing broker) for side effects that fan out across services (e.g., transaction created → Budget Service re-checks thresholds → Notification Service sends an alert; goal completed → Notification Service).
- JWT validation becomes a shared library each service applies independently (same HS256 `SECRET_KEY`, same 15-min/7-day token lifetimes) so no service depends on a synchronous call to Auth just to authenticate a request.
- Celery workers/beat split per service that owns background jobs (Recurring Service, Insights Service for digest emails, Notification Service).
- **BREAKING**: `docker-compose.yml` is restructured to define one container per service plus the API Gateway, instead of a single `backend` container.

## Capabilities

### New Capabilities
- `api-gateway`: Routes incoming `/api/v1/*` requests to the owning backend service, forwards auth headers, preserves CORS and the existing public contract.
- `service-communication`: Contracts and conventions for synchronous inter-service REST calls and asynchronous event publish/consume between services.
- `service-data-ownership`: Each service owns an isolated database/schema; documents which service is authoritative for each entity and how other services obtain that data (API call vs. event-driven local copy).

### Modified Capabilities
(none — existing capability requirements are unchanged; this change is architectural/deployment-level. The runtime topology behind each capability changes, not its behavior.)

## Impact

- **Affected code**: `backend/app/` is restructured from one FastAPI app into one FastAPI app per service (e.g., `services/user-service/`, `services/transaction-service/`, ...), each with its own `main.py`, models, and Alembic migrations scoped to the tables it owns.
- **Frontend**: `frontend/src/api/axios.js` base URL points at the API Gateway instead of the monolith; no other frontend changes required if the gateway preserves the current response shapes.
- **Infrastructure**: `docker-compose.yml` rewritten for multiple service containers plus a gateway container; Redis is reused as both the event bus and the Celery broker; each service gets its own PostgreSQL database/schema.
- **Auth**: `SECRET_KEY` and token semantics are shared across services via a common library/package rather than a single in-process dependency.
- **Out of scope for this change**: introducing Kubernetes or any specific orchestration platform, and changing any user-facing API behavior or contract.
