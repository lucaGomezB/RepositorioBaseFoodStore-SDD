## Why

MercadoPago estaba causando problemas en el flujo de pago (SDK no configurado, errores 503). Además, los CRUDs de productos, categorías e ingredientes tenían bugs que impedían la creación correcta de productos.

## What Changes

- **BREAKING**: Removed MercadoPago from PagoPage and CheckoutPage. Replaced with simple card form + mock payment.
- Added category and ingredient selectors to product creation form (required by backend).
- Fixed `imagenes_url` validation to accept empty strings (was blocking form submission).
- Fixed PostgreSQL sequences (productos_id_seq out of sync causing 503).
- Flattened category tree in CategoriasCRUD to show all categories.
- Replaced Parent ID input (number) with dropdown selector.
- Removed ID columns from Categorias and Ingredientes tables.
- Fixed IngredientesCRUD pagination to filter all items, not just current page.

## Capabilities

### New Capabilities
- `product-crud`: Product creation with category and ingredient assignment.

### Modified Capabilities
*(none — no spec-level requirement changes)*

## Impact

- `frontend/src/pages/PagoPage.tsx` — full rewrite
- `frontend/src/pages/CheckoutPage.tsx` — simplified
- `frontend/src/pages/ProductoFormPage.tsx` — added selectors, fixed validation
- `frontend/src/pages/CategoriasCRUD.tsx` — flattened tree, parent dropdown, removed ID
- `frontend/src/pages/IngredientesCRUD.tsx` — pagination fix, removed ID
- `frontend/src/entities/product/schemas.ts` — imagen_url accepts empty string
- `frontend/src/entities/product/model.ts` — added categorias_ids, ingredientes
- `backend` — fixed PostgreSQL sequences (setval)
