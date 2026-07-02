# recurring-transactions Specification

## Purpose
TBD - created by archiving change daily-expense-app. Update Purpose after archive.

## Requirements

### Requirement: Recurring Pattern Definition
The system SHALL allow marking an expense or income as recurring with patterns: Daily, Weekly, Monthly, or Yearly.

#### Scenario: Create recurring monthly expense
- **WHEN** user sets an expense to recur 'Monthly' starting today
- **THEN** system saves a template for automatic generation

### Requirement: Automated Transaction Generation
The system SHALL automatically generate the next occurrence of a recurring transaction on the scheduled date.

#### Scenario: Scheduled generation trigger
- **WHEN** the current date matches the next scheduled date of a template
- **THEN** system creates a new transaction record and updates the template's next run date

### Requirement: Recurring Instance Modification
The system SHALL allow users to edit or delete a recurring transaction with a choice to affect "only this occurrence" or "all future occurrences".

#### Scenario: Update future occurrences
- **WHEN** user edits a recurring instance and selects "this and all future"
- **THEN** system updates the current record and the underlying recurrence template
