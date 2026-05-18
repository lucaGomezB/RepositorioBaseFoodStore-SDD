// MisPedidosPage tests
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import type { ReactElement } from 'react';

// Mock the pedidos hook
vi.mock('../../entities/order/api', () => ({
  usePedidos: vi.fn(),
}));

import MisPedidosPage from '../MisPedidosPage';
import { usePedidos } from '../../entities/order/api';
import type { Mock } from 'vitest';

function renderWithProviders(ui: ReactElement, { route = '/' } = {}) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>
    </QueryClientProvider>,
  );
}

describe('MisPedidosPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockPedidos = {
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

  it('should show loading skeleton', () => {
    (usePedidos as Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
    });

    renderWithProviders(<MisPedidosPage />);

    expect(screen.getByText('Mis Pedidos')).toBeInTheDocument();
    const skeleton = document.querySelector('.animate-pulse');
    expect(skeleton).toBeInTheDocument();
  });

  it('should render pedidos list', () => {
    (usePedidos as Mock).mockReturnValue({
      data: mockPedidos,
      isLoading: false,
      isError: false,
    });

    renderWithProviders(<MisPedidosPage />);

    // Should render table headers
    expect(screen.getByText('# Pedido')).toBeInTheDocument();
    expect(screen.getByText('Fecha')).toBeInTheDocument();
    expect(screen.getByText('Estado')).toBeInTheDocument();
    expect(screen.getByText('Total')).toBeInTheDocument();
    expect(screen.getByText('Items')).toBeInTheDocument();
    expect(screen.getByText('Acción')).toBeInTheDocument();

    // Should render pedido data
    expect(screen.getByText('#1')).toBeInTheDocument();
    expect(screen.getByText('#2')).toBeInTheDocument();
    expect(screen.getByText('$150.00')).toBeInTheDocument();
    expect(screen.getByText('$85.50')).toBeInTheDocument();

    // Should show estado labels (both in filter dropdown and table row)
    expect(screen.getAllByText('Pendiente').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('Entregado').length).toBeGreaterThanOrEqual(1);

    // Should have action buttons
    const buttons = screen.getAllByText('Ver detalle');
    expect(buttons).toHaveLength(2);
  });

  it('should show empty state when no pedidos', () => {
    (usePedidos as Mock).mockReturnValue({
      data: { items: [], total_count: 0 },
      isLoading: false,
      isError: false,
    });

    renderWithProviders(<MisPedidosPage />);

    expect(screen.getByText('No tenés pedidos todavía')).toBeInTheDocument();
  });

  it('should show error message on fetch failure', () => {
    (usePedidos as Mock).mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error('Error de conexión'),
    });

    renderWithProviders(<MisPedidosPage />);

    expect(screen.getByText('Error de conexión')).toBeInTheDocument();
  });

  it('should show pagination info', () => {
    (usePedidos as Mock).mockReturnValue({
      data: {
        items: Array.from({ length: 10 }, (_, i) => ({
          id: i + 1,
          usuario_id: 1,
          estado_codigo: 'PENDIENTE',
          total: 100.00,
          costo_envio: 50.00,
          forma_pago_codigo: null,
          created_at: '2024-06-01T10:00:00Z',
          items_count: 1,
          usuario_nombre: 'User',
        })),
        total_count: 25,
      },
      isLoading: false,
      isError: false,
    });

    renderWithProviders(<MisPedidosPage />);

    // Should show pagination (total_count = 25, page_size = 10 => 3 pages)
    expect(screen.getByText('Página 1 de 3')).toBeInTheDocument();
    expect(screen.getByText('← Anterior')).toBeDisabled();
    expect(screen.getByText('Siguiente →')).not.toBeDisabled();
  });

  it('should show filter options', () => {
    (usePedidos as Mock).mockReturnValue({
      data: mockPedidos,
      isLoading: false,
      isError: false,
    });

    renderWithProviders(<MisPedidosPage />);

    // Filter dropdown should exist
    const filterSelect = screen.getByRole('combobox');
    expect(filterSelect).toBeInTheDocument();
    expect(screen.getByText('Todos los estados')).toBeInTheDocument();
    expect(screen.getAllByText('Pendiente').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('En Preparación')).toBeInTheDocument();
    expect(screen.getAllByText('Entregado').length).toBeGreaterThanOrEqual(1);
  });
});
