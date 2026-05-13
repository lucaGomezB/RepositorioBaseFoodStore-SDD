import { useReducer, useEffect, useCallback, useState } from "react";
import type { Categoria, CategoriaCreate } from "../api/categorias";
import { categoriasApi } from "../api/categorias";
import { exportToExcel } from "../utils/exportExcel";

const PAGE_SIZE = 10;

interface State {
  items: Categoria[];
  loading: boolean;
  error: string | null;
  page: number;
  filter: string;
  editingId: number | null;
  showForm: boolean;
  form: CategoriaCreate;
}

type Action =
  | { type: "SET_ITEMS"; payload: Categoria[] }
  | { type: "SET_LOADING"; payload: boolean }
  | { type: "SET_ERROR"; payload: string | null }
  | { type: "SET_PAGE"; payload: number }
  | { type: "SET_FILTER"; payload: string }
  | { type: "START_EDIT"; payload: Categoria }
  | { type: "START_CREATE" }
  | { type: "CLOSE_FORM" }
  | { type: "UPDATE_FORM"; payload: Partial<CategoriaCreate> };

const emptyForm: CategoriaCreate = {
  nombre: "", descripcion: "", parent_id: null, orden_display: 0,
};

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "SET_ITEMS": return { ...state, items: action.payload, loading: false };
    case "SET_LOADING": return { ...state, loading: action.payload };
    case "SET_ERROR": return { ...state, error: action.payload, loading: false };
    case "SET_PAGE": return { ...state, page: action.payload };
    case "SET_FILTER": return { ...state, filter: action.payload, page: 0 };
    case "START_EDIT":
      return {
        ...state, editingId: action.payload.id, showForm: true,
        form: {
          nombre: action.payload.nombre,
          descripcion: action.payload.descripcion ?? "",
          parent_id: action.payload.parent_id,
          orden_display: action.payload.orden_display,
        },
      };
    case "START_CREATE": return { ...state, editingId: null, showForm: true, form: emptyForm };
    case "CLOSE_FORM": return { ...state, showForm: false, editingId: null, form: emptyForm };
    case "UPDATE_FORM": return { ...state, form: { ...state.form, ...action.payload } };
    default: return state;
  }
}

const init: State = {
  items: [], loading: false, error: null, page: 0, filter: "",
  editingId: null, showForm: false, form: emptyForm,
};

/* ── Popup de Subcategorías ── */
function SubcategoriasPopup({ categoria, allCategorias, onClose }: {
  categoria: Categoria; allCategorias: Categoria[]; onClose: () => void;
}) {
  const subcats = allCategorias.filter((c) => c.parent_id === categoria.id);

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-white rounded p-6 w-full max-w-md max-h-[80vh] overflow-auto" onClick={(e) => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-bold">Subcategorías de "{categoria.nombre}"</h2>
          <button onClick={onClose} className="text-gray-500 text-xl cursor-pointer">✕</button>
        </div>
        {subcats.length === 0 ? (
          <p className="text-gray-500">Sin subcategorías.</p>
        ) : (
          <table className="w-full border-collapse border">
            <thead><tr className="bg-gray-200">
              <th className="border p-2 text-left">ID</th>
              <th className="border p-2 text-left">Nombre</th>
              <th className="border p-2 text-left">Descripción</th>
            </tr></thead>
            <tbody>
              {subcats.map((sc) => (
                <tr key={sc.id}>
                  <td className="border p-2">{sc.id}</td>
                  <td className="border p-2">{sc.nombre}</td>
                  <td className="border p-2">{sc.descripcion ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default function CategoriasCRUD() {
  const [state, dispatch] = useReducer(reducer, init);
  const [allCats, setAllCats] = useState<Categoria[]>([]);
  const [subcatPopup, setSubcatPopup] = useState<Categoria | null>(null);

  const fetchData = useCallback(async () => {
    dispatch({ type: "SET_LOADING", payload: true });
    try {
      const data = await categoriasApi.getAll(state.page * PAGE_SIZE, PAGE_SIZE);
      dispatch({ type: "SET_ITEMS", payload: data });
    } catch (e) {
      dispatch({ type: "SET_ERROR", payload: (e as Error).message });
    }
  }, [state.page]);

  // Fetch all categories once for subcategory detection
  useEffect(() => {
    categoriasApi.getAll(0, 1000).then(setAllCats);
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (state.editingId) {
        await categoriasApi.update(state.editingId, state.form);
      } else {
        await categoriasApi.create(state.form);
      }
      dispatch({ type: "CLOSE_FORM" });
      fetchData();
      categoriasApi.getAll(0, 1000).then(setAllCats); // refresh allCats
    } catch (err) {
      dispatch({ type: "SET_ERROR", payload: (err as Error).message });
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("¿Eliminar esta categoría?")) return;
    try {
      await categoriasApi.delete(id);
      fetchData();
      categoriasApi.getAll(0, 1000).then(setAllCats);
    } catch (err) {
      dispatch({ type: "SET_ERROR", payload: (err as Error).message });
    }
  };

  const filtered = state.items.filter((c) =>
    c.nombre.toLowerCase().includes(state.filter.toLowerCase())
  );

  // Pre-compute which categories have children
  const hasChildren = (catId: number) => allCats.some((c) => c.parent_id === catId);

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Categorías</h1>
      {state.error && <div className="bg-red-100 text-red-700 p-2 mb-4 rounded">{state.error}</div>}

      <div className="flex gap-2 mb-4 flex-wrap">
        <input type="text" placeholder="Filtrar por nombre..." value={state.filter}
          onChange={(e) => dispatch({ type: "SET_FILTER", payload: e.target.value })}
          className="border px-3 py-1 rounded" />
        <button onClick={() => dispatch({ type: "START_CREATE" })}
          className="bg-green-600 text-white px-4 py-1 rounded cursor-pointer">+ Nueva</button>
        <button onClick={() => exportToExcel(filtered.map(({ id, nombre, descripcion, parent_id, orden_display }) => ({
              id, nombre, descripcion: descripcion ?? "", parent_id: parent_id ?? "", orden_display,
            })), "categorias")}
          className="bg-blue-600 text-white px-4 py-1 rounded cursor-pointer">Exportar Excel</button>
      </div>

      {state.showForm && (
        <form onSubmit={handleSubmit} className="border p-4 mb-4 rounded bg-gray-50 grid grid-cols-2 gap-2">
          <div>
            <label className="block text-sm font-medium">Nombre</label>
            <input value={state.form.nombre}
              onChange={(e) => dispatch({ type: "UPDATE_FORM", payload: { nombre: e.target.value } })}
              className="border px-2 py-1 rounded w-full" required />
          </div>
          <div>
            <label className="block text-sm font-medium">Descripción</label>
            <input value={state.form.descripcion ?? ""}
              onChange={(e) => dispatch({ type: "UPDATE_FORM", payload: { descripcion: e.target.value } })}
              className="border px-2 py-1 rounded w-full" />
          </div>
          <div>
            <label className="block text-sm font-medium">Parent ID</label>
            <input type="number" value={state.form.parent_id ?? ""}
              onChange={(e) => dispatch({ type: "UPDATE_FORM",
                payload: { parent_id: e.target.value ? Number(e.target.value) : null } })}
              className="border px-2 py-1 rounded w-full" />
          </div>
          <div>
            <label className="block text-sm font-medium">Orden Display</label>
            <input type="number" value={state.form.orden_display ?? 0}
              onChange={(e) => dispatch({ type: "UPDATE_FORM", payload: { orden_display: Number(e.target.value) } })}
              className="border px-2 py-1 rounded w-full" />
          </div>
          <div className="col-span-2 flex gap-2 mt-2">
            <button type="submit" className="bg-blue-600 text-white px-4 py-1 rounded cursor-pointer">
              {state.editingId ? "Actualizar" : "Crear"}</button>
            <button type="button" onClick={() => dispatch({ type: "CLOSE_FORM" })}
              className="bg-gray-400 text-white px-4 py-1 rounded cursor-pointer">Cancelar</button>
          </div>
        </form>
      )}

      {state.loading ? <p>Cargando...</p> : (
        <table className="w-full border-collapse border">
          <thead><tr className="bg-gray-200">
            <th className="border p-2 text-left">ID</th>
            <th className="border p-2 text-left">Nombre</th>
            <th className="border p-2 text-left">Descripción</th>
            <th className="border p-2 text-left">Subcategorías</th>
            <th className="border p-2 text-left">Acciones</th>
          </tr></thead>
          <tbody>
            {filtered.map((cat) => (
              <tr key={cat.id} className="hover:bg-gray-100">
                <td className="border p-2">{cat.id}</td>
                <td className="border p-2">{cat.nombre}</td>
                <td className="border p-2">{cat.descripcion ?? "-"}</td>
                <td className="border p-2">
                  {hasChildren(cat.id) ? (
                    <button onClick={() => setSubcatPopup(cat)}
                      className="bg-indigo-600 text-white px-2 py-1 rounded text-sm cursor-pointer">
                      Ver Subcategorías
                    </button>
                  ) : (
                    <span className="text-gray-400 text-sm">Ninguna</span>
                  )}
                </td>
                <td className="border p-2">
                  <div className="flex gap-1">
                    <button onClick={() => dispatch({ type: "START_EDIT", payload: cat })}
                      className="bg-yellow-500 text-white px-2 py-1 rounded text-sm cursor-pointer">Editar</button>
                    <button onClick={() => handleDelete(cat.id)}
                      className="bg-red-600 text-white px-2 py-1 rounded text-sm cursor-pointer">Eliminar</button>
                  </div>
                </td>
              </tr>
            ))}
            {filtered.length === 0 && (
              <tr><td colSpan={5} className="border p-2 text-center text-gray-500">Sin resultados</td></tr>
            )}
          </tbody>
        </table>
      )}

      <div className="flex gap-2 mt-4 items-center">
        <button disabled={state.page === 0}
          onClick={() => dispatch({ type: "SET_PAGE", payload: state.page - 1 })}
          className="bg-gray-300 px-3 py-1 rounded disabled:opacity-50 cursor-pointer">← Anterior</button>
        <span>Página {state.page + 1}</span>
        <button disabled={state.items.length < PAGE_SIZE}
          onClick={() => dispatch({ type: "SET_PAGE", payload: state.page + 1 })}
          className="bg-gray-300 px-3 py-1 rounded disabled:opacity-50 cursor-pointer">Siguiente →</button>
      </div>

      {/* Popup */}
      {subcatPopup && <SubcategoriasPopup categoria={subcatPopup} allCategorias={allCats} onClose={() => setSubcatPopup(null)} />}
    </div>
  );
}
