import React from 'react';
import { motion } from 'framer-motion';
import { theme } from '../../design-system/tokens';
import Button from './Button';

export interface ErrorStateProps {
  /** Error title */
  title?: string;
  /** Error message */
  message: string;
  /** Error details (optional, collapsed by default) */
  details?: string;
  /** Retry callback */
  onRetry?: () => void;
  /** Reset/Go back callback */
  onReset?: () => void;
  /** Custom error code */
  errorCode?: string;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = 'Something went wrong',
  message,
  details,
  onRetry,
  onReset,
  errorCode,
}) => {
  const [showDetails, setShowDetails] = React.useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
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
      {/* Error Icon */}
      <motion.div
        animate={{
          x: [0, -10, 10, -10, 10, 0],
        }}
        transition={{
          duration: 0.5,
          ease: 'easeInOut',
        }}
        style={{
          width: '4rem',
          height: '4rem',
          borderRadius: theme.borderRadius.full,
          backgroundColor: theme.colors.status.criticalBg,
          border: `2px solid ${theme.colors.semantic.error}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '2rem',
          marginBottom: theme.spacing[4],
        }}
      >
        ✕
      </motion.div>

      {/* Error Code */}
      {errorCode && (
        <div
          style={{
            fontSize: theme.typography.fontSize.xs,
            color: theme.colors.text.muted,
            textTransform: 'uppercase',
            letterSpacing: theme.typography.letterSpacing.wider,
            marginBottom: theme.spacing[2],
          }}
        >
          Error: {errorCode}
        </div>
      )}

      {/* Title */}
      <h3
        style={{
          margin: 0,
          marginBottom: theme.spacing[2],
          fontSize: theme.typography.fontSize['2xl'],
          fontWeight: theme.typography.fontWeight.semibold,
          color: theme.colors.semantic.error,
        }}
      >
        {title}
      </h3>

      {/* Message */}
      <p
        style={{
          margin: 0,
          marginBottom: theme.spacing[6],
          fontSize: theme.typography.fontSize.base,
          color: theme.colors.text.secondary,
          maxWidth: '500px',
          lineHeight: theme.typography.lineHeight.relaxed,
        }}
      >
        {message}
      </p>

      {/* Actions */}
      <div style={{ display: 'flex', gap: theme.spacing[3], flexWrap: 'wrap', marginBottom: theme.spacing[4] }}>
        {onRetry && (
          <Button variant="primary" onClick={onRetry}>
            Try Again
          </Button>
        )}
        {onReset && (
          <Button variant="outline" onClick={onReset}>
            Go Back
          </Button>
        )}
      </div>

      {/* Details (collapsible) */}
      {details && (
        <div style={{ width: '100%', maxWidth: '600px' }}>
          <button
            onClick={() => setShowDetails(!showDetails)}
            style={{
              background: 'transparent',
              border: 'none',
              color: theme.colors.text.muted,
              cursor: 'pointer',
              fontSize: theme.typography.fontSize.sm,
              textDecoration: 'underline',
              padding: theme.spacing[2],
            }}
          >
            {showDetails ? 'Hide' : 'Show'} technical details
          </button>

          {showDetails && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              style={{
                marginTop: theme.spacing[3],
                padding: theme.spacing[4],
                backgroundColor: theme.colors.background.input,
                border: `1px solid ${theme.colors.border.error}`,
                borderRadius: theme.borderRadius.base,
                textAlign: 'left',
                maxHeight: '200px',
                overflowY: 'auto',
              }}
            >
              <pre
                style={{
                  margin: 0,
                  fontFamily: theme.typography.fontFamily.code,
                  fontSize: theme.typography.fontSize.sm,
                  color: theme.colors.text.secondary,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {details}
              </pre>
            </motion.div>
          )}
        </div>
      )}
    </motion.div>
  );
};

export default ErrorState;
