# LOKI Interceptor - Frontend Architecture Documentation

**Version:** 1.0.0
**Last Updated:** 2025-11-11
**Author:** Agent 16 - React UI Architect

---

## Executive Summary

This document provides comprehensive documentation for the LOKI Interceptor React frontend application. The frontend is a modern, production-ready web application built with React 18+, TypeScript, and cutting-edge web technologies, designed to provide an intuitive interface for compliance document validation and correction.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Core Systems](#core-systems)
5. [Component Library](#component-library)
6. [State Management](#state-management)
7. [API Integration](#api-integration)
8. [Routing & Navigation](#routing--navigation)
9. [Theming & Styling](#theming--styling)
10. [Performance Optimization](#performance-optimization)
11. [Accessibility](#accessibility)
12. [Testing Strategy](#testing-strategy)
13. [Deployment Guide](#deployment-guide)
14. [Development Workflow](#development-workflow)
15. [Best Practices](#best-practices)

---

## Architecture Overview

### Design Philosophy

The LOKI Interceptor frontend follows modern React best practices:

- **Component-Driven**: Modular, reusable components
- **Type-Safe**: Full TypeScript coverage with strict mode
- **Performance-First**: Code splitting, lazy loading, optimized bundles
- **Accessible**: WCAG 2.1 AA compliant
- **Responsive**: Mobile-first design approach
- **Developer Experience**: Fast HMR, comprehensive tooling

### Application Flow

```
User Input → Validation → API Request → State Update → UI Render
     ↓           ↓            ↓            ↓            ↓
  Upload → Module Selection → Backend → Zustand/Query → Components
```

### Architecture Layers

```
┌─────────────────────────────────────┐
│     Presentation Layer (Pages)      │
│  Dashboard, Validator, History      │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│   Component Layer (UI Components)   │
│  Buttons, Cards, Forms, Charts      │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│    Business Logic Layer (Hooks)     │
│  useValidation, useModules, etc.    │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│   State Management (Zustand/Query)  │
│  Global State, Server State Cache   │
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│    API Layer (Services)             │
│  REST API, WebSocket                │
└─────────────────────────────────────┘
```

---

## Technology Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.3+ | UI Framework |
| TypeScript | 5.3+ | Type Safety |
| Vite | 5.1+ | Build Tool |
| Tailwind CSS | 3.4+ | Styling |
| React Router | 6.22+ | Routing |
| React Query | 5.22+ | Server State |
| Zustand | 4.5+ | Client State |

### UI Components

| Library | Purpose |
|---------|---------|
| Radix UI | Accessible primitives |
| Shadcn/UI | Component patterns |
| Lucide React | Icon system |
| Recharts | Data visualization |
| Framer Motion | Animations |

### Developer Tools

| Tool | Purpose |
|------|---------|
| ESLint | Code linting |
| Prettier | Code formatting |
| Vitest | Unit testing |
| Testing Library | Component testing |

---

## Project Structure

### Directory Organization

```
frontend/
├── src/
│   ├── components/          # UI Components
│   │   ├── ui/             # Base Shadcn components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── input.tsx
│   │   │   ├── badge.tsx
│   │   │   ├── progress.tsx
│   │   │   └── textarea.tsx
│   │   ├── layout/         # Layout components
│   │   │   └── app-layout.tsx
│   │   └── features/       # Feature components
│   │       ├── document-uploader.tsx
│   │       ├── validation-results.tsx
│   │       └── compliance-score-chart.tsx
│   │
│   ├── pages/              # Page components
│   │   ├── dashboard.tsx   # Main dashboard
│   │   ├── validator.tsx   # Validation interface
│   │   ├── history.tsx     # Validation history
│   │   └── settings.tsx    # User settings
│   │
│   ├── hooks/              # Custom React hooks
│   │   ├── use-validation.ts  # Validation operations
│   │   ├── use-modules.ts     # Module management
│   │   ├── use-history.ts     # History operations
│   │   └── use-theme.ts       # Theme management
│   │
│   ├── services/           # API integration
│   │   ├── api-client.ts        # HTTP client
│   │   ├── validation-service.ts # Validation API
│   │   ├── module-service.ts     # Module API
│   │   ├── history-service.ts    # History API
│   │   ├── stats-service.ts      # Statistics API
│   │   └── websocket-service.ts  # WebSocket client
│   │
│   ├── stores/             # State management
│   │   ├── validation-store.ts  # Validation state
│   │   ├── settings-store.ts    # User settings
│   │   └── ui-store.ts          # UI state
│   │
│   ├── types/              # TypeScript types
│   │   └── index.ts        # Type definitions
│   │
│   ├── lib/                # Utilities
│   │   └── utils.ts        # Helper functions
│   │
│   ├── styles/             # Global styles
│   │   └── globals.css     # Tailwind + custom styles
│   │
│   ├── App.tsx             # Root component
│   └── main.tsx            # Entry point
│
├── public/                 # Static assets
├── index-react.html        # HTML template
├── package-react.json      # Dependencies
├── tsconfig.json          # TypeScript config
├── vite.config.ts         # Vite config
├── tailwind.config.ts     # Tailwind config
├── postcss.config.js      # PostCSS config
├── .eslintrc.cjs          # ESLint config
├── .prettierrc            # Prettier config
└── README.md              # Documentation
```

### File Naming Conventions

- **Components**: PascalCase (`DocumentUploader.tsx`)
- **Hooks**: camelCase with `use` prefix (`useValidation.ts`)
- **Services**: camelCase with suffix (`validation-service.ts`)
- **Types**: camelCase (`index.ts`)
- **Utilities**: camelCase (`utils.ts`)

---

## Core Systems

### 1. Validation System

**Purpose**: Handle document validation operations

**Components**:
- `ValidatorPage`: Main validation interface
- `DocumentUploader`: File upload component
- `ValidationResults`: Results display

**Hooks**:
```typescript
const { validate, isValidating, data } = useValidation()

validate({
  content: "document content",
  modules: ["gdpr_uk", "uk_employment"],
  options: {
    includeExplanations: true,
    autoCorrect: false,
  },
})
```

**Flow**:
1. User uploads document or pastes content
2. Selects compliance modules
3. Initiates validation
4. Results displayed with issues and corrections
5. User can apply corrections

### 2. Correction System

**Purpose**: Apply automated corrections to compliance issues

**Components**:
- `ValidationResults`: Issue cards with fix buttons
- `CorrectionPreview`: Diff viewer for changes

**Hooks**:
```typescript
const { correct, isCorrecting, data } = useCorrection()

correct({
  validationId: "validation-id",
  issueIds: ["issue-1", "issue-2"],
  reviewRequired: false,
})
```

### 3. Module System

**Purpose**: Manage compliance modules

**Components**:
- `ModuleSelector`: Select modules for validation
- `ModuleSettings`: Configure module preferences

**Hooks**:
```typescript
const { data: modules, isLoading } = useModules()
const { mutate: toggleModule } = useToggleModule()
```

### 4. History System

**Purpose**: Track and manage validation history

**Components**:
- `HistoryPage`: History list with filters
- `HistoryFilters`: Search and filter controls

**Hooks**:
```typescript
const { data, isLoading } = useHistory(page, pageSize, filter)
const { mutate: deleteItem } = useDeleteHistoryItem()
```

---

## Component Library

### Base Components (Shadcn/UI)

#### Button Component

```typescript
import { Button } from '@/components/ui/button'

<Button variant="default" size="lg" onClick={handleClick}>
  Click Me
</Button>

// Variants: default, destructive, outline, secondary, ghost, link
// Sizes: default, sm, lg, icon
```

#### Card Component

```typescript
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from '@/components/ui/card'

<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
    <CardDescription>Description</CardDescription>
  </CardHeader>
  <CardContent>Content</CardContent>
  <CardFooter>Footer</CardFooter>
</Card>
```

#### Input Component

```typescript
import { Input } from '@/components/ui/input'

<Input
  type="text"
  placeholder="Enter text..."
  value={value}
  onChange={(e) => setValue(e.target.value)}
/>
```

#### Badge Component

```typescript
import { Badge } from '@/components/ui/badge'

<Badge variant="success">Passed</Badge>
<Badge variant="destructive">Failed</Badge>
<Badge variant="warning">Warning</Badge>
```

### Feature Components

#### Document Uploader

```typescript
import { DocumentUploader } from '@/components/features/document-uploader'

<DocumentUploader
  onFileSelect={(content, fileName) => {
    setContent(content)
    setDocumentName(fileName)
  }}
  accept={{
    'text/plain': ['.txt'],
    'application/pdf': ['.pdf'],
  }}
  maxSize={10 * 1024 * 1024} // 10MB
/>
```

**Features**:
- Drag-and-drop upload
- Multiple file support
- File type validation
- Size validation
- Progress tracking

#### Validation Results

```typescript
import { ValidationResults } from '@/components/features/validation-results'

<ValidationResults
  result={validationResult}
  onApplyCorrection={(issueId) => {
    // Apply correction for specific issue
  }}
/>
```

**Features**:
- Issue categorization by severity
- Module-based grouping
- Expandable issue details
- Auto-correction buttons
- Suggestion display

#### Compliance Score Chart

```typescript
import { ComplianceScoreChart } from '@/components/features/compliance-score-chart'

<ComplianceScoreChart
  score={85}
  title="Overall Compliance"
/>
```

**Features**:
- Radial bar chart visualization
- Color-coded scores (green/yellow/red)
- Responsive design
- Tooltip with details

---

## State Management

### Zustand Stores

#### Validation Store

```typescript
import { useValidationStore } from '@/stores/validation-store'

const {
  currentValidation,
  currentCorrection,
  isValidating,
  isCorrecting,
  setCurrentValidation,
  setIsValidating,
  reset,
} = useValidationStore()
```

**State**:
- `currentValidation`: Active validation result
- `currentCorrection`: Active correction result
- `isValidating`: Validation in progress
- `isCorrecting`: Correction in progress
- `error`: Error message

**Persistence**: Stores validation/correction in localStorage

#### Settings Store

```typescript
import { useSettingsStore } from '@/stores/settings-store'

const {
  theme,
  defaultModules,
  autoCorrect,
  setTheme,
  setDefaultModules,
  updateUIPreferences,
} = useSettingsStore()
```

**State**:
- `theme`: 'light' | 'dark' | 'system'
- `language`: User language preference
- `defaultModules`: Default module selection
- `autoCorrect`: Auto-correction enabled
- `uiPreferences`: UI customization

**Persistence**: All settings persisted to localStorage

#### UI Store

```typescript
import { useUIStore } from '@/stores/ui-store'

const {
  sidebarOpen,
  toggleSidebar,
  addNotification,
  removeNotification,
} = useUIStore()
```

**State**:
- `sidebarOpen`: Sidebar visibility
- `commandPaletteOpen`: Command palette state
- `settingsPanelOpen`: Settings panel state
- `notifications`: Toast notifications

### React Query

**Server State Management**:

```typescript
import { useQuery, useMutation } from '@tanstack/react-query'

// Query example
const { data, isLoading, error } = useQuery({
  queryKey: ['modules'],
  queryFn: () => moduleService.getModules(),
  staleTime: 10 * 60 * 1000, // 10 minutes
})

// Mutation example
const { mutate, isPending } = useMutation({
  mutationFn: (request) => validationService.validate(request),
  onSuccess: (data) => {
    // Handle success
  },
  onError: (error) => {
    // Handle error
  },
})
```

**Query Keys**:
- `['modules']`: Compliance modules
- `['validation', id]`: Validation result
- `['history', page, filter]`: History items
- `['system-stats']`: System statistics

---

## API Integration

### API Client

**Base Configuration**:

```typescript
// services/api-client.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })
    this.setupInterceptors()
  }
}
```

**Features**:
- Request/response interceptors
- API key authentication
- Error handling
- Request ID tracking
- File upload with progress
- File download

### Service Layer

#### Validation Service

```typescript
import { validationService } from '@/services/validation-service'

// Validate document
const result = await validationService.validate({
  content: "document content",
  modules: ["gdpr_uk"],
  options: { includeExplanations: true },
})

// Apply corrections
const correction = await validationService.correct({
  validationId: "validation-id",
  issueIds: ["issue-1"],
})

// Export result
await validationService.exportValidation(id, 'pdf')
```

#### Module Service

```typescript
import { moduleService } from '@/services/module-service'

// Get all modules
const modules = await moduleService.getModules()

// Get module details
const module = await moduleService.getModule('gdpr_uk')

// Get recommendations
const recommended = await moduleService.getRecommendedModules(content)
```

#### History Service

```typescript
import { historyService } from '@/services/history-service'

// Get history with pagination
const history = await historyService.getHistory(1, 20, {
  status: 'failed',
  modules: ['gdpr_uk'],
})

// Export history
await historyService.exportHistory('csv', filter)
```

### WebSocket Integration

**Real-time Validation Updates**:

```typescript
import { websocketService, createValidationProgressHandler } from '@/services/websocket-service'

// Subscribe to validation progress
const unsubscribe = websocketService.subscribe(
  createValidationProgressHandler((data) => {
    console.log(`Progress: ${data.progress}%`)
    console.log(`Module: ${data.currentModule}`)
  })
)

// Cleanup
unsubscribe()
```

**Features**:
- Automatic reconnection
- Heartbeat/ping mechanism
- Type-safe message handling
- Connection status tracking

---

## Routing & Navigation

### Route Structure

```typescript
<Routes>
  <Route path="/" element={<AppLayout />}>
    <Route index element={<DashboardPage />} />
    <Route path="validator" element={<ValidatorPage />} />
    <Route path="history" element={<HistoryPage />} />
    <Route path="settings" element={<SettingsPage />} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Route>
</Routes>
```

### Navigation Menu

```typescript
const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Validator', href: '/validator', icon: FileCheck },
  { name: 'History', href: '/history', icon: History },
  { name: 'Settings', href: '/settings', icon: Settings },
]
```

### Programmatic Navigation

```typescript
import { useNavigate } from 'react-router-dom'

const navigate = useNavigate()

// Navigate to page
navigate('/validator')

// Navigate with state
navigate('/history', { state: { filter: {...} } })

// Go back
navigate(-1)
```

---

## Theming & Styling

### Color System

**CSS Variables** (`globals.css`):

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  --secondary: 210 40% 96.1%;
  --accent: 210 40% 96.1%;
  --destructive: 0 84.2% 60.2%;
  --success: 142 76% 36%;
  --warning: 38 92% 50%;
  --info: 199 89% 48%;
}

.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  /* ... dark mode colors */
}
```

### Tailwind Utilities

```typescript
// Using theme colors
<div className="bg-background text-foreground">
  <button className="bg-primary text-primary-foreground">
    Primary Button
  </button>
</div>

// Status colors
<div className="status-passed">Passed</div>
<div className="status-failed">Failed</div>
<div className="status-warning">Warning</div>
```

### Theme Switching

```typescript
import { useTheme } from '@/hooks/use-theme'

const { theme, setTheme, isDark } = useTheme()

// Set theme
setTheme('dark')      // Dark mode
setTheme('light')     // Light mode
setTheme('system')    // Follow system preference
```

### Responsive Design

```typescript
// Mobile-first breakpoints
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  {/* 1 col mobile, 2 cols tablet, 3 cols desktop */}
</div>

// Tailwind breakpoints:
// sm: 640px
// md: 768px
// lg: 1024px
// xl: 1280px
// 2xl: 1536px
```

---

## Performance Optimization

### Code Splitting

**Route-based splitting** (automatic with React Router):

```typescript
// Each page is a separate chunk
const DashboardPage = lazy(() => import('./pages/dashboard'))
const ValidatorPage = lazy(() => import('./pages/validator'))
```

**Manual code splitting**:

```typescript
import { lazy, Suspense } from 'react'

const HeavyComponent = lazy(() => import('./HeavyComponent'))

<Suspense fallback={<Loading />}>
  <HeavyComponent />
</Suspense>
```

### Bundle Optimization

**Vite configuration**:

```typescript
// vite.config.ts
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        'react-vendor': ['react', 'react-dom', 'react-router-dom'],
        'ui-vendor': ['@radix-ui/react-dialog', ...],
        'chart-vendor': ['recharts'],
      },
    },
  },
}
```

### React Query Optimization

```typescript
// Aggressive caching
const { data } = useQuery({
  queryKey: ['modules'],
  queryFn: getModules,
  staleTime: 10 * 60 * 1000,    // 10 minutes
  cacheTime: 30 * 60 * 1000,    // 30 minutes
  refetchOnWindowFocus: false,   // Don't refetch on focus
})
```

### Image Optimization

```typescript
// Lazy loading images
<img
  src={imageSrc}
  loading="lazy"
  alt="Description"
/>
```

### Performance Monitoring

```typescript
// Use React DevTools Profiler
import { Profiler } from 'react'

<Profiler id="ComponentName" onRender={onRenderCallback}>
  <Component />
</Profiler>
```

---

## Accessibility

### WCAG 2.1 AA Compliance

**Keyboard Navigation**:
- All interactive elements accessible via keyboard
- Logical tab order
- Focus visible indicators

**Screen Reader Support**:
- Semantic HTML elements
- ARIA labels and roles
- Descriptive button text

**Color Contrast**:
- Minimum 4.5:1 for normal text
- Minimum 3:1 for large text
- Success/error states use more than color

### Accessible Components

**Button with proper labeling**:

```typescript
<Button aria-label="Validate document">
  <Play className="h-4 w-4" aria-hidden="true" />
  <span>Validate</span>
</Button>
```

**Form inputs with labels**:

```typescript
<label htmlFor="email" className="sr-only">
  Email address
</label>
<Input
  id="email"
  type="email"
  placeholder="Email"
  aria-required="true"
/>
```

**Focus management**:

```typescript
import { useRef, useEffect } from 'react'

const inputRef = useRef<HTMLInputElement>(null)

useEffect(() => {
  inputRef.current?.focus()
}, [])

<Input ref={inputRef} />
```

### Testing Accessibility

```bash
# Install axe-core
npm install @axe-core/react

# Use in development
import React from 'react'
import ReactDOM from 'react-dom'
import axe from '@axe-core/react'

if (process.env.NODE_ENV !== 'production') {
  axe(React, ReactDOM, 1000)
}
```

---

## Testing Strategy

### Unit Testing with Vitest

**Component test example**:

```typescript
import { render, screen } from '@testing-library/react'
import { Button } from '@/components/ui/button'

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('handles click events', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    screen.getByText('Click me').click()
    expect(handleClick).toHaveBeenCalledTimes(1)
  })
})
```

**Hook testing**:

```typescript
import { renderHook } from '@testing-library/react'
import { useValidation } from '@/hooks/use-validation'

describe('useValidation', () => {
  it('validates document', async () => {
    const { result } = renderHook(() => useValidation())

    act(() => {
      result.current.validate({
        content: 'test content',
        modules: ['gdpr_uk'],
      })
    })

    await waitFor(() => {
      expect(result.current.data).toBeDefined()
    })
  })
})
```

### Integration Testing

**Page test example**:

```typescript
import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ValidatorPage } from '@/pages/validator'

describe('ValidatorPage', () => {
  it('renders validator interface', () => {
    const queryClient = new QueryClient()

    render(
      <QueryClientProvider client={queryClient}>
        <ValidatorPage />
      </QueryClientProvider>
    )

    expect(screen.getByText('Document Validator')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Enter your document content here...')).toBeInTheDocument()
  })
})
```

### Test Configuration

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
  },
})
```

---

## Deployment Guide

### Production Build

```bash
# Build for production
npm run build

# Output directory: dist/
# Files optimized and minified
```

### Environment Variables

```env
# .env.production
VITE_API_URL=https://api.example.com/api
VITE_WS_URL=wss://api.example.com/ws
VITE_ENABLE_ANALYTICS=true
```

### Docker Deployment

**Dockerfile**:

```dockerfile
# Build stage
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**nginx.conf**:

```nginx
server {
  listen 80;
  server_name _;

  root /usr/share/nginx/html;
  index index.html;

  location / {
    try_files $uri $uri/ /index.html;
  }

  location /api {
    proxy_pass http://backend:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}
```

### CDN Deployment

**Vercel**:

```bash
npm install -g vercel
vercel --prod
```

**Netlify**:

```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

---

## Development Workflow

### Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd loki-interceptor/frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start development server
npm run dev
```

### Code Style

**ESLint configuration**:

```javascript
// .eslintrc.cjs
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  rules: {
    '@typescript-eslint/no-unused-vars': 'warn',
    '@typescript-eslint/no-explicit-any': 'warn',
  },
}
```

**Prettier configuration**:

```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/new-feature
```

### Commit Message Convention

```
feat: add new feature
fix: fix bug
docs: update documentation
style: format code
refactor: refactor code
test: add tests
chore: update dependencies
```

---

## Best Practices

### React Best Practices

1. **Use Functional Components**: Always use hooks, avoid class components
2. **Component Composition**: Break down complex components
3. **Props Destructuring**: Destructure props for cleaner code
4. **Key Props**: Always use unique keys in lists
5. **Error Boundaries**: Wrap components that might error

### TypeScript Best Practices

1. **Strict Mode**: Enable TypeScript strict mode
2. **Type Inference**: Let TypeScript infer when possible
3. **Interface vs Type**: Use interface for objects, type for unions
4. **Avoid `any`**: Always type your data
5. **Generics**: Use generics for reusable components

### Performance Best Practices

1. **Memoization**: Use `useMemo` and `useCallback` appropriately
2. **Code Splitting**: Split routes and heavy components
3. **Lazy Loading**: Load images and components lazily
4. **Query Optimization**: Cache data with React Query
5. **Bundle Size**: Monitor and optimize bundle size

### Accessibility Best Practices

1. **Semantic HTML**: Use proper HTML elements
2. **ARIA Labels**: Add ARIA labels where needed
3. **Keyboard Support**: Ensure keyboard navigation
4. **Focus Management**: Manage focus properly
5. **Color Contrast**: Maintain proper contrast ratios

### Security Best Practices

1. **Input Validation**: Validate all user inputs
2. **XSS Prevention**: Sanitize user content
3. **API Keys**: Never expose API keys in frontend
4. **HTTPS**: Always use HTTPS in production
5. **CSP Headers**: Implement Content Security Policy

---

## Troubleshooting

### Common Issues

**Module not found errors**:
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**TypeScript errors**:
```bash
# Check TypeScript configuration
npm run type-check

# Restart TypeScript server in IDE
```

**Build errors**:
```bash
# Check environment variables
cat .env

# Clean build cache
rm -rf dist node_modules/.vite

# Rebuild
npm run build
```

**Hot reload not working**:
```bash
# Check Vite configuration
# Ensure correct port and proxy settings
```

---

## Conclusion

The LOKI Interceptor frontend is a production-ready React application designed for scalability, performance, and maintainability. This architecture document serves as a comprehensive guide for development, deployment, and maintenance.

For questions or contributions, please refer to the main project repository.

---

**Document Version:** 1.0.0
**Last Updated:** 2025-11-11
**Maintained By:** LOKI Development Team
