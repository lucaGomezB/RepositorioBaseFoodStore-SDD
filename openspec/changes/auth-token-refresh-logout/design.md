## Context

The authentication system needs to support session continuation via refresh tokens and explicit session termination. This extends the auth-login-register change.

## Goals / Non-Goals

**Goals:**
- Implement refresh token endpoint with automatic rotation
- Implement logout endpoint with token revocation in database
- Ensure refresh tokens are invalidated after use (rotation)
- Support multiple valid refresh tokens per user (for multiple devices)

**Non-Goals:**
- Token refresh from frontend (handled in frontend-auth-guards change)
- Session listing/revocation from admin panel (future change)

## Decisions

### 1. Token Rotation Strategy
**Decision**: Each refresh request invalidates the old token and issues a new one.

**Rationale**: Rotation limits the window of opportunity if a token is compromised.

### 2. Refresh Token Storage
**Decision**: Store refresh tokens in database with status field (active/revoked).

**Rationale**: Allows server-side token revocation and prevents use of revoked tokens.

### 3. Refresh Token Expiry
**Decision**: Refresh tokens expire in 7 days (configurable).

**Rationale**: Balances security with user convenience.

## Implementation Details

- Endpoint: POST /api/v1/auth/refresh
- Endpoint: POST /api/v1/auth/logout
- Token storage: refresh_token table
- Rotation: Old token marked as revoked, new token created