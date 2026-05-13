# Design: add-jwt-auth

## Context

We need to add authentication to protect certain endpoints. The database already has users (Usuario) with password_hash, and roles (Rol). JWT is chosen as it's stateless and scales well.

## Goals / Non-Goals

**Goals:**
- Generate JWT access tokens on login
- Generate refresh tokens for session persistence
- Protect admin endpoints with role verification
- Protect customer endpoints (own data only)

**Non-Goals:**
- OAuth2 integration (Google, Facebook) — future
- Password reset flow — future
- Email verification — future

## Decisions

### 1. JWT over Sessions
**Decision**: Use JWT access + refresh tokens.
**Rationale**: Stateless, scales better, works with mobile.
**Alternative considered**: Server sessions — rejected, requires Redis or sticky sessions.

### 2. Token Lifetimes
**Decision**: Access token = 15 minutes, Refresh token = 7 days.
**Rationale**: Short access limits damage window, refresh allows persistence.
**Alternative considered**: 1 hour access — rejected, too long for sensitive ops.

### 3. Token Storage
**Decision**: Refresh tokens stored in database (refreshtokens table).
**Rationale**: Allows revocation, tracks active sessions.
**Alternative considered**: JWT only (stateless) — rejected, no way to logout.

### 4. Password Verification
**Decision**: Use bcrypt (already in project) for password hashing/verification.
**Rationale**: Already installed, industry standard.

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|-------------|
| Token in localStorage (XSS) | Account takeover | Short-lived access token limits exposure |
| Refresh token theft | Persistent access | Store refresh token in DB, allow revocation |
| Lost refresh token | User locked out | Allow email/password login to get new refresh |

## Open Questions

- Should we use API keys for service-to-service?
  - **Current decision**: Not in this change, JWT only for user auth
- How to handle concurrent logouts?
  - **Current decision**: Revoke refresh token in DB, simple approach