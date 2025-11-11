import React from 'react';
import { motion } from 'framer-motion';
import { theme } from '../../design-system/tokens';

export type SpinnerSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
export type SpinnerVariant = 'default' | 'primary' | 'success' | 'error';

export interface SpinnerProps {
  /** Size of the spinner */
  size?: SpinnerSize;
  /** Color variant */
  variant?: SpinnerVariant;
  /** Custom color override */
  color?: string;
  /** Label for accessibility */
  label?: string;
}

const getSizeValue = (size: SpinnerSize): string => {
  const sizes = {
    xs: '1rem',
    sm: '1.5rem',
    md: '2rem',
    lg: '2.5rem',
    xl: '3rem',
  };
  return sizes[size];
};

const getVariantColor = (variant: SpinnerVariant): string => {
  const colors = {
    default: theme.colors.text.secondary,
    primary: theme.colors.brand.primary,
    success: theme.colors.semantic.success,
    error: theme.colors.semantic.error,
  };
  return colors[variant];
};

export const Spinner: React.FC<SpinnerProps> = ({
  size = 'md',
  variant = 'default',
  color,
  label = 'Loading...',
}) => {
  const sizeValue = getSizeValue(size);
  const colorValue = color || getVariantColor(variant);

  return (
    <div
      role="status"
      aria-label={label}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <motion.div
        animate={{ rotate: 360 }}
        transition={{
          duration: 1,
          repeat: Infinity,
          ease: 'linear',
        }}
        style={{
          width: sizeValue,
          height: sizeValue,
          border: `2px solid ${colorValue}`,
          borderTopColor: 'transparent',
          borderRadius: '50%',
        }}
      />
      <span style={{ position: 'absolute', width: '1px', height: '1px', overflow: 'hidden', clip: 'rect(0,0,0,0)' }}>
        {label}
      </span>
    </div>
  );
};

export const SpinnerOverlay: React.FC<SpinnerProps & { message?: string }> = ({
  size = 'lg',
  variant = 'primary',
  message,
  ...props
}) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: theme.spacing[4],
        backgroundColor: theme.colors.background.overlay,
        zIndex: theme.zIndex.modal,
        backdropFilter: 'blur(4px)',
      }}
    >
      <Spinner size={size} variant={variant} {...props} />
      {message && (
        <p
          style={{
            margin: 0,
            fontSize: theme.typography.fontSize.base,
            color: theme.colors.text.secondary,
          }}
        >
          {message}
        </p>
      )}
    </motion.div>
  );
};

export default Spinner;
