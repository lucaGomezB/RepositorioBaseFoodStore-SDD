// CatalogPagination — Page navigation with "Mostrando X-Y de Z productos"
interface CatalogPaginationProps {
  page: number;
  totalCount: number;
  limit: number;
  onPageChange: (page: number) => void;
}

export function CatalogPagination({
  page,
  totalCount,
  limit,
  onPageChange,
}: CatalogPaginationProps) {
  if (totalCount === 0) return null;

  const totalPages = Math.ceil(totalCount / limit);
  const startItem = page * limit + 1;
  const endItem = Math.min((page + 1) * limit, totalCount);

  /** Builds a window of up to 7 page numbers around the current page */
  function getPageNumbers(): (number | '...')[] {
    const pages: (number | '...')[] = [];

    if (totalPages <= 7) {
      for (let i = 0; i < totalPages; i++) pages.push(i);
    } else {
      // Always show first page
      pages.push(0);

      // Ellipsis after first page if needed
      if (page > 2) pages.push('...');

      // Window around current page
      const start = Math.max(1, page - 1);
      const end = Math.min(totalPages - 2, page + 1);
      for (let i = start; i <= end; i++) pages.push(i);

      // Ellipsis before last page if needed
      if (page < totalPages - 3) pages.push('...');

      // Always show last page
      pages.push(totalPages - 1);
    }

    return pages;
  }

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-8">
      <p className="text-sm text-gray-600">
        Mostrando {startItem}-{endItem} de {totalCount} productos
      </p>

      <div className="flex items-center gap-1">
        {/* Previous */}
        <button
          disabled={page === 0}
          onClick={() => onPageChange(page - 1)}
          className="px-3 py-1.5 rounded border border-gray-300 text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 cursor-pointer transition-colors"
        >
          Anterior
        </button>

        {/* Page numbers */}
        {getPageNumbers().map((p, idx) =>
          p === '...' ? (
            <span
              key={`ellipsis-${idx}`}
              className="px-2 text-gray-400 select-none"
            >
              ...
            </span>
          ) : (
            <button
              key={p}
              onClick={() => onPageChange(p)}
              className={`px-3 py-1.5 rounded text-sm cursor-pointer transition-colors ${
                p === page
                  ? 'bg-blue-600 text-white'
                  : 'border border-gray-300 hover:bg-gray-100'
              }`}
            >
              {p + 1}
            </button>
          ),
        )}

        {/* Next */}
        <button
          disabled={page >= totalPages - 1}
          onClick={() => onPageChange(page + 1)}
          className="px-3 py-1.5 rounded border border-gray-300 text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 cursor-pointer transition-colors"
        >
          Siguiente
        </button>
      </div>
    </div>
  );
}
