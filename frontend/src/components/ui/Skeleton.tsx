import React from 'react';
import { motion } from 'framer-motion';
import { theme } from '../../design-system/tokens';

export type SkeletonVariant = 'text' | 'circular' | 'rectangular';

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  /** Shape variant */
  variant?: SkeletonVariant;
  /** Width of the skeleton */
  width?: string | number;
  /** Height of the skeleton */
  height?: string | number;
  /** Whether to animate */
  animate?: boolean;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'text',
  width,
  height,
  animate = true,
  style,
  ...props
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'text':
        return {
          height: height || '1em',
          width: width || '100%',
          borderRadius: theme.borderRadius.base,
        };
      case 'circular':
        return {
          height: height || '2.5rem',
          width: width || '2.5rem',
          borderRadius: theme.borderRadius.full,
        };
      case 'rectangular':
        return {
          height: height || '100%',
          width: width || '100%',
          borderRadius: theme.borderRadius.base,
        };
    }
  };

  const variantStyles = getVariantStyles();

  return (
    <motion.div
      animate={
        animate
          ? {
              opacity: [0.5, 0.8, 0.5],
            }
          : undefined
      }
      transition={
        animate
          ? {
              duration: 1.5,
              repeat: Infinity,
              ease: 'easeInOut',
            }
          : undefined
      }
      style={{
        backgroundColor: theme.colors.background.elevated,
        ...variantStyles,
        ...style,
      }}
      {...props}
    />
  );
};

export const SkeletonText: React.FC<{ lines?: number; lastLineWidth?: string }> = ({
  lines = 3,
  lastLineWidth = '60%',
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing[2] }}>
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          variant="text"
          width={index === lines - 1 ? lastLineWidth : '100%'}
        />
      ))}
    </div>
  );
};

export const SkeletonCard: React.FC = () => {
  return (
    <div
      style={{
        backgroundColor: theme.colors.background.panel,
        border: `1px solid ${theme.colors.border.default}`,
        borderRadius: theme.borderRadius.base,
        padding: theme.spacing[5],
        display: 'flex',
        flexDirection: 'column',
        gap: theme.spacing[4],
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing[3] }}>
        <Skeleton variant="circular" width="3rem" height="3rem" />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: theme.spacing[2] }}>
          <Skeleton variant="text" width="40%" />
          <Skeleton variant="text" width="60%" />
        </div>
      </div>
      <SkeletonText lines={3} />
    </div>
  );
};

export default Skeleton;
