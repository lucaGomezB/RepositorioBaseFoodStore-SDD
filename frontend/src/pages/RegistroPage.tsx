// RegistroPage — User registration with auto-assigned CLIENT role
import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { httpClient } from '@/shared/api/httpClient';

interface RegisterForm {
  nombre: string;
  apellido: string;
  email: string;
  password: string;
  confirmar_password: string;
}

interface FormErrors {
  nombre?: string;
  apellido?: string;
  email?: string;
  password?: string;
  confirmar_password?: string;
}

function validarForm(form: RegisterForm): FormErrors {
  const errors: FormErrors = {};

  if (!form.nombre.trim()) errors.nombre = 'El nombre es obligatorio';
  if (!form.apellido.trim()) errors.apellido = 'El apellido es obligatorio';

  if (!form.email.trim()) {
    errors.email = 'El email es obligatorio';
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Email inválido';
  }

  if (!form.password) {
    errors.password = 'La contraseña es obligatoria';
  } else if (form.password.length < 6) {
    errors.password = 'Mínimo 6 caracteres';
  }

  if (form.password !== form.confirmar_password) {
    errors.confirmar_password = 'Las contraseñas no coinciden';
  }

  return errors;
}

export default function RegistroPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState<RegisterForm>({
    nombre: '',
    apellido: '',
    email: '',
    password: '',
    confirmar_password: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setServerError(null);

    const validation = validarForm(form);
    if (Object.keys(validation).length > 0) {
      setErrors(validation);
      return;
    }
    setErrors({});
    setLoading(true);

    try {
      await httpClient.post('/auth/register', {
        nombre: form.nombre.trim(),
        apellido: form.apellido.trim(),
        email: form.email.trim().toLowerCase(),
        password: form.password,
      });
      // Redirect to login with success message
      navigate('/login?registrado=1');
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
        || (err as Error).message
        || 'Error al registrarse';
      setServerError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-6">Crear cuenta</h1>
        <p className="text-sm text-gray-500 text-center mb-6">
          Registrate para empezar a comprar
        </p>

        {serverError && (
          <div className="bg-red-100 border border-red-200 text-red-700 p-3 rounded mb-4 text-sm">
            {serverError}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Nombre</label>
              <input
                type="text"
                value={form.nombre}
                onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
                className={`w-full border px-3 py-2 rounded ${errors.nombre ? 'border-red-500' : 'border-gray-300'}`}
                placeholder="Juan"
              />
              {errors.nombre && <p className="text-red-500 text-xs mt-1">{errors.nombre}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Apellido</label>
              <input
                type="text"
                value={form.apellido}
                onChange={(e) => setForm((f) => ({ ...f, apellido: e.target.value }))}
                className={`w-full border px-3 py-2 rounded ${errors.apellido ? 'border-red-500' : 'border-gray-300'}`}
                placeholder="Pérez"
              />
              {errors.apellido && <p className="text-red-500 text-xs mt-1">{errors.apellido}</p>}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
              className={`w-full border px-3 py-2 rounded ${errors.email ? 'border-red-500' : 'border-gray-300'}`}
              placeholder="juan@ejemplo.com"
            />
            {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Contraseña</label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
              className={`w-full border px-3 py-2 rounded ${errors.password ? 'border-red-500' : 'border-gray-300'}`}
              placeholder="Mínimo 6 caracteres"
            />
            {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Confirmar contraseña</label>
            <input
              type="password"
              value={form.confirmar_password}
              onChange={(e) => setForm((f) => ({ ...f, confirmar_password: e.target.value }))}
              className={`w-full border px-3 py-2 rounded ${errors.confirmar_password ? 'border-red-500' : 'border-gray-300'}`}
              placeholder="Repetí la contraseña"
            />
            {errors.confirmar_password && <p className="text-red-500 text-xs mt-1">{errors.confirmar_password}</p>}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-bold py-2.5 px-4 rounded transition-colors cursor-pointer disabled:opacity-50"
          >
            {loading ? 'Registrando...' : 'Crear cuenta'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-6">
          ¿Ya tenés cuenta?{' '}
          <Link to="/login" className="text-blue-600 hover:underline">
            Iniciar sesión
          </Link>
        </p>
      </div>
    </div>
  );
}
