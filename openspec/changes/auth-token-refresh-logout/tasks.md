## 1. Verify Existing Implementation

- [x] 1.1 Verify refresh token endpoint exists in app/api/auth.py
- [x] 1.2 Verify logout endpoint exists in app/api/auth.py
- [x] 1.3 Verify refresh token repository has create/revoke methods

## 2. Test Endpoints

- [ ] 2.1 Test refresh endpoint with valid token (requires seeded DB)
- [ ] 2.2 Test refresh endpoint invalidates old token (rotation)
- [ ] 2.3 Test logout endpoint revokes refresh token
- [ ] 2.4 Test refresh with revoked token returns 401

## 3. Verification

- [x] 3.1 Verify backend build succeeds
- [x] 3.2 Verify code compiles (endpoints exist, repository methods exist)