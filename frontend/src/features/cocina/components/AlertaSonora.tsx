// AlertaSonora — Sound + visual alert for new KDS orders (US-COCINA-05)
//
// Plays a short beep via Web Audio API when a PEDIDO_CONFIRMADO event arrives,
// and optionally shows a full-screen visual flash. The alert can be toggled
// ON/OFF via a button; the preference is persisted in localStorage.
//
// Usage:
//   <AlertaSonora notificar={newOrderCount} />
//
//   Pass the number of new orders received since the last render. When > 0,
//   the component will beep and flash (if enabled).
import { useState, useEffect, useRef, useCallback } from 'react';

// ── Constants ──────────────────────────────────────────────────────────────
const STORAGE_KEY = 'kds_alerta_sonora';
const BEEP_FREQUENCY = 880; // Hz (A5)
const BEEP_DURATION = 0.2; // seconds

// ── Web Audio API beep ─────────────────────────────────────────────────────
let _audioCtx: AudioContext | null = null;
function getAudioContext(): AudioContext {
  if (!_audioCtx) {
    _audioCtx = new AudioContext();
  }
  return _audioCtx;
}

function playBeep(): void {
  try {
    const ctx = getAudioContext();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sine';
    osc.frequency.value = BEEP_FREQUENCY;
    gain.gain.value = 0.3;

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + BEEP_DURATION);
  } catch {
    // Web Audio API not available — silently ignore
  }
}

// ── Props ──────────────────────────────────────────────────────────────────
interface AlertaSonoraProps {
  /** Number of new CONFIRMADO events since last render. Triggers alert when > 0. */
  notificar: number;
}

// ── Component ──────────────────────────────────────────────────────────────
export function AlertaSonora({ notificar }: AlertaSonoraProps) {
  const [habilitado, setHabilitado] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEY) !== 'off';
    } catch {
      return true;
    }
  });

  const [flashVisible, setFlashVisible] = useState(false);
  const prevNotificarRef = useRef(notificar);
  const isInitialMount = useRef(true);
  const flashTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── Toggle handler ───────────────────────────────────────────────────
  const toggle = useCallback(() => {
    setHabilitado((prev) => {
      const next = !prev;
      try {
        localStorage.setItem(STORAGE_KEY, next ? 'on' : 'off');
      } catch {
        // localStorage may be unavailable
      }
      return next;
    });
  }, []);

  // ── Alert on new orders ──────────────────────────────────────────────
  useEffect(() => {
    // Skip initial mount — existing orders should not trigger alerts
    if (isInitialMount.current) {
      isInitialMount.current = false;
      prevNotificarRef.current = notificar;
      return;
    }

    // Only trigger when notificar INCREASES (new orders arrived)
    if (notificar <= prevNotificarRef.current) {
      prevNotificarRef.current = notificar;
      return;
    }
    prevNotificarRef.current = notificar;

    if (!habilitado) return;

    // Play sound
    playBeep();

    // Flash visual
    setFlashVisible(true);
    if (flashTimerRef.current) clearTimeout(flashTimerRef.current);
    flashTimerRef.current = setTimeout(() => setFlashVisible(false), 800);
  }, [notificar, habilitado]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (flashTimerRef.current) clearTimeout(flashTimerRef.current);
    };
  }, []);

  return (
    <>
      {/* Visual flash overlay */}
      {flashVisible && (
        <div className="fixed inset-0 z-50 pointer-events-none bg-yellow-300/30 animate-pulse transition-opacity duration-700" />
      )}

      {/* Toggle button */}
      <button
        onClick={toggle}
        className={`fixed bottom-4 left-4 z-50 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium shadow-lg transition-colors cursor-pointer ${
          habilitado
            ? 'bg-green-600 text-white hover:bg-green-700'
            : 'bg-gray-400 text-white hover:bg-gray-500'
        }`}
        title={habilitado ? 'Desactivar alerta sonora' : 'Activar alerta sonora'}
        aria-label={habilitado ? 'Desactivar alerta sonora' : 'Activar alerta sonora'}
      >
        {/* Speaker icon */}
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          {habilitado ? (
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15.536 8.464a5 5 0 010 7.072M17.95 6.05a8 8 0 010 11.9M6.5 8.5H4a1 1 0 00-1 1v5a1 1 0 001 1h2.5l3.5 3.5V5L6.5 8.5z"
            />
          ) : (
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707A1 1 0 0112 5v14a1 1 0 01-1.707.707L5.586 15z M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2"
            />
          )}
        </svg>
        <span>{habilitado ? 'Sonido ON' : 'Sonido OFF'}</span>
      </button>
    </>
  );
}
