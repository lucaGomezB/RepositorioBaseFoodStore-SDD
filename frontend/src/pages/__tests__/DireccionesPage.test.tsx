// DireccionesPage tests — verifies lat/lng UI integration
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import type { ReactElement } from 'react';

// Mock httpClient module
vi.mock('@/shared/api/httpClient', () => ({
  httpClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    patch: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  },
}));

import DireccionesPage from '../DireccionesPage';
import { httpClient } from '@/shared/api/httpClient';

const mockDirecciones = [
  {
    id: 1,
    calle: 'Av. Corrientes',
    numero: '1234',
    piso_depto: '3B',
    ciudad: 'Buenos Aires',
    codigo_postal: 'C1043',
    es_predeterminada: true,
    latitud: -34.6037,
    longitud: -58.3816,
  },
  {
    id: 2,
    calle: 'Av. Santa Fe',
    numero: '5678',
    piso_depto: null,
    ciudad: 'Buenos Aires',
    codigo_postal: 'C1425',
    es_predeterminada: false,
  },
];

function renderWithProviders(ui: ReactElement) {
  return render(<BrowserRouter>{ui}</BrowserRouter>);
}

beforeEach(() => {
  vi.clearAllMocks();
  // Mock GET to return addresses
  (httpClient.get as any).mockResolvedValue({ data: mockDirecciones });
});

describe('DireccionesPage', () => {
  // ── Task 6.4: Coordenadas column in table ──

  it('should display a "Coordenadas" column header in the table', async () => {
    renderWithProviders(<DireccionesPage />);

    await waitFor(() => {
      expect(screen.getByText('Coordenadas')).toBeInTheDocument();
    });
  });

  it('should display lat/lng values in table rows when present', async () => {
    renderWithProviders(<DireccionesPage />);

    await waitFor(() => {
      // The address with lat/lng should show coordinates
      expect(screen.getByText(/-34.6037/)).toBeInTheDocument();
      expect(screen.getByText(/-58.3816/)).toBeInTheDocument();
    });
  });

  it('should display a dash when lat/lng are not present', async () => {
    renderWithProviders(<DireccionesPage />);

    // Open create form
    await waitFor(() => {
      fireEvent.click(screen.getByText('+ Nueva Dirección'));
    });

    // The table row without lat/lng should show '-'
    await waitFor(() => {
      const rows = screen.getAllByRole('row');
      // Second row is the address without lat/lng
      expect(rows[2].textContent).toContain('-');
    });
  });

  // ── Task 6.1: Lat/lng inputs in form ──

  it('should show latitud and longitud input fields when form is open', async () => {
    renderWithProviders(<DireccionesPage />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('+ Nueva Dirección'));
    });

    await waitFor(() => {
      expect(screen.getByPlaceholderText('-34.6037')).toBeInTheDocument();
      expect(screen.getByPlaceholderText('-58.3816')).toBeInTheDocument();
    });
  });

  // ── Task 6.2: "Usar ubicación actual" button ──

  it('should render a "Usar ubicación actual" button in the form', async () => {
    renderWithProviders(<DireccionesPage />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('+ Nueva Dirección'));
    });

    await waitFor(() => {
      expect(screen.getByText('Usar ubicación actual')).toBeInTheDocument();
    });
  });

  // ── Task 6.5: Lat/lng included in create/update payloads ──

  it('should include latitud and longitud when creating an address', async () => {
    (httpClient.post as any).mockResolvedValue({ data: { id: 3 } });

    renderWithProviders(<DireccionesPage />);

    await waitFor(() => {
      fireEvent.click(screen.getByText('+ Nueva Dirección'));
    });

    // Fill required fields
    await waitFor(() => {
      const calleInput = screen.getByPlaceholderText('Av. Corrientes');
      fireEvent.change(calleInput, { target: { value: 'Calle Test' } });
    });

    const numeroInput = screen.getByPlaceholderText('1234');
    fireEvent.change(numeroInput, { target: { value: '999' } });

    const ciudadInput = screen.getByPlaceholderText('Buenos Aires');
    fireEvent.change(ciudadInput, { target: { value: 'La Plata' } });

    const cpInput = screen.getByPlaceholderText('C1043');
    fireEvent.change(cpInput, { target: { value: '1900' } });

    // Set lat/lng
    const latInput = screen.getByPlaceholderText('-34.6037');
    fireEvent.change(latInput, { target: { value: '-34.9214' } });

    const lngInput = screen.getByPlaceholderText('-58.3816');
    fireEvent.change(lngInput, { target: { value: '-57.9545' } });

    // Submit the form
    fireEvent.click(screen.getByText('Guardar'));

    await waitFor(() => {
      expect(httpClient.post).toHaveBeenCalledWith('/direcciones/', expect.objectContaining({
        calle: 'Calle Test',
        numero: '999',
        latitud: -34.9214,
        longitud: -57.9545,
      }));
    });
  });
});
