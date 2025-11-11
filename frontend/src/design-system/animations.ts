/**
 * LOKI Design System - Animation Library
 *
 * Reusable animation variants and utilities for Framer Motion
 */

import { Variants, Transition } from 'framer-motion';

// ============================================================================
// TIMING FUNCTIONS
// ============================================================================

export const easings = {
  ease: [0.4, 0, 0.2, 1],
  easeIn: [0.4, 0, 1, 1],
  easeOut: [0, 0, 0.2, 1],
  easeInOut: [0.4, 0, 0.2, 1],
  spring: { type: 'spring' as const, stiffness: 300, damping: 30 },
  springGentle: { type: 'spring' as const, stiffness: 100, damping: 20 },
  springBouncy: { type: 'spring' as const, stiffness: 500, damping: 25 },
} as const;

// ============================================================================
// ENTRANCE ANIMATIONS
// ============================================================================

export const fadeIn: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
};

export const fadeInUp: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 20 },
};

export const fadeInDown: Variants = {
  initial: { opacity: 0, y: -20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
};

export const fadeInLeft: Variants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 },
};

export const fadeInRight: Variants = {
  initial: { opacity: 0, x: 20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
};

export const scaleIn: Variants = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 },
};

export const scaleUp: Variants = {
  initial: { opacity: 0, scale: 0.8 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.8 },
};

export const slideInUp: Variants = {
  initial: { y: '100%' },
  animate: { y: 0 },
  exit: { y: '100%' },
};

export const slideInDown: Variants = {
  initial: { y: '-100%' },
  animate: { y: 0 },
  exit: { y: '-100%' },
};

export const slideInLeft: Variants = {
  initial: { x: '-100%' },
  animate: { x: 0 },
  exit: { x: '-100%' },
};

export const slideInRight: Variants = {
  initial: { x: '100%' },
  animate: { x: 0 },
  exit: { x: '100%' },
};

// ============================================================================
// CONTINUOUS ANIMATIONS
// ============================================================================

export const pulse: Variants = {
  animate: {
    scale: [1, 1.05, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      repeatType: 'loop',
    },
  },
};

export const bounce: Variants = {
  animate: {
    y: [0, -10, 0],
    transition: {
      duration: 0.6,
      repeat: Infinity,
      repeatType: 'loop',
    },
  },
};

export const spin: Variants = {
  animate: {
    rotate: 360,
    transition: {
      duration: 1,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

export const wiggle: Variants = {
  animate: {
    rotate: [-3, 3, -3, 3, 0],
    transition: {
      duration: 0.5,
      repeat: Infinity,
      repeatDelay: 2,
    },
  },
};

export const float: Variants = {
  animate: {
    y: [-5, 5, -5],
    transition: {
      duration: 3,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

// ============================================================================
// ATTENTION SEEKERS
// ============================================================================

export const shake: Variants = {
  animate: {
    x: [0, -10, 10, -10, 10, 0],
    transition: {
      duration: 0.5,
    },
  },
};

export const heartbeat: Variants = {
  animate: {
    scale: [1, 1.1, 1, 1.1, 1],
    transition: {
      duration: 1,
      repeat: Infinity,
      repeatDelay: 1,
    },
  },
};

export const flash: Variants = {
  animate: {
    opacity: [1, 0, 1, 0, 1],
    transition: {
      duration: 0.75,
    },
  },
};

export const rubberBand: Variants = {
  animate: {
    scaleX: [1, 1.25, 0.75, 1.15, 0.95, 1],
    scaleY: [1, 0.75, 1.25, 0.85, 1.05, 1],
    transition: {
      duration: 0.8,
    },
  },
};

// ============================================================================
// LIST ANIMATIONS
// ============================================================================

export const staggerContainer: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

export const staggerFastContainer: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.05,
    },
  },
};

export const staggerSlowContainer: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.2,
    },
  },
};

export const listItem: Variants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -20 },
};

// ============================================================================
// MODAL & OVERLAY ANIMATIONS
// ============================================================================

export const modalBackdrop: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
};

export const modalContent: Variants = {
  initial: { opacity: 0, scale: 0.95, y: 20 },
  animate: { opacity: 1, scale: 1, y: 0 },
  exit: { opacity: 0, scale: 0.95, y: 20 },
};

export const drawerLeft: Variants = {
  initial: { x: '-100%' },
  animate: { x: 0 },
  exit: { x: '-100%' },
};

export const drawerRight: Variants = {
  initial: { x: '100%' },
  animate: { x: 0 },
  exit: { x: '100%' },
};

export const drawerTop: Variants = {
  initial: { y: '-100%' },
  animate: { y: 0 },
  exit: { y: '-100%' },
};

export const drawerBottom: Variants = {
  initial: { y: '100%' },
  animate: { y: 0 },
  exit: { y: '100%' },
};

// ============================================================================
// NOTIFICATION ANIMATIONS
// ============================================================================

export const toastEnter: Variants = {
  initial: { opacity: 0, x: '100%', scale: 0.9 },
  animate: { opacity: 1, x: 0, scale: 1 },
  exit: { opacity: 0, x: '100%', scale: 0.9 },
};

export const alertPulse: Variants = {
  animate: {
    scale: [1, 1.02, 1],
    boxShadow: [
      '0 0 0 0 rgba(220, 53, 69, 0)',
      '0 0 0 10px rgba(220, 53, 69, 0.2)',
      '0 0 0 0 rgba(220, 53, 69, 0)',
    ],
    transition: {
      duration: 1.5,
      repeat: Infinity,
    },
  },
};

// ============================================================================
// MICRO-INTERACTIONS
// ============================================================================

export const buttonTap: Transition = {
  scale: 0.98,
  transition: { duration: 0.1 },
};

export const buttonHover: Transition = {
  scale: 1.02,
  transition: { duration: 0.2 },
};

export const cardHover: Transition = {
  y: -4,
  boxShadow: '0 10px 30px rgba(0, 0, 0, 0.3)',
  transition: { duration: 0.2 },
};

// ============================================================================
// PAGE TRANSITIONS
// ============================================================================

export const pageTransition: Variants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
};

export const pageFade: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
};

// ============================================================================
// SKELETON LOADING
// ============================================================================

export const skeletonPulse: Variants = {
  animate: {
    opacity: [0.5, 0.8, 0.5],
    transition: {
      duration: 1.5,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

export const shimmer: Variants = {
  animate: {
    backgroundPosition: ['200% 0', '-200% 0'],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'linear',
    },
  },
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Create a custom fade animation with configurable direction and distance
 */
export const createFade = (direction: 'up' | 'down' | 'left' | 'right', distance = 20): Variants => {
  const axis = direction === 'up' || direction === 'down' ? 'y' : 'x';
  const sign = direction === 'up' || direction === 'left' ? -1 : 1;
  const value = distance * sign;

  return {
    initial: { opacity: 0, [axis]: value },
    animate: { opacity: 1, [axis]: 0 },
    exit: { opacity: 0, [axis]: value },
  };
};

/**
 * Create a custom scale animation
 */
export const createScale = (from = 0.95, to = 1): Variants => ({
  initial: { opacity: 0, scale: from },
  animate: { opacity: 1, scale: to },
  exit: { opacity: 0, scale: from },
});

/**
 * Create a stagger container with custom delay
 */
export const createStagger = (staggerDelay = 0.1): Variants => ({
  initial: {},
  animate: {
    transition: {
      staggerChildren: staggerDelay,
    },
  },
});

// ============================================================================
// PRESET TRANSITIONS
// ============================================================================

export const transitions = {
  fast: { duration: 0.15 },
  base: { duration: 0.2 },
  slow: { duration: 0.3 },
  slower: { duration: 0.5 },
  spring: easings.spring,
  springGentle: easings.springGentle,
  springBouncy: easings.springBouncy,
} as const;

// ============================================================================
// EXPORT ALL
// ============================================================================

export const animations = {
  // Entrance
  fadeIn,
  fadeInUp,
  fadeInDown,
  fadeInLeft,
  fadeInRight,
  scaleIn,
  scaleUp,
  slideInUp,
  slideInDown,
  slideInLeft,
  slideInRight,
  // Continuous
  pulse,
  bounce,
  spin,
  wiggle,
  float,
  // Attention
  shake,
  heartbeat,
  flash,
  rubberBand,
  // Lists
  staggerContainer,
  staggerFastContainer,
  staggerSlowContainer,
  listItem,
  // Modals
  modalBackdrop,
  modalContent,
  drawerLeft,
  drawerRight,
  drawerTop,
  drawerBottom,
  // Notifications
  toastEnter,
  alertPulse,
  // Pages
  pageTransition,
  pageFade,
  // Loading
  skeletonPulse,
  shimmer,
  // Utils
  createFade,
  createScale,
  createStagger,
} as const;

export default animations;
