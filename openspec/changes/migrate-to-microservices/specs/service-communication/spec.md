## ADDED Requirements

### Requirement: Synchronous Reference Lookups
The system SHALL provide synchronous REST APIs for services to validate or fetch reference data they do not own (e.g., Transaction Service validating a `category_id` against the Category & Tag Service), with a bounded timeout on every such call.

#### Scenario: Valid reference confirmed
- **WHEN** the Transaction Service creates an expense referencing an existing `category_id`
- **THEN** it calls the Category & Tag Service's lookup API synchronously and proceeds only after receiving confirmation the category exists

#### Scenario: Invalid reference rejected
- **WHEN** the Transaction Service validates a `category_id` that does not exist in the Category & Tag Service
- **THEN** the transaction creation request is rejected with a validation error before any local write occurs

#### Scenario: Reference service times out
- **WHEN** a synchronous reference lookup does not receive a response within the configured timeout
- **THEN** the calling service fails the triggering request with an error rather than waiting indefinitely

### Requirement: Asynchronous Event Publication
The system SHALL publish domain events for state changes that other services need to react to (e.g., transaction created, savings goal completed, budget threshold breached), using the shared Redis-backed event stream.

#### Scenario: Transaction created event published
- **WHEN** the Transaction Service successfully creates a new expense or income record
- **THEN** it publishes a `transaction.created` event containing the transaction ID, user ID, category ID, amount, and type

#### Scenario: Downstream event consumption
- **WHEN** the Budget Service consumes a `transaction.created` event for a transaction within a budget period
- **THEN** it re-evaluates the relevant budget's threshold status and publishes a `budget.threshold_breached` event if a threshold is newly crossed

### Requirement: Idempotent Event Handling
The system SHALL process each event idempotently, so that redelivery of the same event (at-least-once delivery) does not produce duplicate side effects.

#### Scenario: Duplicate event delivered
- **WHEN** a consuming service receives the same event ID a second time
- **THEN** it detects the duplicate and skips re-applying the side effect (e.g., does not send a second duplicate notification)

### Requirement: Event Schema Versioning
The system SHALL version each event type's schema so consuming services can detect and safely ignore or handle fields added in later versions without breaking.

#### Scenario: Consumer receives event with additional fields
- **WHEN** a consuming service receives an event with a newer schema version containing fields it does not recognize
- **THEN** it processes the fields it understands and does not fail on the unrecognized additional fields
