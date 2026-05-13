// PedidoDetailPage — detalle de pedido con items y timeline de estados
import { useParams, useNavigate } from 'react-router-dom';
import { usePedido, useAdminPedido, usePedidoHistorial } from '../entities/order';
import { useAuthStore } from '../shared/stores/authStore';

const ESTADO_LABELS: Record<string, string> = {
  PENDIENTE: 'Pendiente',
  CONFIRMADO: 'Confirmado',
  EN_PREPARACION: 'En Preparación',
  EN_CAMINO: 'En Camino',
  ENTREGADO: 'Entregado',
  CANCELADO: 'Cancelado',
};

const ESTADO_COLORS: Record<string, string> = {
  PENDIENTE: 'bg-yellow-100 text-yellow-800 border-yellow-400',
  CONFIRMADO: 'bg-blue-100 text-blue-800 border-blue-400',
  EN_PREPARACION: 'bg-indigo-100 text-indigo-800 border-indigo-400',
  EN_CAMINO: 'bg-purple-100 text-purple-800 border-purple-400',
  ENTREGADO: 'bg-green-100 text-green-800 border-green-400',
  CANCELADO: 'bg-red-100 text-red-800 border-red-400',
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

export default function PedidoDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const pedidoId = id ? Number(id) : undefined;

  // Determine if user can see customer contact info
  const { user } = useAuthStore();
  const isAdminOrPedidos = user?.rol_id === 1 || user?.rol_id === 3;

  const { data: pedido, isLoading, isError, error } = usePedido(pedidoId);
  const { data: adminPedido } = useAdminPedido(isAdminOrPedidos ? pedidoId : undefined);
  const { data: historial } = usePedidoHistorial(pedidoId);

  // Merge admin data (includes usuario_email, usuario_telefono) when available
  const displayPedido = adminPedido ?? pedido;

  if (isLoading) {
    return (
      <div className="p-4">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3" />
          <div className="h-40 bg-gray-200 rounded" />
          <div className="h-32 bg-gray-200 rounded" />
        </div>
      </div>
    );
  }

  if (isError || !displayPedido) {
    return (
      <div className="p-4">
        <div className="bg-red-100 text-red-700 p-3 rounded mb-4">
          {(error as Error)?.message || 'Pedido no encontrado'}
        </div>
        <button
          onClick={() => navigate(-1)}
          className="bg-gray-500 text-white px-4 py-2 rounded cursor-pointer hover:bg-gray-600 transition-colors"
        >
          Volver
        </button>
      </div>
    );
  }

  const historyEntries = historial ?? displayPedido.historial_estados;

  return (
    <div className="p-4 max-w-4xl mx-auto">
      {/* ── Header ── */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => navigate(-1)}
          className="bg-gray-400 text-white px-4 py-2 rounded cursor-pointer hover:bg-gray-500 transition-colors text-sm"
        >
          ← Volver
        </button>
        <h1 className="text-2xl font-bold">Pedido #{displayPedido.id}</h1>
        <span
          className={`text-sm font-medium px-3 py-1 rounded-full border ${
            ESTADO_COLORS[displayPedido.estado_codigo] ?? 'bg-gray-100 text-gray-800'
          }`}
        >
          {ESTADO_LABELS[displayPedido.estado_codigo] ?? displayPedido.estado_codigo}
        </span>
      </div>

      {/* ── Customer Info Card (ADMIN/PEDIDOS only) ── */}
      {isAdminOrPedidos && adminPedido && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-3">Datos del Cliente</h2>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Nombre:</span>
              <p className="font-medium">{adminPedido.usuario_nombre || '—'}</p>
            </div>
            <div>
              <span className="text-gray-500">Email:</span>
              <p className="font-medium">{adminPedido.usuario_email || '—'}</p>
            </div>
            <div>
              <span className="text-gray-500">Teléfono:</span>
              <p className="font-medium">{adminPedido.usuario_telefono || '—'}</p>
            </div>
          </div>
        </div>
      )}

      {/* ── Order Info Card ── */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-3">Información del Pedido</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Fecha:</span>
            <p className="font-medium">{formatFecha(displayPedido.created_at)}</p>
          </div>
          <div>
            <span className="text-gray-500">Total:</span>
            <p className="font-medium text-lg">${displayPedido.total.toFixed(2)}</p>
          </div>
          <div>
            <span className="text-gray-500">Costo de envío:</span>
            <p className="font-medium">${displayPedido.costo_envio.toFixed(2)}</p>
          </div>
          <div>
            <span className="text-gray-500">Forma de pago:</span>
            <p className="font-medium">{displayPedido.forma_pago_codigo || 'No especificada'}</p>
          </div>
          <div className="col-span-2">
            <span className="text-gray-500">Dirección de entrega:</span>
            <p className="font-medium">
              {displayPedido.direccion_calle} {displayPedido.direccion_numero}
              {displayPedido.direccion_piso ? `, Piso ${displayPedido.direccion_piso}` : ''}
            </p>
            <p className="text-gray-600">
              {displayPedido.direccion_ciudad}, CP {displayPedido.direccion_cp}
            </p>
          </div>
        </div>
      </div>

      {/* ── Items Table ── */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-3">Items del Pedido</h2>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse border">
            <thead>
              <tr className="bg-gray-100">
                <th className="border p-2 text-left">Producto</th>
                <th className="border p-2 text-left">Precio Unit.</th>
                <th className="border p-2 text-left">Cantidad</th>
                <th className="border p-2 text-left">Exclusiones</th>
                <th className="border p-2 text-left">Subtotal</th>
              </tr>
            </thead>
            <tbody>
              {displayPedido.detalles.map((det) => (
                <tr key={det.id} className="hover:bg-gray-50">
                  <td className="border p-2 font-medium">{det.nombre_snapshot}</td>
                  <td className="border p-2">${det.precio_snapshot.toFixed(2)}</td>
                  <td className="border p-2">{det.cantidad}</td>
                  <td className="border p-2 text-sm">
                    {det.exclusiones.length > 0
                      ? `Sin ingredientes: #${det.exclusiones.join(', #')}`
                      : '—'}
                  </td>
                  <td className="border p-2 font-semibold">${det.subtotal.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="bg-gray-50 font-semibold">
                <td colSpan={4} className="border p-2 text-right">
                  Total (con envío):
                </td>
                <td className="border p-2">${displayPedido.total.toFixed(2)}</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      {/* ── State History Timeline ── */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Historial de Estados</h2>
        {historyEntries.length === 0 ? (
          <p className="text-gray-500 text-sm">Sin historial disponible</p>
        ) : (
          <div className="relative">
            {/* Vertical line */}
            <div className="absolute left-4 top-2 bottom-2 w-0.5 bg-gray-300" />

            <ul className="space-y-6">
              {[...historyEntries].reverse().map((entry, idx) => {
                const isLast = idx === historyEntries.length - 1;
                return (
                  <li key={entry.id} className="relative pl-10">
                    {/* Timeline dot */}
                    <div
                      className={`absolute left-2.5 top-1.5 w-3 h-3 rounded-full border-2 ${
                        isLast
                          ? 'bg-blue-500 border-blue-500'
                          : 'bg-white border-gray-400'
                      }`}
                    />

                    <div className="text-sm">
                      <div className="flex items-center gap-2">
                        {entry.estado_desde && (
                          <>
                            <span className="font-medium text-gray-700">
                              {ESTADO_LABELS[entry.estado_desde] ?? entry.estado_desde}
                            </span>
                            <span className="text-gray-400">→</span>
                          </>
                        )}
                        <span className="font-semibold text-blue-700">
                          {ESTADO_LABELS[entry.estado_hacia] ?? entry.estado_hacia}
                        </span>
                      </div>
                      <p className="text-gray-500 text-xs mt-0.5">{formatFecha(entry.created_at)}</p>
                      {entry.motivo && (
                        <p className="text-gray-600 text-xs mt-1 italic">
                          Motivo: {entry.motivo}
                        </p>
                      )}
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
