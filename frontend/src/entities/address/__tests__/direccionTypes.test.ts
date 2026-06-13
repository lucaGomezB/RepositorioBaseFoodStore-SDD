// Direccion types — verify that latitud/longitud are accepted and optional
import { describe, it, expect } from 'vitest';
import type { Direccion, DireccionCreate, DireccionUpdate } from '../index';

describe('Direccion types — latitud / longitud fields', () => {
  it('should accept latitud and longitud in Direccion', () => {
    const direccion: Direccion = {
      id: 1,
      calle: 'Test',
      numero: '123',
      ciudad: 'Test',
      codigo_postal: '1234',
      es_predeterminada: false,
      latitud: -34.6037,
      longitud: -58.3816,
    };
    expect(direccion.latitud).toBe(-34.6037);
    expect(direccion.longitud).toBe(-58.3816);
  });

  it('should make latitud and longitud optional in Direccion', () => {
    const direccion: Direccion = {
      id: 1,
      calle: 'Test',
      numero: '123',
      ciudad: 'Test',
      codigo_postal: '1234',
      es_predeterminada: false,
    };
    expect(direccion.latitud).toBeUndefined();
    expect(direccion.longitud).toBeUndefined();
  });

  it('should accept latitud and longitud in DireccionCreate', () => {
    const payload: DireccionCreate = {
      calle: 'Test',
      numero: '123',
      ciudad: 'Test',
      codigo_postal: '1234',
      latitud: -34.6037,
      longitud: -58.3816,
    };
    expect(payload.latitud).toBe(-34.6037);
    expect(payload.longitud).toBe(-58.3816);
  });

  it('should make latitud and longitud optional in DireccionCreate', () => {
    const payload: DireccionCreate = {
      calle: 'Test',
      numero: '123',
      ciudad: 'Test',
      codigo_postal: '1234',
    };
    expect(payload.latitud).toBeUndefined();
  });

  it('should accept latitud and longitud in DireccionUpdate', () => {
    const payload: DireccionUpdate = {
      latitud: -34.6037,
      longitud: -58.3816,
    };
    expect(payload.latitud).toBe(-34.6037);
    expect(payload.longitud).toBe(-58.3816);
  });

  it('should make latitud and longitud optional in DireccionUpdate', () => {
    const payload: DireccionUpdate = {};
    expect(payload.latitud).toBeUndefined();
  });
});
