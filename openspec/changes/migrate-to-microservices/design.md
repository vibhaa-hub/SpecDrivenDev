## Context

The backend today is a single FastAPI process (`backend/app/`) with one SQLAlchemy engine/database, one Alembic migration history, and one Celery app. Nine business capabilities (user-management, categories-tags, transaction-management, recurring-transactions, savings-goals, budgeting-engine, dashboard-analytics, reporting-service, notification-service) live as controller/service pairs inside that process. Cross-capability behavior currently happens via in-process function calls and shared SQLAlchemy sessions — e.g., expense creation directly calls `budget_service` threshold logic in the same transaction, and `analytics_service` joins across `transactions`, `categories`, and `budgets` tables directly.

Constraints:
- Same JWT scheme (HS256, 15-min access / 7-day refresh) and `SECRET_KEY` must keep working across whatever comes out of the split — no forced re-login for existing users.
- Frontend (`frontend/src/api/axios.js`) must keep calling `/api/v1/*` with the same request/response shapes; the gateway absorbs the routing change.
- Existing infra (PostgreSQL, Redis, MinIO, Mailpit) stays; no new infra platform (e.g. Kubernetes) is being introduced by this change.
- The nine capabilities already map to `services/*_service.py` modules fairly cleanly — that mapping is the basis for service boundaries rather than inventing new ones.

## Goals / Non-Goals

**Goals:**
- Decompose the monolith into independently deployable services along the existing domain boundaries so each can be built, deployed, and scaled on its own.
- Give each service its own database/schema and remove direct cross-service SQL access.
- Define clear synchronous (REST) and asynchronous (event) contracts for the interactions that today are in-process calls.
- Preserve the current public API contract (`/api/v1/*` paths, request/response bodies) so the frontend needs only a base-URL change.
- Keep JWT-based auth working without every service needing a network round-trip to the Auth service for every request.

**Non-Goals:**
- Choosing or introducing a specific orchestration platform (Kubernetes, ECS, etc.) — services are containerized via docker-compose for this change; orchestration platform choice is a follow-up.
- Changing any user-facing behavior, UI, or API response shape.
- Introducing a service mesh, distributed tracing backend, or API versioning scheme beyond what already exists (trace-ID middleware carries over per-service).
- Splitting further than the nine existing capabilities (e.g., no per-entity microservices within a capability).

## Decisions

**Service boundaries mirror existing capabilities, with two merges.**
Eight services: User & Auth, Category & Tag, Transaction, Recurring, Savings Goal, Budget, Insights (merges dashboard-analytics + reporting-service, since both are read-only aggregations over transaction data and would otherwise duplicate the same read paths), and Notification.
Alternative considered: one service per capability (9 services). Rejected for now — dashboard-analytics and reporting-service have near-identical data dependencies (transactions, categories, budgets) and splitting them would just duplicate the same cross-service read calls twice for no isolation benefit.

**API Gateway as a thin reverse proxy, not a BFF.**
The gateway's job is routing + auth-header pass-through + CORS; it does not aggregate or transform responses. Each route maps 1:1 to a backend service (e.g., `/api/v1/transactions/*` → Transaction Service). This keeps the gateway simple and avoids it becoming a second monolith.
Alternative considered: Backend-for-Frontend that composes responses from multiple services (e.g., a single dashboard endpoint calling Transaction + Budget + Insights). Rejected for this change to keep the gateway stateless and cacheable; composition, if needed, stays in the frontend or a dedicated Insights Service call.

**Database-per-service with synchronous lookups for referential data, events for side effects.**
- Referential lookups where a service needs to validate a foreign reference it doesn't own (e.g., Transaction Service validating `category_id` against Category Service) are synchronous REST calls with short timeouts and a local cache (few-minute TTL) to avoid chatty calls on every write.
- Side effects that fan out (transaction created → budget threshold check → notification) are asynchronous events published to Redis Streams, consumed by the owning service. This mirrors the existing Celery/Redis broker so no new infra is added.
Alternative considered: keep a shared database with per-service schemas (schema-per-service, same Postgres instance) instead of full database-per-service. Rejected because it still allows accidental cross-schema joins and doesn't force the API/event discipline this migration is meant to establish; the design doc's `service-data-ownership` capability documents the schema-per-service databases used to start (same Postgres instance, separate database per service), with full physical separation as a later, non-blocking step.

**JWT validation via a shared library, not a per-request Auth service call.**
Each service verifies JWTs locally using the shared `SECRET_KEY` and a common `jwt_utils` package (extracted from today's `auth_service.py`). This avoids making every authenticated request depend on the Auth service being up.
Alternative considered: gateway validates JWTs once and forwards a trusted internal header. Rejected as the sole mechanism — services should stay independently securable (e.g., callable directly in tests, or if the gateway is bypassed internally) — but the gateway MAY still short-circuit obviously invalid tokens as an optimization.

**Celery split per owning service.**
Recurring Service keeps the daily Celery Beat job for generating occurrences. Insights Service keeps the weekly digest Celery task. Notification Service owns dispatch. Each service runs its own worker process against the same Redis broker (different queues/routing keys per service to avoid cross-service task pickup).

## Risks / Trade-offs

- [Distributed transactions] Actions that used to be one DB transaction (e.g., create expense + check budget threshold + write notification) become multiple network calls/events, opening a window for partial failure (expense saved, threshold check lost). → Mitigation: budget/notification side effects move to at-least-once event consumption with idempotent handlers keyed on transaction ID, not a synchronous multi-service transaction.
- [Referential integrity across databases] Foreign keys like `transactions.category_id` can no longer be enforced by the database once Category and Transaction split databases. → Mitigation: Transaction Service validates `category_id` synchronously at write time via the Category Service API; accepts eventual-consistency risk if a category is deleted concurrently (soft-delete/prevent-delete-if-referenced logic already exists per `categories-tags` spec and moves to the Category Service).
- [Increased operational complexity] Eight services + gateway + Redis + eight databases is materially harder to run locally and debug than one process. → Mitigation: docker-compose remains the single `docker-compose up -d` entrypoint for all services in dev; trace-ID middleware carries over so a single request can be followed across service logs.
- [N+1 network calls in read-heavy paths] Insights Service aggregating a dashboard may need data from Transaction, Category, and Budget services. → Mitigation: Insights Service maintains its own read-optimized local copies of the fields it needs (populated via events), rather than calling out synchronously on every dashboard load.
- [Latency] Synchronous inter-service calls add network round-trips where in-process calls used to be instant. → Mitigation: short timeouts, local caching of rarely-changing reference data (categories, tags), and preferring events over synchronous calls wherever the caller doesn't need an immediate answer.

## Migration Plan

1. Extract shared code first (JWT/auth verification, DB session helpers, logging middleware, trace-ID context) into a shared internal package used by all services, without moving any business logic yet.
2. Stand up services one at a time, starting with the ones fewest other capabilities depend on (Notification, then Recurring, Savings Goal, Budget), and finishing with the ones most depended-on (Category & Tag, Transaction, User & Auth) so downstream services can validate against real APIs sooner.
3. For each service: move its models/schemas/controllers/service code into the new service directory, point it at its own database, generate a fresh Alembic history scoped to its tables, and add the synchronous/event integration points defined by `service-communication`.
4. Stand up the API Gateway last, once all services expose their `/api/v1/*` routes, and cut the frontend over to the gateway's base URL.
5. Run the existing Pytest suites per-service against the new boundaries; add contract tests for the synchronous REST calls and event schemas.
6. Rollback strategy: keep the monolith deployable in parallel (feature-flag-free — it's just the old `docker-compose` target) until the gateway + all services pass the existing test suite end-to-end; cut over by switching the frontend's API base URL, which is a single-line, instantly revertible change.

## Open Questions

- Should Category & Tag data be replicated into Transaction/Budget/Insights services via events (local read copies) instead of synchronous lookups, to reduce inter-service latency? Leaning yes for Insights, undecided for Transaction's write-path validation.
- Does Notification Service need its own database, or can it stay stateless (reading in-app notifications from an events-derived read model owned by each source service)? Current proposal gives it a database for the notification center list; may be revisited.
- What's the target for full physical database separation (separate Postgres instances/hosts) vs. the interim schema-per-service-same-instance state described in `service-data-ownership`?
