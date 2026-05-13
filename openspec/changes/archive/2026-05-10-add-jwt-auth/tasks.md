# Tasks: add-jwt-auth

## 1. JWT Configuration

- [x] 1.1 Install python-jose and pyjwt packages
- [x] 1.2 Create JWT config in app/core/config.py (SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS)
- [x] 1.3 Add JWT config to settings

## 2. Token Generation & Validation

- [x] 2.1 Create app/core/auth/tokens.py with create_access_token() function
- [x] 2.2 Create create_refresh_token() function
- [x] 2.3 Create decode_token() function to validate and extract payload
- [x] 2.4 Implement token expiration check

## 3. Refresh Token Storage

- [x] 3.1 Create RefreshToken model in app/models/
- [x] 3.2 Add RefreshToken table to database
- [x] 3.3 Create RefreshTokenRepository
- [x] 3.4 Implement save and validate refresh token methods

## 4. Auth Dependencies (Middleware)

- [x] 4.1 Create app/core/auth/deps.py with get_current_user dependency
- [x] 4.2 Create require_admin dependency
- [x] 4.3 Create get_current_active_user dependency
- [x] 4.4 Implement token extraction from Authorization header

## 5. Auth Endpoints

- [x] 5.1 Create app/api/auth.py router
- [x] 5.2 Implement POST /auth/login endpoint
- [x] 5.3 Implement POST /auth/refresh endpoint
- [x] 5.4 Implement POST /auth/logout endpoint
- [x] 5.5 Add password verification using bcrypt

## 6. Protect Existing Endpoints

- [x] 6.1 Update /api/v1/productos POST to require admin
- [x] 6.2 Update /api/v1/productos PATCH to require admin
- [x] 6.3 Update /api/v1/productos DELETE to require admin
- [x] 6.4 Keep GET /productos public (read-only)

## 7. Tests

- [ ] 7.1 Add unit tests for token generation
- [ ] 7.2 Add unit tests for auth dependencies
- [ ] 7.3 Add integration tests for auth endpoints

## 8. Verification

- [x] 8.1 Test login with valid credentials returns tokens
- [x] 8.2 Test login with invalid credentials returns 401
- [x] 8.3 Test refresh token endpoint returns new access token
- [x] 8.4 Test protected endpoint without token returns 401
- [x] 8.5 Test admin endpoint with customer token returns 403