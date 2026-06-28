## Why

Individuals often struggle to maintain a clear picture of their financial health due to fragmented tracking of expenses, income, budgets, and savings goals. This "Daily Expense Application" solves this by providing a unified, standardized platform for personal finance management, offering automated recurring transactions, goal-oriented savings tracking, and proactive budget alerts to help users make informed financial decisions.

## What Changes

- **User Lifecycle Management**: Implementation of a secure authentication system with email verification, profile updates, password resets, and GDPR-compliant data export/account deletion.
- **Hierarchical Categorization**: A dual-system for transaction classification using both typed categories (Expense, Income, Both) and flexible user-defined tags.
- **Unified Transaction Engine**: Support for logging expenses (with receipt uploads) and income, including bulk import via CSV and historical data export.
- **Automation Engine**: Automatic generation of next occurrences for recurring expenses and income based on defined patterns (Daily, Weekly, Monthly, Yearly).
- **Savings & Goal Tracking**: A system to manage savings goals, allowing direct contributions or association of existing expenses, with progress visualization and automated completion logic.
- **Proactive Budgeting**: Weekly and monthly budget management with rollover capabilities and automated alerts at 80% and 100% spending thresholds.
- **Data Visualization & Reporting**: A comprehensive dashboard for spending trends and category breakdowns, plus a reporting engine for PDF/CSV generation of historical data.
- **Notification Hub**: Delivery of weekly digests, budget breaches, and system failures via in-app and email channels.

## Capabilities

### New Capabilities
- `user-management`: Secure registration, JWT-based authentication, and user profile/data management.
- `categories-tags`: Management of system-default and custom categories, plus multi-assignment tags.
- `transaction-management`: Core expense and income logging, receipt storage (MinIO), and CSV import/export.
- `recurring-transactions`: Automated generation logic for scheduled financial events.
- `savings-goals`: Goal-oriented contribution tracking with progress analytics and automated state transitions.
- `budgeting-engine`: Budget monitoring with rollover logic and threshold alert triggers.
- `dashboard-analytics`: Real-time summary metrics and historical trend visualization for the dashboard.
- `reporting-service`: Engine for generating and exporting Monthly/Yearly/Custom PDF and CSV reports.
- `notification-service`: Centralized delivery for email and in-app alerts including budget warnings and weekly digests.

### Modified Capabilities
- None: This is a greenfield project.

## Impact

- **API**: Implementation of a versioned REST API (`/api/v1/...`) with standardized error handling and pagination.
- **Database**: New relational schema requiring tables for users, transactions, goals, budgets, and audit timestamps.
- **Infrastructure**: Requirement for object storage (MinIO) for receipt images and an SMTP gateway for email notifications.
- **Frontend**: Development of a React-based SPA using Axios for API communication and a centralized state for user sessions.
