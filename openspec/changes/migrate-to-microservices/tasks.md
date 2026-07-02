## 1. Shared Foundation

- [ ] 1.1 Extract JWT creation/validation from `auth_service.py` into a shared internal package (`shared/jwt_utils`) usable by every service without a network call.
- [ ] 1.2 Extract the logging middleware and trace-ID context var (`middleware/logging_middleware.py`) into the shared package so every service emits consistent structured logs and `X-Trace-ID` headers.
- [ ] 1.3 Extract a common DB session/engine helper (SQLAlchemy setup boilerplate) into the shared package, parameterized per-service by `DATABASE_URL`.
- [ ] 1.4 Build a shared Redis event bus client (publish/subscribe helper over Redis Streams) with idempotency-key support and schema-version tagging, per the `service-communication` spec.
- [ ] 1.5 Define the initial event catalog (event names, payload schemas, versions) for `transaction.created`, `transaction.updated`, `transaction.deleted`, `budget.threshold_breached`, `goal.completed`, `recurring.generated`.

## 2. Infrastructure Scaffolding

- [ ] 2.1 Restructure the repo to hold one directory per service (e.g., `services/user-service/`, `services/category-service/`, `services/transaction-service/`, `services/recurring-service/`, `services/savings-goal-service/`, `services/budget-service/`, `services/insights-service/`, `services/notification-service/`, `services/gateway/`).
- [ ] 2.2 Rewrite `docker-compose.yml` to define one container per service plus the gateway, each with its own `DATABASE_URL` pointing at a dedicated database, while keeping shared PostgreSQL, Redis, MinIO, and Mailpit containers.
- [ ] 2.3 Provision a separate database (or schema, per the interim approach in `design.md`) per service and set up a per-service Alembic migration history scoped to the tables that service owns.
- [ ] 2.4 Add per-service `Dockerfile`s and health-check endpoints (`/actuator/health`) consistent with the current monolith's convention.

## 3. Extract Notification Service

- [ ] 3.1 Move `notification_controller.py`, notification models, and notification-related service logic into `services/notification-service/`.
- [ ] 3.2 Point the Notification Service at its own database containing the `notifications` table.
- [ ] 3.3 Implement event consumers for `budget.threshold_breached`, `goal.completed`, and any other events that should trigger an in-app notification or email.
- [ ] 3.4 Migrate the weekly digest Celery task to run under the Notification Service's own Celery worker/beat.
- [ ] 3.5 Verify existing notification-center API behavior (list, mark read, mark all read) is unchanged from the client's perspective.

## 4. Extract Recurring Service

- [ ] 4.1 Move `recurring_controller.py`, `RecurringTemplate` model, and `recurring_service.py` into `services/recurring-service/`.
- [ ] 4.2 Point the Recurring Service at its own database containing the `recurring_templates` table.
- [ ] 4.3 Move the daily Celery Beat job (next-occurrence generation) to the Recurring Service's own worker/beat process.
- [ ] 4.4 Implement the Recurring Service publishing a `recurring.generated` event (or directly calling Transaction Service's create API) when a new occurrence is generated, replacing the current in-process write.
- [ ] 4.5 Implement single-occurrence vs. future-occurrences edit/delete handling against the new service boundary.

## 5. Extract Savings Goal Service

- [ ] 5.1 Move `savings_goal_controller.py`, `SavingsGoal` model, and related service logic into `services/savings-goal-service/`.
- [ ] 5.2 Point the Savings Goal Service at its own database containing the `savings_goals` table.
- [ ] 5.3 Implement the contribution endpoint calling the Transaction Service's API to log a transaction in the 'Savings' category (replacing the current in-process transaction write).
- [ ] 5.4 Implement transaction-to-goal association by having the Savings Goal Service call/consume from the Transaction Service rather than joining tables directly.
- [ ] 5.5 Implement the goal-completion check publishing a `goal.completed` event for the Notification Service to consume.

## 6. Extract Budget Service

- [ ] 6.1 Move `budget_controller.py`, `Budget` model, and `budget_service.py` into `services/budget-service/`.
- [ ] 6.2 Point the Budget Service at its own database containing the `budgets` table.
- [ ] 6.3 Implement the Budget Service consuming `transaction.created`/`transaction.updated` events to re-run threshold checks, replacing the current synchronous in-process call from expense creation.
- [ ] 6.4 Implement the Budget Service publishing a `budget.threshold_breached` event at 80% and 100% thresholds for the Notification Service to consume.
- [ ] 6.5 Implement the budget rollover engine against the new service boundary (no cross-service table joins).

## 7. Extract Category & Tag Service

- [ ] 7.1 Move `category_controller.py`, `tag_controller.py`, `Category`/`Tag` models, and related service logic into `services/category-service/`.
- [ ] 7.2 Point the Category & Tag Service at its own database containing `categories` and `tags` tables; re-run the default-category seeder against it.
- [ ] 7.3 Implement a synchronous lookup/validation API (e.g., `GET /internal/categories/{id}/exists`) for other services to validate category references, per `service-communication`.
- [ ] 7.4 Implement referential deletion safety: category deletion checks with the Transaction Service (synchronously or via a pending-deletion event handshake) before allowing delete, per `service-data-ownership`.

## 8. Extract Transaction Service

- [ ] 8.1 Move `transaction_controller.py`, `import_controller.py`, `portability_controller.py`, `Transaction`/`Tag` association tables, and `import_service.py`/`export_service.py`/`portability_service.py` into `services/transaction-service/`.
- [ ] 8.2 Point the Transaction Service at its own database containing the `transactions` and `transaction_tags` tables; configure its own MinIO client for receipt upload/download/deletion.
- [ ] 8.3 Implement synchronous `category_id` validation against the Category & Tag Service on transaction create/update, per `service-communication`.
- [ ] 8.4 Implement publication of `transaction.created`, `transaction.updated`, and `transaction.deleted` events after each successful write.
- [ ] 8.5 Update the CSV bulk import engine and data-portability exporter to call the other services' APIs (or read from local event-derived copies) instead of joining local tables for category/tag/goal names.

## 9. Extract User & Auth Service

- [ ] 9.1 Move `auth_controller.py`, `User` model, `auth_service.py`, and `token_blacklist.py` into `services/user-service/`.
- [ ] 9.2 Point the User & Auth Service at its own database containing the `users` table.
- [ ] 9.3 Publish the shared `jwt_utils` package (from Task 1.1) as the library every other service imports to verify tokens locally.
- [ ] 9.4 Verify signup, login, logout, refresh, password reset, profile update, and account deletion endpoints behave identically to the monolith version.
- [ ] 9.5 Implement account-deletion fan-out: publish a `user.deleted` event so owning services (Transaction, Budget, Savings Goal, etc.) purge that user's rows instead of relying on in-process cascading deletes.

## 10. Extract Insights Service (Analytics + Reporting)

- [ ] 10.1 Move `analytics_controller.py`, `analytics_service.py`, and `reporting_service.py` into `services/insights-service/`.
- [ ] 10.2 Point the Insights Service at its own database holding a read-optimized local copy of the transaction/category/budget fields it needs (per `service-data-ownership`).
- [ ] 10.3 Implement event consumers (`transaction.created`, `transaction.updated`, `transaction.deleted`) that keep the local read copy up to date.
- [ ] 10.4 Rework `date_trunc`-based analytics queries (currently PostgreSQL-specific) against the Insights Service's own database.
- [ ] 10.5 Verify dashboard summaries, category breakdowns, trends, top-5 categories, and PDF/CSV report generation match the monolith's output.

## 11. API Gateway

- [ ] 11.1 Scaffold the gateway service (`services/gateway/`) with route-to-service mapping for every existing `/api/v1/*` prefix.
- [ ] 11.2 Implement request forwarding that preserves method, headers (including `Authorization`), query params, and body, per the `api-gateway` spec.
- [ ] 11.3 Implement CORS enforcement at the gateway and remove per-service CORS configuration.
- [ ] 11.4 Implement bounded timeouts and 502/503 handling for unreachable backend services.
- [ ] 11.5 Mount Prometheus metrics and the `/actuator/health` check on the gateway, aggregating or forwarding to per-service health checks as needed.

## 12. Cutover and Verification

- [ ] 12.1 Update `frontend/src/api/axios.js` base URL to point at the API Gateway.
- [ ] 12.2 Run the existing Pytest suite against each service in isolation, updating tests that relied on in-process cross-capability calls to instead mock the new synchronous/event boundaries.
- [ ] 12.3 Write contract tests for each synchronous inter-service REST endpoint and each published/consumed event schema.
- [ ] 12.4 Run an end-to-end smoke test through the gateway covering signup → login → create category → create transaction → budget threshold notification → dashboard summary, confirming behavior matches the monolith.
- [ ] 12.5 Confirm the old monolith `docker-compose` target still runs standalone as a rollback path, and document the cutover/rollback steps.
