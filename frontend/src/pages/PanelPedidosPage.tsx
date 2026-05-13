// PanelPedidosPage — panel de administración de pedidos (ADMIN/PEDIDOS)
import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { usePedidos, useTransicionarEstado } from '../entities/order';
import { useUIStore } from '../shared/stores/uiStore';

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

// FSM next "advance" state for each state
const NEXT_STATE: Record<string, string> = {
  PENDIENTE: 'CONFIRMADO',
  CONFIRMADO: 'EN_PREPARACION',
  EN_PREPARACION: 'EN_CAMINO',
  EN_CAMINO: 'ENTREGADO',
};

// States where cancellation is allowed
const CANCELABLE_STATES = new Set(['PENDIENTE', 'CONFIRMADO', 'EN_PREPARACION']);

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

export default function PanelPedidosPage() {
  const navigate = useNavigate();
  const addToast = useUIStore((s) => s.addToast);
  const transicionar = useTransicionarEstado();
  const queryClient = useQueryClient();

  const [page, setPage] = useState(0);
  const [estadoFilter, setEstadoFilter] = useState('');
  const [desdeFilter, setDesdeFilter] = useState('');
  const [hastaFilter, setHastaFilter] = useState('');
  const [busquedaFilter, setBusquedaFilter] = useState('');

  const filters = {
    estado: estadoFilter || undefined,
    desde: desdeFilter || undefined,
    hasta: hastaFilter || undefined,
    busqueda: busquedaFilter || undefined,
    skip: page * PAGE_SIZE,
    limit: PAGE_SIZE,
  };

  const { data, isLoading, isError, error } = usePedidos(filters);

  const pedidos = data?.items ?? [];
  const totalCount = data?.total_count ?? 0;
  const totalPages = Math.ceil(totalCount / PAGE_SIZE);

  const handleTransition = useCallback(
    async (pedidoId: number, nuevoEstado: string) => {
      try {
        const rawMotivo = nuevoEstado === 'CANCELADO'
          ? prompt('Motivo de la cancelación:')
          : undefined;

        const motivo = rawMotivo ?? undefined;

        if (nuevoEstado === 'CANCELADO' && !motivo) {
          addToast({ type: 'warning', message: 'Cancelación requiere un motivo' });
          return;
        }

        await transicionar.mutateAsync({ pedidoId, nuevoEstado, motivo });
        addToast({
          type: 'success',
          message: `Pedido #${pedidoId} → ${ESTADO_LABELS[nuevoEstado] ?? nuevoEstado}`,
        });
        queryClient.invalidateQueries({ queryKey: ['pedidos'] });
      } catch (err) {
        const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
          || (err as Error)?.message
          || 'Error al transicionar estado';
        addToast({ type: 'error', message: msg });
      }
    },
    [transicionar, addToast, queryClient],
  );

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Panel de Pedidos</h1>

      {/* ── Filters ── */}
      <div className="flex gap-3 mb-4 flex-wrap items-end">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Estado</label>
          <select
            value={estadoFilter}
            onChange={(e) => {
              setEstadoFilter(e.target.value);
              setPage(0);
            }}
            className="border px-3 py-2 rounded w-40"
          >
            <option value="">Todos</option>
            {Object.entries(ESTADO_LABELS).map(([code, label]) => (
              <option key={code} value={code}>{label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">Desde</label>
          <input
            type="datetime-local"
            value={desdeFilter}
            onChange={(e) => {
              setDesdeFilter(e.target.value);
              setPage(0);
            }}
            className="border px-3 py-2 rounded"
          />
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">Hasta</label>
          <input
            type="datetime-local"
            value={hastaFilter}
            onChange={(e) => {
              setHastaFilter(e.target.value);
              setPage(0);
            }}
            className="border px-3 py-2 rounded"
          />
        </div>

        <div>
          <label className="block text-xs text-gray-500 mb-1">Buscar cliente</label>
          <input
            type="text"
            placeholder="Nombre o apellido..."
            value={busquedaFilter}
            onChange={(e) => {
              setBusquedaFilter(e.target.value);
              setPage(0);
            }}
            className="border px-3 py-2 rounded w-48"
          />
        </div>

        {(estadoFilter || desdeFilter || hastaFilter || busquedaFilter) && (
          <button
            onClick={() => {
              setEstadoFilter('');
              setDesdeFilter('');
              setHastaFilter('');
              setBusquedaFilter('');
              setPage(0);
            }}
            className="text-sm text-blue-600 hover:text-blue-800 underline cursor-pointer mb-0.5"
          >
            Limpiar filtros
          </button>
        )}
      </div>

      {/* ── Error ── */}
      {isError && (
        <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
          {(error as Error)?.message || 'Error al cargar pedidos'}
        </div>
      )}

      {/* ── Loading / Table ── */}
      {isLoading ? (
        <div className="animate-pulse space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="h-12 bg-gray-200 rounded" />
          ))}
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse border">
              <thead>
                <tr className="bg-gray-200">
                  <th className="border p-2 text-left">#</th>
                  <th className="border p-2 text-left">Cliente</th>
                  <th className="border p-2 text-left">Fecha</th>
                  <th className="border p-2 text-left">Estado</th>
                  <th className="border p-2 text-left">Total</th>
                  <th className="border p-2 text-left">Items</th>
                  <th className="border p-2 text-left">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {pedidos.length > 0 ? (
                  pedidos.map((pedido) => {
                    const canAdvance = NEXT_STATE[pedido.estado_codigo] !== undefined;
                    const canCancel = CANCELABLE_STATES.has(pedido.estado_codigo);

                    return (
                      <tr key={pedido.id} className="hover:bg-gray-100">
                        <td className="border p-2 font-medium">#{pedido.id}</td>
                        <td className="border p-2">{pedido.usuario_nombre ?? `ID ${pedido.usuario_id}`}</td>
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
                          <div className="flex gap-1.5 flex-wrap">
                            <button
                              onClick={() => navigate(`/mis-pedidos/${pedido.id}`)}
                              className="bg-blue-600 text-white px-2 py-1 rounded text-xs cursor-pointer hover:bg-blue-700 transition-colors"
                            >
                              Ver
                            </button>
                            {canAdvance && (
                              <button
                                onClick={() => handleTransition(pedido.id, NEXT_STATE[pedido.estado_codigo])}
                                disabled={transicionar.isPending}
                                className="bg-green-600 text-white px-2 py-1 rounded text-xs cursor-pointer hover:bg-green-700 transition-colors disabled:opacity-50"
                              >
                                Adelantar
                              </button>
                            )}
                            {canCancel && (
                              <button
                                onClick={() => handleTransition(pedido.id, 'CANCELADO')}
                                disabled={transicionar.isPending}
                                className="bg-red-600 text-white px-2 py-1 rounded text-xs cursor-pointer hover:bg-red-700 transition-colors disabled:opacity-50"
                              >
                                Cancelar
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={7} className="border p-2 text-center text-gray-500">
                      No se encontraron pedidos con esos filtros
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
              Página {page + 1} de {totalPages || 1} ({totalCount} pedidos)
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
