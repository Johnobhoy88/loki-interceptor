import React from 'react';
import { motion } from 'framer-motion';
import { theme } from '../../design-system/tokens';
import Button, { ButtonProps } from './Button';

export interface EmptyStateProps {
  /** Icon or illustration */
  icon?: React.ReactNode;
  /** Title text */
  title: string;
  /** Description text */
  description?: string;
  /** Primary action button */
  action?: {
    label: string;
    onClick: () => void;
  } & Partial<ButtonProps>;
  /** Secondary action button */
  secondaryAction?: {
    label: string;
    onClick: () => void;
  } & Partial<ButtonProps>;
  /** Custom children */
  children?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  secondaryAction,
  children,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        textAlign: 'center',
        padding: `${theme.spacing[12]} ${theme.spacing[6]}`,
        minHeight: '300px',
      }}
    >
      {icon && (
        <div
          style={{
            fontSize: '4rem',
            marginBottom: theme.spacing[4],
            color: theme.colors.text.muted,
            opacity: 0.5,
          }}
        >
          {icon}
        </div>
      )}

      <h3
        style={{
          margin: 0,
          marginBottom: theme.spacing[2],
          fontSize: theme.typography.fontSize['2xl'],
          fontWeight: theme.typography.fontWeight.semibold,
          color: theme.colors.text.primary,
        }}
      >
        {title}
      </h3>

      {description && (
        <p
          style={{
            margin: 0,
            marginBottom: theme.spacing[6],
            fontSize: theme.typography.fontSize.base,
            color: theme.colors.text.muted,
            maxWidth: '400px',
            lineHeight: theme.typography.lineHeight.relaxed,
          }}
        >
          {description}
        </p>
      )}

      {(action || secondaryAction) && (
        <div style={{ display: 'flex', gap: theme.spacing[3], flexWrap: 'wrap' }}>
          {action && (
            <Button
              variant={action.variant || 'primary'}
              size={action.size || 'md'}
              onClick={action.onClick}
              {...action}
            >
              {action.label}
            </Button>
          )}
          {secondaryAction && (
            <Button
              variant={secondaryAction.variant || 'outline'}
              size={secondaryAction.size || 'md'}
              onClick={secondaryAction.onClick}
              {...secondaryAction}
            >
              {secondaryAction.label}
            </Button>
          )}
        </div>
      )}

      {children && <div style={{ marginTop: theme.spacing[6] }}>{children}</div>}
    </motion.div>
  );
};

export default EmptyState;
