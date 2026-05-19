## ADDED Requirements

### Requirement: Frontend soporta modo mock para desarrollo
El sistema DEBE detectar automáticamente si debe usar el flujo real de MercadoPago o el flujo mock basado en la configuración de `VITE_MP_PUBLIC_KEY`.

#### Scenario: Flujo real con MP configurado
- **WHEN** `VITE_MP_PUBLIC_KEY` tiene un valor no vacío
- **THEN** se renderiza `CardPaymentForm` (SDK de MercadoPago.js)
- **THEN** al pagar se llama a `POST /pagos/crear` con el `card_token`

#### Scenario: Flujo mock sin MP configurado
- **WHEN** `VITE_MP_PUBLIC_KEY` está vacía
- **THEN** se renderiza el formulario de tarjeta simulado (validación cliente-side)
- **THEN** al pagar se llama a `POST /pagos/mock`
- **THEN** se muestra un indicador visual de que es una simulación
