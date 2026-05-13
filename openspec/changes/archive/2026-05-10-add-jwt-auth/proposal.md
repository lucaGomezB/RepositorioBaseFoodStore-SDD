# Proposal: add-jwt-auth

## Why

We have the producto endpoints working, but they're publicly accessible. We need JWT authentication to:
- Protect admin-only endpoints (CRUD operations)
- Allow customers to access only public endpoints (read products)
- Secure user sessions with access/refresh tokens

## What Changes

1. **JWT Access Token** — Short-lived token (15 min) for API authentication
2. **Refresh Token** — Long-lived token (7 days) to get new access tokens
3. **Auth Middleware** — FastAPI dependency to verify JWT and extract user
4. **Role-based Access** — Different permissions for admin vs customer
5. **Protected Routes** — Secure endpoints with Depends(get_current_user) or Depends(require_admin)
6. **Login/Logout endpoints** — Auth flow implementation

## Capabilities

### New Capabilities

- **jwt-authentication**: JWT token generation, validation, and refresh logic
- **auth-middleware**: FastAPI dependencies for route protection
- **role-based-access**: Role checking (admin vs customer)

### Modified Capabilities

- (none) — New capability, no existing specs to modify

## Impact

- **Files created**: `app/core/auth/`, `app/api/auth.py`
- **Files modified**: Product router to add auth (or create new protected router)
- **Breaking changes**: None — existing endpoints remain, new ones add auth
- **Depends on**: setup-backend-patterns