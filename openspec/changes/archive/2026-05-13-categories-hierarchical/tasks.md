## 1. Schemas

- [x] 1.1 Create `backend/app/schemas/categoria.py` with CategoriaCreate, CategoriaUpdate, CategoriaResponse, CategoriaTree

## 2. Service

- [x] 2.1 Create `backend/app/services/categoria.py` with CRUD + validations (no cycles, unique name, soft delete)
- [x] 2.2 Implement tree builder that returns nested categories

## 3. Router

- [x] 3.1 Create `backend/app/api/categorias.py` with CRUD endpoints protected by require_roles(Role.STOCK, Role.ADMIN)
- [x] 3.2 Add public GET /categorias that returns the category tree
- [x] 3.3 Register router in `app/api/__init__.py`
- [x] 3.4 Add `eliminado_en` field to `app/models/categoria.py` (named `eliminado_en` per spec)

## 4. Tests

- [x] 4.1 Test create root and subcategory
- [x] 4.2 Test public tree returns correct hierarchy
- [x] 4.3 Test update and circular reference prevention
- [x] 4.4 Test soft delete hides from public tree
- [x] 4.5 Test RBAC: non-STOCK/ADMIN cannot modify categories
