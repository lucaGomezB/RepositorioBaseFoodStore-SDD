import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useCartStore, selectCartItemCount } from '../stores/cartStore';
import { useUIStore } from '../stores/uiStore';
import { apiLogout } from '../api/httpClient';
import Sidebar from './Sidebar';
import { CartDrawer } from '@/features/cart/components/CartDrawer';

export default function AppLayout() {
  const navigate = useNavigate();
  const { user, isLoggedIn, logout } = useAuthStore();
  const itemCount = useCartStore(selectCartItemCount);
  const toggleCartDrawer = useUIStore((s) => s.toggleCartDrawer);

  const handleLogout = async () => {
    try {
      await apiLogout(); // Revoca refresh token + limpia cookies httpOnly
    } catch {
      // Si el logout falla (ej: token ya expirado), igual limpiamos estado local
    }
    logout(); // Limpia estado local + carrito
    navigate('/login', { replace: true });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar (left) */}
      <Sidebar />

      {/* Right side: header + main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top header bar */}
        <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-6 sticky top-0 z-20">
          {/* Spacer to offset mobile hamburger button */}
          <div className="lg:hidden w-8" />

          {/* Right side: cart badge + user info or login link */}
          <div className="flex items-center gap-4 ml-auto">
            {/* Cart badge */}
            <button
              onClick={toggleCartDrawer}
              className="relative p-2 text-gray-600 hover:text-gray-900 transition-colors cursor-pointer"
              aria-label="Abrir carrito"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z" />
              </svg>
              {itemCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-blue-600 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                  {itemCount > 99 ? '99+' : itemCount}
                </span>
              )}
            </button>

            {isLoggedIn && user ? (
              <>
                <span className="text-sm text-gray-700 font-medium">
                  {user.nombre} {user.apellido}
                </span>
                <button
                  onClick={handleLogout}
                  className="text-sm text-red-600 hover:text-red-800 font-medium transition-colors cursor-pointer"
                >
                  Cerrar Sesión
                </button>
              </>
            ) : (
              <Link
                to="/login"
                className="text-sm text-blue-600 hover:text-blue-800 font-medium transition-colors"
              >
                Iniciar Sesión
              </Link>
            )}
          </div>
        </header>

        {/* Page content rendered by active route */}
        <main className="flex-1">
          <Outlet />
        </main>
      </div>

      {/* Floating Cart Button (FAB) */}
      {itemCount > 0 && (
        <button
          onClick={toggleCartDrawer}
          className="fixed bottom-6 right-6 z-30 w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 active:bg-blue-800 transition-colors flex items-center justify-center cursor-pointer"
          aria-label="Abrir carrito flotante"
        >
          <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z" />
          </svg>
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center shadow-md">
            {itemCount > 99 ? '99+' : itemCount}
          </span>
        </button>
      )}

      {/* Cart Drawer */}
      <CartDrawer />
    </div>
  );
}
