// DireccionesPage — CRUD de direcciones de entrega para el usuario autenticado
import { useReducer, useEffect, useCallback, useState } from 'react';
import { httpClient } from '@/shared/api/httpClient';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Direccion {
  id: number;
  calle: string;
  numero: string;
  piso_depto?: string | null;
  ciudad: string;
  codigo_postal: string;
  es_predeterminada: boolean;
  latitud?: number | null;
  longitud?: number | null;
}

interface DireccionForm {
  calle: string;
  numero: string;
  piso_depto: string;
  ciudad: string;
  codigo_postal: string;
  latitud: number | null;
  longitud: number | null;
}

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

interface State {
  items: Direccion[];
  loading: boolean;
  error: string | null;
  editingId: number | null;
  showForm: boolean;
  form: DireccionForm;
}

type Action =
  | { type: 'SET_ITEMS'; payload: Direccion[] }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'START_EDIT'; payload: Direccion }
  | { type: 'START_CREATE' }
  | { type: 'CLOSE_FORM' }
  | { type: 'UPDATE_FORM'; payload: Partial<DireccionForm> };

const emptyForm: DireccionForm = {
  calle: '',
  numero: '',
  piso_depto: '',
  ciudad: '',
  codigo_postal: '',
  latitud: null,
  longitud: null,
};

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'SET_ITEMS':
      return { ...state, items: action.payload, loading: false };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false };
    case 'START_EDIT':
      return {
        ...state,
        editingId: action.payload.id,
        showForm: true,
        form: {
          calle: action.payload.calle,
          numero: action.payload.numero,
          piso_depto: action.payload.piso_depto ?? '',
          ciudad: action.payload.ciudad,
          codigo_postal: action.payload.codigo_postal,
          latitud: action.payload.latitud ?? null,
          longitud: action.payload.longitud ?? null,
        },
      };
    case 'START_CREATE':
      return { ...state, editingId: null, showForm: true, form: emptyForm };
    case 'CLOSE_FORM':
      return { ...state, showForm: false, editingId: null, form: emptyForm };
    case 'UPDATE_FORM':
      return { ...state, form: { ...state.form, ...action.payload } };
    default:
      return state;
  }
}

const init: State = {
  items: [],
  loading: false,
  error: null,
  editingId: null,
  showForm: false,
  form: emptyForm,
};

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function DireccionesPage() {
  const [state, dispatch] = useReducer(reducer, init);
  const [locationLoading, setLocationLoading] = useState(false);
  const [locationError, setLocationError] = useState<string | null>(null);

  // ── Fetch addresses ──

  const fetchData = useCallback(async () => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const { data } = await httpClient.get<Direccion[]>('/direcciones/');
      dispatch({ type: 'SET_ITEMS', payload: data });
    } catch (e) {
      const msg =
        (e as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || (e as Error).message;
      dispatch({ type: 'SET_ERROR', payload: msg });
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // ── Get current location ──

  const handleGetLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setLocationError('Geolocalización no soportada por el navegador');
      return;
    }

    setLocationLoading(true);
    setLocationError(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        dispatch({
          type: 'UPDATE_FORM',
          payload: {
            latitud: position.coords.latitude,
            longitud: position.coords.longitude,
          },
        });
        setLocationLoading(false);
      },
      (error) => {
        switch (error.code) {
          case error.PERMISSION_DENIED:
            setLocationError('Permiso de ubicación denegado');
            break;
          case error.POSITION_UNAVAILABLE:
            setLocationError('Ubicación no disponible');
            break;
          case error.TIMEOUT:
            setLocationError('Tiempo de espera agotado');
            break;
          default:
            setLocationError('Error al obtener ubicación');
            break;
        }
        setLocationLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 },
    );
  }, []);

  // ── Create / Update ──

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const { calle, numero, ciudad, codigo_postal } = state.form;
    if (!calle.trim() || !numero.trim() || !ciudad.trim() || !codigo_postal.trim()) {
      dispatch({
        type: 'SET_ERROR',
        payload: 'Completá todos los campos obligatorios (calle, número, ciudad, código postal)',
      });
      return;
    }
    try {
      const payload: Record<string, unknown> = {
        calle: state.form.calle.trim(),
        numero: state.form.numero.trim(),
        piso_depto: state.form.piso_depto.trim() || null,
        ciudad: state.form.ciudad.trim(),
        codigo_postal: state.form.codigo_postal.trim(),
      };

      // Include lat/lng if set
      if (state.form.latitud !== null) {
        payload.latitud = state.form.latitud;
      }
      if (state.form.longitud !== null) {
        payload.longitud = state.form.longitud;
      }

      if (state.editingId) {
        await httpClient.put(`/direcciones/${state.editingId}`, payload);
      } else {
        await httpClient.post('/direcciones/', payload);
      }
      dispatch({ type: 'CLOSE_FORM' });
      fetchData();
    } catch (err) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || (err as Error).message;
      dispatch({ type: 'SET_ERROR', payload: msg });
    }
  };

  // ── Delete ──

  const handleDelete = async (id: number) => {
    if (!confirm('¿Eliminar esta dirección?')) return;
    try {
      await httpClient.delete(`/direcciones/${id}`);
      fetchData();
    } catch (err) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || (err as Error).message;
      dispatch({ type: 'SET_ERROR', payload: msg });
    }
  };

  // ── Set as default ──

  const handleSetDefault = async (id: number) => {
    try {
      await httpClient.patch(`/direcciones/${id}/predeterminada`);
      fetchData();
    } catch (err) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || (err as Error).message;
      dispatch({ type: 'SET_ERROR', payload: msg });
    }
  };

  // ── Render ──

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Mis Direcciones</h1>

      {/* Error banner */}
      {state.error && (
        <div className="bg-red-100 text-red-700 p-3 mb-4 rounded flex justify-between items-center">
          <span>{state.error}</span>
          <button
            onClick={() => dispatch({ type: 'SET_ERROR', payload: null })}
            className="text-red-500 hover:text-red-700 font-bold cursor-pointer ml-4"
            aria-label="Cerrar error"
          >
            ✕
          </button>
        </div>
      )}

      {/* Actions bar */}
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => dispatch({ type: 'START_CREATE' })}
          className="bg-green-600 text-white px-4 py-1.5 rounded cursor-pointer hover:bg-green-700 transition-colors"
        >
          + Nueva Dirección
        </button>
      </div>

      {/* Inline form */}
      {state.showForm && (
        <form
          onSubmit={handleSubmit}
          className="border border-gray-300 p-4 mb-4 rounded bg-gray-50 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4"
        >
          <div>
            <label className="block text-sm font-medium mb-0.5">
              Calle <span className="text-red-500">*</span>
            </label>
            <input
              value={state.form.calle}
              onChange={(e) =>
                dispatch({ type: 'UPDATE_FORM', payload: { calle: e.target.value } })
              }
              className="border px-2 py-1.5 rounded w-full"
              required
              placeholder="Av. Corrientes"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-0.5">
              Número <span className="text-red-500">*</span>
            </label>
            <input
              value={state.form.numero}
              onChange={(e) =>
                dispatch({ type: 'UPDATE_FORM', payload: { numero: e.target.value } })
              }
              className="border px-2 py-1.5 rounded w-full"
              required
              placeholder="1234"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-0.5">Piso / Depto</label>
            <input
              value={state.form.piso_depto}
              onChange={(e) =>
                dispatch({ type: 'UPDATE_FORM', payload: { piso_depto: e.target.value } })
              }
              className="border px-2 py-1.5 rounded w-full"
              placeholder="3B"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-0.5">
              Ciudad <span className="text-red-500">*</span>
            </label>
            <input
              value={state.form.ciudad}
              onChange={(e) =>
                dispatch({ type: 'UPDATE_FORM', payload: { ciudad: e.target.value } })
              }
              className="border px-2 py-1.5 rounded w-full"
              required
              placeholder="Buenos Aires"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-0.5">
              Código Postal <span className="text-red-500">*</span>
            </label>
            <input
              value={state.form.codigo_postal}
              onChange={(e) =>
                dispatch({ type: 'UPDATE_FORM', payload: { codigo_postal: e.target.value } })
              }
              className="border px-2 py-1.5 rounded w-full"
              required
              placeholder="C1043"
            />
          </div>
          {/* Coordinates */}
          <div>
            <label className="block text-sm font-medium mb-0.5">Latitud</label>
            <div className="flex gap-2 items-center">
              <input
                value={state.form.latitud ?? ''}
                onChange={(e) =>
                  dispatch({
                    type: 'UPDATE_FORM',
                    payload: { latitud: e.target.value === '' ? null : Number(e.target.value) },
                  })
                }
                className="border px-2 py-1.5 rounded w-full"
                placeholder="-34.6037"
                type="number"
                step="any"
              />
              <button
                type="button"
                onClick={handleGetLocation}
                className="bg-purple-600 text-white px-3 py-1.5 rounded text-sm cursor-pointer hover:bg-purple-700 transition-colors whitespace-nowrap"
              >
                {locationLoading ? 'Obteniendo...' : 'Usar ubicación actual'}
              </button>
            </div>
            {locationError && (
              <p className="text-red-500 text-xs mt-1">{locationError}</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium mb-0.5">Longitud</label>
            <input
              value={state.form.longitud ?? ''}
              onChange={(e) =>
                dispatch({
                  type: 'UPDATE_FORM',
                  payload: { longitud: e.target.value === '' ? null : Number(e.target.value) },
                })
              }
              className="border px-2 py-1.5 rounded w-full"
              placeholder="-58.3816"
              type="number"
              step="any"
            />
          </div>
          {/* Form actions */}
          <div className="flex items-end gap-2 sm:col-span-2 lg:col-span-3">
            <button
              type="submit"
              className="bg-blue-600 text-white px-4 py-1.5 rounded cursor-pointer hover:bg-blue-700 transition-colors"
            >
              {state.editingId ? 'Actualizar' : 'Guardar'}
            </button>
            <button
              type="button"
              onClick={() => dispatch({ type: 'CLOSE_FORM' })}
              className="bg-gray-400 text-white px-4 py-1.5 rounded cursor-pointer hover:bg-gray-500 transition-colors"
            >
              Cancelar
            </button>
          </div>
        </form>
      )}

      {/* Loading */}
      {state.loading && (
        <p className="text-gray-500 py-8 text-center">Cargando direcciones...</p>
      )}

      {/* Address list */}
      {!state.loading && state.items.length === 0 && (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg mb-2">No tenés direcciones guardadas</p>
          <p className="text-sm">Hacé clic en "+ Nueva Dirección" para agregar una.</p>
        </div>
      )}

      {!state.loading && state.items.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse border">
            <thead>
              <tr className="bg-gray-200">
                <th className="border p-2 text-left">Dirección</th>
                <th className="border p-2 text-left">Ciudad</th>
                <th className="border p-2 text-left">CP</th>
                <th className="border p-2 text-left">Coordenadas</th>
                <th className="border p-2 text-center">Predeterminada</th>
                <th className="border p-2 text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {state.items.map((dir) => (
                <tr key={dir.id} className="hover:bg-gray-50">
                  <td className="border p-2">
                    {dir.calle} {dir.numero}
                    {dir.piso_depto ? `, ${dir.piso_depto}` : ''}
                  </td>
                  <td className="border p-2">{dir.ciudad}</td>
                  <td className="border p-2">{dir.codigo_postal}</td>
                  <td className="border p-2 text-sm text-gray-600">
                    {dir.latitud != null && dir.longitud != null
                      ? `${dir.latitud.toFixed(4)}, ${dir.longitud.toFixed(4)}`
                      : '-'}
                  </td>
                  <td className="border p-2 text-center">
                    {dir.es_predeterminada ? (
                      <span className="inline-block bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded-full">
                        Predeterminada
                      </span>
                    ) : (
                      <button
                        onClick={() => handleSetDefault(dir.id)}
                        className="text-sm text-blue-600 hover:text-blue-800 underline cursor-pointer"
                        title="Establecer como dirección predeterminada"
                      >
                        Establecer como predeterminada
                      </button>
                    )}
                  </td>
                  <td className="border p-2">
                    <div className="flex gap-1 justify-center">
                      <button
                        onClick={() => dispatch({ type: 'START_EDIT', payload: dir })}
                        className="bg-yellow-500 text-white px-2.5 py-1 rounded text-sm cursor-pointer hover:bg-yellow-600 transition-colors"
                      >
                        Editar
                      </button>
                      <button
                        onClick={() => handleDelete(dir.id)}
                        className="bg-red-600 text-white px-2.5 py-1 rounded text-sm cursor-pointer hover:bg-red-700 transition-colors"
                      >
                        Eliminar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
