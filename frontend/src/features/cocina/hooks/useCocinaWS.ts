// useCocinaWS — WebSocket hook for real-time KDS updates with polling fallback
//
// The browser sends the JWT access_token cookie automatically during the
// WebSocket handshake (RFC 6455). No query parameter is needed.
// When the cookie is not present or the connection fails, the hook
// gracefully falls back to 30-second polling via REST.
import { useState, useEffect, useRef, useCallback } from 'react';
import type { PedidoCocinaRead, CocinaEventType } from '../cocina.types';
import { fetchCocinaPedidos, transicionarEstadoPedido } from '../api';

// ── Constants ──────────────────────────────────────────────────────────────
const WS_BASE = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1/cocina/ws`;
const POLL_INTERVAL_MS = 30000; // 30 second polling fallback
const RECONNECT_BASE_MS = 1000; // 1 second initial reconnect delay
const RECONNECT_MAX_MS = 30000; // 30 second max reconnect delay
const PING_INTERVAL_MS = 25000; // send ping every 25s to keep alive

// ── Types ──────────────────────────────────────────────────────────────────
interface WSMessage {
  type: CocinaEventType | 'pong';
  pedido_id?: number;
}

interface UseCocinaWSReturn {
  pedidos: PedidoCocinaRead[];
  loading: boolean;
  connected: boolean;
  error: string | null;
  iniciarPreparacion: (pedidoId: number) => Promise<void>;
  marcarTerminado: (pedidoId: number) => Promise<void>;
}

// ── Hook ───────────────────────────────────────────────────────────────────
export function useCocinaWS(): UseCocinaWSReturn {
  const [pedidos, setPedidos] = useState<PedidoCocinaRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Refs to persist across renders without causing re-renders
  const wsRef = useRef<WebSocket | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const pingRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectAttemptRef = useRef(0);
  const mountedRef = useRef(true);

  // ── Load initial data via REST ───────────────────────────────────────
  const loadInitial = useCallback(async () => {
    try {
      setError(null);
      const response = await fetchCocinaPedidos();
      if (mountedRef.current) {
        setPedidos(response.items ?? []);
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Error al cargar pedidos';
      if (mountedRef.current) {
        setError(msg);
      }
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, []);

  // ── WebSocket message handler ────────────────────────────────────────
  const handleWSMessage = useCallback(
    (event: MessageEvent) => {
      try {
        const msg: WSMessage = JSON.parse(event.data);

        switch (msg.type) {
          case 'PEDIDO_CONFIRMADO':
            loadInitial();
            break;
          case 'PEDIDO_EN_PREPARACION':
            setPedidos(prev => prev.map(p =>
              p.id === msg.pedido_id ? { ...p, estado_codigo: 'EN_PREPARACION' as const } : p
            ));
            break;
          case 'PEDIDO_EN_CAMINO':
          case 'PEDIDO_CANCELADO':
            setPedidos(prev => prev.filter(p => p.id !== msg.pedido_id));
            break;
          case 'pong':
            // Heartbeat acknowledged — nothing to do
            break;
          default:
            break;
        }
      } catch {
        // Ignore malformed messages
      }
    },
    [loadInitial],
  );

  // ── WebSocket connect ────────────────────────────────────────────────
  const connect = useCallback(() => {
    // Clean up any existing connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    try {
      const ws = new WebSocket(WS_BASE);
      wsRef.current = ws;

      ws.onopen = () => {
        if (mountedRef.current) {
          setConnected(true);
          setError(null);
          reconnectAttemptRef.current = 0;
        }
      };

      ws.onmessage = handleWSMessage;

      ws.onclose = () => {
        if (mountedRef.current) {
          setConnected(false);
          // Exponential backoff reconnect
          const delay = Math.min(
            RECONNECT_BASE_MS * 2 ** reconnectAttemptRef.current,
            RECONNECT_MAX_MS,
          );
          reconnectAttemptRef.current += 1;
          reconnectTimerRef.current = setTimeout(connect, delay);
        }
      };

      ws.onerror = () => {
        // onclose will fire after this, triggering reconnect
        ws.close();
      };
    } catch {
      // WebSocket instantiation failed — polling will handle it
      setConnected(false);
    }
  }, [handleWSMessage]);

  // ── Initialize polling ───────────────────────────────────────────────
  const startPolling = useCallback(() => {
    if (pollRef.current) return; // already polling
    pollRef.current = setInterval(async () => {
      try {
        const response = await fetchCocinaPedidos();
        if (mountedRef.current) {
          setPedidos(response.items ?? []);
        }
      } catch {
        // Silently retry on next interval
      }
    }, POLL_INTERVAL_MS);
  }, []);

  const stopPolling = useCallback(() => {
    if (pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }
  }, []);

  // ── Ping keep-alive ──────────────────────────────────────────────────
  const startPing = useCallback(() => {
    if (pingRef.current) return;
    pingRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send('ping');
      }
    }, PING_INTERVAL_MS);
  }, []);

  const stopPing = useCallback(() => {
    if (pingRef.current) {
      clearInterval(pingRef.current);
      pingRef.current = null;
    }
  }, []);

  // ── Actions ──────────────────────────────────────────────────────────
  const iniciarPreparacion = useCallback(async (pedidoId: number) => {
    await transicionarEstadoPedido(pedidoId, 'EN_PREPARACION');
    // Optimistic update: move to EN_PREPARACION locally
    setPedidos((prev) =>
      prev.map((p) =>
        p.id === pedidoId ? { ...p, estado_codigo: 'EN_PREPARACION' as const } : p,
      ),
    );
  }, []);

  const marcarTerminado = useCallback(async (pedidoId: number) => {
    await transicionarEstadoPedido(pedidoId, 'EN_CAMINO');
    // Optimistic removal: remove from KDS view
    setPedidos((prev) => prev.filter((p) => p.id !== pedidoId));
  }, []);

  // ── Effect: initialize ───────────────────────────────────────────────
  useEffect(() => {
    mountedRef.current = true;

    // Load initial data
    loadInitial();

    // Start polling fallback (always runs and supplements WS)
    startPolling();

    // Try WebSocket connection
    connect();

    // Start ping interval
    startPing();

    // ── Cleanup ──
    return () => {
      mountedRef.current = false;

      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }

      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }

      stopPolling();
      stopPing();
    };
  }, [loadInitial, startPolling, stopPolling, startPing, stopPing, connect]);

  return { pedidos, loading, connected, error, iniciarPreparacion, marcarTerminado };
}
