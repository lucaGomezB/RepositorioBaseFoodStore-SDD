// Address entity — types and TanStack Query hooks

export interface Direccion {
  id: number;
  calle: string;
  numero: string;
  piso_depto?: string;
  ciudad: string;
  codigo_postal: string;
  es_predeterminada: boolean;
}

export interface DireccionCreate {
  calle: string;
  numero: string;
  piso_depto?: string;
  ciudad: string;
  codigo_postal: string;
}

export interface DireccionUpdate {
  calle?: string;
  numero?: string;
  piso_depto?: string;
  ciudad?: string;
  codigo_postal?: string;
}

export {
  useDirecciones,
  useCreateDireccion,
  useUpdateDireccion,
  useDeleteDireccion,
  useSetDefaultDireccion,
} from './api';
