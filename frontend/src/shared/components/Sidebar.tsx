import { NavLink } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useState } from 'react';

interface NavItem {
  label: string;
  path: string;
  icon: string;
  /** If set, only users with these role IDs can see this item */
  allowedRoles?: number[];
  /** If true, only visible when user is NOT authenticated */
  guestOnly?: boolean;
}

const allNavItems: NavItem[] = [
  // Public (visible to all)
  { label: 'Catálogo', path: '/', icon: '📋' },

  // CLIENT items (roles=[4]) + ADMIN (roles=[1])
  { label: 'Mi Carrito', path: '/carrito', icon: '🛒', allowedRoles: [1, 4] },
  { label: 'Mis Pedidos', path: '/mis-pedidos', icon: '📦', allowedRoles: [1, 4] },
  { label: 'Mi Perfil', path: '/perfil', icon: '👤', allowedRoles: [1, 4] },
  { label: 'Mis Direcciones', path: '/direcciones', icon: '📍', allowedRoles: [1, 4] },

  // STOCK items (roles=[2]) + ADMIN (roles=[1])
  { label: 'Productos', path: '/productos', icon: '🍽️', allowedRoles: [1, 2] },
  { label: 'Categorías', path: '/categorias', icon: '🏷️', allowedRoles: [1, 2] },
  { label: 'Ingredientes', path: '/ingredientes', icon: '🥘', allowedRoles: [1, 2] },
  { label: 'Stock', path: '/stock', icon: '📊', allowedRoles: [1, 2] },

  // PEDIDOS items (roles=[3]) + ADMIN (roles=[1])
  { label: 'Panel de Pedidos', path: '/panel-pedidos', icon: '📋', allowedRoles: [1, 3] },

  // ADMIN-only items
  { label: 'Usuarios', path: '/usuarios', icon: '👥', allowedRoles: [1] },
  { label: 'Métricas', path: '/metricas', icon: '📈', allowedRoles: [1] },
  { label: 'Configuración', path: '/configuracion', icon: '⚙️', allowedRoles: [1] },

  // Guest-only items (visible when NOT authenticated)
  { label: 'Iniciar Sesión', path: '/login', icon: '🔑', guestOnly: true },
  { label: 'Registrarse', path: '/registro', icon: '📝', guestOnly: true },
];

export default function Sidebar() {
  const { user, isLoggedIn } = useAuthStore();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Filter items based on auth status and user role
  const filteredItems = allNavItems.filter((item) => {
    if (!isLoggedIn) {
      // Not logged in: show public + guest-only items
      return !item.allowedRoles || item.guestOnly;
    }
    // Logged in: hide guest-only, show public + role-specific
    if (item.guestOnly) return false;
    if (!item.allowedRoles) return true;
    // Check if user has at least one of the allowed roles
    return item.allowedRoles.some((roleId) => user!.roles.includes(roleId));
  });

  return (
    <>
      {/* Mobile hamburger button */}
      <button
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-gray-800 text-white rounded-md shadow-lg hover:bg-gray-700 transition-colors"
        onClick={() => setMobileOpen(!mobileOpen)}
        aria-label={mobileOpen ? 'Cerrar menú' : 'Abrir menú'}
      >
        {mobileOpen ? (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        )}
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-40 w-64 bg-gray-900 text-white
          transform transition-transform duration-200 ease-in-out
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0 lg:static lg:min-h-screen
          flex flex-col shadow-xl
        `}
      >
        {/* Brand */}
        <div className="h-16 flex items-center px-6 border-b border-gray-700">
          <h1 className="text-xl font-bold tracking-tight">Food Store</h1>
        </div>

        {/* Navigation items */}
        <nav className="flex-1 overflow-y-auto py-4 px-3">
          <ul className="space-y-1">
            {filteredItems.map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  end={item.path === '/'}
                  onClick={() => setMobileOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors
                    ${
                      isActive
                        ? 'bg-blue-600 text-white shadow-sm'
                        : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                    }`
                  }
                >
                  <span className="text-lg flex-shrink-0">{item.icon}</span>
                  <span>{item.label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        {/* Sidebar footer */}
        <div className="p-4 border-t border-gray-700">
          <p className="text-xs text-gray-500">© 2026 Food Store</p>
        </div>
      </aside>
    </>
  );
}
