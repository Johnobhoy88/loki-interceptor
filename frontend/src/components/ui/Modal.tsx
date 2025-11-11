import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { theme } from '../../design-system/tokens';
import { CloseIcon } from '../../assets/icons';

export type ModalSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';

export interface ModalProps {
  /** Whether modal is open */
  isOpen: boolean;
  /** Callback when modal should close */
  onClose: () => void;
  /** Modal title */
  title?: string;
  /** Modal size */
  size?: ModalSize;
  /** Whether to show close button */
  showCloseButton?: boolean;
  /** Whether clicking backdrop closes modal */
  closeOnBackdropClick?: boolean;
  /** Whether pressing Escape closes modal */
  closeOnEscape?: boolean;
  /** Modal header content */
  header?: React.ReactNode;
  /** Modal footer content */
  footer?: React.ReactNode;
  /** Children content */
  children: React.ReactNode;
}

const getSizeStyles = (size: ModalSize) => {
  const sizes = {
    sm: { maxWidth: '400px' },
    md: { maxWidth: '600px' },
    lg: { maxWidth: '800px' },
    xl: { maxWidth: '1200px' },
    full: { maxWidth: '95vw', maxHeight: '95vh' },
  };
  return sizes[size];
};

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  size = 'md',
  showCloseButton = true,
  closeOnBackdropClick = true,
  closeOnEscape = true,
  header,
  footer,
  children,
}) => {
  const sizeStyles = getSizeStyles(size);

  // Handle escape key
  useEffect(() => {
    if (!isOpen || !closeOnEscape) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, closeOnEscape, onClose]);

  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            onClick={closeOnBackdropClick ? onClose : undefined}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: theme.colors.background.overlay,
              zIndex: theme.zIndex.modalBackdrop,
              backdropFilter: 'blur(4px)',
            }}
          />

          {/* Modal */}
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: theme.zIndex.modal,
              padding: theme.spacing[4],
              pointerEvents: 'none',
            }}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
              onClick={(e) => e.stopPropagation()}
              style={{
                backgroundColor: theme.colors.background.modal,
                border: `1px solid ${theme.colors.border.default}`,
                borderRadius: theme.borderRadius.lg,
                boxShadow: theme.shadows['2xl'],
                width: '100%',
                display: 'flex',
                flexDirection: 'column',
                maxHeight: size === 'full' ? '95vh' : '90vh',
                pointerEvents: 'all',
                ...sizeStyles,
              }}
            >
              {/* Header */}
              {(title || header || showCloseButton) && (
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: `${theme.spacing[5]} ${theme.spacing[6]}`,
                    borderBottom: `1px solid ${theme.colors.border.default}`,
                  }}
                >
                  {header || (
                    <h2
                      style={{
                        margin: 0,
                        fontSize: theme.typography.fontSize['2xl'],
                        fontWeight: theme.typography.fontWeight.semibold,
                        color: theme.colors.text.primary,
                      }}
                    >
                      {title}
                    </h2>
                  )}
                  {showCloseButton && (
                    <button
                      onClick={onClose}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: theme.colors.text.muted,
                        cursor: 'pointer',
                        padding: theme.spacing[2],
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        borderRadius: theme.borderRadius.base,
                        transition: `all ${theme.transitions.duration.fast} ${theme.transitions.timing.ease}`,
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = theme.colors.background.elevated;
                        e.currentTarget.style.color = theme.colors.text.primary;
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'transparent';
                        e.currentTarget.style.color = theme.colors.text.muted;
                      }}
                      aria-label="Close modal"
                    >
                      <CloseIcon size={20} />
                    </button>
                  )}
                </div>
              )}

              {/* Content */}
              <div
                style={{
                  padding: `${theme.spacing[6]}`,
                  overflowY: 'auto',
                  flex: 1,
                }}
              >
                {children}
              </div>

              {/* Footer */}
              {footer && (
                <div
                  style={{
                    padding: `${theme.spacing[5]} ${theme.spacing[6]}`,
                    borderTop: `1px solid ${theme.colors.border.default}`,
                    display: 'flex',
                    justifyContent: 'flex-end',
                    gap: theme.spacing[3],
                  }}
                >
                  {footer}
                </div>
              )}
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
};

export default Modal;
