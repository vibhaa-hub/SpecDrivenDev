## ADDED Requirements

### Requirement: Goal Creation
The system SHALL allow users to create savings goals with a target amount, name, and optional target date.

#### Scenario: Set up new savings goal
- **WHEN** user provides goal name "Emergency Fund" and target $10,000
- **THEN** system initializes the goal with 0% progress

### Requirement: Direct Goal Contribution
The system SHALL allow recording contributions directly from the goal view, automatically creating a linked transaction in the 'Savings' category.

#### Scenario: Contribute from goal UI
- **WHEN** user enters $500 contribution on the goal screen
- **THEN** system creates an expense record in 'Savings' category and increments goal total

### Requirement: Transaction Association
The system SHALL allow users to link existing expenses to a savings goal to count them as contributions.

#### Scenario: Link expense to goal
- **WHEN** user associates a $100 'Savings' expense with an active goal
- **THEN** system updates the goal's current progress total

### Requirement: Goal Completion Logic
The system SHALL automatically mark a goal as 'Completed' and notify the user when contributions meet or exceed the target amount.

#### Scenario: Reach target amount
- **WHEN** a contribution brings the total to >= target amount
- **THEN** system updates status to 'Completed' and generates an in-app notification

### Requirement: Goal Analytics
The system SHALL calculate and display percentage achieve, remaining amount, and projected completion date for every active goal.

#### Scenario: View goal progress
- **WHEN** user opens goal details
- **THEN** system returns calculated progress metrics based on contribution history
