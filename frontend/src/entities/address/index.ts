// Address entity — types and TanStack Query hooks

export interface Direccion {
  id: number;
  calle: string;
  numero: string;
  piso_depto?: string;
  ciudad: string;
  codigo_postal: string;
  es_predeterminada: boolean;
  latitud?: number;
  longitud?: number;
}

export interface DireccionCreate {
  calle: string;
  numero: string;
  piso_depto?: string;
  ciudad: string;
  codigo_postal: string;
  latitud?: number;
  longitud?: number;
}

export interface DireccionUpdate {
  calle?: string;
  numero?: string;
  piso_depto?: string;
  ciudad?: string;
  codigo_postal?: string;
  latitud?: number;
  longitud?: number;
}

export {
  useDirecciones,
  useCreateDireccion,
  useUpdateDireccion,
  useDeleteDireccion,
  useSetDefaultDireccion,
} from './api';
