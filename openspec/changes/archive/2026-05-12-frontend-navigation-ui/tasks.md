## 1. Sidebar Component

- [x] 1.1 Define `SidebarItem` type and menu items configuration with `allowedRoles` per item
- [x] 1.2 Create `shared/components/Sidebar.tsx` with role-based filtering of menu items
- [x] 1.3 Add active route highlighting using `NavLink` from react-router-dom
- [x] 1.4 Export Sidebar from `shared/components/index.ts`

## 2. Layout Refactor

- [x] 2.1 Create `AppLayout` component with sidebar + header + main content areas
- [x] 2.2 Refactor `App.tsx` to use `AppLayout` and include router outlet
- [x] 2.3 Initialize `router.tsx` with basic route definitions using existing pages
- [x] 2.4 Add user info and logout to header section

## 3. Public Pages Layout

- [x] 3.1 Ensure login page renders without sidebar (standalone layout)
- [x] 3.2 Ensure public catalog page is accessible without auth
