// StockPage — Vista de productos con stock bajo y actualización rápida
import { useState, useMemo } from 'react';
import { useProductos, useUpdateStock } from '../entities/product';
import { StockUpdateSchema } from '../entities/product';
import { useUIStore } from '../shared/stores/uiStore';

/* ── Stock Update Modal (reusa lógica del StockUpdateModal de ProductosListPage) ── */
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

/* ── Página principal ── */
export default function StockPage() {
  // Límite de stock bajo (default 10)
  const [limite, setLimite] = useState<number>(10);

  // Stock modal state
  const [stockModal, setStockModal] = useState<{
    id: number;
    nombre: string;
    stock: number;
  } | null>(null);

  // Fetch all products (no pagination for stock management)
  const { data: productos, isLoading, isError, error } = useProductos({
    skip: 0,
    limit: 1000,
  });

  // Filter and sort: only products with stock < limite
  const bajoStock = useMemo(() => {
    if (!productos) return [];
    return productos
      .filter((p) => p.stock_cantidad < limite)
      .sort((a, b) => a.stock_cantidad - b.stock_cantidad);
  }, [productos, limite]);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Stock Bajo</h1>

      {/* ── Limite input ── */}
      <div className="flex items-center gap-3 mb-4">
        <label className="text-sm font-medium" htmlFor="limite-stock">
          Mostrar productos con stock menor a:
        </label>
        <input
          id="limite-stock"
          type="number"
          min={1}
          value={limite}
          onChange={(e) => setLimite(Number(e.target.value) || 1)}
          className="border px-3 py-2 rounded w-24 text-center"
        />
      </div>

      {/* ── Error ── */}
      {isError && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
          {(error as Error)?.message || 'Error al cargar productos'}
        </div>
      )}

      {/* ── Tabla ── */}
      {isLoading ? (
        <p className="text-gray-500">Cargando productos...</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse border">
            <thead>
              <tr className="bg-gray-200">
                <th className="border p-2 text-left">Nombre</th>
                <th className="border p-2 text-left">Stock Actual</th>
                <th className="border p-2 text-left">Precio</th>
                <th className="border p-2 text-left">Disponible</th>
                <th className="border p-2 text-left">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {bajoStock.length > 0 ? (
                bajoStock.map((prod) => (
                  <tr key={prod.id} className="hover:bg-gray-100">
                    <td className="border p-2 font-medium">{prod.nombre}</td>
                    <td className="border p-2">
                      <span
                        className={`font-semibold ${
                          prod.stock_cantidad < 5
                            ? 'text-red-600'
                            : prod.stock_cantidad < 10
                              ? 'text-yellow-600'
                              : 'text-green-700'
                        }`}
                      >
                        {prod.stock_cantidad}
                      </span>
                    </td>
                    <td className="border p-2">${prod.precio_base}</td>
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
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="border p-2 text-center text-gray-500">
                    No hay productos con stock por debajo del límite
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Stock Modal ── */}
      {stockModal && (
        <StockUpdateModal
          productoId={stockModal.id}
          productoNombre={stockModal.nombre}
          stockActual={stockModal.stock}
          onClose={() => setStockModal(null)}
        />
      )}
    </div>
  );
}
