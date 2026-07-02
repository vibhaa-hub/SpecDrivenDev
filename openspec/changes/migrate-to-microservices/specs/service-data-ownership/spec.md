## ADDED Requirements

### Requirement: Exclusive Service Ownership of Data
The system SHALL designate exactly one service as the authoritative owner of each entity's data (e.g., Category & Tag Service owns `categories` and `tags`; Transaction Service owns `transactions`), and no other service SHALL write to that data directly.

#### Scenario: Non-owning service attempts direct write
- **WHEN** a service other than the designated owner attempts to write to an entity it does not own
- **THEN** the write is rejected because the non-owning service has no database connection or credentials to that entity's underlying database

### Requirement: No Cross-Service Database Access
The system SHALL isolate each service's database/schema such that no service can directly query another service's tables; all cross-service data access SHALL go through the owning service's API or published events.

#### Scenario: Cross-service query attempted
- **WHEN** the Insights Service needs transaction data to build a dashboard summary
- **THEN** it obtains that data via the Transaction Service's API or via consuming `transaction.created`/`transaction.updated` events, not by querying the Transaction Service's database directly

### Requirement: Local Read Copies for Aggregation
The system SHALL allow a service to maintain a local, read-optimized copy of data it does not own, populated via consumed events, when synchronous cross-service calls on the read path would be impractical (e.g., dashboard aggregation).

#### Scenario: Insights Service serves a dashboard request
- **WHEN** a client requests a monthly spending summary from the Insights Service
- **THEN** the Insights Service computes the summary from its own locally maintained read copy of transaction/category data rather than calling other services synchronously for every field

#### Scenario: Local read copy staleness bound
- **WHEN** a source event (e.g., `transaction.created`) has not yet been consumed and applied to a service's local read copy
- **THEN** that service's read copy may be briefly stale, and the system does not guarantee strict real-time consistency across services for read-optimized copies

### Requirement: Referential Deletion Safety
The system SHALL prevent deletion of an entity that is referenced by data owned by another service, enforced by the owning service checking with (or having been notified by) the referencing service(s) before allowing the delete.

#### Scenario: Category deletion blocked by existing transactions
- **WHEN** a user requests deletion of a category that has transactions referencing it in the Transaction Service
- **THEN** the Category & Tag Service rejects the deletion, consistent with existing category-deletion-prevention behavior now enforced across service boundaries
