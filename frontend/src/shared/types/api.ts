// API response types

export interface User {
  id: number;
  email: string;
  nombre: string;
  apellido: string;
  telefono?: string;
  rol_id: number;
  activo: boolean;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface Producto {
  id: number;
  nombre: string;
  descripcion?: string;
  precio_base: number;
  imagenes_url?: string;
  tiempo_prep_min: number;
  disponible: boolean;
  fecha_creacion?: string;
  fecha_actualizacion?: string;
}

export interface Categoria {
  id: number;
  nombre: string;
  descripcion?: string;
  parent_id?: number;
  orden_display: number;
}

export interface Ingrediente {
  id: number;
  nombre: string;
  descripcion?: string;
}

// Toast notification types
export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}