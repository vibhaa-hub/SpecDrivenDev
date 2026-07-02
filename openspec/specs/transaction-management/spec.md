# transaction-management Specification

## Purpose
TBD - created by archiving change daily-expense-app. Update Purpose after archive.

## Requirements

### Requirement: Expense Logging
The system SHALL allow users to record expenses with amount, date, category, payment method, and optional fields (description, merchant, tags, notes).

#### Scenario: Successful expense entry
- **WHEN** user submits required expense data
- **THEN** system saves the transaction and returns the created record

### Requirement: Receipt Upload
The system SHALL support uploading image receipts (JPEG, PNG, WEBP, max 5MB) for any expense.

#### Scenario: Attach receipt to expense
- **WHEN** user uploads a valid image to an existing expense
- **THEN** system stores the image in MinIO and links it to the transaction

### Requirement: Income Tracking
The system SHALL allow users to record income entries with amount, date, category, and source name.

#### Scenario: Successful income entry
- **WHEN** user submits income data
- **THEN** system persists the record and updates the user's net balance calculation

### Requirement: Bulk Transaction Import
The system SHALL support importing transactions from a CSV file.

#### Scenario: CSV Import with validation
- **WHEN** user uploads a transaction CSV
- **THEN** system processes rows, reporting successes and specific failures for invalid rows

### Requirement: Transaction History Export
The system SHALL allow users to export a filtered list of transactions to a CSV file.

#### Scenario: Export transactions by date range
- **WHEN** user requests export for '2024-01-01' to '2024-01-31'
- **THEN** system generates a CSV containing matching transactions
