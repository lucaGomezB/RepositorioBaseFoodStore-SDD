// CardPaymentForm — Secure card payment form using MercadoPago.js
// PCI SAQ-A compliant: card data NEVER reaches our server
import { useEffect, useState, useCallback } from 'react';
import { initMercadoPago, CardPayment } from '@mercadopago/sdk-react';

const MP_PUBLIC_KEY = import.meta.env.VITE_MP_PUBLIC_KEY || '';

interface CardPaymentFormProps {
  /** Called with the card token when the form is submitted successfully */
  onToken: (token: string) => void;
  /** Called when an error occurs during tokenization */
  onError?: (error: string) => void;
  /** Disables the form (e.g., while processing payment) */
  disabled?: boolean;
}

export function CardPaymentForm({ onToken, onError, disabled: _disabled }: CardPaymentFormProps) {
  const [mpReady, setMpReady] = useState(false);
  const [mpError, setMpError] = useState<string | null>(null);

  // Initialize MercadoPago on mount
  useEffect(() => {
    if (!MP_PUBLIC_KEY) {
      setMpError('Falta la clave pública de MercadoPago. Configurá VITE_MP_PUBLIC_KEY en .env');
      return;
    }
    try {
      initMercadoPago(MP_PUBLIC_KEY);
      setMpReady(true);
    } catch {
      setMpError('Error al inicializar MercadoPago');
    }
  }, []);

  const handleReady = useCallback(() => {
    setMpReady(true);
  }, []);

  const handleError = useCallback(
    (error: unknown) => {
      const message = typeof error === 'string' ? error : 'Error en el formulario de pago';
      setMpError(message);
      onError?.(message);
    },
    [onError],
  );

  const handleSubmit = useCallback(
    async (param: unknown) => {
      // CardPayment returns the token via its parameter
      const cardToken = typeof param === 'string' ? param : (param as { token?: string })?.token;
      if (cardToken) {
        onToken(cardToken);
      } else {
        const errorMsg = 'No se pudo generar el token de la tarjeta';
        setMpError(errorMsg);
        onError?.(errorMsg);
      }
    },
    [onToken, onError],
  );

  if (mpError) {
    return (
      <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-red-700">
        <p className="font-medium">Error de pago</p>
        <p className="text-sm mt-1">{mpError}</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {mpReady && (
        <CardPayment
          initialization={{ amount: 0 }}
          onSubmit={handleSubmit}
          onReady={handleReady}
          onError={handleError}
        />
      )}
      {!mpReady && !mpError && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
          <span className="ml-3 text-gray-500">Cargando formulario de pago...</span>
        </div>
      )}
    </div>
  );
}
