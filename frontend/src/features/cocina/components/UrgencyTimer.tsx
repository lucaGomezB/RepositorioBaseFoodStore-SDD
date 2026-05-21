// UrgencyTimer — Displays elapsed kitchen time with color-coded urgency
//
// Thresholds (from RN-CO01 / US-COCINA-02):
//   < 10 min  → normal   (gray / green)
//   10–20 min → warning  (orange)
//   > 20 min  → critical (red)
//
// Recalculates every 15 seconds to keep the display fresh.
import { useState, useEffect } from 'react';

interface UrgencyTimerProps {
  /** Elapsed seconds since the order entered the kitchen */
  tiempoEnCocinaSegundos: number;
}

function formatDuration(totalSeconds: number): string {
  const m = Math.floor(totalSeconds / 60);
  const s = totalSeconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function getUrgencyLevel(totalSeconds: number): 'normal' | 'warning' | 'critical' {
  if (totalSeconds >= 1200) return 'critical'; // >= 20 min
  if (totalSeconds >= 600) return 'warning';   // >= 10 min
  return 'normal';
}

const URGENCY_STYLES: Record<string, string> = {
  normal: 'bg-gray-100 text-gray-700 border-gray-300',
  warning: 'bg-orange-100 text-orange-800 border-orange-400 animate-pulse',
  critical: 'bg-red-100 text-red-800 border-red-500 animate-pulse font-bold',
};

export function UrgencyTimer({ tiempoEnCocinaSegundos }: UrgencyTimerProps) {
  // Recalculate every 15 seconds to keep elapsed time accurate
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => setTick((t) => t + 1), 15000);
    return () => clearInterval(interval);
  }, []);

  // Use current tick as a signal to re-render; elapsed = base + tick*15
  // We use the server-provided `tiempoEnCocinaSegundos` as the base,
  // and add 15s per tick since mount to keep it "live".
  // This provides a reasonable approximation without WebSocket sync.
  const elapsed = tiempoEnCocinaSegundos + tick * 15;
  const level = getUrgencyLevel(elapsed);

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${URGENCY_STYLES[level]}`}
      title={`Tiempo en cocina: ${formatDuration(elapsed)}`}
    >
      {/* Clock icon */}
      <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      {formatDuration(elapsed)}
    </span>
  );
}
