// ProductosListPage — tabla con filtros, stock updater modal y soft delete
import { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { useProductos, useDeleteProducto, useUpdateStock } from '../entities/product';
import { StockUpdateSchema } from '../entities/product';
import { useUIStore } from '../shared/stores/uiStore';

const PAGE_SIZE = 10;

/* ── Stock Update Modal ── */
function StockUpdateModal({
  productoId,
  productoNombre,
  stockActual,
  onClose,
}: {
  productoId: number;
  productoNombre: string;
  stockActual: number;
  onClose: () => void;
}) {
  const addToast = useUIStore((s) => s.addToast);
  const updateStock = useUpdateStock();
  const [cantidad, setCantidad] = useState<string>('');

  const handleSubmit = async () => {
    // Parse and validate
    const parsed = StockUpdateSchema.safeParse({ cantidad: Number(cantidad) });
    if (!parsed.success) {
      addToast({ type: 'error', message: 'Ingresá un número entero válido' });
      return;
    }

    try {
      await updateStock.mutateAsync({ id: productoId, payload: parsed.data });
      addToast({
        type: 'success',
        message: `Stock de "${productoNombre}" actualizado`,
      });
      onClose();
    } catch {
      addToast({ type: 'error', message: 'No se pudo actualizar el stock' });
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
        <h2 className="text-lg font-bold mb-2">Actualizar Stock</h2>
        <p className="text-sm text-gray-600 mb-4">
          Producto: <span className="font-medium">{productoNombre}</span>
          <br />
          Stock actual: <span className="font-medium">{stockActual}</span>
        </p>

        <label className="block text-sm font-medium mb-1">
          Cantidad (positivo = incrementar, negativo = decrementar)
        </label>
        <input
          type="number"
          value={cantidad}
          onChange={(e) => setCantidad(e.target.value)}
          placeholder="ej: 10 o -5"
          className="border px-3 py-2 rounded w-full mb-4"
          autoFocus
        />

        <div className="flex gap-2 justify-end">
          <button
            onClick={onClose}
            className="bg-gray-400 text-white px-4 py-2 rounded cursor-pointer hover:bg-gray-500 transition-colors"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            disabled={updateStock.isPending}
            className="bg-blue-600 text-white px-4 py-2 rounded cursor-pointer hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {updateStock.isPending ? 'Actualizando...' : 'Actualizar'}
          </button>
        </div>

        {updateStock.isError && (
          <p className="text-red-600 text-sm mt-2">
            {(updateStock.error as Error)?.message || 'Error al actualizar stock'}
          </p>
        )}
      </div>
    </div>
  );
}

/* ── Delete Confirmation Dialog ── */
function DeleteConfirmDialog({
  productoNombre,
  onClose,
  onConfirmed,
}: {
  productoNombre: string;
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
          ¿Estás seguro de que querés eliminar <span className="font-medium">"{productoNombre}"</span>?
          <br />
          El producto quedará oculto (soft delete) pero los datos se conservan.
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
            Eliminar
          </button>
        </div>
      </div>
    </div>
  );
}

/* ── Página principal ── */
export default function ProductosListPage() {
  const addToast = useUIStore((s) => s.addToast);

  // Filters
  const [page, setPage] = useState(0);
  const [search, setSearch] = useState('');
  const [disponibleFilter, setDisponibleFilter] = useState<boolean | undefined>(undefined);

  // Stock modal state
  const [stockModal, setStockModal] = useState<{
    id: number;
    nombre: string;
    stock: number;
  } | null>(null);

  // Delete confirm state
  const [deleteTarget, setDeleteTarget] = useState<{
    id: number;
    nombre: string;
  } | null>(null);

  // Data fetching
  const { data: productos, isLoading, isError, error } = useProductos({
    skip: page * PAGE_SIZE,
    limit: PAGE_SIZE,
    busqueda: search || undefined,
    disponible: disponibleFilter,
  });

  const deleteProducto = useDeleteProducto();

  // Handlers
  const handleDelete = useCallback(async () => {
    if (!deleteTarget) return;
    try {
      await deleteProducto.mutateAsync(deleteTarget.id);
      addToast({
        type: 'success',
        message: `"${deleteTarget.nombre}" eliminado correctamente`,
      });
      setDeleteTarget(null);
    } catch {
      addToast({ type: 'error', message: 'No se pudo eliminar el producto' });
    }
  }, [deleteTarget, deleteProducto, addToast]);

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">Gestión de Productos</h1>
        <Link
          to="/productos/nuevo"
          className="bg-green-600 text-white px-4 py-2 rounded cursor-pointer hover:bg-green-700 transition-colors text-sm font-medium"
        >
          + Nuevo Producto
        </Link>
      </div>

      {/* ── Filters ── */}
      <div className="flex gap-3 mb-4 flex-wrap items-center">
        <input
          type="text"
          placeholder="Buscar por nombre..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(0);
          }}
          className="border px-3 py-2 rounded w-64"
        />

        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={disponibleFilter === true}
            onChange={(e) =>
              setDisponibleFilter(e.target.checked ? true : undefined)
            }
            className="rounded"
          />
          Solo disponibles
        </label>

        {(search || disponibleFilter !== undefined) && (
          <button
            onClick={() => {
              setSearch('');
              setDisponibleFilter(undefined);
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
          {(error as Error)?.message || 'Error al cargar productos'}
        </div>
      )}

      {/* ── Table ── */}
      {isLoading ? (
        <p className="text-gray-500">Cargando productos...</p>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border">
              <thead>
                <tr className="bg-gray-200">
                  <th className="border p-2 text-left">Nombre</th>
                  <th className="border p-2 text-left">Precio</th>
                  <th className="border p-2 text-left">Stock</th>
                  <th className="border p-2 text-left">Disponible</th>
                  <th className="border p-2 text-left">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {productos && productos.length > 0 ? (
                  productos.map((prod) => (
                    <tr key={prod.id} className="hover:bg-gray-100">
                      <td className="border p-2 font-medium">{prod.nombre}</td>
                      <td className="border p-2">${prod.precio_base}</td>
                      <td className="border p-2">
                        <span
                          className={`font-semibold ${
                            prod.stock_cantidad <= 0
                              ? 'text-red-600'
                              : prod.stock_cantidad < 10
                                ? 'text-yellow-600'
                                : 'text-green-700'
                          }`}
                        >
                          {prod.stock_cantidad}
                        </span>
                      </td>
                      <td className="border p-2">
                        {prod.disponible ? (
                          <span className="inline-block bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                            Sí
                          </span>
                        ) : (
                          <span className="inline-block bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                            No
                          </span>
                        )}
                      </td>
                      <td className="border p-2">
                        <div className="flex gap-1.5">
                          <Link
                            to={`/productos/${prod.id}/editar`}
                            className="bg-yellow-500 text-white px-2.5 py-1 rounded text-sm cursor-pointer hover:bg-yellow-600 transition-colors"
                          >
                            Editar
                          </Link>
                          <button
                            onClick={() =>
                              setStockModal({
                                id: prod.id,
                                nombre: prod.nombre,
                                stock: prod.stock_cantidad,
                              })
                            }
                            className="bg-blue-600 text-white px-2.5 py-1 rounded text-sm cursor-pointer hover:bg-blue-700 transition-colors"
                          >
                            Stock
                          </button>
                          <button
                            onClick={() =>
                              setDeleteTarget({
                                id: prod.id,
                                nombre: prod.nombre,
                              })
                            }
                            className="bg-red-600 text-white px-2.5 py-1 rounded text-sm cursor-pointer hover:bg-red-700 transition-colors"
                          >
                            Eliminar
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="border p-2 text-center text-gray-500">
                      {search
                        ? 'No se encontraron productos con ese filtro'
                        : 'No hay productos cargados'}
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
              disabled={!productos || productos.length < PAGE_SIZE}
              onClick={() => setPage((p) => p + 1)}
              className="bg-gray-300 px-3 py-1.5 rounded disabled:opacity-50 cursor-pointer hover:bg-gray-400 transition-colors"
            >
              Siguiente →
            </button>
          </div>
        </>
      )}

      {/* ── Modals ── */}
      {stockModal && (
        <StockUpdateModal
          productoId={stockModal.id}
          productoNombre={stockModal.nombre}
          stockActual={stockModal.stock}
          onClose={() => setStockModal(null)}
        />
      )}

      {deleteTarget && (
        <DeleteConfirmDialog
          productoNombre={deleteTarget.nombre}
          onClose={() => setDeleteTarget(null)}
          onConfirmed={handleDelete}
        />
      )}
    </div>
  );
}
