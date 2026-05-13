## 1. Role Enum and Core Authorization

- [x] 1.1 Create `app/core/auth/roles.py` with `Role(IntEnum)` — ADMIN(1), STOCK(2), PEDIDOS(3), CLIENT(4)
- [x] 1.2 Create `app/core/auth/authorization.py` with `require_roles(*allowed_roles)` dependency
- [x] 1.3 Refactor `require_admin()` in `deps.py` to use `require_roles(Role.ADMIN)`
- [x] 1.4 Add `require_roles` to `app/core/auth/__init__.py`

## 2. Admin Role Assignment Endpoint

- [x] 2.1 Add Pydantic schema `AssignRoleRequest` with `rol_id: int`
- [x] 2.2 Add endpoint `PUT /api/auth/users/{user_id}/role` with `require_roles(Role.ADMIN)`
- [x] 2.3 Implement RN-RB04: verify at least one other ADMIN exists before allowing self-degradation

## 3. Protect Existing Endpoints

- [x] 3.1 Verify health, login, register routes are public (no auth required)
- [x] 3.2 Add `require_roles()` to any admin-only endpoints that exist

## 4. Tests

- [x] 4.1 Test `require_roles()` allows access with sufficient role
- [x] 4.2 Test `require_roles()` denies access with insufficient role
- [x] 4.3 Test `require_roles()` denies access without token
- [x] 4.4 Test admin assigns role to another user successfully
- [x] 4.5 Test non-admin cannot assign roles (403)
- [x] 4.6 Test last admin cannot self-degrade (400)
- [x] 4.7 Test public routes (health, login) are accessible without auth
