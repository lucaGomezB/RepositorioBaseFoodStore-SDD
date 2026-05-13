// MisPedidosPage — lista de pedidos del cliente con filtro y paginación
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { usePedidos } from '../entities/order';

const PAGE_SIZE = 10;

const ESTADO_LABELS: Record<string, string> = {
  PENDIENTE: 'Pendiente',
  CONFIRMADO: 'Confirmado',
  EN_PREPARACION: 'En Preparación',
  EN_CAMINO: 'En Camino',
  ENTREGADO: 'Entregado',
  CANCELADO: 'Cancelado',
};

const ESTADO_COLORS: Record<string, string> = {
  PENDIENTE: 'bg-yellow-100 text-yellow-800',
  CONFIRMADO: 'bg-blue-100 text-blue-800',
  EN_PREPARACION: 'bg-indigo-100 text-indigo-800',
  EN_CAMINO: 'bg-purple-100 text-purple-800',
  ENTREGADO: 'bg-green-100 text-green-800',
  CANCELADO: 'bg-red-100 text-red-800',
};

function formatFecha(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleDateString('es-AR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function LoadingSkeleton() {
  return (
    <div className="animate-pulse space-y-3">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="h-12 bg-gray-200 rounded" />
      ))}
    </div>
  );
}

export default function MisPedidosPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(0);
  const [estadoFilter, setEstadoFilter] = useState<string>('');

  const { data, isLoading, isError, error } = usePedidos({
    estado: estadoFilter || undefined,
    skip: page * PAGE_SIZE,
    limit: PAGE_SIZE,
  });

  const pedidos = data?.items ?? [];
  const totalCount = data?.total_count ?? 0;
  const totalPages = Math.ceil(totalCount / PAGE_SIZE);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Mis Pedidos</h1>

      {/* ── Estado filter ── */}
      <div className="flex gap-3 mb-4 flex-wrap items-center">
        <select
          value={estadoFilter}
          onChange={(e) => {
            setEstadoFilter(e.target.value);
            setPage(0);
          }}
          className="border px-3 py-2 rounded w-48"
        >
          <option value="">Todos los estados</option>
          {Object.entries(ESTADO_LABELS).map(([code, label]) => (
            <option key={code} value={code}>
              {label}
            </option>
          ))}
        </select>

        {estadoFilter && (
          <button
            onClick={() => {
              setEstadoFilter('');
              setPage(0);
            }}
            className="text-sm text-blue-600 hover:text-blue-800 underline cursor-pointer"
          >
            Limpiar filtro
          </button>
        )}
      </div>

      {/* ── Error ── */}
      {isError && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
          {(error as Error)?.message || 'Error al cargar pedidos'}
        </div>
      )}

      {/* ── Table ── */}
      {isLoading ? (
        <LoadingSkeleton />
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border">
              <thead>
                <tr className="bg-gray-200">
                  <th className="border p-2 text-left"># Pedido</th>
                  <th className="border p-2 text-left">Fecha</th>
                  <th className="border p-2 text-left">Estado</th>
                  <th className="border p-2 text-left">Total</th>
                  <th className="border p-2 text-left">Items</th>
                  <th className="border p-2 text-left">Acción</th>
                </tr>
              </thead>
              <tbody>
                {pedidos.length > 0 ? (
                  pedidos.map((pedido) => (
                    <tr key={pedido.id} className="hover:bg-gray-100">
                      <td className="border p-2 font-medium">#{pedido.id}</td>
                      <td className="border p-2 text-sm">{formatFecha(pedido.created_at)}</td>
                      <td className="border p-2">
                        <span
                          className={`inline-block text-xs font-medium px-2.5 py-0.5 rounded-full ${
                            ESTADO_COLORS[pedido.estado_codigo] ?? 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {ESTADO_LABELS[pedido.estado_codigo] ?? pedido.estado_codigo}
                        </span>
                      </td>
                      <td className="border p-2 font-semibold">${pedido.total.toFixed(2)}</td>
                      <td className="border p-2 text-sm">{pedido.items_count}</td>
                      <td className="border p-2">
                        <button
                          onClick={() => navigate(`/mis-pedidos/${pedido.id}`)}
                          className="bg-blue-600 text-white px-3 py-1 rounded text-sm cursor-pointer hover:bg-blue-700 transition-colors"
                        >
                          Ver detalle
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="border p-2 text-center text-gray-500">
                      {estadoFilter
                        ? 'No se encontraron pedidos con ese estado'
                        : 'No tenés pedidos todavía'}
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
            <span className="text-sm text-gray-700">
              Página {page + 1} de {totalPages || 1}
            </span>
            <button
              disabled={page >= totalPages - 1}
              onClick={() => setPage((p) => p + 1)}
              className="bg-gray-300 px-3 py-1.5 rounded disabled:opacity-50 cursor-pointer hover:bg-gray-400 transition-colors"
            >
              Siguiente →
            </button>
          </div>
        </>
      )}
    </div>
  );
}
