// AddressManager — List, create, edit, delete, and set default delivery addresses
import { useState } from 'react';
import {
  useDirecciones,
  useCreateDireccion,
  useUpdateDireccion,
  useDeleteDireccion,
  useSetDefaultDireccion,
} from '@/entities/address';
import type { Direccion, DireccionCreate, DireccionUpdate } from '@/entities/address';
import { useUIStore } from '@/shared/stores/uiStore';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type FormState = DireccionCreate & { id?: number };

const emptyForm: FormState = {
  calle: '',
  numero: '',
  piso_depto: '',
  ciudad: '',
  codigo_postal: '',
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formFromDireccion(d: Direccion): FormState {
  return {
    id: d.id,
    calle: d.calle,
    numero: d.numero,
    piso_depto: d.piso_depto ?? '',
    ciudad: d.ciudad,
    codigo_postal: d.codigo_postal,
  };
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function AddressManager() {
  const { data: direcciones, isLoading, isError, error } = useDirecciones();
  const createDireccion = useCreateDireccion();
  const updateDireccion = useUpdateDireccion();
  const deleteDireccion = useDeleteDireccion();
  const setDefaultDireccion = useSetDefaultDireccion();

  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [form, setForm] = useState<FormState>(emptyForm);

  // -----------------------------------------------------------------------
  // Form helpers
  // -----------------------------------------------------------------------

  const resetForm = () => {
    setForm(emptyForm);
    setShowForm(false);
    setEditingId(null);
  };

  const openAddForm = () => {
    setForm(emptyForm);
    setEditingId(null);
    setShowForm(true);
  };

  const openEditForm = (d: Direccion) => {
    setForm(formFromDireccion(d));
    setEditingId(d.id);
    setShowForm(true);
  };

  const handleFieldChange = (field: keyof FormState, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  // -----------------------------------------------------------------------
  // Mutations
  // -----------------------------------------------------------------------

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const payload: DireccionCreate = {
      calle: form.calle,
      numero: form.numero,
      piso_depto: form.piso_depto || undefined,
      ciudad: form.ciudad,
      codigo_postal: form.codigo_postal,
    };

    try {
      if (editingId) {
        const updatePayload: DireccionUpdate = { ...payload };
        await updateDireccion.mutateAsync({ id: editingId, payload: updatePayload });
        useUIStore.getState().addToast({ type: 'success', message: 'Dirección actualizada correctamente' });
      } else {
        await createDireccion.mutateAsync(payload);
        useUIStore.getState().addToast({ type: 'success', message: 'Dirección agregada correctamente' });
      }
      resetForm();
    } catch {
      useUIStore.getState().addToast({
        type: 'error',
        message: editingId ? 'Error al actualizar la dirección' : 'Error al agregar la dirección',
      });
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteDireccion.mutateAsync(id);
      useUIStore.getState().addToast({ type: 'success', message: 'Dirección eliminada correctamente' });
      setDeletingId(null);
    } catch {
      useUIStore.getState().addToast({ type: 'error', message: 'Error al eliminar la dirección' });
    }
  };

  const handleSetDefault = async (id: number) => {
    try {
      await setDefaultDireccion.mutateAsync(id);
      useUIStore.getState().addToast({ type: 'success', message: 'Dirección predeterminada actualizada' });
    } catch {
      useUIStore.getState().addToast({ type: 'error', message: 'Error al establecer dirección predeterminada' });
    }
  };

  // -----------------------------------------------------------------------
  // Render
  // -----------------------------------------------------------------------

  const isPending =
    createDireccion.isPending || updateDireccion.isPending || deleteDireccion.isPending || setDefaultDireccion.isPending;

  // Loading skeleton
  if (isLoading) {
    return (
      <section className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-40 mb-6" />
        <div className="space-y-4">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="border border-gray-200 rounded-lg p-4 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4" />
              <div className="h-4 bg-gray-200 rounded w-1/2" />
            </div>
          ))}
        </div>
      </section>
    );
  }

  // Error state
  if (isError) {
    return (
      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Direcciones</h2>
        <p className="text-red-600">
          {(error as Error)?.message || 'Error al cargar las direcciones'}
        </p>
      </section>
    );
  }

  return (
    <section className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">Direcciones</h2>
        {!showForm && (
          <button
            onClick={openAddForm}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors cursor-pointer"
          >
            Agregar dirección
          </button>
        )}
      </div>

      {/* Add / Edit form */}
      {showForm && (
        <form onSubmit={handleSubmit} className="mb-6 p-4 border border-gray-200 rounded-lg bg-gray-50 space-y-3">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label htmlFor="addr-calle" className="block text-sm font-medium text-gray-600 mb-1">Calle</label>
              <input
                id="addr-calle"
                type="text"
                value={form.calle}
                onChange={(e) => handleFieldChange('calle', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                required
              />
            </div>
            <div>
              <label htmlFor="addr-numero" className="block text-sm font-medium text-gray-600 mb-1">Número</label>
              <input
                id="addr-numero"
                type="text"
                value={form.numero}
                onChange={(e) => handleFieldChange('numero', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                required
              />
            </div>
            <div>
              <label htmlFor="addr-piso" className="block text-sm font-medium text-gray-600 mb-1">Piso / Depto</label>
              <input
                id="addr-piso"
                type="text"
                value={form.piso_depto}
                onChange={(e) => handleFieldChange('piso_depto', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
              />
            </div>
            <div>
              <label htmlFor="addr-ciudad" className="block text-sm font-medium text-gray-600 mb-1">Ciudad</label>
              <input
                id="addr-ciudad"
                type="text"
                value={form.ciudad}
                onChange={(e) => handleFieldChange('ciudad', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                required
              />
            </div>
            <div>
              <label htmlFor="addr-cp" className="block text-sm font-medium text-gray-600 mb-1">Código Postal</label>
              <input
                id="addr-cp"
                type="text"
                value={form.codigo_postal}
                onChange={(e) => handleFieldChange('codigo_postal', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                required
              />
            </div>
          </div>
          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={isPending}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors cursor-pointer"
            >
              {isPending ? 'Guardando...' : editingId ? 'Actualizar' : 'Agregar'}
            </button>
            <button
              type="button"
              onClick={resetForm}
              disabled={isPending}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors cursor-pointer"
            >
              Cancelar
            </button>
          </div>
        </form>
      )}

      {/* Address list */}
      {direcciones && direcciones.length === 0 ? (
        <p className="text-gray-500 text-center py-6">No tenés direcciones registradas.</p>
      ) : (
        <div className="space-y-3">
          {direcciones?.map((direccion) => (
            <div
              key={direccion.id}
              className="flex items-start justify-between p-4 border border-gray-200 rounded-lg"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <p className="font-medium text-gray-900">
                    {direccion.calle} {direccion.numero}
                  </p>
                  {direccion.es_predeterminada && (
                    <span className="px-2 py-0.5 text-xs font-medium text-green-700 bg-green-100 rounded-full">
                      Predeterminada
                    </span>
                  )}
                </div>
                {direccion.piso_depto && (
                  <p className="text-sm text-gray-600">{direccion.piso_depto}</p>
                )}
                <p className="text-sm text-gray-600">
                  {direccion.ciudad} — CP {direccion.codigo_postal}
                </p>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 ml-4">
                {!direccion.es_predeterminada && (
                  <button
                    onClick={() => handleSetDefault(direccion.id)}
                    disabled={isPending}
                    className="px-3 py-1.5 text-xs font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 disabled:opacity-50 transition-colors cursor-pointer"
                    title="Marcar como predeterminada"
                  >
                    Predeterminar
                  </button>
                )}
                <button
                  onClick={() => openEditForm(direccion)}
                  disabled={isPending}
                  className="px-3 py-1.5 text-xs font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:opacity-50 transition-colors cursor-pointer"
                >
                  Editar
                </button>

                {/* Delete confirmation */}
                {deletingId === direccion.id ? (
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => handleDelete(direccion.id)}
                      disabled={isPending}
                      className="px-3 py-1.5 text-xs font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 transition-colors cursor-pointer"
                    >
                      Confirmar
                    </button>
                    <button
                      onClick={() => setDeletingId(null)}
                      className="px-3 py-1.5 text-xs font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors cursor-pointer"
                    >
                      Cancelar
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => setDeletingId(direccion.id)}
                    disabled={isPending}
                    className="px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 disabled:opacity-50 transition-colors cursor-pointer"
                  >
                    Eliminar
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
