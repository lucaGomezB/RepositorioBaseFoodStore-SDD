// PasswordChangeForm — Form to change the user's password
import { useState } from 'react';
import { useChangePassword } from '@/entities/user';
import { useUIStore } from '@/shared/stores/uiStore';

export function PasswordChangeForm() {
  const changePassword = useChangePassword();

  const [passwordActual, setPasswordActual] = useState('');
  const [passwordNueva, setPasswordNueva] = useState('');
  const [confirmar, setConfirmar] = useState('');
  const [errors, setErrors] = useState<{ password_nueva?: string; confirmar?: string }>({});

  const validate = (): boolean => {
    const newErrors: typeof errors = {};

    if (!passwordActual) {
      // Both old and new password are required
    }

    if (!passwordNueva) {
      newErrors.password_nueva = 'La contraseña nueva es obligatoria';
    } else if (passwordNueva.length < 8) {
      newErrors.password_nueva = 'La contraseña debe tener al menos 8 caracteres';
    }

    if (passwordNueva !== confirmar) {
      newErrors.confirmar = 'Las contraseñas no coinciden';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      await changePassword.mutateAsync({
        password_actual: passwordActual,
        password_nueva: passwordNueva,
      });
      useUIStore.getState().addToast({ type: 'success', message: 'Contraseña actualizada correctamente' });
      // Clear form on success
      setPasswordActual('');
      setPasswordNueva('');
      setConfirmar('');
      setErrors({});
    } catch {
      useUIStore.getState().addToast({ type: 'error', message: 'Error al cambiar la contraseña. Verificá que la contraseña actual sea correcta.' });
    }
  };

  return (
    <section className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">Cambiar Contraseña</h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Contraseña actual */}
        <div>
          <label htmlFor="password-actual" className="block text-sm font-medium text-gray-600 mb-1">
            Contraseña actual
          </label>
          <input
            id="password-actual"
            type="password"
            value={passwordActual}
            onChange={(e) => setPasswordActual(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            required
          />
        </div>

        {/* Contraseña nueva */}
        <div>
          <label htmlFor="password-nueva" className="block text-sm font-medium text-gray-600 mb-1">
            Contraseña nueva
          </label>
          <input
            id="password-nueva"
            type="password"
            value={passwordNueva}
            onChange={(e) => setPasswordNueva(e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none ${
              errors.password_nueva ? 'border-red-400' : 'border-gray-300'
            }`}
            required
          />
          {errors.password_nueva && (
            <p className="text-sm text-red-600 mt-1">{errors.password_nueva}</p>
          )}
        </div>

        {/* Confirmar contraseña */}
        <div>
          <label htmlFor="password-confirmar" className="block text-sm font-medium text-gray-600 mb-1">
            Confirmar contraseña nueva
          </label>
          <input
            id="password-confirmar"
            type="password"
            value={confirmar}
            onChange={(e) => setConfirmar(e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none ${
              errors.confirmar ? 'border-red-400' : 'border-gray-300'
            }`}
            required
          />
          {errors.confirmar && (
            <p className="text-sm text-red-600 mt-1">{errors.confirmar}</p>
          )}
        </div>

        <button
          type="submit"
          disabled={changePassword.isPending}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors cursor-pointer"
        >
          {changePassword.isPending ? 'Cambiando...' : 'Cambiar contraseña'}
        </button>
      </form>
    </section>
  );
}
