// NotFoundPage - 404 page
// Renders standalone (no sidebar) via route configuration
export const NotFoundPage = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-300 mb-4">404</h1>
        <p className="text-xl text-gray-600 mb-2">Página no encontrada</p>
        <p className="text-gray-500">La página que buscas no existe.</p>
      </div>
    </div>
  );
};
