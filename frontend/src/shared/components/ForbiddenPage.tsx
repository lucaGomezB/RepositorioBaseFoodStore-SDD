// ForbiddenPage – 403 Access Denied
import { Link } from 'react-router-dom';

export default function ForbiddenPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="text-center px-6">
        <h1 className="text-7xl font-bold text-gray-300 mb-4">403</h1>
        <p className="text-2xl text-gray-600 mb-2 font-semibold">
          Acceso Denegado
        </p>
        <p className="text-gray-500 mb-8 max-w-md mx-auto">
          No tienes permisos suficientes para acceder a esta página. Si crees
          que esto es un error, contacta al administrador.
        </p>
        <Link
          to="/"
          className="inline-block px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
        >
          Volver al inicio
        </Link>
      </div>
    </div>
  );
}
