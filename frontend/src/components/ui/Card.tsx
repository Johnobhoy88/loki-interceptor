import React from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { theme } from '../../design-system/tokens';

export type CardVariant = 'default' | 'elevated' | 'outlined' | 'ghost';
export type CardPadding = 'none' | 'sm' | 'md' | 'lg';

export interface CardProps extends HTMLMotionProps<'div'> {
  /** Visual style variant */
  variant?: CardVariant;
  /** Padding size */
  padding?: CardPadding;
  /** Whether card is hoverable */
  hoverable?: boolean;
  /** Whether card is clickable */
  clickable?: boolean;
  /** Card header content */
  header?: React.ReactNode;
  /** Card footer content */
  footer?: React.ReactNode;
  /** Children content */
  children?: React.ReactNode;
}

const getVariantStyles = (variant: CardVariant) => {
  const variants = {
    default: {
      backgroundColor: theme.colors.background.panel,
      border: `1px solid ${theme.colors.border.default}`,
      boxShadow: theme.shadows.sm,
    },
    elevated: {
      backgroundColor: theme.colors.background.elevated,
      border: `1px solid ${theme.colors.border.default}`,
      boxShadow: theme.shadows.md,
    },
    outlined: {
      backgroundColor: 'transparent',
      border: `1px solid ${theme.colors.border.accent}`,
      boxShadow: 'none',
    },
    ghost: {
      backgroundColor: 'transparent',
      border: 'none',
      boxShadow: 'none',
    },
  };

  return variants[variant];
};

const getPaddingValue = (padding: CardPadding) => {
  const paddings = {
    none: theme.spacing[0],
    sm: theme.spacing[3],
    md: theme.spacing[5],
    lg: theme.spacing[6],
  };

  return paddings[padding];
};

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
  (
    {
      variant = 'default',
      padding = 'md',
      hoverable = false,
      clickable = false,
      header,
      footer,
      children,
      style,
      ...props
    },
    ref
  ) => {
    const variantStyles = getVariantStyles(variant);
    const paddingValue = getPaddingValue(padding);

    return (
      <motion.div
        ref={ref}
        whileHover={hoverable || clickable ? { y: -2, boxShadow: theme.shadows.lg } : undefined}
        transition={{ duration: 0.2 }}
        style={{
          borderRadius: theme.borderRadius.base,
          display: 'flex',
          flexDirection: 'column',
          cursor: clickable ? 'pointer' : 'default',
          transition: `all ${theme.transitions.duration.base} ${theme.transitions.timing.ease}`,
          ...variantStyles,
          ...style,
        }}
        {...props}
      >
        {header && (
          <div
            style={{
              padding: paddingValue,
              borderBottom: `1px solid ${theme.colors.border.default}`,
            }}
          >
            {header}
          </div>
        )}

        <div style={{ padding: paddingValue, flex: 1 }}>{children}</div>

        {footer && (
          <div
            style={{
              padding: paddingValue,
              borderTop: `1px solid ${theme.colors.border.default}`,
            }}
          >
            {footer}
          </div>
        )}
      </motion.div>
    );
  }
);

Card.displayName = 'Card';

export default Card;
