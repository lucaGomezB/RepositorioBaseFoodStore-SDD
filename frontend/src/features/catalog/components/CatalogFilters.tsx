// CatalogFilters — Search input and category select with debounce support
import type { ChangeEvent } from 'react';

interface CatalogFiltersProps {
  busqueda: string;
  categoria_id: number | undefined;
  onBusquedaChange: (value: string) => void;
  onCategoriaChange: (value: number | undefined) => void;
  onReset: () => void;
}

/** Hardcoded categories for the catalog filter dropdown */
const CATEGORIAS = [
  { id: 1, nombre: 'Pizzas' },
  { id: 2, nombre: 'Hamburguesas' },
  { id: 3, nombre: 'Bebidas' },
  { id: 4, nombre: 'Postres' },
  { id: 5, nombre: 'Ensaladas' },
];

export function CatalogFilters({
  busqueda,
  categoria_id,
  onBusquedaChange,
  onCategoriaChange,
  onReset,
}: CatalogFiltersProps) {
  const hasActiveFilters = busqueda !== '' || categoria_id !== undefined;

  return (
    <div className="flex flex-wrap gap-4 items-center mb-6">
      {/* Search input with magnifying glass icon */}
      <div className="relative flex-1 min-w-[200px] max-w-md">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 select-none">
          🔍
        </span>
        <input
          type="text"
          placeholder="Buscar productos..."
          value={busqueda}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            onBusquedaChange(e.target.value)
          }
          className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
        />
      </div>

      {/* Category select */}
      <select
        value={categoria_id ?? ''}
        onChange={(e: ChangeEvent<HTMLSelectElement>) =>
          onCategoriaChange(
            e.target.value ? Number(e.target.value) : undefined,
          )
        }
        className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white"
      >
        <option value="">Todas las categorías</option>
        {CATEGORIAS.map((cat) => (
          <option key={cat.id} value={cat.id}>
            {cat.nombre}
          </option>
        ))}
      </select>

      {/* Reset filters button */}
      {hasActiveFilters && (
        <button
          onClick={onReset}
          className="text-sm text-blue-600 hover:text-blue-800 underline cursor-pointer whitespace-nowrap"
        >
          Limpiar filtros
        </button>
      )}
    </div>
  );
}
