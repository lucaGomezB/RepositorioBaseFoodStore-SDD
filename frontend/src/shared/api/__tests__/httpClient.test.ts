// httpClient interceptor tests
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useAuthStore } from '../../stores/authStore';
import type { InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

// =========================================================================
// CRITICAL: Mock axios adapter BEFORE any imports to prevent real XHR calls
// =========================================================================
vi.mock('axios', async (importOriginal) => {
  const actual = await importOriginal<typeof import('axios')>();
  const mockAdapter = vi.fn().mockResolvedValue({ data: {} });
  return {
    ...actual,
    default: {
      ...actual.default,
      create: () => {
        const instance = actual.default.create();
        instance.defaults.adapter = mockAdapter;
        return instance;
      },
    },
  };
});

import {
  requestInterceptor,
  responseInterceptorFulfilled,
  responseInterceptorRejected,
  httpClient,
  apiRefresh,
} from '../httpClient';

// Mock handleHttpError from separate module
vi.mock('../errorInterceptor', () => ({
  handleHttpError: vi.fn(),
}));

import { handleHttpError } from '../errorInterceptor';

const originalLocation = window.location;

beforeEach(() => {
  useAuthStore.setState({ accessToken: null, isLoggedIn: false, user: null });
  vi.clearAllMocks();

  // Mock window.location.href
  Object.defineProperty(window, 'location', {
    value: { ...originalLocation, href: '' },
    writable: true,
  });
});

// ===========================================================================
// Test 7.5 — Request interceptor adds Bearer token
// ===========================================================================

describe('httpClient request interceptor (7.5)', () => {
  it('should attach Authorization header when accessToken is present', () => {
    useAuthStore.getState().setAccessToken('my-jwt-token');

    const config: Partial<InternalAxiosRequestConfig> = {
      headers: { Authorization: '' } as any,
    };
    const result = requestInterceptor(config as InternalAxiosRequestConfig);

    expect(result.headers?.Authorization).toBe('Bearer my-jwt-token');
  });

  it('should not attach Authorization header when accessToken is null', () => {
    const config: Partial<InternalAxiosRequestConfig> = {
      headers: {} as any,
    };
    const result = requestInterceptor(config as InternalAxiosRequestConfig);

    expect(result.headers?.Authorization).toBeUndefined();
  });

  it('should return the config unchanged (same reference)', () => {
    useAuthStore.getState().setAccessToken('some-token');

    const config: Partial<InternalAxiosRequestConfig> = {
      headers: {} as any,
    };
    const result = requestInterceptor(config as InternalAxiosRequestConfig);

    expect(result).toBe(config);
  });
});

// ===========================================================================
// Test 7.6 — Response interceptor handles 401 with refresh
// ===========================================================================

describe('httpClient response interceptor (7.6)', () => {
  describe('responseInterceptorFulfilled', () => {
    it('should pass through successful responses unchanged', () => {
      const response = { status: 200, data: {} } as AxiosResponse;
      const result = responseInterceptorFulfilled(response);
      expect(result).toBe(response);
    });
  });

  describe('responseInterceptorRejected', () => {
    const makeError = (status: number, config?: any) => {
      return {
        response: { status, data: {} },
        config: config || { headers: {} },
        isAxiosError: true,
      } as any as AxiosError;
    };

    it('should call handleHttpError for non-401 errors and reject', async () => {
      const error = makeError(400);

      await expect(responseInterceptorRejected(error)).rejects.toThrow();
      expect(handleHttpError).toHaveBeenCalledWith(error);
    });

    it('should call apiRefresh on 401 and retry the original request', async () => {
      const mockConfig = { headers: {}, url: '/protected', method: 'get' };

      useAuthStore.getState().setAccessToken('new-token');

      // Mock apiRefresh to succeed (it uses httpClient.post internally)
      const refreshSpy = vi.spyOn(httpClient, 'post').mockResolvedValue({ data: {} } as any);

      const error = makeError(401, mockConfig);
      const result = await responseInterceptorRejected(error);

      // Verify refresh was attempted
      expect(refreshSpy).toHaveBeenCalledWith('/auth/refresh', {});
      // Verify the retry succeeded (resolves instead of rejecting)
      expect(result).toBeDefined();
    });

    it('should redirect to /login when refresh fails on 401', async () => {
      const mockConfig = { headers: {} };

      // Mock httpClient.post to reject (refresh fails)
      vi.spyOn(httpClient, 'post').mockRejectedValueOnce(new Error('Refresh failed'));

      const error = makeError(401, mockConfig);

      await expect(responseInterceptorRejected(error)).rejects.toThrow();
      expect(window.location.href).toBe('/login');
    });

    it('should queue concurrent 401s and retry them after refresh', async () => {
      const config1 = { headers: {}, url: '/api/1' };
      const config2 = { headers: {}, url: '/api/2' };
      const config3 = { headers: {}, url: '/api/3' };

      useAuthStore.getState().setAccessToken('batch-token');

      // Mock httpClient.post (used by apiRefresh) and httpClient.request (used for retry)
      vi.spyOn(httpClient, 'post').mockResolvedValue({ data: {} } as any);
      vi.spyOn(httpClient, 'request').mockResolvedValue({ data: { ok: true } } as any);

      const error1 = makeError(401, config1);
      const error2 = makeError(401, config2);
      const error3 = makeError(401, config3);

      // Fire all three 401 errors concurrently
      const [r1, r2, r3] = await Promise.allSettled([
        responseInterceptorRejected(error1),
        responseInterceptorRejected(error2),
        responseInterceptorRejected(error3),
      ]);

      // apiRefresh should be called only ONCE (the refresh lock) via httpClient.post
      expect(httpClient.post).toHaveBeenCalledTimes(1);
      expect(httpClient.post).toHaveBeenCalledWith('/auth/refresh', {});

      // All should resolve (since httpClient.request is mocked to resolve)
      expect(r1.status).toBe('fulfilled');
      expect(r2.status).toBe('fulfilled');
      expect(r3.status).toBe('fulfilled');
    });

    it('should not refresh for 401 if _retry flag is set', async () => {
      const mockConfig = { headers: {}, _retry: true };

      const error = makeError(401, mockConfig);

      await expect(responseInterceptorRejected(error)).rejects.toThrow();
      // handleHttpError should be called instead of refresh
      expect(handleHttpError).toHaveBeenCalled();
      expect(httpClient.post).not.toHaveBeenCalledWith('/auth/refresh', {});
    });

    it('should skip 401 handling if error has no response', async () => {
      const error = new Error('Network error') as AxiosError;
      error.config = { headers: {} };

      await expect(responseInterceptorRejected(error)).rejects.toThrow();
      expect(handleHttpError).toHaveBeenCalled();
      expect(httpClient.post).not.toHaveBeenCalledWith('/auth/refresh', {});
    });
  });
});
