## Context

The Food Store API needs protection against brute-force attacks, particularly on the login endpoint. Without rate limiting, attackers can make unlimited authentication attempts.

## Goals / Non-Goals

**Goals:**
- Implement rate limiting on login endpoint (5 attempts per 15 minutes per IP)
- Return RFC 7807 formatted error when rate limit is exceeded
- Add rate limit headers to all responses
- Allow configuration via environment variables

**Non-Goals:**
- User-based rate limiting (IP-based is sufficient for this use case)
- Rate limiting on all endpoints (focus on login initially)
- Distributed rate limiting (single instance for now)

## Decisions

### 1. Use slowapi for rate limiting
**Decision**: Use slowapi library (Flask-Limiter port for FastAPI).

**Rationale**: Well-maintained, battle-tested, integrates well with FastAPI, supports IP-based limiting out of the box.

**Alternative considered**: Custom implementation using Redis. Rejected - adds complexity, Redis dependency.

### 2. IP-based limiting
**Decision**: Track rate limits by client IP address.

**Rationale**: Simple to implement, effective for blocking brute-force attacks from single IPs.

**Alternative considered**: User-based limiting. Rejected - requires authentication first.

### 3. Return 429 with RFC 7807 format
**Decision**: When rate limit exceeded, return HTTP 429 with problem details format.

**Rationale**: Maintains consistency with error handling from setup-error-handling.

## Risks / Trade-offs

- **Risk**: Legitimate users behind NAT could be blocked
  - **Mitigation**: Use relatively generous limits (5 attempts per 15 minutes)

- **Risk**: Attackers could use distributed IPs
  - **Mitigation**: Consider implementing user-based limiting after authentication is working