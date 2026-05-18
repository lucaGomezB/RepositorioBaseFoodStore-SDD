// useCatalogFilters — Manages catalog filter state (search, category, page)
import { useState, useCallback } from 'react';
import type { CatalogoFilters } from '@/entities/product';

const DEFAULT_LIMIT = 12;

export interface UseCatalogFiltersReturn {
  filters: CatalogoFilters;
  setBusqueda: (busqueda: string) => void;
  setCategoria: (categoria_id: number | undefined) => void;
  setExcluirAlergenos: (excluir_alergenos: string | undefined) => void;
  setPage: (page: number) => void;
  resetFilters: () => void;
}

export function useCatalogFilters(): UseCatalogFiltersReturn {
  const [filters, setFilters] = useState<CatalogoFilters>({
    page: 1,
    limit: DEFAULT_LIMIT,
  });

  const setBusqueda = useCallback((busqueda: string) => {
    setFilters((prev) => ({ ...prev, busqueda, page: 1 }));
  }, []);

  const setCategoria = useCallback((categoria_id: number | undefined) => {
    setFilters((prev) => ({ ...prev, categoria_id, page: 1 }));
  }, []);

  const setExcluirAlergenos = useCallback(
    (excluir_alergenos: string | undefined) => {
      setFilters((prev) => ({ ...prev, excluir_alergenos, page: 1 }));
    },
    [],
  );

  const setPage = useCallback((page: number) => {
    setFilters((prev) => ({ ...prev, page }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters({ page: 1, limit: DEFAULT_LIMIT });
  }, []);

  return {
    filters,
    setBusqueda,
    setCategoria,
    setExcluirAlergenos,
    setPage,
    resetFilters,
  };
}
