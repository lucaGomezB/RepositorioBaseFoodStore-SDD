// MetricasPage tests
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';

// Mock all metricas hooks before importing the page
vi.mock('../../entities/metricas/api', () => ({
  useResumenMetricas: vi.fn(),
  useVentasPorPeriodo: vi.fn(),
  useTopProductos: vi.fn(),
  usePedidosPorEstado: vi.fn(),
}));

import MetricasPage from '../MetricasPage';
import {
  useResumenMetricas,
  useVentasPorPeriodo,
  useTopProductos,
  usePedidosPorEstado,
} from '../../entities/metricas/api';
import type { Mock } from 'vitest';

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
    },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{ui}</BrowserRouter>
    </QueryClientProvider>,
  );
}

describe('MetricasPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should show loading skeleton while fetching data', () => {
    (useResumenMetricas as Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
    });
    (useVentasPorPeriodo as Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
    });
    (useTopProductos as Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
    });
    (usePedidosPorEstado as Mock).mockReturnValue({
      data: undefined,
      isLoading: true,
    });

    renderWithProviders(<MetricasPage />);

    // Should show loading animation (animate-pulse class)
    expect(screen.getByText('Dashboard de Métricas')).toBeInTheDocument();
    // Skeleton should be present (multiple divs with bg-gray-200)
    const skeleton = document.querySelector('.animate-pulse');
    expect(skeleton).toBeInTheDocument();
  });

  it('should render KPI cards with mock data', () => {
    (useResumenMetricas as Mock).mockReturnValue({
      data: {
        total_ventas: 150000.00,
        pedidos_por_estado: [
          { codigo: 'ENTREGADO', nombre: 'Entregado', cantidad: 45 },
          { codigo: 'PENDIENTE', nombre: 'Pendiente', cantidad: 12 },
        ],
        total_usuarios: 89,
        top_productos: [{ nombre: 'Hamburguesa Clásica', cantidad: 120 }],
      },
      isLoading: false,
    });
    (useVentasPorPeriodo as Mock).mockReturnValue({
      data: [],
      isLoading: false,
    });
    (useTopProductos as Mock).mockReturnValue({
      data: [{ nombre: 'Hamburguesa Clásica', cantidad: 120 }],
      isLoading: false,
    });
    (usePedidosPorEstado as Mock).mockReturnValue({
      data: [
        { codigo: 'ENTREGADO', nombre: 'Entregado', cantidad: 45 },
        { codigo: 'PENDIENTE', nombre: 'Pendiente', cantidad: 12 },
      ],
      isLoading: false,
    });

    renderWithProviders(<MetricasPage />);

    // KPI Titles should be visible
    expect(screen.getByText('Ventas Totales')).toBeInTheDocument();
    // Locale es-AR formats as $150.000,00
    expect(screen.getByTitle('$150.000,00')).toBeInTheDocument();
    expect(screen.getByText('Pedidos')).toBeInTheDocument();
    expect(screen.getByText('57')).toBeInTheDocument(); // 45 + 12
    expect(screen.getByText('Usuarios')).toBeInTheDocument();
    expect(screen.getByText('89')).toBeInTheDocument();
    expect(screen.getByText('Top Producto')).toBeInTheDocument();
    expect(screen.getByText('Hamburguesa Clásica')).toBeInTheDocument();

    // Chart titles should be visible
    expect(screen.getByText('Ventas por Período')).toBeInTheDocument();
    expect(screen.getByText('Top 10 Productos')).toBeInTheDocument();
    expect(screen.getByText('Pedidos por Estado')).toBeInTheDocument();
  });

  it('should render with empty/zero KPIs', () => {
    (useResumenMetricas as Mock).mockReturnValue({
      data: {
        total_ventas: 0,
        pedidos_por_estado: [],
        total_usuarios: 0,
        top_productos: [],
      },
      isLoading: false,
    });
    (useVentasPorPeriodo as Mock).mockReturnValue({
      data: [],
      isLoading: false,
    });
    (useTopProductos as Mock).mockReturnValue({
      data: [],
      isLoading: false,
    });
    (usePedidosPorEstado as Mock).mockReturnValue({
      data: [],
      isLoading: false,
    });

    renderWithProviders(<MetricasPage />);

    // Should show default/empty values
    expect(screen.getByTitle('$0,00')).toBeInTheDocument();
    // "0" appears in both Pedidos and Usuarios KPIs
    const zeroElements = screen.getAllByText('0');
    expect(zeroElements.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('—')).toBeInTheDocument(); // Top producto placeholder
  });
});
