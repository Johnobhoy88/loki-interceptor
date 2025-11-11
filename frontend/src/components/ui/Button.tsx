import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { theme } from '../../design-system/tokens';

export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
export type ButtonSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

export interface ButtonProps extends Omit<HTMLMotionProps<'button'>, 'size'> {
  /** Visual style variant */
  variant?: ButtonVariant;
  /** Size of the button */
  size?: ButtonSize;
  /** Whether button is disabled */
  disabled?: boolean;
  /** Whether button should take full width */
  fullWidth?: boolean;
  /** Icon to display before text */
  leftIcon?: React.ReactNode;
  /** Icon to display after text */
  rightIcon?: React.ReactNode;
  /** Whether button is in loading state */
  loading?: boolean;
  /** Children content */
  children?: React.ReactNode;
}

const getVariantStyles = (variant: ButtonVariant, disabled: boolean) => {
  if (disabled) {
    return {
      backgroundColor: theme.colors.background.elevated,
      color: theme.colors.text.disabled,
      border: `1px solid ${theme.colors.border.default}`,
      cursor: 'not-allowed',
      opacity: 0.5,
    };
  }

  const variants = {
    primary: {
      backgroundColor: theme.colors.brand.primary,
      color: theme.colors.text.primary,
      border: `1px solid ${theme.colors.brand.primary}`,
      hover: {
        backgroundColor: theme.colors.brand.primaryHover,
        border: `1px solid ${theme.colors.brand.primaryHover}`,
      },
    },
    secondary: {
      backgroundColor: theme.colors.brand.secondary,
      color: theme.colors.text.primary,
      border: `1px solid ${theme.colors.brand.secondary}`,
      hover: {
        backgroundColor: theme.colors.brand.secondaryHover,
        border: `1px solid ${theme.colors.brand.secondaryHover}`,
      },
    },
    outline: {
      backgroundColor: 'transparent',
      color: theme.colors.brand.primary,
      border: `1px solid ${theme.colors.brand.primary}`,
      hover: {
        backgroundColor: 'rgba(74, 124, 255, 0.1)',
        color: theme.colors.text.primary,
      },
    },
    ghost: {
      backgroundColor: 'transparent',
      color: theme.colors.text.secondary,
      border: '1px solid transparent',
      hover: {
        backgroundColor: theme.colors.background.elevated,
        color: theme.colors.text.primary,
      },
    },
    danger: {
      backgroundColor: theme.colors.semantic.error,
      color: theme.colors.text.primary,
      border: `1px solid ${theme.colors.semantic.error}`,
      hover: {
        backgroundColor: theme.colors.semantic.errorDark,
        border: `1px solid ${theme.colors.semantic.errorDark}`,
      },
    },
  };

  return variants[variant];
};

const getSizeStyles = (size: ButtonSize) => {
  const sizes = {
    xs: {
      height: theme.componentSizes.button.xs.height,
      padding: theme.componentSizes.button.xs.padding,
      fontSize: theme.componentSizes.button.xs.fontSize,
    },
    sm: {
      height: theme.componentSizes.button.sm.height,
      padding: theme.componentSizes.button.sm.padding,
      fontSize: theme.componentSizes.button.sm.fontSize,
    },
    md: {
      height: theme.componentSizes.button.md.height,
      padding: theme.componentSizes.button.md.padding,
      fontSize: theme.componentSizes.button.md.fontSize,
    },
    lg: {
      height: theme.componentSizes.button.lg.height,
      padding: theme.componentSizes.button.lg.padding,
      fontSize: theme.componentSizes.button.lg.fontSize,
    },
    xl: {
      height: theme.componentSizes.button.xl.height,
      padding: theme.componentSizes.button.xl.padding,
      fontSize: theme.componentSizes.button.xl.fontSize,
    },
  };

  return sizes[size];
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      disabled = false,
      fullWidth = false,
      leftIcon,
      rightIcon,
      loading = false,
      children,
      style,
      ...props
    },
    ref
  ) => {
    const variantStyles = getVariantStyles(variant, disabled || loading);
    const sizeStyles = getSizeStyles(size);

    return (
      <motion.button
        ref={ref}
        disabled={disabled || loading}
        whileHover={!disabled && !loading ? { scale: 1.02 } : undefined}
        whileTap={!disabled && !loading ? { scale: 0.98 } : undefined}
        transition={{ duration: 0.15 }}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: theme.spacing[2],
          borderRadius: theme.borderRadius.base,
          fontWeight: theme.typography.fontWeight.medium,
          fontFamily: theme.typography.fontFamily.base,
          cursor: disabled || loading ? 'not-allowed' : 'pointer',
          transition: `all ${theme.transitions.duration.base} ${theme.transitions.timing.ease}`,
          outline: 'none',
          width: fullWidth ? '100%' : 'auto',
          boxShadow: variant === 'primary' ? theme.shadows.sm : 'none',
          ...variantStyles,
          ...sizeStyles,
          ...style,
        }}
        {...props}
      >
        {loading && (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            style={{
              width: '1em',
              height: '1em',
              border: '2px solid currentColor',
              borderTopColor: 'transparent',
              borderRadius: '50%',
            }}
          />
        )}
        {!loading && leftIcon && <span style={{ display: 'flex', alignItems: 'center' }}>{leftIcon}</span>}
        {children && <span>{children}</span>}
        {!loading && rightIcon && <span style={{ display: 'flex', alignItems: 'center' }}>{rightIcon}</span>}
      </motion.button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
