// usePerfil hook tests
import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { httpClient } from '@/shared/api/httpClient';
import { usePerfil } from '../api';
import { createQueryWrapper } from '@/shared/test-utils';
import type { User } from '@/shared/types/api';
import type { Mock } from 'vitest';

// Mock the httpClient module
vi.mock('@/shared/api/httpClient');

describe('usePerfil', () => {
  const wrapper = createQueryWrapper();
  const mockUser: User = {
    id: 1,
    email: 'test@example.com',
    nombre: 'Test',
    apellido: 'User',
    telefono: '123456789',
    roles: [1],
    activo: true,
    fecha_creacion: '2024-01-01T00:00:00Z',
    fecha_actualizacion: '2024-01-01T00:00:00Z',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch user profile successfully', async () => {
    (httpClient.get as Mock).mockResolvedValue({ data: mockUser });

    const { result } = renderHook(() => usePerfil(), { wrapper });

    // Initially loading
    expect(result.current.isLoading).toBe(true);

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockUser);
    expect(httpClient.get).toHaveBeenCalledWith('/perfil/');
  });

  it('should handle API error', async () => {
    const error = new Error('Network error');
    (httpClient.get as Mock).mockRejectedValue(error);

    const { result } = renderHook(() => usePerfil(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBeDefined();
    expect(httpClient.get).toHaveBeenCalledWith('/perfil/');
  });

  it('should refetch on mount if query is invalidated', async () => {
    (httpClient.get as Mock).mockResolvedValue({ data: mockUser });

    const { result } = renderHook(() => usePerfil(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(httpClient.get).toHaveBeenCalledTimes(1);
  });
});
