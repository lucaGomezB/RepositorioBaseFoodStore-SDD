// ToastContainer – renders toasts from uiStore in top-right corner
import { useEffect, useState } from 'react';
import { useUIStore, selectToasts } from '../stores/uiStore';
import { ToastType } from '../types/api';

const borderColors: Record<ToastType, string> = {
  success: 'border-l-green-500',
  error: 'border-l-red-500',
  warning: 'border-l-yellow-500',
  info: 'border-l-blue-500',
};

const iconColors: Record<ToastType, string> = {
  success: 'text-green-500',
  error: 'text-red-500',
  warning: 'text-yellow-500',
  info: 'text-blue-500',
};

const icons: Record<ToastType, string> = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ',
};

interface ToastItemProps {
  id: string;
  type: ToastType;
  message: string;
  onRemove: (id: string) => void;
}

function ToastItem({ id, type, message, onRemove }: ToastItemProps) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Trigger enter animation on next frame
    const frame = requestAnimationFrame(() => setVisible(true));
    return () => cancelAnimationFrame(frame);
  }, []);

  return (
    <div
      className={`
        flex items-start gap-3 bg-white rounded-lg shadow-lg border-l-4
        px-4 py-3 max-w-sm w-full pointer-events-auto
        transition-all duration-300 ease-in-out
        ${borderColors[type]}
        ${
          visible
            ? 'translate-x-0 opacity-100'
            : 'translate-x-full opacity-0'
        }
      `}
      role="alert"
    >
      <span className={`text-base font-bold flex-shrink-0 mt-0.5 ${iconColors[type]}`}>
        {icons[type]}
      </span>
      <p className="text-sm text-gray-700 flex-1 leading-relaxed">{message}</p>
      <button
        onClick={() => onRemove(id)}
        className="text-gray-400 hover:text-gray-600 text-lg leading-none flex-shrink-0 ml-2 cursor-pointer transition-colors"
        aria-label="Cerrar"
      >
        ×
      </button>
    </div>
  );
}

export default function ToastContainer() {
  const toasts = useUIStore(selectToasts);
  const removeToast = useUIStore((state) => state.removeToast);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      {toasts.map((toast) => (
        <ToastItem
          key={toast.id}
          id={toast.id}
          type={toast.type}
          message={toast.message}
          onRemove={removeToast}
        />
      ))}
    </div>
  );
}
