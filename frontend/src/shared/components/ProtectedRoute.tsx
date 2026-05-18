// ProtectedRoute – guards routes behind authentication + optional role check
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import ForbiddenPage from './ForbiddenPage';

interface ProtectedRouteProps {
  /** If provided, the user's rol_id must be in this list to access the route */
  requiredRoles?: number[];
}

export default function ProtectedRoute({ requiredRoles }: ProtectedRouteProps) {
  const { isLoggedIn, user } = useAuthStore();
  const location = useLocation();

  // Not authenticated → redirect to login
  if (!isLoggedIn) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Authenticated but user data not loaded yet → still render (will fetch via API)
  // This handles the race condition between login redirect and session init
  if (!user) {
    return <Outlet />;
  }

  // Authenticated but insufficient role → 403
  if (requiredRoles && !requiredRoles.includes(user.rol_id)) {
    return <ForbiddenPage />;
  }

  // Authorized → render child routes
  return <Outlet />;
}
