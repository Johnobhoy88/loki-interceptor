/**
 * LOKI Design System - Design Tokens
 *
 * Foundation tokens for colors, typography, spacing, shadows, and more.
 * These tokens ensure consistency across the entire application.
 */

// ============================================================================
// COLOR SYSTEM
// ============================================================================

export const colors = {
  // Brand Colors
  brand: {
    primary: '#4a7cff',
    primaryHover: '#5a8cff',
    primaryActive: '#3a6cef',
    secondary: '#10b981',
    secondaryHover: '#0ea872',
    accent: '#a78bfa',
    accentHover: '#9676eb',
  },

  // Background Colors
  background: {
    primary: '#0a0e1a',
    panel: '#12161f',
    elevated: '#1a1f2e',
    input: '#0f1319',
    overlay: 'rgba(10, 14, 26, 0.85)',
    modal: '#1a1f2e',
  },

  // Text Colors
  text: {
    primary: '#ffffff',
    secondary: '#a0a8b8',
    muted: '#6c7584',
    disabled: '#4a5160',
    inverse: '#0a0e1a',
  },

  // Semantic Colors
  semantic: {
    success: '#28a745',
    successLight: '#34d399',
    successDark: '#1e7a35',
    warning: '#ff9500',
    warningLight: '#fbbf24',
    warningDark: '#d97706',
    error: '#dc3545',
    errorLight: '#ef4444',
    errorDark: '#b91c1c',
    info: '#3b82f6',
    infoLight: '#60a5fa',
    infoDark: '#1e40af',
  },

  // Status Colors
  status: {
    critical: '#dc3545',
    criticalBg: 'rgba(220, 53, 69, 0.1)',
    criticalBorder: 'rgba(220, 53, 69, 0.3)',
    high: '#ff9500',
    highBg: 'rgba(255, 149, 0, 0.1)',
    highBorder: 'rgba(255, 149, 0, 0.3)',
    medium: '#fbbf24',
    mediumBg: 'rgba(251, 191, 36, 0.1)',
    mediumBorder: 'rgba(251, 191, 36, 0.3)',
    low: '#10b981',
    lowBg: 'rgba(16, 185, 129, 0.1)',
    lowBorder: 'rgba(16, 185, 129, 0.3)',
    pass: '#28a745',
    passBg: 'rgba(40, 167, 69, 0.1)',
    passBorder: 'rgba(40, 167, 69, 0.3)',
  },

  // Border Colors
  border: {
    default: '#2a2f3d',
    accent: '#3a4556',
    hover: '#4a5566',
    focus: '#4a7cff',
    error: '#dc3545',
    success: '#28a745',
  },

  // Compliance-specific Colors
  compliance: {
    gdpr: '#3b82f6',
    gdprBg: 'rgba(59, 130, 246, 0.1)',
    fca: '#a78bfa',
    fcaBg: 'rgba(167, 139, 250, 0.1)',
    tax: '#10b981',
    taxBg: 'rgba(16, 185, 129, 0.1)',
    employment: '#f59e0b',
    employmentBg: 'rgba(245, 158, 11, 0.1)',
  },
} as const;

// ============================================================================
// TYPOGRAPHY
// ============================================================================

export const typography = {
  // Font Families
  fontFamily: {
    base: "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif",
    heading: "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif",
    mono: "'JetBrains Mono', 'SFMono-Regular', Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
    code: "'JetBrains Mono', 'SFMono-Regular', Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
  },

  // Font Sizes
  fontSize: {
    xs: '0.6875rem',    // 11px
    sm: '0.75rem',      // 12px
    base: '0.875rem',   // 14px
    md: '0.9375rem',    // 15px
    lg: '1rem',         // 16px
    xl: '1.125rem',     // 18px
    '2xl': '1.25rem',   // 20px
    '3xl': '1.5rem',    // 24px
    '4xl': '1.875rem',  // 30px
    '5xl': '2.25rem',   // 36px
  },

  // Font Weights
  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
  },

  // Line Heights
  lineHeight: {
    none: 1,
    tight: 1.25,
    snug: 1.375,
    normal: 1.5,
    relaxed: 1.625,
    loose: 2,
  },

  // Letter Spacing
  letterSpacing: {
    tighter: '-0.05em',
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
    wider: '0.05em',
    widest: '0.1em',
  },
} as const;

// ============================================================================
// SPACING
// ============================================================================

export const spacing = {
  0: '0',
  px: '1px',
  0.5: '0.125rem',   // 2px
  1: '0.25rem',      // 4px
  1.5: '0.375rem',   // 6px
  2: '0.5rem',       // 8px
  2.5: '0.625rem',   // 10px
  3: '0.75rem',      // 12px
  3.5: '0.875rem',   // 14px
  4: '1rem',         // 16px
  5: '1.25rem',      // 20px
  6: '1.5rem',       // 24px
  7: '1.75rem',      // 28px
  8: '2rem',         // 32px
  9: '2.25rem',      // 36px
  10: '2.5rem',      // 40px
  12: '3rem',        // 48px
  14: '3.5rem',      // 56px
  16: '4rem',        // 64px
  20: '5rem',        // 80px
  24: '6rem',        // 96px
  28: '7rem',        // 112px
  32: '8rem',        // 128px
} as const;

// ============================================================================
// SHADOWS
// ============================================================================

export const shadows = {
  none: 'none',
  sm: '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
  base: '0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px 0 rgba(0, 0, 0, 0.2)',
  md: '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)',
  lg: '0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2)',
  xl: '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)',
  '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.4)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.3)',
  outline: '0 0 0 3px rgba(74, 124, 255, 0.15)',
  focus: '0 0 0 2px rgba(74, 124, 255, 0.15)',
  glow: '0 0 20px rgba(74, 124, 255, 0.3)',
} as const;

// ============================================================================
// BORDER RADIUS
// ============================================================================

export const borderRadius = {
  none: '0',
  sm: '0.125rem',    // 2px
  base: '0.25rem',   // 4px
  md: '0.375rem',    // 6px
  lg: '0.5rem',      // 8px
  xl: '0.75rem',     // 12px
  '2xl': '1rem',     // 16px
  '3xl': '1.5rem',   // 24px
  full: '9999px',
} as const;

// ============================================================================
// Z-INDEX
// ============================================================================

export const zIndex = {
  base: 0,
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070,
  notification: 9999,
} as const;

// ============================================================================
// BREAKPOINTS
// ============================================================================

export const breakpoints = {
  xs: '375px',
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

// ============================================================================
// TRANSITIONS
// ============================================================================

export const transitions = {
  duration: {
    fast: '150ms',
    base: '200ms',
    slow: '300ms',
    slower: '500ms',
  },
  timing: {
    ease: 'ease',
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
    linear: 'linear',
    spring: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
  },
} as const;

// ============================================================================
// ANIMATION VARIANTS (for Framer Motion)
// ============================================================================

export const animations = {
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.2 },
  },
  slideIn: {
    initial: { x: '100%', opacity: 0 },
    animate: { x: 0, opacity: 1 },
    exit: { x: '100%', opacity: 0 },
    transition: { duration: 0.2 },
  },
  slideUp: {
    initial: { y: 20, opacity: 0 },
    animate: { y: 0, opacity: 1 },
    exit: { y: 20, opacity: 0 },
    transition: { duration: 0.2 },
  },
  scaleIn: {
    initial: { scale: 0.95, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    exit: { scale: 0.95, opacity: 0 },
    transition: { duration: 0.2 },
  },
  bounce: {
    animate: {
      y: [0, -10, 0],
      transition: {
        duration: 0.6,
        repeat: Infinity,
        repeatType: 'loop' as const,
      },
    },
  },
  pulse: {
    animate: {
      scale: [1, 1.05, 1],
      transition: {
        duration: 2,
        repeat: Infinity,
        repeatType: 'loop' as const,
      },
    },
  },
  shake: {
    animate: {
      x: [0, -10, 10, -10, 10, 0],
      transition: {
        duration: 0.5,
      },
    },
  },
} as const;

// ============================================================================
// COMPONENT SIZES
// ============================================================================

export const componentSizes = {
  button: {
    xs: {
      height: '1.5rem',
      padding: '0 0.5rem',
      fontSize: typography.fontSize.xs,
    },
    sm: {
      height: '2rem',
      padding: '0 0.75rem',
      fontSize: typography.fontSize.sm,
    },
    md: {
      height: '2.5rem',
      padding: '0 1rem',
      fontSize: typography.fontSize.base,
    },
    lg: {
      height: '3rem',
      padding: '0 1.5rem',
      fontSize: typography.fontSize.lg,
    },
    xl: {
      height: '3.5rem',
      padding: '0 2rem',
      fontSize: typography.fontSize.xl,
    },
  },
  input: {
    sm: {
      height: '2rem',
      padding: '0 0.75rem',
      fontSize: typography.fontSize.sm,
    },
    md: {
      height: '2.5rem',
      padding: '0 0.875rem',
      fontSize: typography.fontSize.base,
    },
    lg: {
      height: '3rem',
      padding: '0 1rem',
      fontSize: typography.fontSize.lg,
    },
  },
} as const;

// ============================================================================
// EXPORT DEFAULT THEME
// ============================================================================

export const theme = {
  colors,
  typography,
  spacing,
  shadows,
  borderRadius,
  zIndex,
  breakpoints,
  transitions,
  animations,
  componentSizes,
} as const;

export type Theme = typeof theme;
export default theme;
