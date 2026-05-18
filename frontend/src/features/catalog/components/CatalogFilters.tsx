// CatalogFilters — Search input and category select with debounce support
import { useQuery } from '@tanstack/react-query';
import { httpClient } from '@/shared/api/httpClient';
import type { ChangeEvent } from 'react';

interface CategoriaTree {
  id: number;
  nombre: string;
  parent_id: number | null;
  subcategorias: CategoriaTree[];
}

interface CatalogFiltersProps {
  busqueda: string;
  categoria_id: number | undefined;
  onBusquedaChange: (value: string) => void;
  onCategoriaChange: (value: number | undefined) => void;
  onReset: () => void;
}

/** Flatten a category tree into a flat list of root categories with indent labels for subcats */
function flattenTree(cats: CategoriaTree[], depth = 0): { id: number; label: string }[] {
  const result: { id: number; label: string }[] = [];
  for (const cat of cats) {
    result.push({ id: cat.id, label: cat.nombre });
    if (cat.subcategorias && cat.subcategorias.length > 0) {
      result.push(...flattenTree(cat.subcategorias, depth + 1));
    }
  }
  return result;
}

export function CatalogFilters({
  busqueda,
  categoria_id,
  onBusquedaChange,
  onCategoriaChange,
  onReset,
}: CatalogFiltersProps) {
  const hasActiveFilters = busqueda !== '' || categoria_id !== undefined;

  const { data: categorias } = useQuery({
    queryKey: ['categorias-tree'],
    queryFn: async () => {
      const { data } = await httpClient.get<CategoriaTree[]>('/categorias/');
      return flattenTree(data);
    },
  });

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
        {(categorias ?? []).map((cat) => (
          <option key={cat.id} value={cat.id}>
            {cat.label}
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
