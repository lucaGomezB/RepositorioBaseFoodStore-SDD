// Axios HTTP client with httpOnly cookie auth
//
// Las cookies httpOnly se envian automaticamente con cada request
// gracias a `withCredentials: true`. NO hay request interceptor para
// adjuntar tokens — el backend es la autoridad, las cookies son el
// medio de transporte.
import axios from 'axios';

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL || '/api/v1';

export const httpClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ===========================================================================
// Auth helpers — funciones explicitas, sin magia en interceptors
// ===========================================================================

export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthUser {
  id: number;
  email: string;
  nombre: string;
  apellido: string;
  roles: number[];
  activo: boolean;
}

export interface LoginResult {
  user: AuthUser;
}

/** Login: POST /auth/login → el backend setea cookies httpOnly + devuelve user */
export async function apiLogin(payload: LoginPayload): Promise<LoginResult> {
  const { data } = await httpClient.post('/auth/login', payload);
  return { user: data.user as AuthUser };
}

/** Refresh: POST /auth/refresh → el backend rota cookies httpOnly */
export async function apiRefresh(): Promise<void> {
  await httpClient.post('/auth/refresh', {});
}

/** Logout: POST /auth/logout → backend revoca refresh token + limpia cookies */
export async function apiLogout(): Promise<void> {
  try {
    await httpClient.post('/auth/logout', {});
  } catch {
    // Si el logout falla (ej: token ya expirado), ignoramos
  }
}

/** Me: GET /auth/me → devuelve el usuario si las cookies son validas */
export async function apiMe(): Promise<AuthUser | null> {
  try {
    const { data } = await httpClient.get('/auth/me');
    return data as AuthUser;
  } catch {
    return null;
  }
}
