// usePedidos hook tests
import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { httpClient } from '@/shared/api/httpClient';
import { usePedidos } from '../api';
import { createQueryWrapper } from '@/shared/test-utils';
import type { PedidoListResponse } from '../model';
import type { Mock } from 'vitest';

// Mock the httpClient module
vi.mock('@/shared/api/httpClient');

describe('usePedidos', () => {
  const wrapper = createQueryWrapper();

  const mockPedidosResponse: PedidoListResponse = {
    items: [
      {
        id: 1,
        usuario_id: 1,
        estado_codigo: 'PENDIENTE',
        total: 150.00,
        costo_envio: 50.00,
        forma_pago_codigo: 'MERCADOPAGO',
        created_at: '2024-06-01T10:00:00Z',
        items_count: 3,
        usuario_nombre: 'Test User',
      },
      {
        id: 2,
        usuario_id: 1,
        estado_codigo: 'ENTREGADO',
        total: 85.50,
        costo_envio: 50.00,
        forma_pago_codigo: null,
        created_at: '2024-05-15T14:30:00Z',
        items_count: 1,
        usuario_nombre: 'Test User',
      },
    ],
    total_count: 2,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch paginated pedidos without filters', async () => {
    (httpClient.get as Mock).mockResolvedValue({ data: mockPedidosResponse });

    const { result } = renderHook(() => usePedidos(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockPedidosResponse);
    expect(result.current.data?.items).toHaveLength(2);
    expect(httpClient.get).toHaveBeenCalledWith('/pedidos/');
  });

  it('should pass filters as query params', async () => {
    (httpClient.get as Mock).mockResolvedValue({ data: mockPedidosResponse });

    const { result } = renderHook(
      () =>
        usePedidos({
          estado: 'PENDIENTE',
          skip: 0,
          limit: 10,
        }),
      { wrapper },
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(httpClient.get).toHaveBeenCalledWith('/pedidos/?estado=PENDIENTE&skip=0&limit=10');
  });

  it('should handle pagination via skip/limit', async () => {
    (httpClient.get as Mock).mockResolvedValue({ data: { items: [], total_count: 0 } });

    const { result } = renderHook(
      () =>
        usePedidos({
          skip: 10,
          limit: 10,
        }),
      { wrapper },
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(httpClient.get).toHaveBeenCalledWith('/pedidos/?skip=10&limit=10');
  });

  it('should handle empty response', async () => {
    (httpClient.get as Mock).mockResolvedValue({
      data: { items: [], total_count: 0 },
    });

    const { result } = renderHook(() => usePedidos(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data?.items).toHaveLength(0);
    expect(result.current.data?.total_count).toBe(0);
  });

  it('should handle API error', async () => {
    (httpClient.get as Mock).mockRejectedValue(new Error('Failed to fetch'));

    const { result } = renderHook(() => usePedidos(), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBeDefined();
  });
});
