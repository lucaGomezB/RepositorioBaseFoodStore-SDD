# Tasks: setup-zustand-stores

## 1. Create store files structure

- [x] 1.1 Create `frontend/src/shared/stores/authStore.ts`
- [x] 1.2 Create `frontend/src/shared/stores/cartStore.ts`
- [x] 1.3 Create `frontend/src/shared/stores/uiStore.ts`
- [x] 1.4 Update `frontend/src/shared/stores/index.ts` with exports

## 2. Implement authStore

- [x] 2.1 Define AuthState interface (token, refreshToken, user, isLoggedIn)
- [x] 2.2 Implement setAuth() action
- [x] 2.3 Implement logout() action
- [x] 2.4 Implement updateUser() action
- [x] 2.5 Add Zustand persist middleware for auth token only

## 3. Implement cartStore

- [x] 3.1 Define CartItem interface (product, quantity, customization?)
- [x] 3.2 Define CartState interface (items, itemCount, totalAmount)
- [x] 3.3 Add Zustand persist middleware for cart
- [x] 3.4 Implement addItem() with stock validation
- [x] 3.5 Implement removeItem()
- [x] 3.6 Implement updateQuantity() with stock validation
- [x] 3.7 Implement updateCustomization()
- [x] 3.8 Implement clearCart()
- [x] 3.9 Implement getItemCount() computed
- [x] 3.10 Implement getTotalAmount() computed

## 4. Implement uiStore

- [x] 4.1 Define UIState interface (theme, sidebarOpen, activeModal, toasts)
- [x] 4.2 Implement toggleTheme()
- [x] 4.3 Implement toggleSidebar()
- [x] 4.4 Implement openModal() / closeModal()
- [x] 4.5 Implement addToast() / removeToast()
- [x] 4.6 Add persist middleware for theme preference

## 5. TypeScript Integration

- [x] 5.1 Create TypeScript types for each store
- [x] 5.2 Add generic types to store creators
- [x] 5.3 Ensure all state and actions are properly typed

## 6. Integration with React Query

- [x] 6.1 Document how authStore integrates with React Query mutations
- [x] 6.2 Create example usage in a component

## 7. Verification

- [x] 7.1 Verify stores build without TypeScript errors
- [x] 7.2 Verify persist middleware works (reload page test)
- [x] 7.3 Verify cart stock validation logic