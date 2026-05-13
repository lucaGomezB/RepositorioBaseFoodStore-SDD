// Cart Store — Zustand with localStorage persistence
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { ProductoCatalogoRead } from '@/entities/product';

export interface CartItem {
  productoId: number;
  nombre: string;
  precio_base: string;
  cantidad: number;
  exclusiones: number[];
  imagen_url: string | null;
}

interface CartState {
  items: CartItem[];
}

interface CartActions {
  addItem: (
    producto: ProductoCatalogoRead,
    cantidad: number,
    exclusiones?: number[],
  ) => void;
  removeItem: (productoId: number) => void;
  updateQuantity: (productoId: number, cantidad: number) => void;
  addExclusion: (productoId: number, ingredienteId: number) => void;
  removeExclusion: (productoId: number, ingredienteId: number) => void;
  getItem: (productoId: number) => CartItem | undefined;
  clearCart: () => void;
  getItemCount: () => number;
  getTotal: () => number;
}

type CartStore = CartState & CartActions;

export const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      // ── State ──
      items: [] as CartItem[],

      // ── Actions ──

      addItem: (producto, cantidad, exclusiones = []) => {
        const items = get().items;
        const existingIndex = items.findIndex(
          (item) => item.productoId === producto.id,
        );

        if (existingIndex >= 0) {
          set({
            items: items.map((item, index) =>
              index === existingIndex
                ? { ...item, cantidad: item.cantidad + cantidad }
                : item,
            ),
          });
        } else {
          set({
            items: [
              ...items,
              {
                productoId: producto.id,
                nombre: producto.nombre,
                precio_base: producto.precio_base,
                cantidad,
                exclusiones,
                imagen_url: producto.imagenes_url,
              },
            ],
          });
        }
      },

      removeItem: (productoId) => {
        set({
          items: get().items.filter((item) => item.productoId !== productoId),
        });
      },

      updateQuantity: (productoId, cantidad) => {
        if (cantidad <= 0) {
          get().removeItem(productoId);
          return;
        }
        set({
          items: get().items.map((item) =>
            item.productoId === productoId ? { ...item, cantidad } : item,
          ),
        });
      },

      addExclusion: (productoId, ingredienteId) => {
        set({
          items: get().items.map((item) =>
            item.productoId === productoId &&
            !item.exclusiones.includes(ingredienteId)
              ? { ...item, exclusiones: [...item.exclusiones, ingredienteId] }
              : item,
          ),
        });
      },

      removeExclusion: (productoId, ingredienteId) => {
        set({
          items: get().items.map((item) =>
            item.productoId === productoId
              ? {
                  ...item,
                  exclusiones: item.exclusiones.filter(
                    (id) => id !== ingredienteId,
                  ),
                }
              : item,
          ),
        });
      },

      getItem: (productoId) => {
        return get().items.find((item) => item.productoId === productoId);
      },

      clearCart: () => {
        set({ items: [] });
      },

      getItemCount: () => {
        return get().items.reduce((total, item) => total + item.cantidad, 0);
      },

      getTotal: () => {
        return get().items.reduce((total, item) => {
          const precio = Number(item.precio_base) || 0;
          return total + precio * item.cantidad;
        }, 0);
      },
    }),
    {
      name: 'cart-storage',
    },
  ),
);

// ── Selector helpers ──
export const selectCartItems = (state: CartStore) => state.items;
export const selectCartItemCount = (state: CartStore) => state.getItemCount();
export const selectCartTotal = (state: CartStore) => state.getTotal();
export const selectIsCartEmpty = (state: CartStore) => state.items.length === 0;
