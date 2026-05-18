// useAdminPedidos hook tests
import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { httpClient } from '@/shared/api/httpClient';
import { useAdminPedidos } from '../api';
import { createQueryWrapper } from '@/shared/test-utils';
import type { PedidoListResponse } from '../model';
import type { Mock } from 'vitest';

// Mock the httpClient module
vi.mock('@/shared/api/httpClient');

describe('useAdminPedidos', () => {
  const wrapper = createQueryWrapper();

  const mockAdminResponse: PedidoListResponse = {
    items: [
      {
        id: 10,
        usuario_id: 2,
        estado_codigo: 'EN_PREPARACION',
        total: 220.00,
        costo_envio: 50.00,
        forma_pago_codigo: 'MERCADOPAGO',
        created_at: '2024-06-10T08:00:00Z',
        items_count: 4,
        usuario_nombre: 'Juan Pérez',
        usuario_email: 'juan@example.com',
      },
    ],
    total_count: 1,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch admin pedidos without filters', async () => {
    (httpClient.get as Mock).mockResolvedValue({ data: mockAdminResponse });

    const { result } = renderHook(() => useAdminPedidos(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockAdminResponse);
    expect(httpClient.get).toHaveBeenCalledWith('/admin/pedidos/');
  });

  it('should apply estado filter', async () => {
    (httpClient.get as Mock).mockResolvedValue({ data: mockAdminResponse });

    const { result } = renderHook(
      () => useAdminPedidos({ estado: 'EN_PREPARACION' }),
      { wrapper },
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(httpClient.get).toHaveBeenCalledWith(
      '/admin/pedidos/?estado=EN_PREPARACION',
    );
  });

  it('should apply busqueda (search) filter', async () => {
    (httpClient.get as Mock).mockResolvedValue({ data: { items: [], total_count: 0 } });

    const { result } = renderHook(
      () => useAdminPedidos({ busqueda: 'juan' }),
      { wrapper },
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(httpClient.get).toHaveBeenCalledWith(
      '/admin/pedidos/?busqueda=juan',
    );
  });

  it('should apply date range filters', async () => {
    (httpClient.get as Mock).mockResolvedValue({ data: { items: [], total_count: 0 } });

    const { result } = renderHook(
      () =>
        useAdminPedidos({
          desde: '2024-06-01T00:00:00Z',
          hasta: '2024-06-30T23:59:59Z',
        }),
      { wrapper },
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(httpClient.get).toHaveBeenCalledWith(
      '/admin/pedidos/?desde=2024-06-01T00%3A00%3A00Z&hasta=2024-06-30T23%3A59%3A59Z',
    );
  });

  it('should combine multiple filters', async () => {
    (httpClient.get as Mock).mockResolvedValue({ data: { items: [], total_count: 0 } });

    const { result } = renderHook(
      () =>
        useAdminPedidos({
          estado: 'ENTREGADO',
          skip: 0,
          limit: 25,
          busqueda: 'maria',
        }),
      { wrapper },
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(httpClient.get).toHaveBeenCalledWith(
      '/admin/pedidos/?estado=ENTREGADO&busqueda=maria&skip=0&limit=25',
    );
  });

  it('should handle error response', async () => {
    (httpClient.get as Mock).mockRejectedValue(new Error('Unauthorized'));

    const { result } = renderHook(() => useAdminPedidos(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBeDefined();
  });

  it('should refetch on filter change', async () => {
    (httpClient.get as Mock).mockResolvedValue({ data: { items: [], total_count: 0 } });

    const { rerender } = renderHook(
      ({ estado }: { estado?: string }) => useAdminPedidos({ estado }),
      {
        wrapper,
        initialProps: { estado: 'PENDIENTE' },
      },
    );

    // Change filter
    rerender({ estado: 'CONFIRMADO' });

    await waitFor(() => {
      expect(httpClient.get).toHaveBeenCalledWith(
        '/admin/pedidos/?estado=CONFIRMADO',
      );
    });
  });
});
