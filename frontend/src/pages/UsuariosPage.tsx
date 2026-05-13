// UsuariosPage — Admin user management with search, filter, soft-delete, and role assignment
import { useState, useCallback } from 'react';
import {
  useUsuarios,
  useDeleteUsuario,
  useAsignarRol,
} from '../entities/usuarios';
import { useUIStore } from '../shared/stores/uiStore';

const PAGE_SIZE = 10;

// ── Role labels ─────────────────────────────────────────────────────────────

const ROLES: Record<number, string> = {
  1: 'Administrador',
  2: 'Stock',
  3: 'Pedidos',
  4: 'Cliente',
};

// ── Delete Confirmation Dialog ─────────────────────────────────────────────

function DeleteConfirmDialog({
  usuarioNombre,
  onClose,
  onConfirmed,
}: {
  usuarioNombre: string;
  onClose: () => void;
  onConfirmed: () => void;
}) {
  return (
    <div
      className="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded p-6 w-full max-w-sm shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-lg font-bold mb-2">Confirmar eliminación</h2>
        <p className="text-sm text-gray-600 mb-6">
          ¿Estás seguro de que querés desactivar a{' '}
          <span className="font-medium">"{usuarioNombre}"</span>?
          <br />
          El usuario quedará desactivado (soft delete) pero los datos se
          conservan.
        </p>

        <div className="flex gap-2 justify-end">
          <button
            onClick={onClose}
            className="bg-gray-400 text-white px-4 py-2 rounded cursor-pointer hover:bg-gray-500 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={onConfirmed}
            className="bg-red-600 text-white px-4 py-2 rounded cursor-pointer hover:bg-red-700 transition-colors"
          >
            Desactivar
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Assign Role Modal ──────────────────────────────────────────────────────

function AssignRoleModal({
  usuarioId,
  usuarioNombre,
  rolActual,
  onClose,
}: {
  usuarioId: number;
  usuarioNombre: string;
  rolActual: number;
  onClose: () => void;
}) {
  const addToast = useUIStore((s) => s.addToast);
  const asignarRol = useAsignarRol();
  const [selectedRol, setSelectedRol] = useState<number>(rolActual);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (selectedRol === rolActual) {
      onClose();
      return;
    }
    setError(null);
    try {
      await asignarRol.mutateAsync({ id: usuarioId, rol_id: selectedRol });
      addToast({
        type: 'success',
        message: `Rol de "${usuarioNombre}" actualizado a ${ROLES[selectedRol]}`,
      });
      onClose();
    } catch (err) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ||
        (err as Error)?.message ||
        'Error al asignar rol';
      setError(msg);
    }
  };

  return (
    <div
      className="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-white rounded p-6 w-full max-w-sm shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-lg font-bold mb-2">Asignar Rol</h2>
        <p className="text-sm text-gray-600 mb-4">
          Usuario: <span className="font-medium">{usuarioNombre}</span>
        </p>

        <label className="block text-sm font-medium mb-1">Rol</label>
        <select
          value={selectedRol}
          onChange={(e) => setSelectedRol(Number(e.target.value))}
          className="border px-3 py-2 rounded w-full mb-4"
        >
          {Object.entries(ROLES).map(([id, label]) => (
            <option key={id} value={id}>
              {label}
            </option>
          ))}
        </select>

        {error && (
          <p className="text-red-600 text-sm mb-4 bg-red-50 p-2 rounded">
            {error}
          </p>
        )}

        <div className="flex gap-2 justify-end">
          <button
            onClick={onClose}
            className="bg-gray-400 text-white px-4 py-2 rounded cursor-pointer hover:bg-gray-500 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={asignarRol.isPending || selectedRol === rolActual}
            className="bg-blue-600 text-white px-4 py-2 rounded cursor-pointer hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {asignarRol.isPending ? 'Guardando...' : 'Guardar'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Loading Skeleton ───────────────────────────────────────────────────────

function TableSkeleton() {
  return (
    <div className="animate-pulse">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse border">
          <thead>
            <tr className="bg-gray-200">
              {['Nombre', 'Email', 'Rol', 'Activo', 'Fecha creación', 'Acciones'].map(
                (h) => (
                  <th key={h} className="border p-2 text-left">
                    {h}
                  </th>
                ),
              )}
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: 5 }).map((_, i) => (
              <tr key={i} className="hover:bg-gray-100">
                {Array.from({ length: 6 }).map((_, j) => (
                  <td key={j} className="border p-2">
                    <div className="h-4 bg-gray-200 rounded w-3/4" />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────

export default function UsuariosPage() {
  const addToast = useUIStore((s) => s.addToast);

  // Filters & pagination
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState('');
  const [rolFilter, setRolFilter] = useState<number | undefined>(undefined);

  // Modals state
  const [deleteTarget, setDeleteTarget] = useState<{
    id: number;
    nombre: string;
  } | null>(null);

  const [assignRoleTarget, setAssignRoleTarget] = useState<{
    id: number;
    nombre: string;
    rol_id: number;
  } | null>(null);

  // Data fetching
  const { data, isLoading, isError, error } = useUsuarios({
    skip: page * PAGE_SIZE,
    limit: PAGE_SIZE,
    search: search || undefined,
    rol_id: rolFilter,
  });

  const deleteUsuario = useDeleteUsuario();

  // Delete handler
  const handleDelete = useCallback(async () => {
    if (!deleteTarget) return;
    try {
      await deleteUsuario.mutateAsync(deleteTarget.id);
      addToast({
        type: 'success',
        message: `"${deleteTarget.nombre}" desactivado correctamente`,
      });
      setDeleteTarget(null);
    } catch {
      addToast({ type: 'error', message: 'No se pudo desactivar el usuario' });
    }
  }, [deleteTarget, deleteUsuario, addToast]);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Gestión de Usuarios</h1>

      {/* ── Filters ── */}
      <div className="flex gap-3 mb-4 flex-wrap items-center">
        <input
          type="text"
          placeholder="Buscar por nombre o email..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(0);
          }}
          className="border px-3 py-2 rounded w-64"
        />

        <select
          value={rolFilter ?? ''}
          onChange={(e) => {
            setRolFilter(e.target.value ? Number(e.target.value) : undefined);
            setPage(0);
          }}
          className="border px-3 py-2 rounded"
        >
          <option value="">Todos los roles</option>
          {Object.entries(ROLES).map(([id, label]) => (
            <option key={id} value={id}>
              {label}
            </option>
          ))}
        </select>

        {(search || rolFilter !== undefined) && (
          <button
            onClick={() => {
              setSearch('');
              setRolFilter(undefined);
              setPage(0);
            }}
            className="text-sm text-blue-600 hover:text-blue-800 underline cursor-pointer"
          >
            Limpiar filtros
          </button>
        )}
      </div>

      {/* ── Error ── */}
      {isError && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
          {(error as Error)?.message || 'Error al cargar usuarios'}
        </div>
      )}

      {/* ── Table / Skeleton ── */}
      {isLoading ? (
        <TableSkeleton />
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border">
              <thead>
                <tr className="bg-gray-200">
                  <th className="border p-2 text-left">Nombre</th>
                  <th className="border p-2 text-left">Email</th>
                  <th className="border p-2 text-left">Rol</th>
                  <th className="border p-2 text-left">Activo</th>
                  <th className="border p-2 text-left">Fecha creación</th>
                  <th className="border p-2 text-left">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {data?.items && data.items.length > 0 ? (
                  data.items.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-100">
                      <td className="border p-2 font-medium">
                        {user.nombre} {user.apellido}
                      </td>
                      <td className="border p-2 text-gray-600">
                        {user.email}
                      </td>
                      <td className="border p-2">
                        <span className="inline-block bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                          {ROLES[user.rol_id] ?? `Rol ${user.rol_id}`}
                        </span>
                      </td>
                      <td className="border p-2">
                        {user.activo ? (
                          <span className="inline-block bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                            Sí
                          </span>
                        ) : (
                          <span className="inline-block bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                            No
                          </span>
                        )}
                      </td>
                      <td className="border p-2 text-sm text-gray-600">
                        {new Date(user.fecha_creacion).toLocaleDateString(
                          'es-AR',
                          {
                            day: '2-digit',
                            month: 'short',
                            year: 'numeric',
                          },
                        )}
                      </td>
                      <td className="border p-2">
                        <div className="flex gap-1.5">
                          <button
                            onClick={() =>
                              setAssignRoleTarget({
                                id: user.id,
                                nombre: `${user.nombre} ${user.apellido}`,
                                rol_id: user.rol_id,
                              })
                            }
                            className="bg-blue-600 text-white px-2.5 py-1 rounded text-sm cursor-pointer hover:bg-blue-700 transition-colors"
                          >
                            Rol
                          </button>
                          <button
                            onClick={() =>
                              setDeleteTarget({
                                id: user.id,
                                nombre: `${user.nombre} ${user.apellido}`,
                              })
                            }
                            className="bg-red-600 text-white px-2.5 py-1 rounded text-sm cursor-pointer hover:bg-red-700 transition-colors"
                          >
                            Desactivar
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td
                      colSpan={6}
                      className="border p-2 text-center text-gray-500"
                    >
                      {search || rolFilter !== undefined
                        ? 'No se encontraron usuarios con esos filtros'
                        : 'No hay usuarios registrados'}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {/* ── Pagination ── */}
          <div className="flex gap-2 mt-4 items-center">
            <button
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
              className="bg-gray-300 px-3 py-1.5 rounded disabled:opacity-50 cursor-pointer hover:bg-gray-400 transition-colors"
            >
              ← Anterior
            </button>
            <span className="text-sm text-gray-700">Página {page + 1}</span>
            <button
              disabled={!data || data.items.length < PAGE_SIZE}
              onClick={() => setPage((p) => p + 1)}
              className="bg-gray-300 px-3 py-1.5 rounded disabled:opacity-50 cursor-pointer hover:bg-gray-400 transition-colors"
            >
              Siguiente →
            </button>
          </div>

          {/* Total counter */}
          {data && (
            <p className="text-sm text-gray-500 mt-2">
              Mostrando {data.items.length} de {data.total} usuarios
            </p>
          )}
        </>
      )}

      {/* ── Modals ── */}
      {deleteTarget && (
        <DeleteConfirmDialog
          usuarioNombre={deleteTarget.nombre}
          onClose={() => setDeleteTarget(null)}
          onConfirmed={handleDelete}
        />
      )}

      {assignRoleTarget && (
        <AssignRoleModal
          usuarioId={assignRoleTarget.id}
          usuarioNombre={assignRoleTarget.nombre}
          rolActual={assignRoleTarget.rol_id}
          onClose={() => setAssignRoleTarget(null)}
        />
      )}
    </div>
  );
}
