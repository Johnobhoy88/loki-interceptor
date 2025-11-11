import React, { createContext, useContext, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { theme } from '../../design-system/tokens';

export type ToastVariant = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  title: string;
  message?: string;
  variant: ToastVariant;
  duration?: number;
}

interface ToastContextValue {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
};

const getVariantStyles = (variant: ToastVariant) => {
  const variants = {
    success: {
      backgroundColor: theme.colors.status.passBg,
      borderColor: theme.colors.semantic.success,
      iconColor: theme.colors.semantic.success,
      icon: '✓',
    },
    error: {
      backgroundColor: theme.colors.status.criticalBg,
      borderColor: theme.colors.semantic.error,
      iconColor: theme.colors.semantic.error,
      icon: '✕',
    },
    warning: {
      backgroundColor: theme.colors.status.highBg,
      borderColor: theme.colors.semantic.warning,
      iconColor: theme.colors.semantic.warning,
      icon: '⚠',
    },
    info: {
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      borderColor: theme.colors.semantic.info,
      iconColor: theme.colors.semantic.info,
      icon: 'ℹ',
    },
  };

  return variants[variant];
};

interface ToastItemProps {
  toast: Toast;
  onRemove: (id: string) => void;
}

const ToastItem: React.FC<ToastItemProps> = ({ toast, onRemove }) => {
  const styles = getVariantStyles(toast.variant);

  React.useEffect(() => {
    if (toast.duration !== 0) {
      const timer = setTimeout(() => {
        onRemove(toast.id);
      }, toast.duration || 5000);

      return () => clearTimeout(timer);
    }
  }, [toast.id, toast.duration, onRemove]);

  return (
    <motion.div
      initial={{ x: '100%', opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: '100%', opacity: 0 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
      style={{
        backgroundColor: styles.backgroundColor,
        border: `1px solid ${styles.borderColor}`,
        borderRadius: theme.borderRadius.base,
        padding: `${theme.spacing[3.5]} ${theme.spacing[4]}`,
        minWidth: '280px',
        maxWidth: '400px',
        boxShadow: theme.shadows.xl,
        display: 'flex',
        alignItems: 'flex-start',
        gap: theme.spacing[3],
        pointerEvents: 'all',
      }}
    >
      <div
        style={{
          width: '20px',
          height: '20px',
          borderRadius: theme.borderRadius.sm,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: theme.typography.fontSize.sm,
          fontWeight: theme.typography.fontWeight.bold,
          flexShrink: 0,
          backgroundColor: styles.iconColor,
          color: theme.colors.text.primary,
        }}
      >
        {styles.icon}
      </div>

      <div style={{ flex: 1 }}>
        <div
          style={{
            fontWeight: theme.typography.fontWeight.semibold,
            fontSize: theme.typography.fontSize.base,
            marginBottom: toast.message ? theme.spacing[1] : 0,
            color: theme.colors.text.primary,
          }}
        >
          {toast.title}
        </div>
        {toast.message && (
          <div
            style={{
              fontSize: theme.typography.fontSize.sm,
              color: theme.colors.text.muted,
              lineHeight: theme.typography.lineHeight.snug,
            }}
          >
            {toast.message}
          </div>
        )}
      </div>

      <button
        onClick={() => onRemove(toast.id)}
        style={{
          background: 'transparent',
          border: 'none',
          color: theme.colors.text.muted,
          cursor: 'pointer',
          padding: 0,
          fontSize: theme.typography.fontSize.lg,
          lineHeight: 1,
          transition: `color ${theme.transitions.duration.fast} ${theme.transitions.timing.ease}`,
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.color = theme.colors.text.primary;
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.color = theme.colors.text.muted;
        }}
      >
        ✕
      </button>
    </motion.div>
  );
};

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    setToasts((prev) => [...prev, { ...toast, id }]);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <div
        style={{
          position: 'fixed',
          top: theme.spacing[4],
          right: theme.spacing[4],
          zIndex: theme.zIndex.notification,
          display: 'flex',
          flexDirection: 'column',
          gap: theme.spacing[2],
          pointerEvents: 'none',
        }}
      >
        <AnimatePresence>
          {toasts.map((toast) => (
            <ToastItem key={toast.id} toast={toast} onRemove={removeToast} />
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  );
};

export default ToastProvider;
