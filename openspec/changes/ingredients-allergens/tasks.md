## 1. Model + Schemas

- [x] 1.1 Add `es_alergeno: bool = Field(default=False)` and `eliminado_en: Optional[str]` to `app/models/ingrediente.py`
- [x] 1.2 Create `backend/app/schemas/ingrediente.py` with IngredienteCreate, IngredienteUpdate, IngredienteResponse

## 2. Service

- [x] 2.1 Create `backend/app/services/ingrediente.py` with CRUD + validations (unique name, soft delete)

## 3. Router

- [x] 3.1 Create `backend/app/api/ingredientes.py` with GET (público, filtro es_alergeno), POST/PUT/DELETE (STOCK/ADMIN)
- [x] 3.2 Register router in `app/api/__init__.py`

## 4. Tests

- [x] 4.1 Test create ingredient with and without allergen flag
- [x] 4.2 Test list ingredients with es_alergeno filter
- [x] 4.3 Test update ingredient
- [x] 4.4 Test soft delete
- [x] 4.5 Test RBAC: non-STOCK/ADMIN cannot modify
