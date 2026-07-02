## ADDED Requirements

### Requirement: Single Entry Point Routing
The system SHALL expose a single API Gateway as the sole entry point for all client traffic at `/api/v1/*`, routing each request to the backend service that owns the matched path prefix.

#### Scenario: Request routed to owning service
- **WHEN** a client sends a request to `/api/v1/transactions/{id}`
- **THEN** the gateway forwards the request to the Transaction Service and returns its response unmodified to the client

#### Scenario: Unknown route
- **WHEN** a client sends a request to a path with no matching service route
- **THEN** the gateway returns a 404 response without forwarding the request to any backend service

### Requirement: Auth Header Pass-Through
The system SHALL forward the client's `Authorization` header unmodified to the backend service on every proxied request, without performing its own token issuance or replacement.

#### Scenario: Authenticated request forwarded
- **WHEN** a client sends a request with a valid `Authorization: Bearer <token>` header
- **THEN** the gateway forwards that same header value to the owning backend service

### Requirement: Response Contract Preservation
The system SHALL NOT transform, aggregate, or reshape response bodies returned by backend services; the gateway returns each service's response as-is (status code, headers relevant to the client, and body).

#### Scenario: Backend error surfaced unchanged
- **WHEN** a backend service returns a 4xx or 5xx response
- **THEN** the gateway returns that same status code and response body to the client

### Requirement: CORS Enforcement at the Edge
The system SHALL enforce CORS policy (allowed origins, methods, headers) at the gateway, and backend services SHALL NOT need their own CORS configuration for browser clients.

#### Scenario: Disallowed origin rejected
- **WHEN** a browser request originates from an origin not in the gateway's allowed-origins list
- **THEN** the gateway rejects the request per CORS policy before it reaches any backend service

### Requirement: Backend Service Unavailability Handling
The system SHALL return a 502/503 response to the client when the routed backend service is unreachable or times out, rather than hanging the client request indefinitely.

#### Scenario: Backend service down
- **WHEN** the gateway routes a request to a backend service that is not responding
- **THEN** the gateway returns a 502 or 503 response to the client after a bounded timeout
