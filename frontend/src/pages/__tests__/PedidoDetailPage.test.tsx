// PedidoDetailPage tests
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import type { ReactElement } from 'react';

// Mock order hooks
vi.mock('../../entities/order/api', () => ({
  usePedido: vi.fn(),
  useAdminPedido: vi.fn(),
  usePedidoHistorial: vi.fn(),
}));

// Mock authStore
vi.mock('../../shared/stores/authStore', () => ({
  useAuthStore: vi.fn(),
}));

import PedidoDetailPage from '../PedidoDetailPage';
import { usePedido, useAdminPedido, usePedidoHistorial } from '../../entities/order/api';
import { useAuthStore } from '../../shared/stores/authStore';
import type { Mock } from 'vitest';

function renderWithProviders(
  ui: ReactElement,
  { route = '/mis-pedidos/1' } = {},
) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]}>
        <Routes>
          <Route path="/mis-pedidos/:id" element={ui} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

const mockPedidoDetail = {
  id: 1,
  usuario_id: 1,
  estado_codigo: 'EN_PREPARACION',
  total: 150.00,
  costo_envio: 50.00,
  forma_pago_codigo: 'MERCADOPAGO',
  created_at: '2024-06-01T10:00:00Z',
  items_count: 2,
  usuario_nombre: 'Test User',
  direccion_calle: 'Av. Corrientes',
  direccion_numero: '1234',
  direccion_piso: '3B',
  direccion_ciudad: 'Buenos Aires',
  direccion_cp: 'C1043',
  detalles: [
    {
      id: 10,
      producto_id: 5,
      nombre_snapshot: 'Hamburguesa Clásica',
      precio_snapshot: 15.00,
      cantidad: 2,
      exclusiones: [3, 7],
      subtotal: 30.00,
    },
  ],
  historial_estados: [
    {
      id: 100,
      estado_desde: null,
      estado_hacia: 'PENDIENTE',
      motivo: null,
      created_at: '2024-06-01T10:00:00Z',
    },
    {
      id: 101,
      estado_desde: 'PENDIENTE',
      estado_hacia: 'CONFIRMADO',
      motivo: null,
      created_at: '2024-06-01T10:05:00Z',
    },
    {
      id: 102,
      estado_desde: 'CONFIRMADO',
      estado_hacia: 'EN_PREPARACION',
      motivo: null,
      created_at: '2024-06-01T10:15:00Z',
    },
  ],
};

describe('PedidoDetailPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Default: user is a regular CLIENT (roles=[2])
    (useAuthStore as Mock).mockReturnValue({
      user: { roles: [2] },
    });
  });

  it('should show loading state', () => {
    (usePedido as Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
    });
    (useAdminPedido as Mock).mockReturnValue({
      data: undefined,
    });
    (usePedidoHistorial as Mock).mockReturnValue({
      data: undefined,
    });

    renderWithProviders(<PedidoDetailPage />);

    // Should show loading skeleton
    const skeleton = document.querySelector('.animate-pulse');
    expect(skeleton).toBeInTheDocument();
  });

  it('should render pedido detail with timeline', () => {
    (usePedido as Mock).mockReturnValue({
      data: mockPedidoDetail,
      isLoading: false,
      isError: false,
    });
    (useAdminPedido as Mock).mockReturnValue({
      data: undefined,
    });
    (usePedidoHistorial as Mock).mockReturnValue({
      data: undefined, // Will use displayPedido.historial_estados
    });

    renderWithProviders(<PedidoDetailPage />);

    // Header
    expect(screen.getByText('Pedido #1')).toBeInTheDocument();
    // "En Preparación" appears both in the status badge and the timeline
    expect(screen.getAllByText('En Preparación').length).toBeGreaterThanOrEqual(1);

    // Order Info section
    expect(screen.getByText('Información del Pedido')).toBeInTheDocument();
    // $150.00 appears both in order info total and table footer
    expect(screen.getAllByText('$150.00').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('$50.00')).toBeInTheDocument(); // Costo envío

    // Address
    expect(screen.getByText('Av. Corrientes 1234, Piso 3B')).toBeInTheDocument();

    // Items
    expect(screen.getByText('Hamburguesa Clásica')).toBeInTheDocument();
    expect(screen.getByText('$15.00')).toBeInTheDocument();
    expect(screen.getByText('$30.00')).toBeInTheDocument(); // Subtotal

    // Timeline
    expect(screen.getByText('Historial de Estados')).toBeInTheDocument();
    // Estado labels appear both in status badge and timeline
    expect(screen.getAllByText('En Preparación').length).toBeGreaterThanOrEqual(1);
  });

  it('should show client info for admin users', () => {
    // Admin user (roles=[1])
    (useAuthStore as Mock).mockReturnValue({
      user: { roles: [1] },
    });

    (usePedido as Mock).mockReturnValue({
      data: mockPedidoDetail,
      isLoading: false,
      isError: false,
    });
    (useAdminPedido as Mock).mockReturnValue({
      data: {
        ...mockPedidoDetail,
        usuario_email: 'cliente@example.com',
        usuario_telefono: '11-5555-1234',
      },
    });
    (usePedidoHistorial as Mock).mockReturnValue({
      data: undefined,
    });

    renderWithProviders(<PedidoDetailPage />);

    // Should show customer info
    expect(screen.getByText('Datos del Cliente')).toBeInTheDocument();
  });

  it('should show error state when pedido not found', () => {
    (usePedido as Mock).mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error('Pedido no encontrado'),
    });
    (useAdminPedido as Mock).mockReturnValue({
      data: undefined,
    });
    (usePedidoHistorial as Mock).mockReturnValue({
      data: undefined,
    });

    renderWithProviders(<PedidoDetailPage />);

    expect(screen.getByText('Pedido no encontrado')).toBeInTheDocument();
    expect(screen.getByText('Volver')).toBeInTheDocument();
  });

  it('should show empty history message when no entries', () => {
    const detailWithoutHistory = {
      ...mockPedidoDetail,
      historial_estados: [],
    };

    (usePedido as Mock).mockReturnValue({
      data: detailWithoutHistory,
      isLoading: false,
      isError: false,
    });
    (useAdminPedido as Mock).mockReturnValue({
      data: undefined,
    });
    (usePedidoHistorial as Mock).mockReturnValue({
      data: [],
    });

    renderWithProviders(<PedidoDetailPage />);

    expect(screen.getByText('Sin historial disponible')).toBeInTheDocument();
  });

  it('should not show customer section for regular client user', () => {
    (useAuthStore as Mock).mockReturnValue({
      user: { roles: [2] }, // CLIENT
    });

    (usePedido as Mock).mockReturnValue({
      data: mockPedidoDetail,
      isLoading: false,
      isError: false,
    });
    (useAdminPedido as Mock).mockReturnValue({
      data: undefined, // Admin query not enabled for CLIENT
    });
    (usePedidoHistorial as Mock).mockReturnValue({
      data: undefined,
    });

    renderWithProviders(<PedidoDetailPage />);

    // Should NOT show customer info for non-admin
    expect(screen.queryByText('Datos del Cliente')).not.toBeInTheDocument();
  });
});
