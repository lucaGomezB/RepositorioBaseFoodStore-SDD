// KDSColumn — A Kanban-style column for the Kitchen Display System
//
// Renders a title with count badge and a scrollable list of KDSCards.
import type { PedidoCocinaRead } from '../cocina.types';
import { KDSCard } from './KDSCard';

interface KDSColumnProps {
  title: string;
  pedidos: PedidoCocinaRead[];
  onIniciar?: (id: number) => void;
  onTerminar?: (id: number) => void;
  emptyMessage?: string;
}

const COLUMN_BG: Record<string, string> = {
  'Por preparar': 'bg-blue-50',
  'En preparación': 'bg-indigo-50',
};

export function KDSColumn({
  title,
  pedidos,
  onIniciar,
  onTerminar,
  emptyMessage,
}: KDSColumnProps) {
  const bgClass = COLUMN_BG[title] ?? 'bg-gray-50';
  const orderCount = pedidos.length;

  return (
    <div className={`flex flex-col rounded-lg ${bgClass} min-h-[70vh]`}>
      {/* ── Column header ── */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800">{title}</h2>
        <span className="inline-flex items-center justify-center min-w-[1.5rem] h-6 px-1.5 rounded-full bg-gray-800 text-white text-xs font-bold">
          {orderCount}
        </span>
      </div>

      {/* ── Cards list ── */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {orderCount > 0 ? (
          pedidos.map((pedido) => (
            <KDSCard
              key={pedido.id}
              pedido={pedido}
              onIniciar={onIniciar}
              onTerminar={onTerminar}
            />
          ))
        ) : (
          <div className="flex flex-col items-center justify-center py-12 text-gray-400">
            <svg className="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <p className="text-sm font-medium">{emptyMessage ?? 'No hay pedidos'}</p>
          </div>
        )}
      </div>
    </div>
  );
}
