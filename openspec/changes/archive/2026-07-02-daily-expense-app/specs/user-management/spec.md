## ADDED Requirements

### Requirement: User Registration
The system SHALL allow new users to register with their full name, email address, and a secure password.

#### Scenario: Successful registration
- **WHEN** user provides valid name, unique email, and complex password
- **THEN** system creates an inactive account and sends a verification email

### Requirement: Email Verification
The system SHALL require email verification before allowing account access.

#### Scenario: Account verification
- **WHEN** user clicks the link in the verification email
- **THEN** system activates the account and allows login

### Requirement: Secure Authentication
The system SHALL authenticate users using email and password, issuing JWT access and refresh tokens upon success.

#### Scenario: Successful login
- **WHEN** user provides correct credentials
- **THEN** system returns 200 OK with access and refresh tokens

### Requirement: Password Reset
The system SHALL provide a time-limited password reset mechanism via email.

#### Scenario: Request password reset
- **WHEN** user requests a reset link for their email
- **THEN** system sends an email with a unique, expiring token link

### Requirement: Data Portability
The system SHALL allow users to export all their personal data in a single downloadable format.

#### Scenario: Full data export
- **WHEN** user requests account data export
- **THEN** system generates and downloads a file containing all transactions, goals, and profile info

### Requirement: Account Deletion
The system SHALL allow users to delete their account, which MUST result in the removal of all associated personal data.

#### Scenario: Permanent account removal
- **WHEN** user confirms account deletion
- **THEN** system deletes user record and all related transaction/goal/budget data
