## 1. Project Setup and Infrastructure

- [x] 1.1 Scaffold the FastAPI backend with structured directories (app/controllers, app/services, app/repositories, app/models, app/schemas).
- [x] 1.2 Initialize the React TypeScript frontend using Vite, configuring Tailwind CSS, Axios, and React Router.
- [x] 1.3 Create a docker-compose.yml file configuring PostgreSQL, Redis, MinIO, and a mock SMTP mailer (e.g., Mailpit).
- [x] 1.4 Set up Alembic on the backend for database migrations.
- [x] 1.5 Configure custom Python logging middleware to inject a unique `traceId` context var (MDC equivalent) into every request and log line.

## 2. Database Models and Migrations

- [x] 2.1 Create the User database model and migrations (including fields for verification, timezone, preferred currency, and timestamps).
- [x] 2.2 Create Category and Tag database models and migrations (with Category types: Expense, Income, Both).
- [x] 2.3 Create Transaction (Expenses and Income) models and migrations, including payment method, merchant, notes, and receipt URL.
- [x] 2.4 Create SavingsGoal and Budget models with active/paused statuses, rollover options, and period definitions.
- [x] 2.5 Create RecurringTemplate and Notification models with schema definitions.
- [x] 2.6 Implement base SQL repository layer or SQLAlchemy session helpers with transactional write wrapper.


## 3. User Management and Authentication

- [x] 3.1 Implement password hashing using BCrypt with a cost factor of 12.
- [x] 3.2 Build the signup API endpoint, including the dispatch of a verification email containing an expiring token.
- [x] 3.3 Build JWT token generation, verification, and rotation logic (15-min access token, rotating 7-day refresh token).
- [x] 3.4 Build login, logout (token invalidation), and password reset request/confirm API endpoints.
- [x] 3.5 Create profile update (name, currency, timezone), password change, and permanent account deletion endpoints (purges all linked rows).
- [x] 3.6 Implement client-side Auth forms, global React Auth context, and Axios interceptor for transparent JWT refresh.

## 4. Categories and Tags Management

- [x] 4.1 Create database seeder to populate immutable default categories (Food, Transport, Housing, etc.).
- [x] 4.2 Build custom category CRUD APIs with validation (name, icon, color, type constraints) and prevent deletion if linked to transactions.
- [x] 4.3 Build tag CRUD APIs allowing users to manage custom personal tags.
- [x] 4.4 Build React UI components for adding/editing categories and managing tags.

## 5. Core Transaction Management (Expenses and Income)

- [x] 5.1 Implement Expense CRUD API endpoints with Pydantic request body validation.
- [x] 5.2 Implement Income CRUD API endpoints.
- [x] 5.3 Configure MinIO client on the backend and build receipt upload, download, and deletion endpoints (validate images <5MB, JPEG/PNG/WEBP only).
- [x] 5.4 Develop CSV transaction bulk import engine with validation and warning dispatch for mismatched goals.
- [x] 5.5 Develop CSV transaction exporter with date filters.
- [x] 5.6 Create full user data portability exporter generating a single ZIP file containing JSON files of all user tables.
- [x] 5.7 Create transaction list React screen (featuring pagination, sorting, filters) and creation forms with receipt drag-and-drop.

## 6. Automation and Recurring Engine

- [x] 6.1 Set up Celery worker and Celery Beat scheduler in the backend environment.
- [x] 6.2 Build API endpoints to manage active recurring templates for expenses and income.
- [x] 6.3 Implement a scheduled Celery task running daily to generate the next instances of scheduled templates.
- [x] 6.4 Build single-occurrence vs. future-occurrences editing/deletion handler logic on the backend.
- [ ] 6.5 Add recurring settings to the React transaction form and list templates.

## 7. Savings Goals

- [x] 7.1 Build SavingsGoal CRUD APIs including calculations (remaining amount, progress percentage, completion projections).
- [x] 7.2 Implement primary contribution endpoint (automatically logs a transaction in 'Savings' category behind the scenes).
- [x] 7.3 Implement secondary association logic to link existing transactions to a goal and update totals.
- [x] 7.4 Implement automatic 'Completed' state change triggering an in-app notification when target amount is reached.
- [x] 7.5 Design goal progress dashboard and contribution timeline React components.

## 8. Budgeting Engine

- [x] 8.1 Build Budget CRUD APIs supporting weekly/monthly category or overall budgets.
- [x] 8.2 Build budget rollover engine to carry forward unspent balances to the next period.
- [x] 8.3 Implement threshold checking logic triggered on every expense creation/modification.
- [x] 8.4 Implement notification trigger for 80% and 100% budget breaches (dispatching one in-app alert and email per threshold per period).
- [x] 8.5 Build active budget progress bars and rollover settings in the React frontend.

## 9. Dashboard, Analytics, and Reports

- [x] 9.1 Build analytical API endpoints providing spending summaries, category breakdowns (donut charts), 12m trends, and top 5 categories.
- [x] 9.2 Build Report generation service for Monthly, Yearly, and Custom reports with PDF and CSV export formats.
- [x] 9.3 Build notification center APIs (retrieve list, mark read, mark all read).
- [x] 9.4 Create background weekly digest mailer Celery task (running every Monday, opt-in).
- [x] 9.5 Create React dashboards with Chart.js or Recharts, a Reports viewer, and a global notification dropdown.

## 10. Testing, Verification, and Observability

- [x] 10.1 Write Pytest unit tests for all core business services (mocking database repositories).
- [ ] 10.2 Write integration tests utilizing Testcontainers-python for API testing against spin-up PostgreSQL and MinIO databases.
- [x] 10.3 Implement `/health` and Prometheus metrics endpoints on the backend.
- [ ] 10.4 Run full backend test suite and compile coverage reports.
- [x] 10.5 Verify frontend forms client-side validations and run a localized mock integration build.

