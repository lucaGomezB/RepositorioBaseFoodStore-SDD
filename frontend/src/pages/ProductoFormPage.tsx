// ProductoFormPage — create/edit page with TanStack Form + Zod validation
import { useNavigate, useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { useForm } from '@tanstack/react-form';
import { useQuery } from '@tanstack/react-query';
import { httpClient } from '@/shared/api/httpClient';
import {
  useProducto,
  useCreateProducto,
  useUpdateProducto,
  ProductoFormSchema,
} from '../entities/product';
import { useUIStore } from '../shared/stores/uiStore';

// ---------------------------------------------------------------------------
// Types for fetched selector data
// ---------------------------------------------------------------------------
interface CategoriaOption {
  id: number;
  nombre: string;
}

interface IngredienteOption {
  id: number;
  nombre: string;
  es_alergeno: boolean;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Render the first validation error string regardless of error shape */
function firstError(errors: unknown): string | null {
  if (!Array.isArray(errors) || errors.length === 0) return null;
  const e = errors[0];
  if (typeof e === 'string') return e;
  if (e && typeof e === 'object' && 'message' in e) return String((e as { message: string }).message);
  return String(e);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export default function ProductoFormPage() {
  const { id } = useParams<{ id: string }>();
  const isEdit = id !== undefined;
  const navigate = useNavigate();
  const addToast = useUIStore((s) => s.addToast);

  // ── Product queries ──
  const { data: producto, isLoading: loadingProducto } = useProducto(
    isEdit ? Number(id) : undefined,
  );
  const createProducto = useCreateProducto();
  const updateProducto = useUpdateProducto();

  // ── Fetch categories for selector ──
  const { data: categorias = [], isLoading: loadingCategorias } = useQuery({
    queryKey: ['categorias', 'all'],
    queryFn: async () => {
      const { data } = await httpClient.get<CategoriaOption[]>('/categorias/');
      return data;
    },
  });

  // ── Fetch ingredients for selector ──
  const { data: ingredientes = [], isLoading: loadingIngredientes } = useQuery({
    queryKey: ['ingredientes', 'all'],
    queryFn: async () => {
      const { data } = await httpClient.get<IngredienteOption[]>('/ingredientes/');
      return data;
    },
  });

  // ── Selected category IDs (local state, not TanStack Form) ──
  const [selectedCategoriaIds, setSelectedCategoriaIds] = useState<number[]>([]);
  const [selectedIngredienteIds, setSelectedIngredienteIds] = useState<number[]>([]);

  const toggleCategoria = (catId: number) => {
    setSelectedCategoriaIds((prev) =>
      prev.includes(catId) ? prev.filter((id) => id !== catId) : [...prev, catId],
    );
  };

  const toggleIngrediente = (ingId: number) => {
    setSelectedIngredienteIds((prev) =>
      prev.includes(ingId) ? prev.filter((id) => id !== ingId) : [...prev, ingId],
    );
  };

  // ── Form ──
  const form = useForm({
    defaultValues: {
      nombre: '',
      descripcion: '',
      precio_base: '',
      stock_cantidad: 0,
      disponible: true,
      imagenes_url: '',
      tiempo_prep_min: 0,
    },
    onSubmit: async ({ value }) => {
      // Validate with Zod
      const parsed = ProductoFormSchema.safeParse(value);
      if (!parsed.success) {
        addToast({
          type: 'error',
          message: parsed.error.issues[0]?.message || 'Error de validación',
        });
        return;
      }

      // Validate categories & ingredients (not in Zod schema)
      if (selectedCategoriaIds.length === 0) {
        addToast({
          type: 'error',
          message: 'Seleccioná al menos una categoría',
        });
        return;
      }
      if (selectedIngredienteIds.length === 0) {
        addToast({
          type: 'error',
          message: 'Seleccioná al menos un ingrediente',
        });
        return;
      }

      try {
        if (isEdit && id) {
          await updateProducto.mutateAsync({
            id: Number(id),
            payload: {
              nombre: parsed.data.nombre,
              descripcion: parsed.data.descripcion || null,
              precio_base: parsed.data.precio_base,
              stock_cantidad: parsed.data.stock_cantidad,
              disponible: parsed.data.disponible,
              imagenes_url: parsed.data.imagenes_url || null,
              tiempo_prep_min: parsed.data.tiempo_prep_min || null,
            },
          });
          addToast({ type: 'success', message: 'Producto actualizado correctamente' });
        } else {
          await createProducto.mutateAsync({
            nombre: parsed.data.nombre,
            descripcion: parsed.data.descripcion || null,
            precio_base: parsed.data.precio_base,
            stock_cantidad: parsed.data.stock_cantidad,
            disponible: parsed.data.disponible,
            imagenes_url: parsed.data.imagenes_url || null,
            tiempo_prep_min: parsed.data.tiempo_prep_min,
            categorias_ids: selectedCategoriaIds,
            ingredientes: selectedIngredienteIds.map((ingId) => ({
              ingrediente_id: ingId,
            })),
          });
          addToast({ type: 'success', message: 'Producto creado correctamente' });
        }
        navigate('/productos');
      } catch {
        addToast({
          type: 'error',
          message: isEdit
            ? 'No se pudo actualizar el producto'
            : 'No se pudo crear el producto',
        });
      }
    },
  });

  // Populate form when editing an existing product
  useEffect(() => {
    if (producto) {
      form.setFieldValue('nombre', producto.nombre);
      form.setFieldValue('descripcion', producto.descripcion ?? '');
      form.setFieldValue('precio_base', producto.precio_base);
      form.setFieldValue('stock_cantidad', producto.stock_cantidad);
      form.setFieldValue('disponible', producto.disponible);
      form.setFieldValue('imagenes_url', producto.imagenes_url ?? '');
      form.setFieldValue('tiempo_prep_min', producto.tiempo_prep_min ?? 0);
    }
  }, [producto, form]);

  // Show loading while fetching product for edit
  if (isEdit && loadingProducto) {
    return (
      <div className="p-4">
        <h1 className="text-2xl font-bold mb-4">Editar Producto</h1>
        <p className="text-gray-500">Cargando producto...</p>
      </div>
    );
  }

  const isPending = createProducto.isPending || updateProducto.isPending;

  return (
    <div className="p-4 max-w-2xl">
      <h1 className="text-2xl font-bold mb-6">
        {isEdit ? 'Editar Producto' : 'Nuevo Producto'}
      </h1>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          e.stopPropagation();
          void form.handleSubmit();
        }}
        className="space-y-4"
      >
        {/* Nombre */}
        <form.Field name="nombre">
          {(field) => (
            <div>
              <label className="block text-sm font-medium mb-1" htmlFor="nombre">
                Nombre
                <span className="text-red-500 ml-0.5" aria-label="requerido">*</span>
              </label>
              <input
                id="nombre"
                name="nombre"
                value={field.state.value}
                onChange={(e) => field.handleChange(e.target.value)}
                className="border px-3 py-2 rounded w-full"
                placeholder="Nombre del producto"
              />
              {firstError(field.state.meta.errors) && (
                <p className="text-red-600 text-sm mt-1">
                  {firstError(field.state.meta.errors)}
                </p>
              )}
            </div>
          )}
        </form.Field>

        {/* Descripción */}
        <form.Field name="descripcion">
          {(field) => (
            <div>
              <label className="block text-sm font-medium mb-1" htmlFor="descripcion">
                Descripción
                <button
                  type="button"
                  className="ml-1.5 text-gray-400 hover:text-gray-600 text-xs border border-gray-300 rounded-full w-4 h-4 inline-flex items-center justify-center"
                  title="Descripción detallada del producto. Opcional."
                  aria-label="Ayuda: descripción"
                >
                  ?
                </button>
              </label>
              <textarea
                id="descripcion"
                name="descripcion"
                value={field.state.value ?? ''}
                onChange={(e) => field.handleChange(e.target.value)}
                className="border px-3 py-2 rounded w-full"
                rows={3}
                placeholder="Descripción del producto (opcional)"
              />
            </div>
          )}
        </form.Field>

        {/* Precio Base */}
        <form.Field name="precio_base">
          {(field) => (
            <div>
              <label className="block text-sm font-medium mb-1" htmlFor="precio_base">
                Precio Base
                <span className="text-red-500 ml-0.5" aria-label="requerido">*</span>
                <button
                  type="button"
                  className="ml-1.5 text-gray-400 hover:text-gray-600 text-xs border border-gray-300 rounded-full w-4 h-4 inline-flex items-center justify-center"
                  title="Precio base del producto en formato decimal (ej: 12.50). Debe ser mayor a 0."
                  aria-label="Ayuda: precio base"
                >
                  ?
                </button>
              </label>
              <div className="relative">
                <span className="absolute left-3 top-2 text-gray-500">$</span>
                <input
                  id="precio_base"
                  name="precio_base"
                  type="text"
                  inputMode="decimal"
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                  className="border px-3 py-2 rounded w-full pl-7"
                  placeholder="0.00"
                />
              </div>
              {firstError(field.state.meta.errors) && (
                <p className="text-red-600 text-sm mt-1">
                  {firstError(field.state.meta.errors)}
                </p>
              )}
            </div>
          )}
        </form.Field>

        {/* Stock Cantidad */}
        <form.Field name="stock_cantidad">
          {(field) => (
            <div>
              <label className="block text-sm font-medium mb-1" htmlFor="stock_cantidad">
                Stock Cantidad
                <span className="text-red-500 ml-0.5" aria-label="requerido">*</span>
                <button
                  type="button"
                  className="ml-1.5 text-gray-400 hover:text-gray-600 text-xs border border-gray-300 rounded-full w-4 h-4 inline-flex items-center justify-center"
                  title="Cantidad disponible en stock. Debe ser un número entero >= 0."
                  aria-label="Ayuda: stock"
                >
                  ?
                </button>
              </label>
              <input
                id="stock_cantidad"
                name="stock_cantidad"
                type="number"
                value={field.state.value}
                onChange={(e) => field.handleChange(Number(e.target.value))}
                className="border px-3 py-2 rounded w-full"
                min={0}
              />
              {firstError(field.state.meta.errors) && (
                <p className="text-red-600 text-sm mt-1">
                  {firstError(field.state.meta.errors)}
                </p>
              )}
            </div>
          )}
        </form.Field>

        {/* Disponible */}
        <form.Field name="disponible">
          {(field) => (
            <div className="flex items-center gap-2">
              <input
                id="disponible"
                name="disponible"
                type="checkbox"
                checked={field.state.value}
                onChange={(e) => field.handleChange(e.target.checked)}
                className="rounded"
              />
              <label className="text-sm font-medium" htmlFor="disponible">
                Producto disponible para la venta
                <button
                  type="button"
                  className="ml-1.5 text-gray-400 hover:text-gray-600 text-xs border border-gray-300 rounded-full w-4 h-4 inline-flex items-center justify-center"
                  title="Si está marcado, el producto aparece en el catálogo público."
                  aria-label="Ayuda: disponible"
                >
                  ?
                </button>
              </label>
            </div>
          )}
        </form.Field>

        {/* Imagen URL */}
        <form.Field name="imagenes_url">
          {(field) => (
            <div>
              <label className="block text-sm font-medium mb-1" htmlFor="imagenes_url">
                URL de Imagen
                <button
                  type="button"
                  className="ml-1.5 text-gray-400 hover:text-gray-600 text-xs border border-gray-300 rounded-full w-4 h-4 inline-flex items-center justify-center"
                  title="URL pública de la imagen del producto. Opcional."
                  aria-label="Ayuda: imagen"
                >
                  ?
                </button>
              </label>
              <input
                id="imagenes_url"
                name="imagenes_url"
                type="url"
                value={field.state.value ?? ''}
                onChange={(e) => field.handleChange(e.target.value)}
                className="border px-3 py-2 rounded w-full"
                placeholder="https://ejemplo.com/imagen.jpg"
              />
            </div>
          )}
        </form.Field>

        {/* Tiempo Prep */}
        <form.Field name="tiempo_prep_min">
          {(field) => (
            <div>
              <label className="block text-sm font-medium mb-1" htmlFor="tiempo_prep_min">
                Tiempo de Preparación (min)
                <button
                  type="button"
                  className="ml-1.5 text-gray-400 hover:text-gray-600 text-xs border border-gray-300 rounded-full w-4 h-4 inline-flex items-center justify-center"
                  title="Tiempo estimado de preparación en minutos. Opcional."
                  aria-label="Ayuda: tiempo preparación"
                >
                  ?
                </button>
              </label>
              <input
                id="tiempo_prep_min"
                name="tiempo_prep_min"
                type="number"
                value={field.state.value ?? ''}
                onChange={(e) =>
                  field.handleChange(
                    e.target.value === '' ? 0 : Number(e.target.value),
                  )
                }
                className="border px-3 py-2 rounded w-full"
                min={0}
                placeholder="ej: 15"
              />
            </div>
          )}
        </form.Field>

        {/* ── Categorías selector ── */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">
            Categorías
            <span className="text-red-500 ml-0.5" aria-label="requerido">*</span>
          </h3>
          {loadingCategorias ? (
            <p className="text-sm text-gray-400">Cargando categorías...</p>
          ) : categorias.length === 0 ? (
            <p className="text-sm text-amber-600">
              No hay categorías disponibles. Creá una primero.
            </p>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {categorias.map((cat) => (
                <label
                  key={cat.id}
                  className={`flex items-center gap-2 px-3 py-2 rounded border text-sm cursor-pointer transition-colors ${
                    selectedCategoriaIds.includes(cat.id)
                      ? 'border-blue-500 bg-blue-50 text-blue-800'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedCategoriaIds.includes(cat.id)}
                    onChange={() => toggleCategoria(cat.id)}
                    className="rounded"
                  />
                  {cat.nombre}
                </label>
              ))}
            </div>
          )}
          {selectedCategoriaIds.length === 0 && (
            <p className="text-xs text-amber-600 mt-1">
              Seleccioná al menos una categoría
            </p>
          )}
        </div>

        {/* ── Ingredientes selector ── */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-900 mb-2">
            Ingredientes
            <span className="text-red-500 ml-0.5" aria-label="requerido">*</span>
          </h3>
          {loadingIngredientes ? (
            <p className="text-sm text-gray-400">Cargando ingredientes...</p>
          ) : ingredientes.length === 0 ? (
            <p className="text-sm text-amber-600">
              No hay ingredientes disponibles. Creá uno primero.
            </p>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {ingredientes.map((ing) => (
                <label
                  key={ing.id}
                  className={`flex items-center gap-2 px-3 py-2 rounded border text-sm cursor-pointer transition-colors ${
                    selectedIngredienteIds.includes(ing.id)
                      ? 'border-blue-500 bg-blue-50 text-blue-800'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedIngredienteIds.includes(ing.id)}
                    onChange={() => toggleIngrediente(ing.id)}
                    className="rounded"
                  />
                  <span>{ing.nombre}</span>
                  {ing.es_alergeno && (
                    <span className="text-xs text-red-500 font-medium" title="Alérgeno">
                      ⚠
                    </span>
                  )}
                </label>
              ))}
            </div>
          )}
          {selectedIngredienteIds.length === 0 && (
            <p className="text-xs text-amber-600 mt-1">
              Seleccioná al menos un ingrediente
            </p>
          )}
        </div>

        {/* ── Submit / Cancel ── */}
        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={isPending}
            className="bg-blue-600 text-white px-6 py-2 rounded cursor-pointer hover:bg-blue-700 transition-colors disabled:opacity-50 font-medium"
          >
            {isPending
              ? 'Guardando...'
              : isEdit
                ? 'Actualizar Producto'
                : 'Crear Producto'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/productos')}
            className="bg-gray-400 text-white px-6 py-2 rounded cursor-pointer hover:bg-gray-500 transition-colors font-medium"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
}
