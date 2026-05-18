## ADDED Requirements

### Requirement: Frontend tests MUST exist for critical stores
Zustand stores (auth, cart, payment, ui) SHALL have unit tests covering all actions and state transitions.

#### Scenario: authStore login/logout flow
- **WHEN** calling authStore.login()
- **THEN** the store SHALL update user state and token
- **WHEN** calling authStore.logout()
- **THEN** the store SHALL clear user state and token

#### Scenario: cartStore add/remove items
- **WHEN** calling cartStore.addItem()
- **THEN** the store SHALL add the item to the cart
- **WHEN** calling cartStore.removeItem()
- **THEN** the store SHALL remove the item from the cart
- **WHEN** calling cartStore.clearCart()
- **THEN** the store SHALL empty the cart

### Requirement: Frontend tests MUST exist for query hooks
TanStack Query hooks (usePerfil, usePedidos, useAdminPedidos) SHALL have integration tests mocking the API layer.

#### Scenario: usePerfil fetches user data
- **WHEN** the usePerfil hook is called
- **THEN** it SHALL fetch user data from the API
- **THEN** it SHALL return loading, data, and error states

### Requirement: Frontend tests MUST exist for page components
Page components (MisPedidosPage, PedidoDetailPage, MetricasPage) SHALL render without crashing.

#### Scenario: MetricasPage renders KPIs
- **WHEN** MetricasPage is rendered with mock data
- **THEN** it SHALL display KPI cards for total sales, orders by state, top products
