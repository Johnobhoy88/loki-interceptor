import React from 'react';
import { theme } from '../../design-system/tokens';

export type InputSize = 'sm' | 'md' | 'lg';
export type InputStatus = 'default' | 'error' | 'success' | 'warning';

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  /** Size of the input */
  size?: InputSize;
  /** Status/validation state */
  status?: InputStatus;
  /** Label for the input */
  label?: string;
  /** Helper text displayed below input */
  helperText?: string;
  /** Error message (sets status to error) */
  error?: string;
  /** Icon to display before input */
  leftIcon?: React.ReactNode;
  /** Icon to display after input */
  rightIcon?: React.ReactNode;
  /** Whether input should take full width */
  fullWidth?: boolean;
}

const getSizeStyles = (size: InputSize) => {
  const sizes = {
    sm: {
      height: theme.componentSizes.input.sm.height,
      padding: theme.componentSizes.input.sm.padding,
      fontSize: theme.componentSizes.input.sm.fontSize,
    },
    md: {
      height: theme.componentSizes.input.md.height,
      padding: theme.componentSizes.input.md.padding,
      fontSize: theme.componentSizes.input.md.fontSize,
    },
    lg: {
      height: theme.componentSizes.input.lg.height,
      padding: theme.componentSizes.input.lg.padding,
      fontSize: theme.componentSizes.input.lg.fontSize,
    },
  };

  return sizes[size];
};

const getStatusStyles = (status: InputStatus, disabled: boolean) => {
  if (disabled) {
    return {
      backgroundColor: theme.colors.background.elevated,
      borderColor: theme.colors.border.default,
      color: theme.colors.text.disabled,
      cursor: 'not-allowed',
      opacity: 0.6,
    };
  }

  const statusMap = {
    default: {
      borderColor: theme.colors.border.default,
      focusBorderColor: theme.colors.border.focus,
    },
    error: {
      borderColor: theme.colors.border.error,
      focusBorderColor: theme.colors.border.error,
    },
    success: {
      borderColor: theme.colors.border.success,
      focusBorderColor: theme.colors.border.success,
    },
    warning: {
      borderColor: theme.colors.semantic.warning,
      focusBorderColor: theme.colors.semantic.warning,
    },
  };

  return statusMap[status];
};

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (
    {
      size = 'md',
      status = 'default',
      label,
      helperText,
      error,
      leftIcon,
      rightIcon,
      fullWidth = false,
      disabled = false,
      className,
      style,
      ...props
    },
    ref
  ) => {
    const actualStatus = error ? 'error' : status;
    const sizeStyles = getSizeStyles(size);
    const statusStyles = getStatusStyles(actualStatus, disabled || false);
    const displayHelperText = error || helperText;

    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: theme.spacing[1.5],
          width: fullWidth ? '100%' : 'auto',
        }}
      >
        {label && (
          <label
            style={{
              fontSize: theme.typography.fontSize.sm,
              fontWeight: theme.typography.fontWeight.medium,
              color: theme.colors.text.secondary,
              textTransform: 'uppercase',
              letterSpacing: theme.typography.letterSpacing.wide,
            }}
          >
            {label}
          </label>
        )}

        <div style={{ position: 'relative', width: fullWidth ? '100%' : 'auto' }}>
          {leftIcon && (
            <div
              style={{
                position: 'absolute',
                left: theme.spacing[3],
                top: '50%',
                transform: 'translateY(-50%)',
                display: 'flex',
                alignItems: 'center',
                color: theme.colors.text.muted,
                pointerEvents: 'none',
              }}
            >
              {leftIcon}
            </div>
          )}

          <input
            ref={ref}
            disabled={disabled}
            className={className}
            style={{
              backgroundColor: theme.colors.background.input,
              color: theme.colors.text.primary,
              border: `1px solid ${statusStyles.borderColor}`,
              borderRadius: theme.borderRadius.base,
              outline: 'none',
              transition: `all ${theme.transitions.duration.base} ${theme.transitions.timing.ease}`,
              fontFamily: theme.typography.fontFamily.base,
              width: fullWidth ? '100%' : 'auto',
              paddingLeft: leftIcon ? `calc(${sizeStyles.padding} + 2rem)` : sizeStyles.padding,
              paddingRight: rightIcon ? `calc(${sizeStyles.padding} + 2rem)` : sizeStyles.padding,
              ...sizeStyles,
              ...statusStyles,
              ...style,
            }}
            onFocus={(e) => {
              e.currentTarget.style.borderColor = statusStyles.focusBorderColor!;
              e.currentTarget.style.boxShadow = theme.shadows.focus;
              props.onFocus?.(e);
            }}
            onBlur={(e) => {
              e.currentTarget.style.borderColor = statusStyles.borderColor!;
              e.currentTarget.style.boxShadow = 'none';
              props.onBlur?.(e);
            }}
            {...props}
          />

          {rightIcon && (
            <div
              style={{
                position: 'absolute',
                right: theme.spacing[3],
                top: '50%',
                transform: 'translateY(-50%)',
                display: 'flex',
                alignItems: 'center',
                color: theme.colors.text.muted,
                pointerEvents: 'none',
              }}
            >
              {rightIcon}
            </div>
          )}
        </div>

        {displayHelperText && (
          <p
            style={{
              margin: 0,
              fontSize: theme.typography.fontSize.sm,
              color: error ? theme.colors.semantic.error : theme.colors.text.muted,
              lineHeight: theme.typography.lineHeight.snug,
            }}
          >
            {error || helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export default Input;
