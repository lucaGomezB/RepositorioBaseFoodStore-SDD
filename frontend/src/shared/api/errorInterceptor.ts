// HTTP error interceptor – maps Axios errors to toast notifications
import { AxiosError } from 'axios';
import { useUIStore } from '../stores/uiStore';

interface ErrorResponseData {
  detail?: string;
  [key: string]: unknown;
}

/**
 * Maps an HTTP status code to a user-facing toast message.
 */
function getErrorMessage(status: number, data?: ErrorResponseData): string {
  switch (status) {
    case 400:
      return data?.detail || 'Error de validación';
    case 403:
      return 'No tenés permisos para esta acción';
    case 404:
      return 'Recurso no encontrado';
    case 429:
      return 'Demasiadas solicitudes, esperá un momento';
    case 500:
      return 'Error interno, intentá de nuevo más tarde';
    default:
      return 'Ocurrió un error inesperado';
  }
}

/**
 * Processes an error (typically from Axios) and shows a toast notification
 * for relevant HTTP error statuses.
 *
 * - Does NOT handle 401 errors (those are managed by the refresh flow in httpClient).
 * - Only processes errors with an HTTP response (network errors are silently ignored
 *   to avoid noisy toasts on connectivity issues).
 */
export function handleHttpError(error: unknown): void {
  // Ignore non-Axios errors and errors without a response
  if (!(error instanceof AxiosError) || !error.response) {
    return;
  }

  const { status, data } = error.response;

  // Skip 401 errors – those are handled by the httpClient refresh flow
  if (status === 401) {
    return;
  }

  const message = getErrorMessage(status, data as ErrorResponseData | undefined);

  useUIStore.getState().addToast({
    type: 'error',
    message,
  });
}
