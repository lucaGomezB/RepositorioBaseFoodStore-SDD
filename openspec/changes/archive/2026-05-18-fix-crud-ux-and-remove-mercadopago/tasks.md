## 1. Remove MercadoPago from Payment Flow

- [x] 1.1 Rewrite PagoPage.tsx — simple card form + mock payment
- [x] 1.2 Rewrite CheckoutPage.tsx — remove CardPaymentForm, direct mock payment
- [x] 1.3 Fix navigation — redirect to `/mis-pedidos/:id` instead of confirmation page

## 2. Fix Product Creation

- [x] 2.1 Make `imagenes_url` optional in Zod schema (accept empty string)
- [x] 2.2 Add `categorias_ids` and `ingredientes` to ProductoCreate type
- [x] 2.3 Add category and ingredient checkbox selectors to ProductoFormPage
- [x] 2.4 Fix silent form validation failure — move validation to onSubmit handler with toasts
- [x] 2.5 Fix PostgreSQL sequence `productos_id_seq` (out of sync with seed data)

## 3. Fix Category CRUD

- [x] 3.1 Flatten category tree from backend for flat table display
- [x] 3.2 Replace Parent ID number input with dropdown selector
- [x] 3.3 Remove ID column from table
- [x] 3.4 Show parent category name instead of ID

## 4. Fix Ingredient CRUD

- [x] 4.1 Remove ID column from table
- [x] 4.2 Switch to in-memory pagination (fetch all, paginate/filter client-side)
