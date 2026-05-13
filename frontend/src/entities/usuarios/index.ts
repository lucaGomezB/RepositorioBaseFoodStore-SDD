// Usuarios entity — types and TanStack Query hooks for admin user management
export type { UsuarioAdmin, UsuariosFilters, UsuariosResponse } from './api';
export {
  useUsuarios,
  useDeleteUsuario,
  useUpdateUsuario,
  useAsignarRol,
} from './api';
