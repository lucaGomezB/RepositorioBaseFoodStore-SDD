// Auth Store — persiste el usuario en localStorage para que sobreviva a recargas
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AuthUser } from '../api/httpClient';
import { useCartStore } from './cartStore';

interface AuthState {
  user: AuthUser | null;
  isLoggedIn: boolean;
  /** JWT access token for WebSocket connections (not persisted, in-memory only) */
  accessToken: string | null;
}

interface AuthActions {
  setUser: (user: AuthUser) => void;
  logout: () => void;
  updateUser: (user: AuthUser) => void;
  setAccessToken: (token: string) => void;
}

type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      isLoggedIn: false,
      accessToken: null,

      setUser: (user) => {
        if (!user) return;
        set({ user, isLoggedIn: true });
      },

      setAccessToken: (token) => {
        set({ accessToken: token });
      },

      logout: () => {
        // Clear cart when user logs out (cart is per-user, not shared across sessions)
        useCartStore.getState().clearCart();
        set({ user: null, isLoggedIn: false, accessToken: null });
      },

      updateUser: (user) =>
        set({ user }),
    }),
    {
      name: 'food-store-auth',
      // Solo persistimos el usuario (no hay tokens que persistir, son httpOnly)
      partialize: (state) => ({
        user: state.user,
        isLoggedIn: state.isLoggedIn,
      }),
    },
  ),
);
