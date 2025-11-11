# LOKI Design System

A comprehensive, professional design system for consistent UI/UX across the LOKI compliance platform.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [Design Tokens](#design-tokens)
- [Components](#components)
- [Patterns](#patterns)
- [Icons](#icons)
- [Animations](#animations)
- [Accessibility](#accessibility)
- [Best Practices](#best-practices)

---

## Overview

The LOKI Design System provides a complete set of design tokens, components, patterns, and guidelines to ensure consistency, accessibility, and professional quality across the entire application.

### Key Features

- **Design Tokens**: Centralized color, typography, spacing, and shadow values
- **Component Library**: 10+ production-ready React components
- **Animation Library**: Framer Motion-powered animations and micro-interactions
- **Icon System**: Custom compliance-focused icons
- **Pattern Library**: Common UI patterns and layouts
- **Storybook**: Interactive component documentation
- **Accessibility**: WCAG 2.1 AA compliant
- **Dark Mode**: Native dark mode support
- **TypeScript**: Fully typed components and tokens

### Technology Stack

- **React** - Component library framework
- **TypeScript** - Type safety and intellisense
- **Framer Motion** - Animation library
- **CSS Custom Properties** - Design token implementation
- **Storybook** - Component documentation and development

---

## Getting Started

### Installation

The design system is already integrated into the LOKI frontend. To use components:

```tsx
import { Button, Input, Card, Badge } from '@/components/ui';
import { theme } from '@/design-system/tokens';
import { GDPRIcon, FCAIcon } from '@/assets/icons';
```

### Basic Usage

```tsx
import React from 'react';
import { Button, Card, Badge } from '@/components/ui';

function MyComponent() {
  return (
    <Card>
      <h2>Welcome to LOKI</h2>
      <Badge variant="success">Active</Badge>
      <Button variant="primary" onClick={() => alert('Clicked!')}>
        Get Started
      </Button>
    </Card>
  );
}
```

### Using Design Tokens

```tsx
import { theme } from '@/design-system/tokens';

const MyStyledComponent = () => (
  <div
    style={{
      backgroundColor: theme.colors.background.panel,
      padding: theme.spacing[4],
      borderRadius: theme.borderRadius.base,
      boxShadow: theme.shadows.md,
    }}
  >
    Content
  </div>
);
```

---

## Design Tokens

Design tokens are the foundation of the design system. They ensure consistency and make it easy to maintain and update the visual design.

### Colors

#### Brand Colors
- `brand.primary` - Primary action color (#4a7cff)
- `brand.secondary` - Secondary action color (#10b981)
- `brand.accent` - Accent color (#a78bfa)

#### Background Colors
- `background.primary` - Main background (#0a0e1a)
- `background.panel` - Panel background (#12161f)
- `background.elevated` - Elevated surfaces (#1a1f2e)
- `background.input` - Input fields (#0f1319)

#### Text Colors
- `text.primary` - Primary text (#ffffff)
- `text.secondary` - Secondary text (#a0a8b8)
- `text.muted` - Muted text (#6c7584)

#### Semantic Colors
- `semantic.success` - Success states (#28a745)
- `semantic.warning` - Warning states (#ff9500)
- `semantic.error` - Error states (#dc3545)
- `semantic.info` - Informational states (#3b82f6)

#### Compliance Colors
- `compliance.gdpr` - GDPR-related UI (#3b82f6)
- `compliance.fca` - FCA-related UI (#a78bfa)
- `compliance.tax` - Tax-related UI (#10b981)
- `compliance.employment` - Employment-related UI (#f59e0b)

### Typography

#### Font Families
- `fontFamily.base` - System font stack
- `fontFamily.mono` - Monospace font stack

#### Font Sizes
- `fontSize.xs` - 11px
- `fontSize.sm` - 12px
- `fontSize.base` - 14px (default)
- `fontSize.lg` - 16px
- `fontSize.xl` - 18px
- `fontSize.2xl` - 20px
- `fontSize.3xl` - 24px

#### Font Weights
- `fontWeight.normal` - 400
- `fontWeight.medium` - 500
- `fontWeight.semibold` - 600
- `fontWeight.bold` - 700

### Spacing

The spacing scale follows a consistent 4px grid:

```
spacing[1] = 4px
spacing[2] = 8px
spacing[3] = 12px
spacing[4] = 16px
spacing[6] = 24px
spacing[8] = 32px
```

### Shadows

- `shadows.sm` - Subtle shadow for cards
- `shadows.md` - Medium shadow for elevated elements
- `shadows.lg` - Large shadow for modals
- `shadows.focus` - Focus ring for keyboard navigation

### Border Radius

- `borderRadius.base` - 4px (default)
- `borderRadius.md` - 6px
- `borderRadius.lg` - 8px
- `borderRadius.full` - 9999px (pills)

---

## Components

### Button

A versatile button component with multiple variants and sizes.

```tsx
<Button variant="primary" size="md" onClick={handleClick}>
  Click Me
</Button>
```

**Variants:** `primary`, `secondary`, `outline`, `ghost`, `danger`
**Sizes:** `xs`, `sm`, `md`, `lg`, `xl`

**Props:**
- `variant` - Visual style
- `size` - Button size
- `disabled` - Disable button
- `loading` - Show loading spinner
- `leftIcon` - Icon before text
- `rightIcon` - Icon after text

### Input

Form input with validation states and helper text.

```tsx
<Input
  label="Email Address"
  type="email"
  placeholder="you@example.com"
  error="Invalid email"
/>
```

**Sizes:** `sm`, `md`, `lg`
**Statuses:** `default`, `error`, `success`, `warning`

**Props:**
- `label` - Field label
- `helperText` - Helper text below input
- `error` - Error message
- `leftIcon` - Icon before input
- `rightIcon` - Icon after input

### Card

Container component for grouping related content.

```tsx
<Card variant="elevated" padding="lg">
  <h3>Card Title</h3>
  <p>Card content...</p>
</Card>
```

**Variants:** `default`, `elevated`, `outlined`, `ghost`
**Padding:** `none`, `sm`, `md`, `lg`

**Props:**
- `header` - Card header content
- `footer` - Card footer content
- `hoverable` - Hover effect
- `clickable` - Pointer cursor

### Badge

Small status indicators and labels.

```tsx
<Badge variant="success" size="md">
  Active
</Badge>
```

**Variants:** `default`, `primary`, `success`, `warning`, `error`, `info`, `critical`, `high`, `medium`, `low`
**Sizes:** `sm`, `md`, `lg`

**Props:**
- `dot` - Show dot indicator
- `leftIcon` - Icon before text
- `rightIcon` - Icon after text

### Toast

Notification system for user feedback.

```tsx
const { addToast } = useToast();

addToast({
  title: 'Success!',
  message: 'Your changes have been saved.',
  variant: 'success',
  duration: 5000,
});
```

**Variants:** `success`, `error`, `warning`, `info`

### Modal

Dialog overlay for focused interactions.

```tsx
<Modal
  isOpen={isOpen}
  onClose={handleClose}
  title="Confirm Action"
  size="md"
>
  <p>Are you sure you want to proceed?</p>
</Modal>
```

**Sizes:** `sm`, `md`, `lg`, `xl`, `full`

### Skeleton

Loading placeholders for content.

```tsx
<Skeleton variant="text" width="80%" />
<SkeletonCard />
<SkeletonText lines={3} />
```

**Variants:** `text`, `circular`, `rectangular`

### EmptyState

Placeholder for empty data states.

```tsx
<EmptyState
  icon={<SearchIcon size={64} />}
  title="No results found"
  description="Try adjusting your search criteria"
  action={{
    label: 'Clear Filters',
    onClick: handleClearFilters,
  }}
/>
```

### ErrorState

Error display with retry capabilities.

```tsx
<ErrorState
  title="Failed to Load Data"
  message="We couldn't load the compliance data. Please try again."
  errorCode="ERR_NETWORK_500"
  onRetry={handleRetry}
  onReset={handleReset}
/>
```

### Spinner

Loading indicator with size variants.

```tsx
<Spinner size="md" variant="primary" />
<SpinnerOverlay message="Loading compliance data..." />
```

---

## Patterns

Common UI patterns and layouts for consistent structure.

### Layout Patterns

```tsx
import { patterns } from '@/design-system/patterns';

// Stack - vertical layout
<div style={patterns.layout.stack(4)}>
  <Item1 />
  <Item2 />
</div>

// Grid - responsive grid
<div style={patterns.layout.gridAutoFit('250px', 4)}>
  <Card />
  <Card />
  <Card />
</div>

// Container - centered with max-width
<div style={patterns.layout.container('1200px')}>
  <Content />
</div>
```

### Card Patterns

```tsx
// Status card
<div style={patterns.card.status('critical')}>
  Critical alert content
</div>

// Hoverable card
<div style={patterns.card.hoverable}>
  Interactive card
</div>
```

### Form Patterns

```tsx
// Form layout
<form style={patterns.form.form}>
  <div style={patterns.form.fieldGroup}>
    <Input label="Name" />
  </div>
  <div style={patterns.form.formActions}>
    <Button>Submit</Button>
  </div>
</form>
```

### Navigation Patterns

```tsx
// Tabs
<div style={patterns.navigation.tabs}>
  <button style={patterns.navigation.tabActive}>Tab 1</button>
  <button style={patterns.navigation.tab}>Tab 2</button>
</div>
```

---

## Icons

Custom compliance-focused icons plus common UI icons.

### Compliance Icons

```tsx
import {
  GDPRIcon,
  FCAIcon,
  TaxIcon,
  EmploymentIcon,
  ComplianceCheckIcon,
} from '@/assets/icons';

<GDPRIcon size={24} color="#3b82f6" />
```

### Status Icons

```tsx
import {
  CheckIcon,
  AlertIcon,
  InfoIcon,
  ErrorIcon,
} from '@/assets/icons';
```

### UI Icons

```tsx
import {
  SearchIcon,
  FilterIcon,
  SettingsIcon,
  CloseIcon,
  MenuIcon,
  UploadIcon,
  DownloadIcon,
} from '@/assets/icons';
```

All icons accept `size` and `color` props.

---

## Animations

Framer Motion animations for smooth interactions.

### Animation Variants

```tsx
import { motion } from 'framer-motion';
import { animations } from '@/design-system/animations';

// Fade in
<motion.div
  initial="initial"
  animate="animate"
  exit="exit"
  variants={animations.fadeIn}
>
  Content
</motion.div>

// Slide in from right
<motion.div variants={animations.slideInRight}>
  Content
</motion.div>

// Staggered list
<motion.div variants={animations.staggerContainer}>
  <motion.div variants={animations.listItem}>Item 1</motion.div>
  <motion.div variants={animations.listItem}>Item 2</motion.div>
</motion.div>
```

### Available Animations

**Entrance:** `fadeIn`, `fadeInUp`, `fadeInDown`, `scaleIn`, `slideInRight`
**Continuous:** `pulse`, `bounce`, `spin`, `float`, `wiggle`
**Attention:** `shake`, `heartbeat`, `flash`, `rubberBand`
**Modals:** `modalBackdrop`, `modalContent`, `drawerRight`

---

## Accessibility

The LOKI Design System follows WCAG 2.1 AA standards.

### Focus Management

All interactive elements have visible focus states:

```tsx
// Components automatically include focus styles
<Button>Accessible Button</Button>
```

### Keyboard Navigation

- **Tab**: Navigate between focusable elements
- **Enter/Space**: Activate buttons and controls
- **Escape**: Close modals and overlays
- **Arrow Keys**: Navigate within composite widgets

### Screen Reader Support

Components include proper ARIA labels and roles:

```tsx
<Spinner label="Loading compliance data" />
<Modal title="Confirm Action" aria-labelledby="modal-title">
  ...
</Modal>
```

### Color Contrast

All text and interactive elements meet WCAG AA contrast ratios:
- Normal text: 4.5:1
- Large text: 3:1
- UI components: 3:1

---

## Best Practices

### Do's

✅ Use design tokens instead of hardcoded values
✅ Use semantic color names (`success`, `error`)
✅ Provide clear labels and helper text for form fields
✅ Include loading and error states
✅ Test with keyboard navigation
✅ Use consistent spacing from the spacing scale
✅ Leverage existing patterns for common layouts

### Don'ts

❌ Don't use arbitrary colors or spacing values
❌ Don't forget to handle loading and error states
❌ Don't use color alone to convey meaning
❌ Don't skip focus indicators
❌ Don't use generic error messages
❌ Don't nest interactive elements

### Performance Tips

1. **Lazy Load Components**: Use React.lazy() for large components
2. **Memoize Heavy Calculations**: Use useMemo for expensive operations
3. **Optimize Images**: Use appropriate formats and sizes
4. **Minimize Animations**: Use animations purposefully, not excessively

---

## Storybook

View all components interactively in Storybook:

```bash
cd frontend
npm run storybook
```

This will open Storybook at `http://localhost:6006` where you can:
- Browse all components
- Test different props and states
- View component documentation
- Test accessibility

---

## File Structure

```
frontend/
├── src/
│   ├── design-system/
│   │   ├── tokens.ts          # Design tokens
│   │   ├── tokens.css         # CSS custom properties
│   │   ├── animations.ts      # Animation library
│   │   └── patterns.ts        # Pattern library
│   ├── components/
│   │   └── ui/
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Card.tsx
│   │       ├── Badge.tsx
│   │       ├── Toast.tsx
│   │       ├── Modal.tsx
│   │       ├── Skeleton.tsx
│   │       ├── EmptyState.tsx
│   │       ├── ErrorState.tsx
│   │       ├── Spinner.tsx
│   │       └── index.ts
│   ├── assets/
│   │   └── icons/
│   │       └── index.tsx      # Icon library
│   └── stories/
│       ├── Button.stories.tsx
│       ├── Input.stories.tsx
│       └── Badge.stories.tsx
└── .storybook/
    ├── main.js
    └── preview.js
```

---

## Version History

- **v1.0** - Initial design system release
  - 10+ core components
  - Complete design token system
  - Animation library
  - Icon system
  - Storybook documentation

---

## Support

For questions or issues with the design system:

1. Check the Storybook documentation
2. Review component examples in `/src/stories`
3. Consult the design tokens in `/src/design-system/tokens.ts`
4. Refer to this documentation

---

## Future Enhancements

Planned improvements for future versions:

- [ ] Additional form components (Select, Checkbox, Radio, Textarea)
- [ ] Data table component with sorting and filtering
- [ ] Chart components for analytics
- [ ] Command palette for quick actions
- [ ] Context menu component
- [ ] Tooltip component
- [ ] Dropdown menu component
- [ ] Date picker component
- [ ] File upload component
- [ ] Multi-step form wizard

---

**Built with care for the LOKI compliance platform** 🛡️
