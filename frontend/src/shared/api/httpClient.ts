// Axios HTTP client with JWT interceptor and automatic token refresh
import axios, {
  AxiosError,
  InternalAxiosRequestConfig,
} from 'axios';
import { useAuthStore } from '../stores/authStore';
import { handleHttpError } from './errorInterceptor';

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const httpClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ---------------------------------------------------------------------------
// Request interceptor – attach JWT token from authStore
// ---------------------------------------------------------------------------
httpClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { token } = useAuthStore.getState();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// ---------------------------------------------------------------------------
// Response interceptor – on 401, try automatic token refresh with request
// queue so that multiple concurrent 401s only trigger a single refresh call.
// ---------------------------------------------------------------------------
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token!);
    }
  });
  failedQueue = [];
};

// Extend Axios config to carry our custom retry flag
interface RequestConfigWithRetry extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

httpClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RequestConfigWithRetry | undefined;

    // Only handle 401 errors that have a config and haven't been retried yet
    if (
      !originalRequest ||
      error.response?.status !== 401 ||
      originalRequest._retry
    ) {
      // Show toast for non-401 HTTP errors (401 is handled by refresh flow)
      handleHttpError(error);
      return Promise.reject(error);
    }

    // Already refreshing → queue this request to be replayed later
    if (isRefreshing) {
      return new Promise<string>((resolve, reject) => {
        failedQueue.push({
          resolve: (token: string) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            resolve(httpClient(originalRequest));
          },
          reject,
        });
      });
    }

    // Start the refresh flow
    originalRequest._retry = true;
    isRefreshing = true;

    const { refreshToken } = useAuthStore.getState();

    if (!refreshToken) {
      // No refresh token available → force logout
      useAuthStore.getState().logout();
      window.location.href = '/login';
      return Promise.reject(error);
    }

    try {
      const response = await axios.post(`${BASE_URL}/auth/refresh`, {
        refresh_token: refreshToken,
      });

      const { access_token, refresh_token: newRefreshToken } = response.data;
      const { user } = useAuthStore.getState();

      // Update store with fresh tokens (user remains the same)
      useAuthStore.getState().setAuth(access_token, newRefreshToken, user!);

      // Retry the original request with the new token
      if (originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
      }

      // Replay all queued requests
      processQueue(null, access_token);

      return httpClient(originalRequest);
    } catch (refreshError) {
      // Refresh failed → reject all queued and force logout
      processQueue(refreshError, null);
      useAuthStore.getState().logout();
      window.location.href = '/login';
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  },
);
