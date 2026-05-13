// PaymentStatusCard — Visual feedback for payment status
import type { PaymentStatus } from '../payment.types';

interface PaymentStatusCardProps {
  status: PaymentStatus;
  statusDetail?: string | null;
  onRetry?: () => void;
  onViewOrder?: () => void;
}

const STATUS_CONFIG: Record<
  PaymentStatus,
  {
    icon: string;
    title: string;
    message: string;
    bgColor: string;
    textColor: string;
    borderColor: string;
    action?: 'retry' | 'view_order';
  }
> = {
  processing: {
    icon: '⏳',
    title: 'Procesando pago...',
    message: 'Estamos procesando tu pago. Por favor esperá.',
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-800',
    borderColor: 'border-blue-300',
  },
  pending: {
    icon: '⏳',
    title: 'Pago pendiente',
    message: 'El pago está en proceso. Te notificaremos cuando se confirme.',
    bgColor: 'bg-yellow-50',
    textColor: 'text-yellow-800',
    borderColor: 'border-yellow-300',
    action: 'view_order',
  },
  approved: {
    icon: '✅',
    title: '¡Pago aprobado!',
    message: 'Tu pago fue procesado correctamente. Tu pedido está siendo preparado.',
    bgColor: 'bg-green-50',
    textColor: 'text-green-800',
    borderColor: 'border-green-300',
    action: 'view_order',
  },
  rejected: {
    icon: '❌',
    title: 'Pago rechazado',
    message: 'El pago fue rechazado. Intentá con otro medio de pago.',
    bgColor: 'bg-red-50',
    textColor: 'text-red-800',
    borderColor: 'border-red-300',
    action: 'retry',
  },
  cancelled: {
    icon: '❌',
    title: 'Pago cancelado',
    message: 'El pago fue cancelado.',
    bgColor: 'bg-gray-50',
    textColor: 'text-gray-800',
    borderColor: 'border-gray-300',
    action: 'retry',
  },
};

export function PaymentStatusCard({
  status,
  statusDetail,
  onRetry,
  onViewOrder,
}: PaymentStatusCardProps) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.pending;

  return (
    <div
      className={`rounded-lg border-2 p-6 text-center ${config.bgColor} ${config.borderColor}`}
    >
      <div className="text-5xl mb-4">{config.icon}</div>
      <h2 className={`text-xl font-bold mb-2 ${config.textColor}`}>{config.title}</h2>
      <p className={`text-sm mb-4 ${config.textColor} opacity-80`}>
        {config.message}
      </p>

      {statusDetail && status === 'rejected' && (
        <p className="text-xs text-red-600 mb-4 bg-red-100 rounded px-3 py-2 inline-block">
          {statusDetail}
        </p>
      )}

      {status === 'processing' && (
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" />
        </div>
      )}

      <div className="mt-4 space-x-3">
        {config.action === 'retry' && onRetry && (
          <button
            onClick={onRetry}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Reintentar pago
          </button>
        )}
        {config.action === 'view_order' && onViewOrder && (
          <button
            onClick={onViewOrder}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Ver detalle del pedido
          </button>
        )}
      </div>
    </div>
  );
}
