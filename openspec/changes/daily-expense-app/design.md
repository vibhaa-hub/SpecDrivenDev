## Context

This project involves building a "Daily Expense Application" from scratch. The system must handle transactional data, user privacy, automated scheduling, and reporting. The core constraints include high security (JWT, BCrypt), data portability, and adherence to specific API and logging standards.

## Goals / Non-Goals

**Goals:**
- Implement a full-stack solution with a Python backend and React frontend.
- Provide secure user authentication and lifecycle management.
- Automate recurring transactions and budget alerts.
- Support file uploads (receipts) and data exports (CSV/PDF).
- Ensure high code quality with separate layers (Controller/Service/Repository).

**Non-Goals:**
- Multi-currency conversion (only preferred currency is stored).
- Social features (no sharing between users).
- Mobile native application (responsive web only).

## Decisions

### 1. Technology Stack
- **Backend**: **Python 3.11+ with FastAPI**.
  - *Rationale*: FastAPI provides high performance, automatic OpenAPI documentation, and native asynchronous support which is beneficial for handle I/O bound tasks like file uploads and external email sending.
  - *Alternatives*: Django (too heavy for this micro-service style), Flask (lacks native async and robust validation compared to FastAPI).
- **Frontend**: **React 18 with TypeScript**.
  - *Rationale*: Industry standard for build complex SPAs; TypeScript ensures type safety as requested.
- **Database**: **PostgreSQL**.
  - *Rationale*: Robust relational database needed for ACID transactions and complex joins between expenses, categories, and goals.
- **Task Queue**: **Celery with Redis**.
  - *Rationale*: Necessary for processing recurring transaction templates, sending budget alerts, and generating large reports without blocking the main API threads.

### 2. Authentication & Security
- **Mechanism**: JWT (Access + Rotating Refresh Tokens).
  - Access token: 15 min expiry.
  - Refresh token: 7 day expiry with rotation.
- **Password Hashing**: BCrypt with cost factor 12.
- **Authorization**: Ownership checks at the service layer to ensure users can only access their own records (returning 403 Forbidden on violation).

### 3. File Storage
- **System**: **MinIO**.
  - *Rationale*: S3-compatible local storage for receipt images, ensuring scalability and easy migration to AWS S3 if needed.
  - *Validation*: Strict MIME type (JPEG/PNG/WEBP) and size (5MB) checks on the server side.

### 4. Code Architecture
- **Layered Pattern**: Controller (API endpoints) → Service (Business Logic) → Repository (SQLAlchemy models/queries).
- **Validation**: Pydantic models for request/response DTOs.
- **Logging**: Custom middleware to inject a `traceId` (UUID) into the request context, ensuring it appears in all log lines (MDC equivalent in Python).

## Risks / Trade-offs

- **[Risk]**: Managing recurring transaction drift or missed runs.
  - **Mitigation**: Use Celery Beat with a persistent schedule and idempotent generation logic that checks for existing records before creating new ones.
- **[Risk]**: Handling large CSV/PDF exports in memory.
  - **Mitigation**: Use streaming responses and chunked database queries (pagination) to keep memory footprint low.
- **[Risk]**: Frontend token expiration during active usage.
  - **Mitigation**: Axios interceptors will handle transparent token refresh logic to avoid user logout while the app is in use.
- **[Risk]**: SMTP or MinIO availability affecting core flows.
  - **Mitigation**: Decouple email sending via the task queue; allow receipt uploads to fail gracefully or retry.
