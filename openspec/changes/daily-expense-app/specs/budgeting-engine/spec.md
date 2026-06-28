## ADDED Requirements

### Requirement: Budget Definition
The system SHALL allow users to set weekly or monthly budgets for specific categories or as an overall limit.

#### Scenario: Set monthly category budget
- **WHEN** user sets 'Food' budget to $500/month
- **THEN** system tracks spending in that category against the limit

### Requirement: Budget Rollover
The system SHALL support optional rollover of unspent budget amounts to the next period.

#### Scenario: Roll over unspent funds
- **WHEN** a period ends and rollover is enabled
- **THEN** system adds the remaining balance to the next period's budget limit

### Requirement: Threshold Notifications
The system SHALL trigger notifications when spending reaches 80% and 100% of a defined budget.

#### Scenario: Reach 80% threshold
- **WHEN** a new expense causes total category spending to hit 80% of budget
- **THEN** system sends an in-app alert and an email notification (once per period)

### Requirement: Budget Status Monitoring
The system SHALL provide real-time status for all active budgets including amount spent, remaining, and percentage used.

#### Scenario: View budget dashboard
- **WHEN** user views budget list
- **THEN** system calculates current period spending for each budget and returns percentage used
