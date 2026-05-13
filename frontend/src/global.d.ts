// Type declarations for third-party modules without bundled types
declare module '@mercadopago/sdk-react' {
  import type { ReactNode } from 'react';

  export function initMercadoPago(publicKey: string): void;

  interface CardPaymentProps {
    initialization: { amount: number };
    onSubmit?: (token: string | { token?: string }) => void;
    onReady?: () => void;
    onError?: (error: unknown) => void;
  }

  export function CardPayment(props: CardPaymentProps): ReactNode;
}
