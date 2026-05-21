// KDSCard — A single order card in the Kitchen Display System
//
// Shows order number, items with dietary exclusions, notes, elapsed time,
// and contextual action buttons.
import type { PedidoCocinaRead } from '../cocina.types';
import { UrgencyTimer } from './UrgencyTimer';

interface KDSCardProps {
  pedido: PedidoCocinaRead;
  onIniciar?: (id: number) => void;
  onTerminar?: (id: number) => void;
}

export function KDSCard({ pedido, onIniciar, onTerminar }: KDSCardProps) {
  const isConfirmado = pedido.estado_codigo === 'CONFIRMADO';
  const isEnPreparacion = pedido.estado_codigo === 'EN_PREPARACION';
  const hasItems = pedido.items.length > 0;
  const hasNotas = pedido.notas && pedido.notas.trim().length > 0;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
      {/* ── Header: order number + timer ── */}
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-bold text-gray-900">
          Pedido #{pedido.numero_pedido}
        </h3>
        <UrgencyTimer tiempoEnCocinaSegundos={pedido.tiempo_en_cocina_segundos} />
      </div>

      {/* ── State badge ── */}
      <div className="mb-3">
        <span
          className={`inline-block text-xs font-semibold px-2.5 py-0.5 rounded-full ${
            isConfirmado
              ? 'bg-blue-100 text-blue-800'
              : 'bg-indigo-100 text-indigo-800'
          }`}
        >
          {isConfirmado ? 'Por preparar' : 'En preparación'}
        </span>
      </div>

      {/* ── Items list ── */}
      {hasItems && (
        <ul className="space-y-1.5 mb-3">
          {pedido.items.map((item, idx) => (
            <li key={idx} className="text-sm">
              <span className="font-medium text-gray-800">
                {item.cantidad}x {item.nombre_producto}
              </span>
              {item.exclusiones.length > 0 && (
                <span className="text-gray-500 ml-1">
                  (sin {item.exclusiones.join(', ')})
                </span>
              )}
            </li>
          ))}
        </ul>
      )}

      {/* ── Notes ── */}
      {hasNotas && (
        <div className="mb-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800">
          <span className="font-medium">Notas: </span>
          {pedido.notas}
        </div>
      )}

      {/* ── Action buttons ── */}
      <div className="flex gap-2 mt-auto pt-2 border-t border-gray-100">
        {isConfirmado && onIniciar && (
          <button
            onClick={() => onIniciar(pedido.id)}
            className="flex-1 bg-green-600 hover:bg-green-700 text-white text-sm font-medium py-2 px-3 rounded-md transition-colors cursor-pointer"
          >
            Iniciar preparación
          </button>
        )}
        {isEnPreparacion && onTerminar && (
          <button
            onClick={() => onTerminar(pedido.id)}
            className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-3 rounded-md transition-colors cursor-pointer"
          >
            Listo — Enviar a delivery
          </button>
        )}
      </div>
    </div>
  );
}
