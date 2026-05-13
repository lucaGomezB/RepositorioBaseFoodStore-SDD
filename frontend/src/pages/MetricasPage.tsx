// MetricasPage — Admin dashboard with KPIs and charts
import { useState, useMemo } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import type { PieLabelRenderProps } from 'recharts';
import {
  useResumenMetricas,
  useVentasPorPeriodo,
  useTopProductos,
  usePedidosPorEstado,
} from '../entities/metricas/api';

// ── Color palette ──────────────────────────────────────────────────────────
const COLORS = [
  '#3B82F6', '#10B981', '#F59E0B', '#EF4444',
  '#8B5CF6', '#EC4899', '#14B8A6', '#F97316',
];

// ── Helpers ────────────────────────────────────────────────────────────────

function formatCurrency(n: number): string {
  return `$${n.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function formatDateInput(iso?: string): string {
  if (!iso) return '';
  // ISO string → datetime-local value (YYYY-MM-DDTHH:mm)
  return iso.slice(0, 16);
}

// ── Component ──────────────────────────────────────────────────────────────

export default function MetricasPage() {
  // Date / granularity filters for the sales chart
  const [desde, setDesde] = useState('');
  const [hasta, setHasta] = useState('');
  const [granularidad, setGranularidad] = useState('dia');

  const desdeParam = desde || undefined;
  const hastaParam = hasta || undefined;

  // Queries
  const { data: resumen, isLoading: loadingResumen } = useResumenMetricas();
  const { data: ventas, isLoading: loadingVentas } = useVentasPorPeriodo(
    desdeParam ? new Date(desdeParam).toISOString() : undefined,
    hastaParam ? new Date(hastaParam).toISOString() : undefined,
    granularidad,
  );
  const { data: topProductos, isLoading: loadingTop } = useTopProductos(10);
  const { data: pedidosPorEstado, isLoading: loadingEstados } = usePedidosPorEstado();

  // Derived KPI values
  const totalPedidos = useMemo(
    () => resumen?.pedidos_por_estado?.reduce((sum, e) => sum + e.cantidad, 0) ?? 0,
    [resumen],
  );

  const topProductoNombre = useMemo(
    () => (resumen?.top_productos?.length ?? 0) > 0
      ? resumen!.top_productos[0].nombre
      : '—',
    [resumen],
  );

  const isLoading = loadingResumen || loadingVentas || loadingTop || loadingEstados;

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Dashboard de Métricas</h1>

      {isLoading && (
        <div className="animate-pulse space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="h-28 bg-gray-200 rounded" />
            ))}
          </div>
          <div className="h-64 bg-gray-200 rounded" />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div className="h-64 bg-gray-200 rounded" />
            <div className="h-64 bg-gray-200 rounded" />
          </div>
        </div>
      )}

      {!isLoading && (
        <>
          {/* ── KPI Cards ─────────────────────────────────────────────── */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <KpiCard
              title="Ventas Totales"
              value={formatCurrency(resumen?.total_ventas ?? 0)}
              color="text-blue-600"
            />
            <KpiCard
              title="Pedidos"
              value={String(totalPedidos)}
              color="text-green-600"
            />
            <KpiCard
              title="Usuarios"
              value={String(resumen?.total_usuarios ?? 0)}
              color="text-purple-600"
            />
            <KpiCard
              title="Top Producto"
              value={topProductoNombre}
              color="text-amber-600"
            />
          </div>

          {/* ── Sales Line Chart with Filters ─────────────────────────── */}
          <div className="bg-white rounded shadow p-4 mb-6">
            <div className="flex flex-wrap items-end gap-4 mb-4">
              <h2 className="text-lg font-semibold mr-2">Ventas por Período</h2>

              <div>
                <label className="block text-xs text-gray-500 mb-1">Desde</label>
                <input
                  type="datetime-local"
                  value={formatDateInput(desde)}
                  onChange={(e) => setDesde(e.target.value)}
                  className="border px-3 py-1.5 rounded text-sm"
                />
              </div>

              <div>
                <label className="block text-xs text-gray-500 mb-1">Hasta</label>
                <input
                  type="datetime-local"
                  value={formatDateInput(hasta)}
                  onChange={(e) => setHasta(e.target.value)}
                  className="border px-3 py-1.5 rounded text-sm"
                />
              </div>

              <div>
                <label className="block text-xs text-gray-500 mb-1">Agrupar por</label>
                <select
                  value={granularidad}
                  onChange={(e) => setGranularidad(e.target.value)}
                  className="border px-3 py-1.5 rounded text-sm"
                >
                  <option value="dia">Día</option>
                  <option value="semana">Semana</option>
                  <option value="mes">Mes</option>
                </select>
              </div>

              {(desde || hasta || granularidad !== 'dia') && (
                <button
                  onClick={() => {
                    setDesde('');
                    setHasta('');
                    setGranularidad('dia');
                  }}
                  className="text-sm text-blue-600 hover:text-blue-800 underline cursor-pointer mb-0.5"
                >
                  Limpiar filtros
                </button>
              )}
            </div>

            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={ventas ?? []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="periodo"
                  tickFormatter={(val) => new Date(val).toLocaleDateString('es-AR')}
                  fontSize={12}
                />
                <YAxis tickFormatter={(val) => `$${Number(val).toLocaleString()}`} fontSize={12} />
                <Tooltip
                  labelFormatter={(val) => new Date(val).toLocaleDateString('es-AR', {
                    day: '2-digit', month: 'long', year: 'numeric',
                  })}
                  formatter={(value) => formatCurrency(Number(value))}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="total"
                  name="Ventas"
                  stroke="#3B82F6"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* ── Two columns: BarChart + PieChart ──────────────────────── */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
            {/* Top Products BarChart */}
            <div className="bg-white rounded shadow p-4">
              <h2 className="text-lg font-semibold mb-4">Top 10 Productos</h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart
                  data={topProductos ?? []}
                  layout="vertical"
                  margin={{ left: 100 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" fontSize={12} />
                  <YAxis
                    type="category"
                    dataKey="nombre"
                    fontSize={11}
                    tick={{ width: 90 }}
                  />
                  <Tooltip formatter={(value) => `${value} vendidos`} />
                  <Bar dataKey="cantidad" name="Cantidad vendida" fill="#10B981" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Orders by State PieChart */}
            <div className="bg-white rounded shadow p-4">
              <h2 className="text-lg font-semibold mb-4">Pedidos por Estado</h2>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={pedidosPorEstado ?? []}
                    dataKey="cantidad"
                    nameKey="codigo"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={(entry: PieLabelRenderProps) => {
                      const item = entry.payload as { nombre: string; cantidad: number };
                      return `${item.nombre}: ${item.cantidad}`;
                    }}
                    labelLine
                  >
                    {(pedidosPorEstado ?? []).map((_, idx) => (
                      <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value, _name, entry) => {
                      const item = entry?.payload as { nombre?: string } | undefined;
                      return [`${value} pedidos`, item?.nombre ?? _name];
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// ── KPI Card sub-component ─────────────────────────────────────────────────

function KpiCard({
  title,
  value,
  color,
}: {
  title: string;
  value: string;
  color: string;
}) {
  return (
    <div className="bg-white rounded shadow p-4 flex flex-col">
      <span className="text-sm text-gray-500 mb-1">{title}</span>
      <span className={`text-2xl font-bold ${color} truncate`} title={value}>
        {value}
      </span>
    </div>
  );
}
