# Requirements → OpenAPI Spec Transformation & Implementation Coverage

---

## Part 1: How FastAPI Generates the OpenAPI Spec

FastAPI derives the entire OpenAPI 3.1 spec automatically at startup — no manual YAML/JSON is written. The pipeline is:

```
Python Code                          OpenAPI 3.1 JSON
────────────────────────────────     ──────────────────────────────────
@router.post("/login")           ──► paths["/api/v1/auth/login"]["post"]
  status_code=201                ──► responses["201"]
  response_model=Token           ──► responses["201"]["schema"] → $ref Token
  tags=["auth"]                  ──► tags: ["auth"]  (Swagger grouping)

class UserLogin(BaseModel):      ──► components/schemas/UserLogin
  email: EmailStr                ──►   {type: string, format: email}
  password: str                  ──►   {type: string}

class BudgetCreate(BaseModel):
  amount: float (Field gt=0))    ──►   {type: number, exclusiveMinimum: 0}
  period: BudgetPeriod           ──►   $ref BudgetPeriod

class BudgetPeriod(str, Enum):   ──► components/schemas/BudgetPeriod
  WEEKLY = "Weekly"              ──►   {type: string, enum: ["Weekly","Monthly"]}
  MONTHLY = "Monthly"

Optional[datetime]               ──►   anyOf: [{type: string, format: date-time},
                                              {type: null}]

UploadFile = File(...)           ──►   requestBody: multipart/form-data
                                        contentMediaType: application/octet-stream

Depends(get_current_user_email)  ──►   (consumed internally, not in spec params)
  ↑ reads Bearer token header         but SecurityScheme could be declared separately

query param: skip: int = 0       ──►   parameters: [{in: query, name: skip,
                                                       schema: {type: integer, default: 0}}]
```

### What gets generated automatically

| Source in code | Generated in spec |
|---|---|
| `@router.get/post/patch/delete(path)` | `paths[prefix+path][method]` |
| `include_router(prefix="/api/v1/auth")` | Route prefix merged into all paths |
| Pydantic `BaseModel` subclass | `components/schemas/<ClassName>` |
| `str / int / float / bool` fields | `type: string/integer/number/boolean` |
| `Optional[X]` or `X \| None` | `anyOf: [{type: X}, {type: null}]` |
| `EmailStr` | `{type: string, format: email}` |
| `datetime` | `{type: string, format: date-time}` |
| `Enum(str, Enum)` | `{type: string, enum: [...values]}` |
| `Field(gt=0)` | `exclusiveMinimum: 0` |
| `response_model=SomeSchema` | `responses.200.content.application/json.schema.$ref` |
| `status_code=201` | `responses.201` key (not 200) |
| `status_code=204` | `responses.204` with no body |
| `tags=["name"]` | Groups routes in Swagger UI sidebar |
| `UploadFile` | `multipart/form-data` with binary content |

### Spec endpoint: `http://localhost:8000/openapi.json`
### Swagger UI: `http://localhost:8000/docs`
### ReDoc UI: `http://localhost:8000/redoc`

---

## Part 2: OpenAPI Spec — What Was Generated

### Endpoint Count (from live spec)

| Domain | Endpoints | HTTP Methods |
|---|---|---|
| Auth | 9 routes | POST ×8, PATCH ×1, DELETE ×1 |
| Categories | 3 routes | GET, POST, PATCH, DELETE |
| Tags | 3 routes | GET, POST, PATCH, DELETE |
| Transactions | 5 routes | GET ×3, POST ×2, PATCH, DELETE ×2 |
| Import | 1 route | POST |
| Portability | 1 route | GET |
| Recurring | 4 routes | GET, POST, PATCH, DELETE ×2 |
| Savings Goals | 5 routes | GET ×2, POST ×3, PATCH, DELETE |
| Budgets | 3 routes | GET ×2, POST, PATCH, DELETE |
| Analytics | 4 routes | GET ×4 |
| Notifications | 3 routes | GET, PATCH ×2 |
| System | 2 routes | GET ×2 (`/metrics`, `/actuator/health`) |
| **Total** | **47 routes** | **~53 HTTP operations** |

### Schema Count (Pydantic → OpenAPI components)

| Category | Schemas |
|---|---|
| Auth | UserCreate, UserLogin, UserResponse, UserUpdate, PasswordResetRequest, PasswordResetConfirm, PasswordChange, Token |
| Categories | CategoryCreate, CategoryUpdate, CategoryResponse, CategoryType (enum) |
| Tags | TagCreate, TagUpdate, TagResponse |
| Transactions | TransactionCreate, TransactionUpdate, TransactionResponse, TransactionType (enum), PaymentMethod (enum) |
| Recurring | RecurringCreate, RecurringUpdate, RecurringResponse, RecurrencePattern (enum) |
| Goals | SavingsGoalCreate, SavingsGoalUpdate, SavingsGoalResponse, GoalStatus (enum) |
| Budgets | BudgetCreate, BudgetUpdate, BudgetResponse, BudgetPeriod (enum) |
| System | HTTPValidationError, ValidationError |
| **Total** | **~34 schemas** |

---

## Part 3: Requirements Implementation Coverage

Legend: ✅ Implemented · ⚠️ Partial · ❌ Not implemented

---

### 1.1 User Management

| Requirement | Status | Notes |
|---|---|---|
| Register with full_name, email, password | ✅ | `POST /auth/register` → `UserCreate` schema |
| Send verification email; account inactive until verified | ❌ | `is_active=False` set but no email is sent; Mailpit wired in docker-compose but SMTP not called |
| Login with email + password | ✅ | `POST /auth/login` → `UserLogin` schema (fixed to remove `full_name`) |
| Logout — invalidate session | ✅ | `POST /auth/logout` → blacklists token in Redis with TTL |
| Password reset via time-limited email link | ⚠️ | Endpoint exists, reset JWT generated and **logged** — email not sent |
| Update profile (name, currency, timezone) | ✅ | `PATCH /auth/profile` → `UserUpdate` |
| Change password (requires current password) | ✅ | `POST /auth/change-password` |
| Delete account + all data | ✅ | `DELETE /auth/account` — deletes user row (cascade removes linked data) |
| Export all data as downloadable file | ✅ | `GET /portability/export-all` → ZIP of 6 JSON files |

**Score: 7/9 = 78%**

---

### 1.2 Categories

| Requirement | Status | Notes |
|---|---|---|
| Default categories available to all users | ✅ | `user_id=NULL` rows; `python -m app.seed` populates them |
| Create custom category with name, icon, color | ✅ | `POST /categories/` → `CategoryCreate` |
| Edit / delete custom categories | ✅ | `PATCH` + `DELETE /categories/{id}` |
| Category typed (Expense / Income / Both) | ✅ | `CategoryType` enum on schema and model |
| Prevent deletion if transactions exist | ❌ | No guard — delete succeeds even with linked transactions |

**Score: 4/5 = 80%**

---

### 1.3 Expense / Transaction Management

| Requirement | Status | Notes |
|---|---|---|
| Add transaction: amount, date, category, description, payment method, merchant, receipt, tags, goal, notes | ✅ | All fields in `TransactionCreate` schema |
| Payment method enum: Cash/Credit Card/Debit Card/UPI/Net Banking/Other | ✅ | `PaymentMethod` enum |
| Paginated + filterable list | ⚠️ | `skip/limit` pagination works; filters: date range ✅, category ✅ — missing: payment method, tag, savings goal filters |
| Sortable list (date, amount) | ❌ | No `sort_by` / `order` query param |
| Edit any field of a transaction | ✅ | `PATCH /transactions/{id}` → `TransactionUpdate` |
| Delete transaction | ✅ | `DELETE /transactions/{id}` 204 |
| Goal contribution update when edit/delete | ❌ | `goal_id` updated on transaction but `SavingsGoal.current_amount` not recalculated on edit/delete |
| Upload receipt image (post-creation) | ✅ | `POST /transactions/{id}/receipt` — validates JPEG/PNG/WEBP, 5MB limit, stores in MinIO |
| View / download receipt | ⚠️ | `receipt_url` returned in response; no dedicated proxy/presigned URL endpoint |
| Delete receipt | ✅ | `DELETE /transactions/{id}/receipt` — removes from MinIO + clears DB field |
| Bulk CSV import with per-row error reporting | ✅ | `POST /import/import-csv` → returns `{success, failed, warnings[]}` |
| Export expenses as CSV | ✅ | `GET /transactions/export?start_date=&end_date=` → `text/csv` streaming response |

**Score: 8/12 = 67%**

---

### 1.4 Recurring Transactions

| Requirement | Status | Notes |
|---|---|---|
| Mark transaction as recurring with pattern (Daily/Weekly/Monthly/Yearly) | ✅ | `POST /recurring/` → `RecurringCreate` with `RecurrencePattern` enum |
| End date or max occurrences; indefinite if neither | ✅ | `end_date` and `max_occurrences` optional fields |
| Auto-generate next occurrence on schedule | ✅ | Celery beat calls `generate_recurring_transactions()` daily at midnight UTC |
| Edit "this occurrence only" vs "this and all future" | ❌ | `PATCH /recurring/{id}` updates the whole template only |
| Delete "this occurrence only" | ✅ | `DELETE /recurring/{template_id}/occurrence/{transaction_id}` |
| Delete "this and all future" | ✅ | `DELETE /recurring/{template_id}` deletes template (stops all future) |
| View all recurring templates and schedules | ✅ | `GET /recurring/` returns list with `next_occurrence_date` |

**Score: 5/7 = 71%**

---

### 1.5 Savings Goals

| Requirement | Status | Notes |
|---|---|---|
| Create goal: name, target, target date, description, icon, color | ✅ | `POST /goals/` → `SavingsGoalCreate` |
| Edit / delete goal | ✅ | `PATCH` + `DELETE /goals/{id}` |
| Delete goal does not delete linked transactions | ✅ | Transactions have nullable `goal_id`; deletion sets to NULL via FK constraint |
| Contribute from goal screen (auto-creates Savings transaction) | ✅ | `POST /goals/{id}/contribute?amount=&date=` |
| Associate existing transaction to goal | ✅ | `POST /goals/{id}/associate/{transaction_id}` |
| Goal detail: target, contributed, remaining, %, projected completion | ✅ | `SavingsGoalResponse` includes `remaining_amount`, `progress_percentage`, `projected_completion_date` |
| Active/Completed/Abandoned/Paused status | ✅ | `GoalStatus` enum; manually set via PATCH |
| Auto-mark goal as Completed when target reached + notify | ❌ | No auto-completion logic; no notification on goal completion |
| Pause goal — excluded from projections, history preserved | ⚠️ | Status exists but `projected_completion_date` calculation doesn't filter out Paused goals |
| Goal list: active and completed shown separately | ❌ | `GET /goals/` returns flat list; no grouping or filter by status |

**Score: 7/10 = 70%**

---

### 1.6 Income Tracking

| Requirement | Status | Notes |
|---|---|---|
| Add income: amount, date, category, source, description | ✅ | `TransactionType.INCOME` on `TransactionCreate`; `merchant_name` serves as source |
| Mark income as recurring | ✅ | `RecurringCreate` supports `transaction_type=Income` |
| View, edit, delete income | ✅ | Same transaction endpoints; filter by `transaction_type` on frontend |
| Edit/delete recurring income: this occurrence / this and future | ⚠️ | Same limitation as recurring expenses — template-level only |

**Score: 3.5/4 = 88%**

---

### 1.7 Tags

| Requirement | Status | Notes |
|---|---|---|
| Create, rename, delete personal tags | ✅ | Full CRUD on `/tags/` |
| Apply tags to transactions (cross-category) | ✅ | `tags: [int]` in `TransactionCreate`; `transaction_tags` join table |
| Delete tag removes from transactions, not transactions | ✅ | `transaction_tags` rows deleted; `Tag` model delete cascades FK |

**Score: 3/3 = 100%**

---

### 1.8 Budgets

| Requirement | Status | Notes |
|---|---|---|
| Budget per category or global, Weekly/Monthly | ✅ | `category_id` nullable; `BudgetPeriod` enum |
| Activate / deactivate without deleting | ✅ | `is_active` field; toggled via PATCH |
| Rollover unspent balance to next period | ✅ | `enable_rollover` flag; `perform_budget_rollover()` via Celery |
| In-app alert at 80% of budget | ✅ | `check_budget_thresholds()` creates `Notification` at 80% |
| In-app alert at 100% (budget exceeded) | ✅ | Same function, 100% threshold |
| Email alert at 80% and 100% | ❌ | Notifications stored in DB only; no email sent |
| One alert per period per threshold (no duplicates) | ❌ | Simplified — duplicate notifications possible within same period |
| View budget status: set, spent, remaining, % used | ⚠️ | `BudgetResponse` returns `amount` and `rollover_amount` but not real-time `spent` or `remaining` |

**Score: 5/8 = 63%**

---

### 1.9 Dashboard / Analytics

| Requirement | Status | Notes |
|---|---|---|
| Monthly summary: total income, expenses, net savings, savings rate | ✅ | `GET /analytics/summary` |
| Transaction count in summary | ❌ | Not included in summary response |
| Active budget statuses on dashboard | ❌ | No budget summary endpoint for dashboard |
| Category breakdown chart | ✅ | `GET /analytics/breakdown` — works on SQLite |
| 12-month spending trend | ⚠️ | `GET /analytics/trends` — implemented but uses `date_trunc` (PostgreSQL only; fails on SQLite) |
| Income vs expense 6-month comparison | ❌ | No such endpoint |
| Top 5 spending categories | ✅ | `GET /analytics/top-categories` |
| Active budget alerts on dashboard | ❌ | Not wired to dashboard |

**Score: 4/8 = 50%**

---

### 1.10 Reports

| Requirement | Status | Notes |
|---|---|---|
| Monthly report for any past month | ❌ | `reporting_service.py` exists with stub functions but no router or endpoint |
| Yearly report for any past year | ❌ | Not implemented |
| Custom date range report | ❌ | Not implemented |
| Report includes income, expenses, breakdown by category, by payment method, day-wise, full transaction list | ❌ | Service stub only; `Transaction.query` syntax in stub is Flask-style (wrong ORM usage) |
| Download report as PDF or CSV | ❌ | PDF is a placeholder `return "PDF Report...".encode()` |

**Score: 0/5 = 0%**

---

### 1.11 Notifications

| Requirement | Status | Notes |
|---|---|---|
| Weekly spending digest email (opt-in) | ❌ | Not implemented |
| Budget breach: in-app notification | ✅ | `Notification` row created by `check_budget_thresholds()` |
| Budget breach: email | ❌ | Not implemented |
| Recurring generation failure: in-app notification | ❌ | Errors only logged, not surfaced as notification |
| View all notifications | ✅ | `GET /notifications/` |
| Mark individual notification as read | ✅ | `PATCH /notifications/{id}/read` |
| Mark all as read | ✅ | `PATCH /notifications/read-all` |

**Score: 4/7 = 57%**

---

## Part 4: Standards Coverage

### 2.1 API Design Standards

| Standard | Status | Notes |
|---|---|---|
| Versioned endpoints `/api/v1/` | ✅ | All routes under `/api/v1/` |
| Pagination envelope: content, page, size, totalElements, totalPages | ❌ | Raw arrays returned; uses `skip/limit` not page envelope |
| HTTP 201 on create (with Location header) | ⚠️ | 201 returned ✅; `Location` header not set |
| HTTP 204 on delete | ✅ | All DELETE endpoints return 204 |
| HTTP 409 for business rule conflict | ❌ | Conflicts return 400 or 500 |
| HTTP 403 for unauthorized resource access | ❌ | Returns 404 instead (e.g., transaction not belonging to user) |
| Uniform error response (timestamp, status, error, message, path, traceId) | ❌ | FastAPI default `{"detail": "..."}` or Pydantic `{"detail": [{loc, msg, type}]}` |
| Auto-generated API docs | ✅ | FastAPI + Pydantic → `/docs`, `/redoc`, `/openapi.json` |
| DTOs for all input/output (no direct entity serialization) | ✅ | Pydantic schemas separate from SQLAlchemy models |

**Score: 4/9 = 44%**

---

### 2.2 Security Standards

| Standard | Status | Notes |
|---|---|---|
| BCrypt with cost factor ≥ 12 | ✅ | passlib default rounds = 12; bcrypt 3.2.2 pinned |
| No plain-text passwords in logs/responses | ✅ | Only `hashed_password` stored; never returned in response |
| JWT: 15-min access + 7-day refresh | ✅ | Configured in `auth_service.py` |
| Old refresh token invalidated on refresh | ❌ | New tokens issued but old refresh token not blacklisted |
| Resource ownership check (403 not 404) | ❌ | Ownership verified but returns 404 on mismatch |
| Server-side input validation | ✅ | Pydantic validates all requests before handler runs |
| Rate limiting on auth endpoints | ❌ | Not implemented |
| File upload: type validation (JPEG/PNG/WEBP only) | ✅ | `validate_receipt()` checks extension |
| File upload: size limit (5MB) | ✅ | `validate_receipt()` checks byte count |
| Secrets from environment variables | ✅ | `DATABASE_URL`, `SECRET_KEY`, `MINIO_*` from `os.getenv()` |

**Score: 6/10 = 60%**

---

### 2.3 Code Quality Standards

| Standard | Status | Notes |
|---|---|---|
| Business logic in service layer | ✅ | `budget_service`, `analytics_service`, etc. separate from controllers |
| Controllers only parse request / shape response | ⚠️ | Some controllers query DB directly (e.g., `transaction_controller`) |
| Repository pattern for data access | ⚠️ | `base_repository.py` exists but not used consistently |
| Enums for constants | ✅ | `TransactionType`, `PaymentMethod`, `BudgetPeriod`, `RecurrencePattern`, `GoalStatus` |
| No commented-out code / TODO in main branch | ⚠️ | `reporting_service.py` has comments like "In a real implementation..." |

**Score: 3/5 = 60%**

---

### 2.4 Testing Standards

| Standard | Status | Notes |
|---|---|---|
| Unit tests per service class with mocks | ✅ | `test_budget.py`, `test_recurring.py`, `test_auth.py`, `test_analytics.py` |
| Integration tests with real DB (Testcontainers) | ❌ | Integration tests use SQLite in-memory, not Testcontainers |
| Happy path + failure cases per endpoint | ⚠️ | Happy paths covered; failure/auth cases partial |
| Tests independent (no shared state) | ✅ | Each test creates its own mock DB / TestClient |

**Score: 2.5/4 = 63%**

---

### 2.5 Logging & Observability Standards

| Standard | Status | Notes |
|---|---|---|
| Every request logged: method, path, status, time, trace ID | ✅ | `LoggingMiddleware` in `middleware/logging_middleware.py` |
| Trace ID on every log line | ✅ | `X-Trace-ID` header added; logged per request |
| Correct log levels (DEBUG/INFO/WARN/ERROR) | ✅ | Services use `logger.info/error` appropriately |
| PII not in logs (email, name, amounts) | ❌ | `auth_service.py` logs `Registered user: {new_user.email}` |
| `/actuator/health` | ✅ | Returns `{"status": "ok"}` |
| Business metrics exposed | ⚠️ | HTTP metrics via Prometheus; no custom business metric counters (expense count, budget alerts sent) |

**Score: 4/6 = 67%**

---

### 2.6 Database Standards

| Standard | Status | Notes |
|---|---|---|
| `created_at` / `updated_at` on all tables | ✅ | All ORM models have both columns with `server_default=func.now()` |
| Indexes on filtered/joined columns | ⚠️ | `users.email`, `users.id` indexed; `transactions.user_id`, `transactions.date` not explicitly indexed |
| Bulk queries use streaming / pagination | ❌ | `export_user_data` loads all records into memory with `.all()` |

**Score: 1.5/3 = 50%**

---

## Part 5: Overall Implementation Score

### Functional Requirements

| Section | Implemented | Total | % |
|---|---|---|---|
| 1.1 User Management | 7 | 9 | 78% |
| 1.2 Categories | 4 | 5 | 80% |
| 1.3 Expense Management | 8 | 12 | 67% |
| 1.4 Recurring Transactions | 5 | 7 | 71% |
| 1.5 Savings Goals | 7 | 10 | 70% |
| 1.6 Income Tracking | 3.5 | 4 | 88% |
| 1.7 Tags | 3 | 3 | 100% |
| 1.8 Budgets | 5 | 8 | 63% |
| 1.9 Dashboard Analytics | 4 | 8 | 50% |
| 1.10 Reports | 0 | 5 | 0% |
| 1.11 Notifications | 4 | 7 | 57% |
| **Functional Total** | **54.5** | **78** | **70%** |

### Standards & Non-Functional

| Section | Implemented | Total | % |
|---|---|---|---|
| 2.1 API Design | 4 | 9 | 44% |
| 2.2 Security | 6 | 10 | 60% |
| 2.3 Code Quality | 3 | 5 | 60% |
| 2.4 Testing | 2.5 | 4 | 63% |
| 2.5 Observability | 4 | 6 | 67% |
| 2.6 Database | 1.5 | 3 | 50% |
| **Standards Total** | **21** | **37** | **57%** |

---

## Part 6: What's Not Implemented (Priority Gap List)

### High Impact — Core Missing Features
1. **Reports (1.10)** — `reporting_service.py` is a stub; no router; 0% done
2. **Email notifications** — Mailpit is set up but never called; affects password reset, budget alerts, weekly digest
3. **Dashboard analytics on SQLite** — `date_trunc` is PostgreSQL-only; blocks dashboard for all local dev

### Medium Impact — Incomplete Features
4. **Pagination envelope** — responses are raw arrays; spec requires `{content, page, size, totalElements, totalPages}`
5. **Transaction filters** — missing payment_method, tag, and goal filters on list endpoint
6. **Budget duplicate alert guard** — same threshold can fire multiple times in one period
7. **Goal auto-completion** — target reached event doesn't auto-mark goal or send notification
8. **Refresh token rotation** — old refresh token not blacklisted on refresh

### Lower Impact — Standards Gaps
9. **403 vs 404 on ownership** — wrong status code for cross-user resource access
10. **Rate limiting on auth endpoints** — brute-force protection missing
11. **PII in logs** — email address logged on registration
12. **Category delete guard** — no check for associated transactions before deletion
