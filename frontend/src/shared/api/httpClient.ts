// Axios HTTP client with httpOnly cookie auth + JWT access token for WebSocket
//
// Las cookies httpOnly se envian automaticamente con cada request
// gracias a `withCredentials: true`.
//
// El request interceptor adjunta el JWT access token en memoria (authStore)
// como Bearer token en el header Authorization.
//
// El response interceptor maneja 401: intenta refresh via apiRefresh(),
// encola requests concurrentes, y si falla redirige a /login.
import axios, { type InternalAxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios';
import { useAuthStore } from '../stores/authStore';
import { handleHttpError } from './errorInterceptor';

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const httpClient = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ===========================================================================
// Interceptors
// ===========================================================================

// ── Request interceptor ──

/**
 * Attaches the JWT access token from authStore to every outgoing request.
 * If no token is available, the request is sent without an Authorization header.
 */
export function requestInterceptor(
  config: InternalAxiosRequestConfig,
): InternalAxiosRequestConfig {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}

httpClient.interceptors.request.use(requestInterceptor);

// ── Response interceptor ──

/** Pass-through for successful responses (2xx). */
export function responseInterceptorFulfilled(response: AxiosResponse): AxiosResponse {
  return response;
}

// Refresh lock — prevents concurrent refresh calls
let isRefreshing = false;
let failedQueue: Array<{ resolve: (token: string | null) => void; reject: (error: unknown) => void }> = [];

/**
 * Processes the queue of requests that arrived while a refresh was in progress.
 * On success, all queued requests resolve with the new token.
 * On failure, all queued requests reject.
 */
function processQueue(error: unknown, token: string | null = null): void {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve(token);
    }
  });
  failedQueue = [];
}

/**
 * Response error interceptor.
 *
 * - 401 errors trigger the refresh flow (apiRefresh) unless already retried.
 * - Non-401 errors are delegated to handleHttpError (toast notifications).
 * - Network errors (no response) are delegated to handleHttpError.
 */
export async function responseInterceptorRejected(
  error: AxiosError,
): Promise<AxiosResponse> {
  const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

  // If there's no request config (e.g. network error before request), delegate and reject
  if (!originalRequest) {
    handleHttpError(error);
    return Promise.reject(error);
  }

  // Handle 401 with refresh flow
  if (error.response?.status === 401 && !originalRequest._retry) {
    if (isRefreshing) {
      // Another refresh is in progress — queue this request
      return new Promise<AxiosResponse>((resolve, reject) => {
        failedQueue.push({
          resolve: (token: string | null) => {
            if (token) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            resolve(httpClient(originalRequest));
          },
          reject,
        });
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      await apiRefresh();
      const newToken = useAuthStore.getState().accessToken;
      processQueue(null, newToken);
      if (newToken) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
      }
      return httpClient(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError, null);
      window.location.href = '/login';
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }

  // Non-401 errors (or already retried 401s) → show toast
  handleHttpError(error);
  return Promise.reject(error);
}

httpClient.interceptors.response.use(
  responseInterceptorFulfilled,
  responseInterceptorRejected,
);

// ===========================================================================
// Auth helpers — funciones explicitas, sin magia en interceptors
// ===========================================================================

export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthUser {
  id: number;
  email: string;
  nombre: string;
  apellido: string;
  roles: number[];
  activo: boolean;
}

export interface LoginResult {
  user: AuthUser;
}

/** Login: POST /auth/login → el backend setea cookies httpOnly + devuelve user */
export async function apiLogin(payload: LoginPayload): Promise<LoginResult> {
  const { data } = await httpClient.post('/auth/login', payload);
  return { user: data.user as AuthUser };
}

/** Refresh: POST /auth/refresh → el backend rota cookies httpOnly */
export async function apiRefresh(): Promise<void> {
  await httpClient.post('/auth/refresh', {});
}

/** Logout: POST /auth/logout → backend revoca refresh token + limpia cookies */
export async function apiLogout(): Promise<void> {
  try {
    await httpClient.post('/auth/logout', {});
  } catch {
    // Si el logout falla (ej: token ya expirado), ignoramos
  }
}

/** Me: GET /auth/me → devuelve el usuario si las cookies son validas */
export async function apiMe(): Promise<AuthUser | null> {
  try {
    const { data } = await httpClient.get('/auth/me');
    return data as AuthUser;
  } catch {
    return null;
  }
}
