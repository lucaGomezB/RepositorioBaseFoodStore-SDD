# role-based-navigation Specification

## Purpose
TBD - created by archiving change frontend-navigation-ui. Update Purpose after archive.
## Requirements
### Requirement: Role-Based Sidebar Navigation
The system SHALL display a sidebar with navigation items filtered by the authenticated user's role.

#### Scenario: Client views client menu
- **WHEN** an authenticated user with role CLIENT views the sidebar
- **THEN** the sidebar SHALL show: Catálogo, Mi Carrito, Mis Pedidos, Mi Perfil, Mis Direcciones

#### Scenario: Stock manager views stock menu
- **WHEN** an authenticated user with role STOCK views the sidebar
- **THEN** the sidebar SHALL show: Productos, Categorías, Ingredientes, Stock

#### Scenario: Orders manager views orders menu
- **WHEN** an authenticated user with role PEDIDOS views the sidebar
- **THEN** the sidebar SHALL show: Panel de Pedidos

#### Scenario: Admin views all menu options
- **WHEN** an authenticated user with role ADMIN views the sidebar
- **THEN** the sidebar SHALL show all options from all roles plus Usuarios, Métricas, Configuración

#### Scenario: Unauthenticated user views public menu
- **WHEN** an unauthenticated user views the navigation
- **THEN** the system SHALL show: Catálogo, Iniciar Sesión, Registrarse

### Requirement: Active Route Highlighting
The sidebar SHALL highlight the currently active route.

#### Scenario: Active link is highlighted
- **WHEN** a user navigates to a route
- **THEN** the corresponding sidebar item SHALL have an active visual state

### Requirement: User Menu in Header
The system SHALL display the current user's name and a logout option in the header when authenticated.

#### Scenario: Authenticated user sees user menu
- **WHEN** an authenticated user views the header
- **THEN** the header SHALL display the user's name and a logout button

