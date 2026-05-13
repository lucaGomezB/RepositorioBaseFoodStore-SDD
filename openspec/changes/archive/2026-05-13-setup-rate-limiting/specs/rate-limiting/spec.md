## ADDED Requirements

### Requirement: Login Endpoint Rate Limiting
The login endpoint SHALL be rate limited to prevent brute-force attacks.

#### Scenario: Normal login attempt
- **WHEN** a user makes a login request from a new IP
- **THEN** the request SHALL be processed normally
- **AND** the response SHALL include rate limit headers

#### Scenario: Rate limit exceeded
- **WHEN** more than 5 login attempts are made from the same IP within 15 minutes
- **THEN** the response SHALL return HTTP 429 status
- **AND** the response SHALL include RFC 7807 problem details with "type": "https://api.foodstore.com/errors/rate-limit-exceeded"

#### Scenario: Rate limit headers present
- **WHEN** any request is made to the login endpoint
- **THEN** the response SHALL include X-RateLimit-Limit header
- **AND** the response SHALL include X-RateLimit-Remaining header
- **AND** the response SHALL include X-RateLimit-Reset header

#### Scenario: After rate limit window expires
- **WHEN** a user makes a login attempt after 15 minutes have passed since the last failed attempt
- **THEN** the request SHALL be processed normally

### Requirement: Configuration via Environment
Rate limiting settings SHALL be configurable via environment variables.

#### Scenario: Default configuration
- **WHEN** no rate limit settings are provided in environment
- **THEN** the system SHALL use default values (5 requests per 15 minutes)

#### Scenario: Custom configuration
- **WHEN** RATE_LIMIT_LOGIN_REQUESTS and RATE_LIMIT_LOGIN_WINDOW are set
- **THEN** the system SHALL use the provided values

### Requirement: Rate Limit Exceeded Response Format
When rate limit is exceeded, the response SHALL follow RFC 7807 format.

#### Scenario: Rate limit error response structure
- **WHEN** a rate limit is exceeded
- **THEN** the response SHALL have "type": "https://api.foodstore.com/errors/rate-limit-exceeded"
- **AND** the response SHALL have "title": "Too Many Requests"
- **AND** the response SHALL have "status": 429
- **AND** the response SHALL have "detail" with information about when to retry