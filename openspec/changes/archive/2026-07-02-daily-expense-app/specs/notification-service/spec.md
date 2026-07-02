## ADDED Requirements

### Requirement: Weekly Spending Digest
The system SHALL send an opt-in email every Monday summarizing the prior week's financial activity.

#### Scenario: Weekly digest delivery
- **WHEN** it is Monday morning and user has opt-in enabled
- **THEN** system sends an email with total income vs expenses for the previous week

### Requirement: In-App Notification Center
The system SHALL provide a notification center where users can view, read, and manage all system alerts.

#### Scenario: Mark notifications as read
- **WHEN** user marks all as read
- **THEN** system updates the status of all unread notifications for that user

### Requirement: Critical Failure Alerts
The system SHALL notify users in-app when automated processes (recurring transaction generation) fail.

#### Scenario: Recurring generation failure
- **WHEN** an automated generation task fails due to a system error
- **THEN** system creates an unread notification for the affected user
