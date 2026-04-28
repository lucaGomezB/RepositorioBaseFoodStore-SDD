# 🍔 Food Store — Frontend

React + TypeScript + Vite para sistema de e-commerce de alimentos.

---

## ⚡ Inicio rápido

```bash
# 1. Instalar dependencias
npm install

# 2. Configurar entorno
cp .env.example .env.local
# Editar .env.local con tus valores

# 3. Iniciar desarrollo
npm run dev
```

**App**: http://localhost:5173

### Build para producción

```bash
# Build
npm run build

# Preview del build
npm run preview
```

---

## 📁 Estructura — Feature-Sliced Design (FSD)

```
frontend/src/
├── app/                    # App root
│   ├── App.tsx            # Componente raíz
│   ├── router.tsx        # React Router DOM config
│   ├── app.css          # Estilos globales
│   └── providers.tsx    # Query providers, theme, etc.
│
├── pages/                 # Rutas completas
│   ├── HomePage.tsx
│   ├── LoginPage.tsx
│   ├── CatalogPage.tsx
│   ├── CartPage.tsx
│   ├── OrdersPage.tsx
│   ├── ProfilePage.tsx
│   └── admin/            # Páginas de admin
│
├── features/             # Interacciones de usuario (autocontenidas)
│   ├── auth/           # LoginForm, RegisterForm, ProtectedRoute
│   ├── catalog/        # ProductGrid, FilterBar, ProductCard
│   ├── cart/          # CartDrawer, AddToCart
│   ├── orders/        # OrdersList, OrderDetail, Timeline
│   ├── payments/      # CardPayment, CheckoutFlow
│   └── admin/        # Dashboard, CRUDs, StockTable
│
├── entities/             # Modelos de dominio + hooks
│   ├── user/           # User type, useUser, useLogin
│   ├── product/       # Product type, useProducts, useProduct
│   ├── order/         # Order type, useOrders, useCreateOrder
│   └── address/       # Address type, useAddresses
│
└── shared/              # Utilidades reutilizables
    ├── api/            # Axios instance, interceptors
    ├── stores/        # Zustand stores (auth, cart, payment, ui)
    ├── components/    # Button, Input, Modal, Loading, ErrorBoundary
    ├── hooks/       # useDebounce, useLocalStorage
    ├── types/        # Global types, API response types
    ├── utils/       # formatters, validators
    └── styles/      # Tailwind globals, theme
```

### Arquitectura — Flujo de imports

```
Pages → Features → Entities → Shared
```

Cada capa solo puede importar de capas inferiores. Nunca al revés.

---

## 🛠️ Comandos

| Comando | Descripción |
|---------|-----------|
| `npm run dev` | Desarrollo en http://localhost:5173 |
| `npm run build` | Build de producción |
| `npm run preview` | Preview del build |
| `npm run lint` | ESLint |
| `npm run typecheck` | TypeScript strict check |

---

## 🎨 Estilos — Tailwind CSS

```bash
# Configurar Tailwind
npx tailwindcss init -p
```

```js
// tailwind.config.js
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

```css
/* src/app/app.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

---

## 🔑 Estado — Zustand + TanStack Query

### Zustand (estado del cliente)

| Store | Uso | Persiste |
|-------|-----|----------|
| `authStore` | tokens JWT, usuario | localStorage |
| `cartStore` | items del carrito | localStorage |
| `paymentStore` | estado del pago | no |
| `uiStore` | modales, sidebar | no |

### TanStack Query (estado del servidor)

```tsx
// Ejemplo de query
const { data, isLoading } = useQuery({
  queryKey: ['products', categoriaId],
  queryFn: () => api.getProducts(categoriaId),
})
```

---

## 📚 Convenciones de código

- **Archivos componentes**: `PascalCase.tsx`
- **Archivos utility**: `camelCase.ts`
- **Funciones**: `camelCase`
- **Componentes**: `PascalCase`
- **Constantes**: `UPPER_SNAKE_CASE`
- **Tipos/Interfaces**: `PascalCase`
- **TanStack Query keys**: `['entity', params]` — siempre como array

---

## 📖 Documentación relacionada

- [README raíz](../README.md) — Setup general
- [docs/Descripcion.txt](../docs/Descripcion.txt) — Stack tecnológico
- [docs/Historias_de_usuario.txt](../docs/Historias_de_usuario.txt) — Historias de usuario

---

**Stack**: React 18 · TypeScript 5 · Vite 5 · Tailwind CSS 3 · TanStack Query 5 · Zustand 4  
**Mantenido por**: Food Store Contributors