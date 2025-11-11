# LOKI Interceptor Frontend - Quick Start Guide

**Get up and running in 5 minutes!**

---

## Prerequisites

- Node.js 18+ and npm 9+
- Backend API running (default: `http://localhost:8000`)

---

## Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Edit .env if needed (optional)
# VITE_API_URL=http://localhost:8000/api
# VITE_WS_URL=ws://localhost:8000/ws
```

---

## Development

```bash
# Start development server with hot reload
npm run dev

# Application will open at http://localhost:3000
```

---

## Available Scripts

```bash
# Development
npm run dev              # Start dev server
npm run preview          # Preview production build

# Build
npm run build            # Build for production
npm run type-check       # Check TypeScript types

# Code Quality
npm run lint             # Run ESLint
npm run format           # Format with Prettier

# Testing
npm run test             # Run tests
npm run test:ui          # Open test UI
npm run test:coverage    # Coverage report
```

---

## Project Structure

```
src/
├── components/          # UI Components
│   ├── ui/             # Base components (Button, Card, etc.)
│   ├── layout/         # Layout components (AppLayout)
│   └── features/       # Feature components (DocumentUploader)
├── pages/              # Pages (Dashboard, Validator, History)
├── hooks/              # Custom React hooks
├── services/           # API integration
├── stores/             # State management (Zustand)
├── types/              # TypeScript types
└── lib/                # Utilities
```

---

## Key Files

| File | Description |
|------|-------------|
| `src/App.tsx` | Root component with routing |
| `src/main.tsx` | Application entry point |
| `src/pages/dashboard.tsx` | Main dashboard |
| `src/pages/validator.tsx` | Validation interface |
| `src/services/api-client.ts` | HTTP client |
| `src/stores/validation-store.ts` | Validation state |
| `src/types/index.ts` | TypeScript types |

---

## Usage Examples

### Validate a Document

```typescript
import { useValidation } from '@/hooks/use-validation'

function ValidatorComponent() {
  const { validate, isValidating, data } = useValidation()

  const handleValidate = () => {
    validate({
      content: "Your document content here",
      modules: ["gdpr_uk", "uk_employment"],
      options: {
        includeExplanations: true,
      },
    })
  }

  return (
    <button onClick={handleValidate} disabled={isValidating}>
      {isValidating ? 'Validating...' : 'Validate'}
    </button>
  )
}
```

### Use Components

```typescript
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

function MyComponent() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>My Card</CardTitle>
      </CardHeader>
      <CardContent>
        <Button onClick={() => console.log('Clicked')}>
          Click Me
        </Button>
      </CardContent>
    </Card>
  )
}
```

### Manage State

```typescript
import { useValidationStore } from '@/stores/validation-store'

function MyComponent() {
  const { currentValidation, setCurrentValidation } = useValidationStore()

  // Access or update validation state
}
```

---

## Common Tasks

### Add a New Page

1. Create file: `src/pages/my-page.tsx`
2. Add route in `src/App.tsx`:

```typescript
<Route path="my-page" element={<MyPage />} />
```

3. Add to navigation in `src/components/layout/app-layout.tsx`

### Add a New Component

1. Create file: `src/components/features/my-component.tsx`
2. Export component
3. Use in pages:

```typescript
import { MyComponent } from '@/components/features/my-component'
```

### Add API Endpoint

1. Add service method in `src/services/`
2. Create custom hook in `src/hooks/`
3. Use in components

---

## Customization

### Change Theme Colors

Edit `src/styles/globals.css`:

```css
:root {
  --primary: 221.2 83.2% 53.3%; /* Your color in HSL */
}
```

### Configure API URL

Edit `.env`:

```env
VITE_API_URL=https://your-api.com/api
```

### Add New Module

1. Add type to `src/types/index.ts`
2. Add service to `src/services/`
3. Add hook to `src/hooks/`

---

## Build & Deploy

### Build for Production

```bash
npm run build
```

Output in `dist/` directory.

### Deploy with Docker

```bash
# Build image
docker build -t loki-frontend .

# Run container
docker run -p 80:80 loki-frontend
```

### Deploy to Vercel

```bash
npm install -g vercel
vercel --prod
```

---

## Troubleshooting

### Port Already in Use

Edit `vite.config.ts`:

```typescript
server: {
  port: 3001, // Change port
}
```

### API Connection Issues

1. Check backend is running
2. Verify `VITE_API_URL` in `.env`
3. Check browser console for errors

### TypeScript Errors

```bash
# Clear and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Build Errors

```bash
# Type check
npm run type-check

# Clean build
rm -rf dist
npm run build
```

---

## Documentation

- **Full README**: `/frontend/README.md`
- **Architecture Guide**: `/FRONTEND_ARCHITECTURE.md`
- **Delivery Report**: `/AGENT_16_DELIVERY_REPORT.md`
- **API Docs**: `/API_DOCUMENTATION.md`

---

## Support

For issues or questions:

1. Check documentation in `/frontend/README.md`
2. Review architecture in `/FRONTEND_ARCHITECTURE.md`
3. Check delivery report for implementation details

---

## Next Steps

1. ✅ Start development server: `npm run dev`
2. ✅ Explore the dashboard at `http://localhost:3000`
3. ✅ Try the validator page
4. ✅ Customize theme and colors
5. ✅ Add your features
6. ✅ Build and deploy

**Happy coding! 🚀**
