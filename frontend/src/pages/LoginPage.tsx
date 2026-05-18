// LoginPage — User authentication with httpOnly cookies
import { useState } from 'react';
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { apiLogin } from '../shared/api/httpClient';
import { useAuthStore } from '../shared/stores/authStore';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const setUser = useAuthStore((s) => s.setUser);

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';
  const registrado = searchParams.get('registrado');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const { user } = await apiLogin({ email, password });
      setUser(user);
      navigate(from, { replace: true });
    } catch (err: unknown) {
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } };
        if (axiosErr.response?.status === 429) {
          setError('Demasiados intentos. Espera un momento antes de reintentar.');
        } else {
          setError(axiosErr.response?.data?.detail || 'Credenciales invalidas');
        }
      } else {
        setError('Error de conexion. Verifica que el servidor este corriendo.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold text-center text-gray-900 mb-6">
          Iniciar Sesion
        </h1>

        {registrado && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-2 rounded mb-4 text-sm text-center">
            Cuenta creada correctamente. Iniciá sesión con tu email y contraseña.
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded mb-4 text-sm text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-gray-300 px-3 py-2 rounded focus:outline-none focus:border-blue-500"
              placeholder="admin@foodstore.com"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Contrasena
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 px-3 py-2 rounded focus:outline-none focus:border-blue-500"
              placeholder="••••••••"
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mt-2 transition-colors cursor-pointer disabled:opacity-50"
          >
            {loading ? 'Entrando...' : 'Entrar'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          ¿No tenes cuenta?{' '}
          <a href="/registro" className="text-blue-600 hover:underline">
            Registrarse
          </a>
        </p>
      </div>
    </div>
  );
};
