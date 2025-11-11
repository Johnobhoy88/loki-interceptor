# LOKI Design System Integration Guide

Quick start guide for developers integrating the LOKI Design System into their workflows.

## Table of Contents

- [Setup](#setup)
- [Quick Start](#quick-start)
- [Component Usage](#component-usage)
- [Theming](#theming)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)

---

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

This installs:
- React 18
- Framer Motion (animations)
- Storybook (component documentation)
- TypeScript

### 2. Import CSS Tokens

Add this to your main application file:

```tsx
// src/main.tsx or src/App.tsx
import './design-system/tokens.css';
```

### 3. Set Up Toast Provider

Wrap your app with the ToastProvider for notifications:

```tsx
import { ToastProvider } from './components/ui';

function App() {
  return (
    <ToastProvider>
      {/* Your app content */}
    </ToastProvider>
  );
}
```

---

## Quick Start

### Basic Component Usage

```tsx
import React from 'react';
import { Button, Card, Badge, Input } from '@/components/ui';

function MyComponent() {
  const [email, setEmail] = React.useState('');

  return (
    <Card>
      <h2>Welcome to LOKI</h2>
      <Badge variant="success">Active</Badge>

      <Input
        label="Email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="you@example.com"
      />

      <Button variant="primary" onClick={() => console.log('Submit')}>
        Submit
      </Button>
    </Card>
  );
}
```

### Using Icons

```tsx
import { GDPRIcon, CheckIcon, AlertIcon } from '@/assets/icons';

function ComplianceStatus() {
  return (
    <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
      <GDPRIcon size={24} color="#3b82f6" />
      <span>GDPR Compliant</span>
      <CheckIcon size={20} color="#28a745" />
    </div>
  );
}
```

### Using Animations

```tsx
import { motion } from 'framer-motion';
import { animations } from '@/design-system/animations';

function AnimatedCard() {
  return (
    <motion.div
      initial="initial"
      animate="animate"
      exit="exit"
      variants={animations.fadeInUp}
      style={{ padding: '2rem', background: '#12161f' }}
    >
      <h3>Animated Content</h3>
      <p>This card fades in with an upward motion</p>
    </motion.div>
  );
}
```

### Using Design Tokens

```tsx
import { theme } from '@/design-system/tokens';

function CustomComponent() {
  return (
    <div
      style={{
        backgroundColor: theme.colors.background.panel,
        padding: theme.spacing[5],
        borderRadius: theme.borderRadius.lg,
        boxShadow: theme.shadows.md,
        color: theme.colors.text.primary,
      }}
    >
      <h3 style={{ fontSize: theme.typography.fontSize['2xl'] }}>
        Custom Styled Component
      </h3>
    </div>
  );
}
```

---

## Component Usage

### Button Examples

```tsx
// Primary action
<Button variant="primary" size="md">
  Save Changes
</Button>

// With icon
<Button variant="primary" leftIcon={<UploadIcon size={16} />}>
  Upload Document
</Button>

// Loading state
<Button variant="primary" loading>
  Processing...
</Button>

// Danger action
<Button variant="danger" onClick={handleDelete}>
  Delete
</Button>
```

### Input Examples

```tsx
// Basic input
<Input
  label="Username"
  placeholder="Enter username"
  value={username}
  onChange={(e) => setUsername(e.target.value)}
/>

// With validation
<Input
  label="Email"
  type="email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  error={emailError}
  status={emailError ? 'error' : 'default'}
/>

// With icon
<Input
  placeholder="Search..."
  leftIcon={<SearchIcon size={18} />}
  value={search}
  onChange={(e) => setSearch(e.target.value)}
/>
```

### Card Examples

```tsx
// Basic card
<Card>
  <h3>Card Title</h3>
  <p>Card content goes here</p>
</Card>

// With header and footer
<Card
  header={<h3>Compliance Report</h3>}
  footer={
    <Button variant="outline" fullWidth>
      View Details
    </Button>
  }
>
  <p>Report content...</p>
</Card>

// Clickable card
<Card clickable onClick={handleCardClick}>
  <h3>Interactive Card</h3>
  <p>Click anywhere to interact</p>
</Card>
```

### Toast Notifications

```tsx
import { useToast } from '@/components/ui';

function MyComponent() {
  const { addToast } = useToast();

  const handleSuccess = () => {
    addToast({
      title: 'Success!',
      message: 'Your changes have been saved.',
      variant: 'success',
      duration: 5000,
    });
  };

  const handleError = () => {
    addToast({
      title: 'Error',
      message: 'Failed to save changes. Please try again.',
      variant: 'error',
      duration: 0, // Don't auto-dismiss
    });
  };

  return (
    <>
      <Button onClick={handleSuccess}>Show Success</Button>
      <Button onClick={handleError}>Show Error</Button>
    </>
  );
}
```

### Modal Examples

```tsx
function MyComponent() {
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <>
      <Button onClick={() => setIsOpen(true)}>
        Open Modal
      </Button>

      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="Confirm Action"
        size="md"
        footer={
          <>
            <Button variant="outline" onClick={() => setIsOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleConfirm}>
              Confirm
            </Button>
          </>
        }
      >
        <p>Are you sure you want to proceed with this action?</p>
      </Modal>
    </>
  );
}
```

### Loading States

```tsx
import { Spinner, SkeletonCard, SkeletonText } from '@/components/ui';

// Inline spinner
<Spinner size="md" variant="primary" />

// Full page loading
<SpinnerOverlay message="Loading compliance data..." />

// Skeleton placeholder
<SkeletonCard />
<SkeletonText lines={3} />
```

### Empty & Error States

```tsx
import { EmptyState, ErrorState } from '@/components/ui';

// Empty state
<EmptyState
  icon={<SearchIcon size={64} />}
  title="No documents found"
  description="Try adjusting your filters or upload a new document"
  action={{
    label: 'Upload Document',
    onClick: handleUpload,
  }}
/>

// Error state
<ErrorState
  title="Failed to Load Data"
  message="We couldn't fetch the compliance data. Please try again."
  errorCode="ERR_500"
  details={error.stack}
  onRetry={handleRetry}
  onReset={handleGoBack}
/>
```

---

## Theming

### Dark Mode (Default)

The design system uses dark mode by default. All components are optimized for dark backgrounds.

### Light Mode (Optional)

To enable light mode, add the `data-theme` attribute:

```tsx
// Add to your root element
<div data-theme="light">
  {/* Your app */}
</div>
```

### Custom Theme Values

Override CSS custom properties for custom themes:

```css
[data-theme='custom'] {
  --color-brand-primary: #your-color;
  --color-bg-primary: #your-background;
  /* ... other overrides */
}
```

---

## Common Patterns

### Form Layout

```tsx
import { patterns } from '@/design-system/patterns';

function MyForm() {
  return (
    <form style={patterns.form.form}>
      <div style={patterns.form.fieldGroup}>
        <Input label="Name" />
      </div>

      <div style={patterns.form.fieldGroup}>
        <Input label="Email" type="email" />
      </div>

      <div style={patterns.form.formActions}>
        <Button variant="outline">Cancel</Button>
        <Button variant="primary">Submit</Button>
      </div>
    </form>
  );
}
```

### Grid Layout

```tsx
import { patterns } from '@/design-system/patterns';

function CardGrid() {
  return (
    <div style={patterns.layout.gridAutoFit('250px', 4)}>
      <Card>Card 1</Card>
      <Card>Card 2</Card>
      <Card>Card 3</Card>
      <Card>Card 4</Card>
    </div>
  );
}
```

### Stacked Layout

```tsx
import { patterns } from '@/design-system/patterns';

function StackedContent() {
  return (
    <div style={patterns.layout.stack(6)}>
      <h2>Section Title</h2>
      <Card>Content 1</Card>
      <Card>Content 2</Card>
      <Card>Content 3</Card>
    </div>
  );
}
```

### Status Cards

```tsx
import { patterns } from '@/design-system/patterns';

function StatusCards() {
  return (
    <>
      <div style={patterns.card.status('success')}>
        <p>All compliance checks passed!</p>
      </div>

      <div style={patterns.card.status('warning')}>
        <p>Review required for FCA compliance</p>
      </div>

      <div style={patterns.card.status('critical')}>
        <p>GDPR violation detected</p>
      </div>
    </>
  );
}
```

### Animated List

```tsx
import { motion } from 'framer-motion';
import { animations } from '@/design-system/animations';

function AnimatedList({ items }) {
  return (
    <motion.div
      initial="initial"
      animate="animate"
      variants={animations.staggerContainer}
    >
      {items.map((item) => (
        <motion.div
          key={item.id}
          variants={animations.listItem}
          style={{ padding: '1rem', background: '#12161f', marginBottom: '0.5rem' }}
        >
          {item.content}
        </motion.div>
      ))}
    </motion.div>
  );
}
```

---

## Best Practices

### ✅ Do's

1. **Use Design Tokens**
   ```tsx
   // Good
   style={{ color: theme.colors.text.primary }}

   // Bad
   style={{ color: '#ffffff' }}
   ```

2. **Provide Feedback**
   ```tsx
   // Good
   <Button loading={isSubmitting}>Submit</Button>

   // Bad
   <Button disabled={isSubmitting}>Submit</Button>
   ```

3. **Handle Errors Gracefully**
   ```tsx
   // Good
   {error && <ErrorState message={error.message} onRetry={retry} />}

   // Bad
   {error && <p>Error!</p>}
   ```

4. **Use Semantic Variants**
   ```tsx
   // Good
   <Badge variant="success">Approved</Badge>

   // Bad
   <Badge style={{ color: 'green' }}>Approved</Badge>
   ```

### ❌ Don'ts

1. **Don't Use Arbitrary Values**
   ```tsx
   // Bad
   style={{ padding: '17px', fontSize: '13.5px' }}

   // Good
   style={{
     padding: theme.spacing[4],
     fontSize: theme.typography.fontSize.sm,
   }}
   ```

2. **Don't Nest Interactive Elements**
   ```tsx
   // Bad
   <Button>
     <a href="/link">Click</a>
   </Button>

   // Good
   <Button onClick={() => navigate('/link')}>
     Click
   </Button>
   ```

3. **Don't Override Component Styles Heavily**
   ```tsx
   // Bad - creating a new component
   <Button style={{ /* 20 custom overrides */ }}>

   // Good - extend the component if needed
   const CustomButton = styled(Button)`...`;
   ```

4. **Don't Forget Loading States**
   ```tsx
   // Bad
   <Button onClick={handleSubmit}>Submit</Button>

   // Good
   <Button
     onClick={handleSubmit}
     loading={isSubmitting}
     disabled={!isValid}
   >
     Submit
   </Button>
   ```

---

## Testing with Storybook

Run Storybook to test components:

```bash
npm run storybook
```

Access at `http://localhost:6006`

### Available Stories

- Button variations and states
- Input with validation
- Card layouts
- Badge variants
- All other components

Use Storybook to:
- Preview components in isolation
- Test different props and states
- Check accessibility
- Verify responsive behavior

---

## TypeScript Support

All components are fully typed. Use IntelliSense for prop suggestions:

```tsx
import { Button, ButtonProps } from '@/components/ui';

// Full type safety
const props: ButtonProps = {
  variant: 'primary', // Autocomplete: primary | secondary | outline | ghost | danger
  size: 'md',         // Autocomplete: xs | sm | md | lg | xl
  loading: false,
};
```

---

## Performance Tips

1. **Lazy Load Modals**
   ```tsx
   const Modal = React.lazy(() => import('@/components/ui/Modal'));
   ```

2. **Memoize Heavy Components**
   ```tsx
   const MemoizedCard = React.memo(Card);
   ```

3. **Use Skeleton Loaders**
   ```tsx
   {loading ? <SkeletonCard /> : <Card>{data}</Card>}
   ```

4. **Debounce Input Handlers**
   ```tsx
   const debouncedSearch = useMemo(
     () => debounce(handleSearch, 300),
     []
   );
   ```

---

## Getting Help

1. **Check Storybook** - Interactive component examples
2. **Read DESIGN_SYSTEM.md** - Complete documentation
3. **Review BRAND_GUIDELINES.md** - Brand usage guidelines
4. **Inspect Component Source** - `/src/components/ui/`
5. **Check Design Tokens** - `/src/design-system/tokens.ts`

---

## Migration from Old Styles

If migrating from the old `style.css`:

1. Replace hardcoded colors with tokens:
   ```css
   /* Old */
   color: #ffffff;
   background: #0a0e1a;

   /* New */
   color: var(--color-text-primary);
   background: var(--color-bg-primary);
   ```

2. Use components instead of CSS classes:
   ```tsx
   /* Old */
   <button className="btn btn--primary">Click</button>

   /* New */
   <Button variant="primary">Click</Button>
   ```

3. Replace custom cards with Card component:
   ```tsx
   /* Old */
   <div className="card">...</div>

   /* New */
   <Card>...</Card>
   ```

---

**Ready to build with LOKI Design System!** 🛡️

For questions or issues, refer to the main documentation or contact the design team.
