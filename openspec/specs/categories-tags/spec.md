# categories-tags Specification

## Purpose
TBD - created by archiving change daily-expense-app. Update Purpose after archive.

## Requirements

### Requirement: Default Categories
The system SHALL provide immutable default categories (Food, Transport, Housing, Health, Entertainment, Shopping, Education, Savings, Other) for all users.

#### Scenario: View default categories
- **WHEN** any authenticated user lists categories
- **THEN** system includes the system-defined default categories in the response

### Requirement: Custom Categories
The system SHALL allow users to create, edit, and delete their own categories with a name, icon, and color.

#### Scenario: Create custom category
- **WHEN** user provides name, icon, and color
- **THEN** system creates a new category available only to that user

### Requirement: Category Type Constraint
The system SHALL enforce that every category is typed as Expense, Income, or Both.

#### Scenario: Assign category to transaction
- **WHEN** user adds an expense
- **THEN** only categories of type 'Expense' or 'Both' are selectable

### Requirement: Personal Tags
The system SHALL allow users to manage a flat list of personal tags that can be applied to any transaction.

#### Scenario: Apply tags to expense
- **WHEN** user saves an expense with tags ["vacation", "2024"]
- **THEN** system persists the association between the expense and those tags
