// PagoPage — Mock payment page with card form and geolocation
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { httpClient } from '@/shared/api/httpClient';
import { useCartStore, selectCartItems, selectCartTotal } from '@/shared/stores/cartStore';
import { useDirecciones, useCreateDireccion } from '@/entities/address';

interface CrearPedidoPayload {
  items: Array<{
    producto_id: number;
    cantidad: number;
    exclusiones: number[];
  }>;
  direccion_id: number;
  forma_pago_codigo: string;
  latitud?: number;
  longitud?: number;
}

interface CardForm {
  nombre: string;
  numero: string;
  vencimiento: string;
  cvv: string;
}

interface FormErrors {
  nombre?: string;
  numero?: string;
  vencimiento?: string;
  cvv?: string;
  direccion?: string;
  ubicacion?: string;
}

function validarTarjeta(form: CardForm): FormErrors {
  const errors: FormErrors = {};
  const now = new Date();

  // Cardholder name
  if (!form.nombre.trim()) {
    errors.nombre = 'El nombre del titular es obligatorio';
  }

  // Card number: remove non-digits, must be exactly 16 digits
  const digitos = form.numero.replace(/\D/g, '');
  if (digitos.length !== 16) {
    errors.numero = 'El número de tarjeta debe tener exactamente 16 dígitos';
  }

  // Expiry: MM/YY format, must be future
  const vencMatch = form.vencimiento.trim().match(/^(\d{1,2})\/(\d{2})$/);
  if (!vencMatch) {
    errors.vencimiento = 'Formato inválido. Usá MM/AA';
  } else {
    const mes = parseInt(vencMatch[1], 10);
    const anio = 2000 + parseInt(vencMatch[2], 10);
    if (mes < 1 || mes > 12) {
      errors.vencimiento = 'Mes inválido (1-12)';
    } else {
      const venc = new Date(anio, mes, 0);
      if (venc < now) {
        errors.vencimiento = 'La tarjeta está vencida';
      }
    }
  }

  // CVV: exactly 3 digits
  if (!/^\d{3}$/.test(form.cvv)) {
    errors.cvv = 'El CVV debe tener 3 dígitos';
  }

  return errors;
}

// ---------------------------------------------------------------------------
// Inline address creation form (shared between empty / has-addresses states)
// ---------------------------------------------------------------------------
function AddressInlineForm({
  values,
  onChange,
  onSave,
  isSaving,
}: {
  values: {
    calle: string;
    numero: string;
    piso_depto: string;
    ciudad: string;
    codigo_postal: string;
  };
  onChange: (v: typeof values) => void;
  onSave: () => Promise<void>;
  isSaving: boolean;
}) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      <div className="sm:col-span-2">
        <label className="block text-xs font-medium mb-1">Calle</label>
        <input
          type="text"
          value={values.calle}
          onChange={(e) => onChange({ ...values, calle: e.target.value })}
          className="w-full border border-gray-300 px-2 py-1.5 rounded text-sm"
        />
      </div>
      <div>
        <label className="block text-xs font-medium mb-1">Número</label>
        <input
          type="text"
          value={values.numero}
          onChange={(e) => onChange({ ...values, numero: e.target.value })}
          className="w-full border border-gray-300 px-2 py-1.5 rounded text-sm"
        />
      </div>
      <div>
        <label className="block text-xs font-medium mb-1">
          Piso/Depto (opcional)
        </label>
        <input
          type="text"
          value={values.piso_depto}
          onChange={(e) => onChange({ ...values, piso_depto: e.target.value })}
          className="w-full border border-gray-300 px-2 py-1.5 rounded text-sm"
        />
      </div>
      <div>
        <label className="block text-xs font-medium mb-1">Ciudad</label>
        <input
          type="text"
          value={values.ciudad}
          onChange={(e) => onChange({ ...values, ciudad: e.target.value })}
          className="w-full border border-gray-300 px-2 py-1.5 rounded text-sm"
        />
      </div>
      <div>
        <label className="block text-xs font-medium mb-1">Código Postal</label>
        <input
          type="text"
          value={values.codigo_postal}
          onChange={(e) => onChange({ ...values, codigo_postal: e.target.value })}
          className="w-full border border-gray-300 px-2 py-1.5 rounded text-sm"
        />
      </div>
      <div className="sm:col-span-2">
        <button
          type="button"
          onClick={onSave}
          disabled={
            isSaving || !values.calle.trim() || !values.numero.trim() || !values.ciudad.trim() || !values.codigo_postal.trim()
          }
          className="w-full bg-blue-600 text-white py-2 rounded text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSaving ? 'Guardando...' : 'Guardar dirección'}
        </button>
      </div>
    </div>
  );
}

export default function PagoPage() {
  const navigate = useNavigate();
  const items = useCartStore(selectCartItems);
  const total = useCartStore(selectCartTotal);
  const clearCart = useCartStore((s) => s.clearCart);

  const { data: direcciones, isLoading: loadingDirecciones } = useDirecciones();

  const [form, setForm] = useState<CardForm>({
    nombre: '',
    numero: '',
    vencimiento: '',
    cvv: '',
  });
  const [direccionId, setDireccionId] = useState<number>(0);
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [ubicacion, setUbicacion] = useState<{ lat: number; lng: number } | null>(null);
  const [ubicacionError, setUbicacionError] = useState<string | null>(null);
  const [showAddressForm, setShowAddressForm] = useState(false);
  const queryClient = useQueryClient();
  const createDireccion = useCreateDireccion();
  const [newAddress, setNewAddress] = useState<{
    calle: string;
    numero: string;
    piso_depto: string;
    ciudad: string;
    codigo_postal: string;
  }>({
    calle: '',
    numero: '',
    piso_depto: '',
    ciudad: '',
    codigo_postal: '',
  });

  // Get geolocation on mount
  useEffect(() => {
    if (!navigator.geolocation) {
      setUbicacionError('Geolocalización no soportada por el navegador');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setUbicacion({ lat: pos.coords.latitude, lng: pos.coords.longitude });
        setUbicacionError(null);
      },
      (err) => {
        setUbicacionError(
          'No se pudo obtener la ubicación. Permití el acceso a la ubicación o ingresala manualmente.',
        );
        console.warn('Geolocation error:', err.message);
      },
      { timeout: 10000, enableHighAccuracy: true },
    );
  }, []);

  const createOrder = useMutation({
    mutationFn: async (payload: CrearPedidoPayload) => {
      const { data } = await httpClient.post<{ id: number }>('/pedidos/', payload);
      return data;
    },
    onSuccess: async (data) => {
      try {
        // Call mock payment endpoint so the confirmation page can find a Pago
        await httpClient.post('/pagos/mock', { pedido_id: data.id });
      } catch {
        // Mock payment might fail, but we still want to proceed
        console.warn('Mock payment warning');
      }
      clearCart();
      navigate(`/pedidos/${data.id}/confirmacion`);
    },
    onError: (err: unknown) => {
      const axiosError = err as {
        response?: { data?: { detail?: string } };
        message?: string;
        code?: string;
      };
      if (axiosError?.response) {
        // Server responded with error detail
        const detail = axiosError.response.data?.detail;
        setSubmitError(detail || 'Error del servidor');
      } else if (axiosError?.message) {
        // Network error — no response received
        setSubmitError(`Error de conexión: ${axiosError.message}`);
      } else {
        setSubmitError('Error al crear el pedido');
      }
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setSubmitError(null);

    // Validate address
    if (!direccionId || direccionId === 0) {
      setErrors({ direccion: 'Seleccioná una dirección de entrega' });
      return;
    }

    // Validate card
    const cardErrors = validarTarjeta(form);
    if (Object.keys(cardErrors).length > 0) {
      setErrors(cardErrors);
      return;
    }

    // Build payload and create order — geolocation is optional
    const payload: CrearPedidoPayload = {
      items: items.map((item) => ({
        producto_id: item.productoId,
        cantidad: item.cantidad,
        exclusiones: item.exclusiones || [],
      })),
      direccion_id: direccionId,
      forma_pago_codigo: 'EFECTIVO',
      ...(ubicacion ? { latitud: ubicacion.lat, longitud: ubicacion.lng } : {}),
    };

    createOrder.mutateAsync(payload).catch(() => {});
  };

  const formatCardNumber = (value: string): string => {
    // Only allow digits, max 16
    const digits = value.replace(/\D/g, '').slice(0, 16);
    // Group in blocks of 4 for readability
    return digits.replace(/(.{4})/g, '$1 ').trim();
  };

  // Redirect if cart is empty (must be in useEffect, not render)
  useEffect(() => {
    if (items.length === 0) {
      navigate('/', { replace: true });
    }
  }, [items.length, navigate]);

  if (items.length === 0) {
    return null;
  }

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Pago</h1>

      {/* Order summary */}
      <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6">
        <h2 className="font-semibold text-gray-900 mb-3">Resumen del pedido</h2>
        <div className="space-y-2 mb-4">
          {items.map((item) => (
            <div key={item.productoId} className="flex justify-between text-sm">
              <span className="text-gray-700">
                {item.cantidad}x {item.nombre}
                {item.exclusiones && item.exclusiones.length > 0 && (
                  <span className="text-gray-400">
                    {' '}
                    (sin ingredientes #{item.exclusiones.join(', #')})
                  </span>
                )}
              </span>
              <span className="text-gray-900 font-medium">
                ${(Number(item.precio_base) * item.cantidad).toFixed(2)}
              </span>
            </div>
          ))}
        </div>
        <div className="border-t pt-2 flex justify-between font-bold text-base">
          <span>Total</span>
          <span>${total.toFixed(2)}</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Address selector */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h2 className="font-semibold text-gray-900 mb-3">Dirección de entrega</h2>
          {loadingDirecciones ? (
            <p className="text-sm text-gray-500">Cargando direcciones...</p>
          ) : !direcciones || direcciones.length === 0 ? (
            <div>
              <p className="text-sm text-amber-600 mb-3">
                No tenés direcciones guardadas. Agregá una para continuar.
              </p>
              <AddressInlineForm
                values={newAddress}
                onChange={setNewAddress}
                onSave={async () => {
                  const result = await createDireccion.mutateAsync(newAddress);
                  setDireccionId(result.id);
                  setNewAddress({
                    calle: '',
                    numero: '',
                    piso_depto: '',
                    ciudad: '',
                    codigo_postal: '',
                  });
                  queryClient.invalidateQueries({ queryKey: ['direcciones'] });
                }}
                isSaving={createDireccion.isPending}
              />
            </div>
          ) : (
            <>
              <select
                value={direccionId || ''}
                onChange={(e) => setDireccionId(Number(e.target.value))}
                className={`w-full border px-3 py-2 rounded ${errors.direccion ? 'border-red-500' : 'border-gray-300'}`}
              >
                <option value="">Seleccionar dirección...</option>
                {direcciones.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.calle} {d.numero}
                    {d.piso_depto ? `, ${d.piso_depto}` : ''} — {d.ciudad} (
                    {d.codigo_postal})
                    {d.es_predeterminada ? ' ★' : ''}
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={() => setShowAddressForm(!showAddressForm)}
                className="mt-2 text-sm text-blue-600 hover:text-blue-800 underline cursor-pointer"
              >
                {showAddressForm ? 'Cancelar' : '+ Agregar nueva dirección'}
              </button>
              {showAddressForm && (
                <div className="mt-3 p-3 border border-gray-200 rounded-lg bg-gray-50">
                  <h3 className="text-sm font-medium mb-2">Nueva dirección</h3>
                  <AddressInlineForm
                    values={newAddress}
                    onChange={setNewAddress}
                    onSave={async () => {
                      const result = await createDireccion.mutateAsync(newAddress);
                      setDireccionId(result.id);
                      setShowAddressForm(false);
                      setNewAddress({
                        calle: '',
                        numero: '',
                        piso_depto: '',
                        ciudad: '',
                        codigo_postal: '',
                      });
                      queryClient.invalidateQueries({ queryKey: ['direcciones'] });
                    }}
                    isSaving={createDireccion.isPending}
                  />
                </div>
              )}
            </>
          )}
          {errors.direccion && (
            <p className="text-red-500 text-xs mt-1">{errors.direccion}</p>
          )}
        </div>

        {/* Card form */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h2 className="font-semibold text-gray-900 mb-3">Datos de la tarjeta</h2>
          <p className="text-xs text-gray-400 mb-4">
            Simulación — no se realizan cobros reales
          </p>

          <div className="space-y-4">
            {/* Cardholder name */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Titular de la tarjeta
              </label>
              <input
                type="text"
                value={form.nombre}
                onChange={(e) => setForm((f) => ({ ...f, nombre: e.target.value }))}
                className={`w-full border px-3 py-2 rounded ${errors.nombre ? 'border-red-500' : 'border-gray-300'}`}
                placeholder="Nombre como figura en la tarjeta"
              />
              {errors.nombre && (
                <p className="text-red-500 text-xs mt-1">{errors.nombre}</p>
              )}
            </div>

            {/* Card number */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Número de tarjeta
              </label>
              <input
                type="text"
                value={formatCardNumber(form.numero)}
                onChange={(e) =>
                  setForm((f) => ({
                    ...f,
                    numero: e.target.value.replace(/\s/g, ''),
                  }))
                }
                className={`w-full border px-3 py-2 rounded font-mono ${errors.numero ? 'border-red-500' : 'border-gray-300'}`}
                placeholder="1234 5678 9012 3456"
                maxLength={19}
              />
              {errors.numero && (
                <p className="text-red-500 text-xs mt-1">{errors.numero}</p>
              )}
            </div>

            {/* Expiry + CVV */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  Vencimiento
                </label>
                <input
                  type="text"
                  value={form.vencimiento}
                  onChange={(e) =>
                    setForm((f) => ({ ...f, vencimiento: e.target.value }))
                  }
                  className={`w-full border px-3 py-2 rounded ${errors.vencimiento ? 'border-red-500' : 'border-gray-300'}`}
                  placeholder="MM/AA"
                  maxLength={5}
                />
                {errors.vencimiento && (
                  <p className="text-red-500 text-xs mt-1">
                    {errors.vencimiento}
                  </p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">CVV</label>
                <input
                  type="text"
                  value={form.cvv}
                  onChange={(e) =>
                    setForm((f) => ({
                      ...f,
                      cvv: e.target.value.replace(/\D/g, '').slice(0, 3),
                    }))
                  }
                  className={`w-full border px-3 py-2 rounded ${errors.cvv ? 'border-red-500' : 'border-gray-300'}`}
                  placeholder="123"
                  maxLength={3}
                />
                {errors.cvv && (
                  <p className="text-red-500 text-xs mt-1">{errors.cvv}</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Geolocation */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h2 className="font-semibold text-gray-900 mb-1">Ubicación</h2>
          {ubicacion ? (
            <p className="text-sm text-green-600">
              ✅ Ubicación capturada: {ubicacion.lat.toFixed(4)},{' '}
              {ubicacion.lng.toFixed(4)}
            </p>
          ) : (
            <p className="text-sm text-gray-500">
              {ubicacionError || 'Obteniendo ubicación...'}
            </p>
          )}
          {errors.ubicacion && (
            <p className="text-red-500 text-xs mt-1">{errors.ubicacion}</p>
          )}
        </div>

        {/* Submit error */}
        {submitError && (
          <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
            {submitError}
          </div>
        )}

        {/* Submit button */}
        <button
          type="submit"
          disabled={createOrder.isPending}
          className="w-full bg-green-600 text-white py-3 rounded-lg font-medium hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-lg"
        >
          {createOrder.isPending ? (
            <span className="flex items-center justify-center gap-2">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
              Creando pedido...
            </span>
          ) : (
            `Pagar $${total.toFixed(2)}`
          )}
        </button>
      </form>
    </div>
  );
}
