import React from 'react';
import { theme } from '../../design-system/tokens';

export type BadgeVariant =
  | 'default'
  | 'primary'
  | 'success'
  | 'warning'
  | 'error'
  | 'info'
  | 'critical'
  | 'high'
  | 'medium'
  | 'low';

export type BadgeSize = 'sm' | 'md' | 'lg';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  /** Visual style variant */
  variant?: BadgeVariant;
  /** Size of the badge */
  size?: BadgeSize;
  /** Icon to display before text */
  leftIcon?: React.ReactNode;
  /** Icon to display after text */
  rightIcon?: React.ReactNode;
  /** Whether badge has dot indicator */
  dot?: boolean;
  /** Children content */
  children?: React.ReactNode;
}

const getVariantStyles = (variant: BadgeVariant) => {
  const variants = {
    default: {
      backgroundColor: theme.colors.background.elevated,
      color: theme.colors.text.secondary,
      border: `1px solid ${theme.colors.border.accent}`,
    },
    primary: {
      backgroundColor: 'rgba(74, 124, 255, 0.15)',
      color: theme.colors.brand.primary,
      border: `1px solid ${theme.colors.brand.primary}`,
    },
    success: {
      backgroundColor: theme.colors.status.passBg,
      color: theme.colors.semantic.success,
      border: `1px solid ${theme.colors.semantic.success}`,
    },
    warning: {
      backgroundColor: theme.colors.status.highBg,
      color: theme.colors.semantic.warning,
      border: `1px solid ${theme.colors.semantic.warning}`,
    },
    error: {
      backgroundColor: theme.colors.status.criticalBg,
      color: theme.colors.semantic.error,
      border: `1px solid ${theme.colors.semantic.error}`,
    },
    info: {
      backgroundColor: 'rgba(59, 130, 246, 0.15)',
      color: theme.colors.semantic.info,
      border: `1px solid ${theme.colors.semantic.info}`,
    },
    critical: {
      backgroundColor: theme.colors.status.criticalBg,
      color: theme.colors.status.critical,
      border: `1px solid ${theme.colors.status.criticalBorder}`,
    },
    high: {
      backgroundColor: theme.colors.status.highBg,
      color: theme.colors.status.high,
      border: `1px solid ${theme.colors.status.highBorder}`,
    },
    medium: {
      backgroundColor: theme.colors.status.mediumBg,
      color: theme.colors.status.medium,
      border: `1px solid ${theme.colors.status.mediumBorder}`,
    },
    low: {
      backgroundColor: theme.colors.status.lowBg,
      color: theme.colors.status.low,
      border: `1px solid ${theme.colors.status.lowBorder}`,
    },
  };

  return variants[variant];
};

const getSizeStyles = (size: BadgeSize) => {
  const sizes = {
    sm: {
      padding: `${theme.spacing[0.5]} ${theme.spacing[2]}`,
      fontSize: theme.typography.fontSize.xs,
      height: '1.25rem',
    },
    md: {
      padding: `${theme.spacing[1]} ${theme.spacing[2.5]}`,
      fontSize: theme.typography.fontSize.sm,
      height: '1.5rem',
    },
    lg: {
      padding: `${theme.spacing[1.5]} ${theme.spacing[3]}`,
      fontSize: theme.typography.fontSize.base,
      height: '2rem',
    },
  };

  return sizes[size];
};

export const Badge: React.FC<BadgeProps> = ({
  variant = 'default',
  size = 'md',
  leftIcon,
  rightIcon,
  dot = false,
  children,
  style,
  ...props
}) => {
  const variantStyles = getVariantStyles(variant);
  const sizeStyles = getSizeStyles(size);

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: theme.spacing[1],
        borderRadius: theme.borderRadius.full,
        fontWeight: theme.typography.fontWeight.medium,
        fontFamily: theme.typography.fontFamily.base,
        textTransform: 'uppercase',
        letterSpacing: theme.typography.letterSpacing.wide,
        whiteSpace: 'nowrap',
        ...variantStyles,
        ...sizeStyles,
        ...style,
      }}
      {...props}
    >
      {dot && (
        <span
          style={{
            width: '0.5rem',
            height: '0.5rem',
            borderRadius: '50%',
            backgroundColor: 'currentColor',
          }}
        />
      )}
      {leftIcon && <span style={{ display: 'flex', alignItems: 'center' }}>{leftIcon}</span>}
      {children && <span>{children}</span>}
      {rightIcon && <span style={{ display: 'flex', alignItems: 'center' }}>{rightIcon}</span>}
    </span>
  );
};

Badge.displayName = 'Badge';

export default Badge;
