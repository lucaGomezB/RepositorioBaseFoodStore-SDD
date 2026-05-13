// ProfileInfo — Displays user profile info with inline edit form
import { useState } from 'react';
import { usePerfil, useUpdatePerfil } from '@/entities/user';
import { useUIStore } from '@/shared/stores/uiStore';

export function ProfileInfo() {
  const { data: user, isLoading, isError, error } = usePerfil();
  const updatePerfil = useUpdatePerfil();

  const [editing, setEditing] = useState(false);
  const [nombre, setNombre] = useState('');
  const [telefono, setTelefono] = useState('');

  // Populate form fields when user data loads or edit is opened
  const startEditing = () => {
    if (!user) return;
    setNombre(user.nombre);
    setTelefono(user.telefono ?? '');
    setEditing(true);
  };

  const cancelEditing = () => {
    setEditing(false);
  };

  const handleSave = async () => {
    try {
      await updatePerfil.mutateAsync({ nombre, telefono: telefono || undefined });
      useUIStore.getState().addToast({ type: 'success', message: 'Perfil actualizado correctamente' });
      setEditing(false);
    } catch {
      useUIStore.getState().addToast({ type: 'error', message: 'Error al actualizar el perfil' });
    }
  };

  // Loading skeleton
  if (isLoading) {
    return (
      <section className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-40 mb-6" />
        <div className="space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i}>
              <div className="h-4 bg-gray-200 rounded w-20 mb-1" />
              <div className="h-5 bg-gray-200 rounded w-full" />
            </div>
          ))}
        </div>
      </section>
    );
  }

  // Error state
  if (isError || !user) {
    return (
      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Información Personal</h2>
        <p className="text-red-600">
          {(error as Error)?.message || 'Error al cargar los datos del perfil'}
        </p>
      </section>
    );
  }

  return (
    <section className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">Información Personal</h2>
        {!editing && (
          <button
            onClick={startEditing}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors cursor-pointer"
          >
            Editar
          </button>
        )}
      </div>

      {editing ? (
        // Inline edit form
        <div className="space-y-4">
          {/* Email — read-only */}
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Email</label>
            <p className="text-gray-900 py-2 px-3 bg-gray-50 rounded-lg">{user.email}</p>
          </div>

          {/* Nombre */}
          <div>
            <label htmlFor="edit-nombre" className="block text-sm font-medium text-gray-600 mb-1">
              Nombre
            </label>
            <input
              id="edit-nombre"
              type="text"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
          </div>

          {/* Teléfono */}
          <div>
            <label htmlFor="edit-telefono" className="block text-sm font-medium text-gray-600 mb-1">
              Teléfono
            </label>
            <input
              id="edit-telefono"
              type="text"
              value={telefono}
              onChange={(e) => setTelefono(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <button
              onClick={handleSave}
              disabled={updatePerfil.isPending}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors cursor-pointer"
            >
              {updatePerfil.isPending ? 'Guardando...' : 'Guardar'}
            </button>
            <button
              onClick={cancelEditing}
              disabled={updatePerfil.isPending}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors cursor-pointer"
            >
              Cancelar
            </button>
          </div>
        </div>
      ) : (
        // Read-only display
        <div className="space-y-4">
          <div>
            <span className="block text-sm font-medium text-gray-600">Email</span>
            <p className="text-gray-900">{user.email}</p>
          </div>
          <div>
            <span className="block text-sm font-medium text-gray-600">Nombre</span>
            <p className="text-gray-900">{user.nombre}</p>
          </div>
          <div>
            <span className="block text-sm font-medium text-gray-600">Teléfono</span>
            <p className="text-gray-900">{user.telefono || '—'}</p>
          </div>
          <div>
            <span className="block text-sm font-medium text-gray-600">Fecha de registro</span>
            <p className="text-gray-900">
              {user.fecha_creacion
                ? new Date(user.fecha_creacion).toLocaleDateString('es-AR', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })
                : '—'}
            </p>
          </div>
        </div>
      )}
    </section>
  );
}
