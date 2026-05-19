## Context

PagoPage and CheckoutPage used MercadoPago SDK which was not properly configured,
causing runtime errors. Product creation was blocked by missing fields and DB sequence issues.

## Goals / Non-Goals

**Goals:**
- Remove MercadoPago dependency from payment flow
- Fix product creation (add category/ingredient selectors)
- Fix category/ingredient CRUD display and UX

**Non-Goals:**
- Not removing MercadoPago from the backend or payments feature module
- Not adding real payment processing

## Decisions

1. **Mock payment always**: Since MP was broken and not configured, all payments go through `/pagos/mock`.
2. **Simple card form**: Replaced MP widget with plain HTML inputs (name, number, expiry, CVV) with client-side validation only.
3. **Inline memory pagination**: Categories and ingredients fetch all records, paginate/filter client-side for consistency.
4. **Tree flattening**: Backend returns categories as tree; frontend flattens for table display.

## Risks / Trade-offs

- Card data is not tokenized — purely cosmetic/simulated.
- Large datasets (>1000 items) could slow client-side pagination — acceptable for current scale.
