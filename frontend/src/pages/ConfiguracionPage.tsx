// ConfiguracionPage — Admin system settings form
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { httpClient } from '@/shared/api/httpClient';

interface ConfigItem {
  clave: string;
  valor: string;
  descripcion: string | null;
}

interface ConfigFormState {
  [key: string]: string;
}

const CONFIG_KEY = 'admin-config';

const CONFIG_LABELS: Record<string, string> = {
  costo_envio: 'Costo de envío ($)',
  horario_apertura: 'Horario de apertura',
  horario_cierre: 'Horario de cierre',
  tiempo_estimado_entrega_min: 'Tiempo estimado de entrega (min)',
  telefono_contacto: 'Teléfono de contacto',
  direccion_local: 'Dirección del local',
};

const CONFIG_GROUPS = [
  {
    title: 'Envíos',
    keys: ['costo_envio', 'tiempo_estimado_entrega_min'],
  },
  {
    title: 'Horarios',
    keys: ['horario_apertura', 'horario_cierre'],
  },
  {
    title: 'Contacto',
    keys: ['telefono_contacto', 'direccion_local'],
  },
];

export default function ConfiguracionPage() {
  const queryClient = useQueryClient();
  const [formState, setFormState] = useState<ConfigFormState>({});
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Fetch configs
  const { data: configs, isLoading } = useQuery({
    queryKey: [CONFIG_KEY],
    queryFn: async () => {
      const { data } = await httpClient.get<ConfigItem[]>('/admin/configuracion');
      // Initialize form state from server data
      const initial: ConfigFormState = {};
      data.forEach((item) => {
        initial[item.clave] = item.valor;
      });
      setFormState(initial);
      return data;
    },
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: async (formData: ConfigFormState) => {
      const configuraciones = Object.entries(formData).map(([clave, valor]) => ({
        clave,
        valor,
      }));
      const { data } = await httpClient.put<ConfigItem[]>('/admin/configuracion', {
        configuraciones,
      });
      return data;
    },
    onSuccess: () => {
      setSuccessMsg('Configuraciones guardadas correctamente');
      queryClient.invalidateQueries({ queryKey: [CONFIG_KEY] });
      setTimeout(() => setSuccessMsg(null), 3000);
    },
  });

  const handleChange = (clave: string, valor: string) => {
    setFormState((prev) => ({ ...prev, [clave]: valor }));
  };

  const handleSave = () => {
    updateMutation.mutateAsync(formState).catch(() => {});
  };

  // ── Loading ──
  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
      </div>
    );
  }

  // ── Form ──
  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Configuración del sistema</h1>

      {successMsg && (
        <div className="mb-4 p-3 rounded-lg bg-green-50 border border-green-200 text-green-700 text-sm">
          {successMsg}
        </div>
      )}

      {updateMutation.isError && (
        <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
          {updateMutation.error instanceof Error
            ? updateMutation.error.message
            : 'Error al guardar configuraciones'}
        </div>
      )}

      {CONFIG_GROUPS.map((group) => (
        <div key={group.title} className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
          <h2 className="font-semibold text-gray-900 mb-3">{group.title}</h2>
          <div className="space-y-4">
            {group.keys.map((key) => (
              <div key={key}>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {CONFIG_LABELS[key] || key}
                </label>
                <input
                  type="text"
                  value={formState[key] ?? ''}
                  onChange={(e) => handleChange(key, e.target.value)}
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                {configs && (
                  <p className="text-xs text-gray-400 mt-1">
                    {configs.find((c) => c.clave === key)?.descripcion}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}

      <button
        onClick={handleSave}
        disabled={updateMutation.isPending}
        className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {updateMutation.isPending ? 'Guardando...' : 'Guardar cambios'}
      </button>
    </div>
  );
}
