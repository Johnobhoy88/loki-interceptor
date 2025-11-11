/**
 * LOKI Design System - Pattern Library
 *
 * Common UI patterns and responsive utilities
 */

import { theme } from './tokens';

// ============================================================================
// LAYOUT PATTERNS
// ============================================================================

export const layoutPatterns = {
  // Stack: Vertical spacing
  stack: (gap: keyof typeof theme.spacing = 4) => ({
    display: 'flex',
    flexDirection: 'column' as const,
    gap: theme.spacing[gap],
  }),

  // Inline: Horizontal spacing
  inline: (gap: keyof typeof theme.spacing = 3) => ({
    display: 'flex',
    flexDirection: 'row' as const,
    alignItems: 'center',
    gap: theme.spacing[gap],
  }),

  // Center: Center content
  center: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },

  // Grid: Responsive grid
  grid: (columns: number, gap: keyof typeof theme.spacing = 4) => ({
    display: 'grid',
    gridTemplateColumns: `repeat(${columns}, 1fr)`,
    gap: theme.spacing[gap],
  }),

  // Auto-fit grid
  gridAutoFit: (minWidth = '250px', gap: keyof typeof theme.spacing = 4) => ({
    display: 'grid',
    gridTemplateColumns: `repeat(auto-fit, minmax(${minWidth}, 1fr))`,
    gap: theme.spacing[gap],
  }),

  // Container: Centered container with max-width
  container: (maxWidth = '1200px') => ({
    maxWidth,
    marginLeft: 'auto',
    marginRight: 'auto',
    paddingLeft: theme.spacing[4],
    paddingRight: theme.spacing[4],
  }),

  // Sidebar layout
  sidebarLayout: (sidebarWidth = '260px') => ({
    display: 'flex',
    minHeight: '100vh',
    sidebar: {
      width: sidebarWidth,
      flexShrink: 0,
    },
    main: {
      flex: 1,
      minWidth: 0,
    },
  }),
};

// ============================================================================
// CARD PATTERNS
// ============================================================================

export const cardPatterns = {
  // Basic card
  base: {
    backgroundColor: theme.colors.background.panel,
    border: `1px solid ${theme.colors.border.default}`,
    borderRadius: theme.borderRadius.base,
    padding: theme.spacing[5],
    boxShadow: theme.shadows.sm,
  },

  // Hoverable card
  hoverable: {
    ...{
      backgroundColor: theme.colors.background.panel,
      border: `1px solid ${theme.colors.border.default}`,
      borderRadius: theme.borderRadius.base,
      padding: theme.spacing[5],
      boxShadow: theme.shadows.sm,
    },
    cursor: 'pointer',
    transition: `all ${theme.transitions.duration.base} ${theme.transitions.timing.ease}`,
    ':hover': {
      transform: 'translateY(-2px)',
      boxShadow: theme.shadows.lg,
    },
  },

  // Feature card
  feature: {
    backgroundColor: theme.colors.background.panel,
    border: `1px solid ${theme.colors.border.default}`,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing[6],
    textAlign: 'center' as const,
    display: 'flex',
    flexDirection: 'column' as const,
    gap: theme.spacing[4],
    alignItems: 'center',
  },

  // Status card (critical, warning, success)
  status: (variant: 'critical' | 'warning' | 'success') => {
    const colors = {
      critical: {
        border: theme.colors.status.criticalBorder,
        background: theme.colors.status.criticalBg,
      },
      warning: {
        border: theme.colors.status.highBorder,
        background: theme.colors.status.highBg,
      },
      success: {
        border: theme.colors.status.passBorder,
        background: theme.colors.status.passBg,
      },
    };

    return {
      backgroundColor: colors[variant].background,
      border: `1px solid ${colors[variant].border}`,
      borderRadius: theme.borderRadius.base,
      padding: theme.spacing[4],
    };
  },
};

// ============================================================================
// FORM PATTERNS
// ============================================================================

export const formPatterns = {
  // Form container
  form: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: theme.spacing[4],
  },

  // Field group
  fieldGroup: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: theme.spacing[1.5],
  },

  // Inline fields
  inlineFields: (gap: keyof typeof theme.spacing = 3) => ({
    display: 'flex',
    gap: theme.spacing[gap],
    alignItems: 'flex-end',
  }),

  // Form actions (buttons at bottom)
  formActions: {
    display: 'flex',
    justifyContent: 'flex-end',
    gap: theme.spacing[3],
    paddingTop: theme.spacing[4],
    borderTop: `1px solid ${theme.colors.border.default}`,
  },
};

// ============================================================================
// TABLE PATTERNS
// ============================================================================

export const tablePatterns = {
  // Table container
  container: {
    width: '100%',
    overflowX: 'auto' as const,
    border: `1px solid ${theme.colors.border.default}`,
    borderRadius: theme.borderRadius.base,
  },

  // Table
  table: {
    width: '100%',
    borderCollapse: 'collapse' as const,
  },

  // Table header
  th: {
    padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
    textAlign: 'left' as const,
    fontSize: theme.typography.fontSize.sm,
    fontWeight: theme.typography.fontWeight.semibold,
    color: theme.colors.text.secondary,
    textTransform: 'uppercase' as const,
    letterSpacing: theme.typography.letterSpacing.wide,
    backgroundColor: theme.colors.background.elevated,
    borderBottom: `2px solid ${theme.colors.border.default}`,
  },

  // Table cell
  td: {
    padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
    fontSize: theme.typography.fontSize.base,
    color: theme.colors.text.primary,
    borderBottom: `1px solid ${theme.colors.border.default}`,
  },

  // Table row hover
  trHover: {
    transition: `background-color ${theme.transitions.duration.fast} ${theme.transitions.timing.ease}`,
    ':hover': {
      backgroundColor: theme.colors.background.elevated,
    },
  },
};

// ============================================================================
// NAVIGATION PATTERNS
// ============================================================================

export const navigationPatterns = {
  // Nav list
  navList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: theme.spacing[1],
    listStyle: 'none',
    margin: 0,
    padding: 0,
  },

  // Nav item
  navItem: {
    padding: `${theme.spacing[2.5]} ${theme.spacing[3]}`,
    borderRadius: theme.borderRadius.base,
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.text.secondary,
    textDecoration: 'none',
    transition: `all ${theme.transitions.duration.base} ${theme.transitions.timing.ease}`,
    cursor: 'pointer',
    ':hover': {
      backgroundColor: theme.colors.background.elevated,
      color: theme.colors.text.primary,
    },
  },

  // Nav item active
  navItemActive: {
    backgroundColor: theme.colors.background.elevated,
    color: theme.colors.text.primary,
    borderLeft: `2px solid ${theme.colors.brand.primary}`,
  },

  // Breadcrumbs
  breadcrumbs: {
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing[2],
    fontSize: theme.typography.fontSize.sm,
    color: theme.colors.text.muted,
  },

  // Tabs container
  tabs: {
    display: 'flex',
    borderBottom: `1px solid ${theme.colors.border.default}`,
    gap: theme.spacing[1],
  },

  // Tab item
  tab: {
    padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
    fontSize: theme.typography.fontSize.base,
    fontWeight: theme.typography.fontWeight.medium,
    color: theme.colors.text.muted,
    backgroundColor: 'transparent',
    border: 'none',
    borderBottom: '2px solid transparent',
    cursor: 'pointer',
    transition: `all ${theme.transitions.duration.base} ${theme.transitions.timing.ease}`,
    ':hover': {
      color: theme.colors.text.primary,
      borderBottomColor: theme.colors.border.accent,
    },
  },

  // Tab active
  tabActive: {
    color: theme.colors.brand.primary,
    borderBottomColor: theme.colors.brand.primary,
  },
};

// ============================================================================
// RESPONSIVE UTILITIES
// ============================================================================

export const responsive = {
  // Media queries
  breakpoints: theme.breakpoints,

  // Helper to create media query
  mediaQuery: (breakpoint: keyof typeof theme.breakpoints) =>
    `@media (min-width: ${theme.breakpoints[breakpoint]})`,

  // Show only on mobile
  showOnMobile: {
    display: 'block',
    [`@media (min-width: ${theme.breakpoints.md})`]: {
      display: 'none',
    },
  },

  // Hide on mobile
  hideOnMobile: {
    display: 'none',
    [`@media (min-width: ${theme.breakpoints.md})`]: {
      display: 'block',
    },
  },

  // Responsive grid columns
  responsiveGrid: {
    display: 'grid',
    gap: theme.spacing[4],
    gridTemplateColumns: '1fr',
    [`@media (min-width: ${theme.breakpoints.sm})`]: {
      gridTemplateColumns: 'repeat(2, 1fr)',
    },
    [`@media (min-width: ${theme.breakpoints.lg})`]: {
      gridTemplateColumns: 'repeat(3, 1fr)',
    },
  },

  // Responsive padding
  responsivePadding: {
    padding: theme.spacing[4],
    [`@media (min-width: ${theme.breakpoints.md})`]: {
      padding: theme.spacing[6],
    },
    [`@media (min-width: ${theme.breakpoints.lg})`]: {
      padding: theme.spacing[8],
    },
  },
};

// ============================================================================
// UTILITY PATTERNS
// ============================================================================

export const utilities = {
  // Truncate text
  truncate: {
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap' as const,
  },

  // Line clamp (multiple lines)
  lineClamp: (lines: number) => ({
    display: '-webkit-box',
    WebkitLineClamp: lines,
    WebkitBoxOrient: 'vertical' as const,
    overflow: 'hidden',
  }),

  // Screen reader only
  srOnly: {
    position: 'absolute' as const,
    width: '1px',
    height: '1px',
    padding: 0,
    margin: '-1px',
    overflow: 'hidden',
    clip: 'rect(0, 0, 0, 0)',
    whiteSpace: 'nowrap' as const,
    borderWidth: 0,
  },

  // Focus visible (keyboard navigation)
  focusVisible: {
    outline: 'none',
    ':focus-visible': {
      boxShadow: theme.shadows.focus,
      borderColor: theme.colors.border.focus,
    },
  },

  // Disabled state
  disabled: {
    opacity: 0.5,
    cursor: 'not-allowed',
    pointerEvents: 'none' as const,
  },
};

// ============================================================================
// EXPORT ALL
// ============================================================================

export const patterns = {
  layout: layoutPatterns,
  card: cardPatterns,
  form: formPatterns,
  table: tablePatterns,
  navigation: navigationPatterns,
  responsive,
  utilities,
};

export default patterns;
