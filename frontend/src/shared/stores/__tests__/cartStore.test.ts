// Cart Store tests
import { describe, it, expect, beforeEach } from 'vitest';
import { useCartStore } from '../cartStore';
import type { ProductoCatalogoRead } from '@/entities/product';

describe('cartStore', () => {
  const mockProducto: ProductoCatalogoRead = {
    id: 1,
    nombre: 'Hamburguesa Clásica',
    precio_base: '15.00',
    descripcion: 'Deliciosa hamburguesa',
    disponible: true,
    imagenes_url: 'https://example.com/img.jpg',
    tiempo_prep_min: 15,
    categoria_ids: [],
    ingredientes: [],
  };

  const mockProducto2: ProductoCatalogoRead = {
    id: 2,
    nombre: 'Papas Fritas',
    precio_base: '8.50',
    descripcion: 'Papas crujientes',
    disponible: true,
    imagenes_url: null,
    tiempo_prep_min: 10,
    categoria_ids: [],
    ingredientes: [],
  };

  beforeEach(() => {
    // Reset store to initial state before each test
    useCartStore.setState({ items: [] });
    localStorage.clear();
  });

  // ── addItem ─────────────────────────────────────────────────

  it('should add a new item to empty cart', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 2);

    const items = useCartStore.getState().items;
    expect(items).toHaveLength(1);
    expect(items[0].productoId).toBe(1);
    expect(items[0].nombre).toBe('Hamburguesa Clásica');
    expect(items[0].cantidad).toBe(2);
    expect(items[0].precio_base).toBe('15.00');
    expect(items[0].imagen_url).toBe('https://example.com/img.jpg');
    expect(items[0].exclusiones).toEqual([]);
  });

  it('should increment quantity if item already exists', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 2);
    store.addItem(mockProducto, 3);

    const items = useCartStore.getState().items;
    expect(items).toHaveLength(1);
    expect(items[0].cantidad).toBe(5);
  });

  it('should add multiple different items', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 1);
    store.addItem(mockProducto2, 3);

    const items = useCartStore.getState().items;
    expect(items).toHaveLength(2);
    expect(items[0].productoId).toBe(1);
    expect(items[1].productoId).toBe(2);
  });

  // ── removeItem ──────────────────────────────────────────────

  it('should remove an item by productoId', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 1);
    store.addItem(mockProducto2, 2);
    expect(useCartStore.getState().items).toHaveLength(2);

    store.removeItem(1);
    const items = useCartStore.getState().items;
    expect(items).toHaveLength(1);
    expect(items[0].productoId).toBe(2);
  });

  it('should not fail when removing non-existent item', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 1);
    store.removeItem(999);

    expect(useCartStore.getState().items).toHaveLength(1);
  });

  // ── clearCart ───────────────────────────────────────────────

  it('should clear all items', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 1);
    store.addItem(mockProducto2, 2);
    expect(useCartStore.getState().items).toHaveLength(2);

    store.clearCart();
    expect(useCartStore.getState().items).toHaveLength(0);
  });

  it('should clear an already empty cart without errors', () => {
    const store = useCartStore.getState();
    store.clearCart();
    expect(useCartStore.getState().items).toHaveLength(0);
  });

  // ── addExclusion ────────────────────────────────────────────

  it('should add an exclusion to an item', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 1);

    store.addExclusion(1, 5);
    const items = useCartStore.getState().items;
    expect(items[0].exclusiones).toEqual([5]);
  });

  it('should not duplicate an exclusion', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 1);

    store.addExclusion(1, 5);
    store.addExclusion(1, 5); // Add same exclusion again

    const items = useCartStore.getState().items;
    expect(items[0].exclusiones).toEqual([5]); // Still only one
  });

  it('should add multiple exclusions to an item', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 2);

    store.addExclusion(1, 3);
    store.addExclusion(1, 7);
    store.addExclusion(1, 9);

    const items = useCartStore.getState().items;
    expect(items[0].exclusiones).toEqual([3, 7, 9]);
  });

  it('should not add exclusion to non-existent item', () => {
    const store = useCartStore.getState();
    store.addExclusion(999, 1);

    expect(useCartStore.getState().items).toHaveLength(0);
  });

  // ── removeExclusion ─────────────────────────────────────────

  it('should remove an exclusion from an item', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 1);
    store.addExclusion(1, 3);
    store.addExclusion(1, 5);
    expect(useCartStore.getState().items[0].exclusiones).toEqual([3, 5]);

    store.removeExclusion(1, 3);
    const items = useCartStore.getState().items;
    expect(items[0].exclusiones).toEqual([5]);
  });

  // ── updateQuantity ──────────────────────────────────────────

  it('should update quantity of an item', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 1);

    store.updateQuantity(1, 5);
    expect(useCartStore.getState().items[0].cantidad).toBe(5);
  });

  it('should remove item if quantity is set to 0 or negative', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 1);

    store.updateQuantity(1, 0);
    expect(useCartStore.getState().items).toHaveLength(0);
  });

  // ── getItem ─────────────────────────────────────────────────

  it('should find an item by productoId', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 1);
    store.addItem(mockProducto2, 2);

    const item = store.getItem(2);
    expect(item).toBeDefined();
    expect(item!.nombre).toBe('Papas Fritas');
  });

  it('should return undefined for non-existent item', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 1);
    const item = store.getItem(999);
    expect(item).toBeUndefined();
  });

  // ── getItemCount ────────────────────────────────────────────

  it('should return total count of all items', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 3);
    store.addItem(mockProducto2, 2);

    expect(store.getItemCount()).toBe(5);
  });

  it('should return 0 for empty cart', () => {
    const store = useCartStore.getState();
    expect(store.getItemCount()).toBe(0);
  });

  // ── getTotal ────────────────────────────────────────────────

  it('should calculate total price correctly', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 2);    // 15.00 * 2 = 30
    store.addItem(mockProducto2, 3);   // 8.50 * 3 = 25.50

    expect(store.getTotal()).toBe(55.5);
  });

  it('should return 0 for empty cart total', () => {
    const store = useCartStore.getState();
    expect(store.getTotal()).toBe(0);
  });

  // ── Edge cases ──────────────────────────────────────────────

  it('should add item with custom exclusiones', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 1, [2, 4, 6]);

    const items = useCartStore.getState().items;
    expect(items[0].exclusiones).toEqual([2, 4, 6]);
  });

  it('should handle addExclusion on items with existing exclusiones', () => {
    const store = useCartStore.getState();
    store.addItem(mockProducto, 1, [1, 2]);

    store.addExclusion(1, 3);
    const items = useCartStore.getState().items;
    expect(items[0].exclusiones).toEqual([1, 2, 3]);
  });
});
