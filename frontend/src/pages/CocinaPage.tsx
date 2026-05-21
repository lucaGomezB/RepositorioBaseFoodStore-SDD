// CocinaPage — Kitchen Display System main view (US-COCINA-01)
//
// Two-column Kanban layout:
//   "Por preparar"    — orders in CONFIRMADO state
//   "En preparación"  — orders in EN_PREPARACION state
//
// Features:
//   - Real-time updates via WebSocket with 30s polling fallback
//   - Iniciar preparación / Listo buttons trigger PATCH /pedidos/{id}/estado
//   - Sound + visual alerts on new orders (US-COCINA-05)
//   - Connection status indicator
import { useMemo } from 'react';
import { useCocinaWS } from '../features/cocina/hooks/useCocinaWS';
import { KDSColumn } from '../features/cocina/components/KDSColumn';
import { AlertaSonora } from '../features/cocina/components/AlertaSonora';

export default function CocinaPage() {
  const {
    pedidos,
    loading,
    connected,
    error,
    iniciarPreparacion,
    marcarTerminado,
  } = useCocinaWS();

  // ── Split orders by state ────────────────────────────────────────────
  const pendientes = useMemo(
    () => pedidos.filter((p) => p.estado_codigo === 'CONFIRMADO'),
    [pedidos],
  );

  const enPreparacion = useMemo(
    () => pedidos.filter((p) => p.estado_codigo === 'EN_PREPARACION'),
    [pedidos],
  );

  // Count new orders for the sound alert — the number of current CONFIRMADO
  // orders that weren't there before. We use the array length as a proxy;
  // the AlertaSonora component detects increases internally.
  const newOrdersCount = pendientes.length;

  // ── Render ───────────────────────────────────────────────────────────
  return (
    <div className="p-4 h-full flex flex-col">
      {/* ── Header ── */}
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-gray-900">
          Pantalla de Cocina
        </h1>

        {/* Connection status */}
        <div className="flex items-center gap-2">
          <span
            className={`inline-block w-2.5 h-2.5 rounded-full ${
              connected ? 'bg-green-500' : 'bg-yellow-500 animate-pulse'
            }`}
            title={connected ? 'Conectado en tiempo real' : 'Usando polling (30s)'}
          />
          <span className="text-xs text-gray-500 font-medium">
            {connected ? 'Tiempo real' : 'Polling 30s'}
          </span>
        </div>
      </div>

      {/* ── Error banner ── */}
      {error && (
        <div className="mb-4 bg-red-100 border border-red-300 text-red-700 px-4 py-2 rounded-lg text-sm flex items-center gap-2">
          <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>{error}</span>
        </div>
      )}

      {/* ── Loading skeleton ── */}
      {loading ? (
        <div className="flex gap-4 flex-1">
          {[1, 2].map((col) => (
            <div key={col} className="flex-1 bg-gray-100 rounded-lg animate-pulse p-4">
              <div className="h-6 bg-gray-200 rounded w-1/3 mb-4" />
              {[1, 2, 3].map((card) => (
                <div key={card} className="h-32 bg-gray-200 rounded mb-3" />
              ))}
            </div>
          ))}
        </div>
      ) : (
        /* ── Two-column KDS layout ── */
        <div className="flex gap-4 flex-1 min-h-0">
          {/* "Por preparar" column */}
          <div className="flex-1 min-w-0">
            <KDSColumn
              title="Por preparar"
              pedidos={pendientes}
              onIniciar={iniciarPreparacion}
              emptyMessage="No hay pedidos pendientes"
            />
          </div>

          {/* "En preparación" column */}
          <div className="flex-1 min-w-0">
            <KDSColumn
              title="En preparación"
              pedidos={enPreparacion}
              onTerminar={marcarTerminado}
              emptyMessage="No hay pedidos en preparación"
            />
          </div>
        </div>
      )}

      {/* ── Sound alert toggle (floating, bottom-left) ── */}
      <AlertaSonora notificar={newOrdersCount} />
    </div>
  );
}
