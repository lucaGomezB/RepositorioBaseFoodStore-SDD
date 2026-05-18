// UI Store tests
import { describe, it, expect, beforeEach } from 'vitest';
import { useUIStore } from '../uiStore';

describe('uiStore', () => {
  beforeEach(() => {
    // Reset store to initial state
    useUIStore.setState({
      theme: 'light',
      sidebarOpen: false,
      activeModal: null,
      toasts: [],
      cartDrawerOpen: false,
    });
    localStorage.clear();
  });

  it('should start with default state', () => {
    const state = useUIStore.getState();
    expect(state.theme).toBe('light');
    expect(state.sidebarOpen).toBe(false);
    expect(state.activeModal).toBeNull();
    expect(state.toasts).toEqual([]);
    expect(state.cartDrawerOpen).toBe(false);
  });

  // ── Theme ───────────────────────────────────────────────────

  it('should toggle theme from light to dark', () => {
    useUIStore.getState().toggleTheme();
    expect(useUIStore.getState().theme).toBe('dark');
  });

  it('should toggle theme from dark to light', () => {
    useUIStore.getState().setTheme('dark');
    useUIStore.getState().toggleTheme();
    expect(useUIStore.getState().theme).toBe('light');
  });

  it('should set theme explicitly', () => {
    useUIStore.getState().setTheme('dark');
    expect(useUIStore.getState().theme).toBe('dark');

    useUIStore.getState().setTheme('light');
    expect(useUIStore.getState().theme).toBe('light');
  });

  // ── Sidebar ─────────────────────────────────────────────────

  it('should toggle sidebar', () => {
    useUIStore.getState().toggleSidebar();
    expect(useUIStore.getState().sidebarOpen).toBe(true);

    useUIStore.getState().toggleSidebar();
    expect(useUIStore.getState().sidebarOpen).toBe(false);
  });

  it('should set sidebar explicitly', () => {
    useUIStore.getState().setSidebarOpen(true);
    expect(useUIStore.getState().sidebarOpen).toBe(true);

    useUIStore.getState().setSidebarOpen(false);
    expect(useUIStore.getState().sidebarOpen).toBe(false);
  });

  // ── Modal ───────────────────────────────────────────────────

  it('should open and close modal', () => {
    useUIStore.getState().openModal('confirm-delete');
    expect(useUIStore.getState().activeModal).toBe('confirm-delete');

    useUIStore.getState().closeModal();
    expect(useUIStore.getState().activeModal).toBeNull();
  });

  // ── Toasts ──────────────────────────────────────────────────

  it('should add a toast', () => {
    useUIStore.getState().addToast({
      type: 'success',
      message: 'Operación exitosa',
      duration: 3000,
    });

    const toasts = useUIStore.getState().toasts;
    expect(toasts).toHaveLength(1);
    expect(toasts[0].type).toBe('success');
    expect(toasts[0].message).toBe('Operación exitosa');
    expect(toasts[0].duration).toBe(3000);
    expect(toasts[0].id).toBeDefined();
  });

  it('should add a toast without explicit duration (defaults to 5000ms timeout)', () => {
    useUIStore.getState().addToast({
      type: 'info',
      message: 'Info message',
    });

    const toasts = useUIStore.getState().toasts;
    expect(toasts).toHaveLength(1);
    // duration is optional; store stores what was passed (undefined)
    // but the auto-remove runs at 5000ms internally
    expect(toasts[0].duration).toBeUndefined();
  });

  it('should remove a toast by id', () => {
    useUIStore.getState().addToast({ type: 'success', message: 'First' });
    useUIStore.getState().addToast({ type: 'error', message: 'Second' });

    const idToRemove = useUIStore.getState().toasts[0].id;
    useUIStore.getState().removeToast(idToRemove);

    const toasts = useUIStore.getState().toasts;
    expect(toasts).toHaveLength(1);
    expect(toasts[0].message).toBe('Second');
  });

  it('should clear all toasts', () => {
    useUIStore.getState().addToast({ type: 'success', message: 'First' });
    useUIStore.getState().addToast({ type: 'error', message: 'Second' });

    useUIStore.getState().clearToasts();
    expect(useUIStore.getState().toasts).toHaveLength(0);
  });

  // ── Cart Drawer ─────────────────────────────────────────────

  it('should toggle cart drawer', () => {
    useUIStore.getState().toggleCartDrawer();
    expect(useUIStore.getState().cartDrawerOpen).toBe(true);

    useUIStore.getState().toggleCartDrawer();
    expect(useUIStore.getState().cartDrawerOpen).toBe(false);
  });

  it('should set cart drawer explicitly', () => {
    useUIStore.getState().setCartDrawerOpen(true);
    expect(useUIStore.getState().cartDrawerOpen).toBe(true);

    useUIStore.getState().setCartDrawerOpen(false);
    expect(useUIStore.getState().cartDrawerOpen).toBe(false);
  });
});
