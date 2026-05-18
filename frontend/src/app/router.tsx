// React Router DOM configuration
import type { RouteObject } from 'react-router-dom';
import AppLayout from '../shared/components/AppLayout';
import ProtectedRoute from '../shared/components/ProtectedRoute';
import { HomePage } from '../pages/HomePage';
import { LoginPage } from '../pages/LoginPage';
import RegistroPage from '../pages/RegistroPage';
import { NotFoundPage } from '../pages/NotFoundPage';
import { ProfilePage } from '../pages/ProfilePage';
import CartPage from '../pages/CartPage';
import DireccionesPage from '../pages/DireccionesPage';
import CategoriasCRUD from '../pages/CategoriasCRUD';
import IngredientesCRUD from '../pages/IngredientesCRUD';
import ProductosListPage from '../pages/ProductosListPage';
import ProductoFormPage from '../pages/ProductoFormPage';
import MisPedidosPage from '../pages/MisPedidosPage';
import PedidoDetailPage from '../pages/PedidoDetailPage';
import PanelPedidosPage from '../pages/PanelPedidosPage';
import CheckoutPage from '../pages/CheckoutPage';
import OrderConfirmationPage from '../pages/OrderConfirmationPage';
import MetricasPage from '../pages/MetricasPage';
import StockPage from '../pages/StockPage';
import UsuariosPage from '../pages/UsuariosPage';
import ConfiguracionPage from '../pages/ConfiguracionPage';

/**
 * Route configuration for the Food Store frontend.
 *
 * Layout routes (wrapped in AppLayout) get the sidebar + header.
 * Standalone routes (login, 404) render without sidebar.
 *
 * Protected routes are wrapped with <ProtectedRoute> which checks
 * authentication and (optionally) role-based access.
 */
export const routes: RouteObject[] = [
  {
    // Routes wrapped in AppLayout (sidebar + header)
    element: <AppLayout />,
    children: [
      // Public: home page (no auth required)
      { index: true, element: <HomePage /> },
      // Protected: CRUD pages restricted to ADMIN(1) and STOCK(2) roles
      {
        element: <ProtectedRoute requiredRoles={[1, 2]} />,
        children: [
          { path: 'categorias', element: <CategoriasCRUD /> },
          { path: 'ingredientes', element: <IngredientesCRUD /> },
          // Productos routes: list, create, edit
          { path: 'productos', element: <ProductosListPage /> },
          { path: 'productos/nuevo', element: <ProductoFormPage /> },
          { path: 'productos/:id/editar', element: <ProductoFormPage /> },
          { path: 'stock', element: <StockPage /> },
        ],
      },
      // Protected: Pages accessible to ADMIN(1) and CLIENT(4)
      {
        element: <ProtectedRoute requiredRoles={[1, 4]} />,
        children: [
          { path: 'direcciones', element: <DireccionesPage /> },
          { path: 'carrito', element: <CartPage /> },
          { path: 'checkout', element: <CheckoutPage /> },
          { path: 'pedidos/:id/confirmacion', element: <OrderConfirmationPage /> },
          { path: 'perfil', element: <ProfilePage /> },
          { path: 'mis-pedidos', element: <MisPedidosPage /> },
          { path: 'mis-pedidos/:id', element: <PedidoDetailPage /> },
        ],
      },
      // Protected: Pages accessible to ADMIN(1) and PEDIDOS(3)
      {
        element: <ProtectedRoute requiredRoles={[1, 3]} />,
        children: [
          { path: 'panel-pedidos', element: <PanelPedidosPage /> },
        ],
      },
      // Protected: Admin-only pages
      {
        element: <ProtectedRoute requiredRoles={[1]} />,
        children: [
          { path: 'metricas', element: <MetricasPage /> },
          { path: 'usuarios', element: <UsuariosPage /> },
          { path: 'configuracion', element: <ConfiguracionPage /> },
        ],
      },
    ],
  },
  // Standalone routes (no sidebar) — always public
  { path: 'login', element: <LoginPage /> },
  { path: 'registro', element: <RegistroPage /> },
  { path: '*', element: <NotFoundPage /> },
];
