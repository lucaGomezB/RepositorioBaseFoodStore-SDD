// UI Store - State-only (simple setters)
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Toast } from '../types/api';

interface UIState {
  theme: 'light' | 'dark';
  sidebarOpen: boolean;
  activeModal: string | null;
  toasts: Toast[];
  cartDrawerOpen: boolean;
}

interface UIActions {
  toggleTheme: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  openModal: (modalId: string) => void;
  closeModal: () => void;
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  clearToasts: () => void;
  toggleCartDrawer: () => void;
  setCartDrawerOpen: (open: boolean) => void;
}

type UIStore = UIState & UIActions;

export const useUIStore = create<UIStore>()(
  persist(
    (set, get) => ({
      // Initial state
      theme: 'light',
      sidebarOpen: false,
      activeModal: null,
      toasts: [],
      cartDrawerOpen: false,

      // Actions
      toggleTheme: () => {
        const newTheme = get().theme === 'light' ? 'dark' : 'light';
        set({ theme: newTheme });
      },

      setTheme: (theme) => {
        set({ theme });
      },

      toggleSidebar: () => {
        set({ sidebarOpen: !get().sidebarOpen });
      },

      setSidebarOpen: (open) => {
        set({ sidebarOpen: open });
      },

      openModal: (modalId) => {
        set({ activeModal: modalId });
      },

      closeModal: () => {
        set({ activeModal: null });
      },

      addToast: (toast) => {
        const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        const newToast: Toast = { ...toast, id };
        set({ toasts: [...get().toasts, newToast] });

        // Auto-remove after default duration (5 seconds)
        const duration = toast.duration || 5000;
        setTimeout(() => {
          get().removeToast(id);
        }, duration);
      },

      removeToast: (id) => {
        set({
          toasts: get().toasts.filter((toast) => toast.id !== id),
        });
      },

      clearToasts: () => {
        set({ toasts: [] });
      },

      toggleCartDrawer: () => {
        set({ cartDrawerOpen: !get().cartDrawerOpen });
      },

      setCartDrawerOpen: (open) => {
        set({ cartDrawerOpen: open });
      },
    }),
    {
      name: 'ui-storage',
      partialize: (state) => ({
        // Only persist theme, not UI state that resets on reload
        theme: state.theme,
      }),
    }
  )
);

// Convenience selectors
export const selectTheme = (state: UIStore) => state.theme;
export const selectSidebarOpen = (state: UIStore) => state.sidebarOpen;
export const selectActiveModal = (state: UIStore) => state.activeModal;
export const selectToasts = (state: UIStore) => state.toasts;
export const selectCartDrawerOpen = (state: UIStore) => state.cartDrawerOpen;