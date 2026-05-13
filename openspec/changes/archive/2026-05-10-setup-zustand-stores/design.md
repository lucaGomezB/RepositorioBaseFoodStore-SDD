# Design: setup-zustand-stores

## Context

We need 4 Zustand stores with different patterns:
- authStore: Hybrid (state + React Query delegation)
- cartStore: Smart (logic, math, persist)
- uiStore: State-only (simple setters)
- paymentStore: Defer to future change (depends on MP API)

## Goals / Non-Goals

**Goals:**
- Create 3 stores with correct patterns
- Add TypeScript typing for all state and actions
- Configure persist middleware for cart
- Integrate stores with existing React Query setup

**Non-Goals:**
- paymentStore — deferred (depends on MercadoPago API)
- Complex selectors — use simple direct access initially
- Redux DevTools beyond basic — debug with browser extension

## Decisions

### 1. Zustand v4 persist middleware
**Decision**: Use Zustand's built-in persist middleware with localStorage.
**Rationale**: Simple, no additional dependencies, works offline.
**Alternative**: zustand-persist — rejected, unnecessary extra dependency

### 2. CartStore structure
**Decision**: Store items with full product object + quantity.
**Rationale**: Avoids repeated API calls to get product details for each item.
**Structure**:
```typescript
interface CartItem {
  product: Producto;
  quantity: number;
  customization?: string;
}
```

### 3. AuthStore + React Query integration
**Decision**: AuthStore only holds state. React Query mutation results are "injected" into store.
**Rationale**: Separation of concerns — store handles state, React Query handles API logic.
**Flow**: React Query mutation onLoginSuccess → store.setToken() → store.setUser()

### 4. Store organization
**Decision**: All stores in `frontend/src/shared/stores/` with index export.
**Rationale**: Simple, matches existing structure, easy to add store later.

## Store Contracts

### authStore
```typescript
interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: User | null;
  isLoggedIn: boolean;
}
interface AuthActions {
  setAuth: (token, refreshToken, user) => void;
  logout: () => void;
  updateUser: (user) => void;
}
```

### cartStore
```typescript
interface CartState {
  items: CartItem[];
  itemCount: number;
  totalAmount: number;
}
interface CartActions {
  addItem: (product, quantity, customization?) => boolean; // returns false if stock insufficient
  removeItem: (productId) => void;
  updateQuantity: (productId, quantity) => boolean;
  updateCustomization: (productId, customization) => void;
  clearCart: () => void;
}
```

### uiStore
```typescript
interface UIState {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  activeModal: string | null;
  toasts: Toast[];
}
interface UIActions {
  toggleTheme: () => void;
  toggleSidebar: () => void;
  openModal: (modalId) => void;
  closeModal: () => void;
  addToast: (toast) => void;
  removeToast: (id) => void;
}
```

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|-------------|
| Stale product data in cart | Cart shows outdated prices/stock | Clear cart on logout, re-fetch on login |
| localStorage full | Cart won't persist | Implement storage size limit, warn user |
| TypeScript complexity | Many any types if API changes | Create shared types, keep in sync |

## Open Questions

- Should cart items store only productId instead of full product?
  - **Current decision**: Store full product — simpler UI rendering, but needs refresh
- When to clear cart? On logout? On payment completion?
  - **Current decision**: On logout AND after successful payment (webhook confirmation)

## Dependencies

- **Frontend**: setup-frontend-config ✅ (completed)
- **Backend**: add-jwt-auth ✅ (completed) — auth endpoints exist