// Auth Store — persiste el usuario en localStorage para que sobreviva a recargas
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AuthUser } from '../api/httpClient';

interface AuthState {
  user: AuthUser | null;
  isLoggedIn: boolean;
}

interface AuthActions {
  setUser: (user: AuthUser) => void;
  logout: () => void;
  updateUser: (user: AuthUser) => void;
}

type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      isLoggedIn: false,

      setUser: (user) => {
        if (!user) return;
        set({ user, isLoggedIn: true });
      },

      logout: () =>
        set({ user: null, isLoggedIn: false }),

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
