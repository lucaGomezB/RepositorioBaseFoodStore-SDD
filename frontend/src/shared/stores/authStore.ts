// Auth Store - Hybrid (state + React Query delegation)
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '../types/api';

interface AuthState {
  token: string | null;
  refreshToken: string | null;
  user: User | null;
  isLoggedIn: boolean;
}

interface AuthActions {
  setAuth: (token: string, refreshToken: string, user: User) => void;
  logout: () => void;
  updateUser: (user: User) => void;
}

type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      // Initial state
      token: null,
      refreshToken: null,
      user: null,
      isLoggedIn: false,

      // Actions
      setAuth: (token, refreshToken, user) =>
        set({
          token,
          refreshToken,
          user,
          isLoggedIn: true,
        }),

      logout: () =>
        set({
          token: null,
          refreshToken: null,
          user: null,
          isLoggedIn: false,
        }),

      updateUser: (user) =>
        set({
          user,
        }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        // Only persist token and user, not refreshToken for security
        token: state.token,
        user: state.user,
        isLoggedIn: state.isLoggedIn,
      }),
    }
  )
);

// Usage notes:
// - This store holds state only
// - API logic (login, refresh, logout) is handled by React Query mutations
// - After successful login: useAuthStore.getState().setAuth(token, refreshToken, user)
// - After logout: useAuthStore.getState().logout()