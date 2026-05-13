// OrderConfirmationPage — Post-payment status with polling
import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { usePaymentStatus, extractPagoData, extractPagoStatus } from '@/features/payments';
import { PaymentStatusCard } from '@/features/payments';
import { usePedido } from '@/entities/order';

const PAYMENT_KEY = 'pagos';

export default function OrderConfirmationPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const pedidoId = id ? Number(id) : undefined;

  // Poll payment status every 3 seconds
  const query = usePaymentStatus(pedidoId);
  const pago = extractPagoData(query);
  const pagoStatus = extractPagoStatus(pago);

  useEffect(() => {
    if (!pedidoId) return;

    const interval = setInterval(() => {
      queryClient.invalidateQueries({ queryKey: [PAYMENT_KEY, pedidoId] });
    }, 3000);

    // Stop polling when we get a final status
    if (pagoStatus === 'approved' || pagoStatus === 'rejected' || pagoStatus === 'cancelled') {
      clearInterval(interval);
    }

    // Timeout after 2 minutes
    const timeout = setTimeout(() => {
      clearInterval(interval);
    }, 120000);

    return () => {
      clearInterval(interval);
      clearTimeout(timeout);
    };
  }, [pedidoId, queryClient, pagoStatus]);

  // Fetch order details for context
  const { data: pedido, isLoading: isLoadingPedido } = usePedido(pedidoId);

  const handleRetry = () => {
    if (pedidoId) {
      navigate(`/checkout?pedido_id=${pedidoId}`);
    }
  };

  const handleViewOrder = () => {
    if (pedidoId) {
      navigate(`/mis-pedidos/${pedidoId}`);
    }
  };

  // ── Loading state ──
  if (query.isLoading || isLoadingPedido) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-500">Consultando estado del pago...</p>
        </div>
      </div>
    );
  }

  // ── Error state ──
  if (query.isError) {
    return (
      <div className="p-6 flex flex-col items-center justify-center min-h-[60vh]">
        <div className="rounded-lg border border-yellow-300 bg-yellow-50 p-6 text-center max-w-md">
          <div className="text-4xl mb-4">⏳</div>
          <h2 className="text-lg font-bold text-yellow-800 mb-2">
            Pago en proceso
          </h2>
          <p className="text-sm text-yellow-700 mb-4">
            No pudimos verificar el estado del pago. Si ya pagaste, el pedido se
            procesará automáticamente cuando se confirme el pago.
          </p>
          <button
            onClick={handleViewOrder}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Ver detalle del pedido
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 flex flex-col items-center justify-center min-h-[60vh]">
      <div className="max-w-md w-full">
        <PaymentStatusCard
          status={pagoStatus}
          statusDetail={pago?.status_detail}
          onRetry={handleRetry}
          onViewOrder={handleViewOrder}
        />

        {pedido && (
          <div className="mt-4 text-center text-sm text-gray-500">
            <p>Pedido #{pedido.id}</p>
            <p className="text-xs text-gray-400">
              Guardá este número para hacer seguimiento
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
