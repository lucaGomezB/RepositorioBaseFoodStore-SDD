// Auth Store tests (httpOnly cookie version)
import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from '../authStore';

describe('authStore', () => {
  const mockUser = {
    id: 1,
    email: 'test@example.com',
    nombre: 'Test',
    apellido: 'User',
    telefono: '123456789',
    rol_id: 1,
    activo: true,
    fecha_creacion: '2024-01-01T00:00:00Z',
    fecha_actualizacion: '2024-01-01T00:00:00Z',
  };

  beforeEach(() => {
    // Reset store to initial state before each test
    useAuthStore.setState({
      user: null,
      isLoggedIn: false,
    });
  });

  it('should start with null user and not logged in', () => {
    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isLoggedIn).toBe(false);
  });

  it('should set user on login', () => {
    useAuthStore.getState().setUser(mockUser);

    const state = useAuthStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.isLoggedIn).toBe(true);
  });

  it('should clear auth state on logout', () => {
    // First login
    useAuthStore.getState().setUser(mockUser);
    expect(useAuthStore.getState().isLoggedIn).toBe(true);

    // Then logout
    useAuthStore.getState().logout();

    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.isLoggedIn).toBe(false);
  });

  it('should update user', () => {
    useAuthStore.getState().setUser(mockUser);

    const updatedUser = { ...mockUser, nombre: 'Updated', apellido: 'Name' };
    useAuthStore.getState().updateUser(updatedUser);

    const state = useAuthStore.getState();
    expect(state.user?.nombre).toBe('Updated');
    expect(state.user?.apellido).toBe('Name');
    expect(state.isLoggedIn).toBe(true);
  });

  it('should handle multiple login/logout cycles', () => {
    // Cycle 1
    useAuthStore.getState().setUser(mockUser);
    expect(useAuthStore.getState().isLoggedIn).toBe(true);

    useAuthStore.getState().logout();
    expect(useAuthStore.getState().isLoggedIn).toBe(false);

    // Cycle 2
    const user2 = { ...mockUser, id: 2, email: 'user2@test.com' };
    useAuthStore.getState().setUser(user2);
    expect(useAuthStore.getState().user?.email).toBe('user2@test.com');
  });
});
