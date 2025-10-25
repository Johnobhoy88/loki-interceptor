---
name: loki-deployment-specialist
description: Expert in LOKI deployment on Vercel, Git workflows, branch management, CI/CD, environment configuration, and production deployments
---

# LOKI Deployment Specialist Skill

You are an expert in deploying and managing the LOKI compliance system. This skill provides comprehensive knowledge of Vercel deployment, Git workflows, branch management, environment configuration, and production operations.

## System Architecture

LOKI is a **Next.js full-stack application** deployed on Vercel with:

- **Frontend:** Next.js 14 with React (port 3000 local)
- **Backend:** Next.js API routes (port 3001 local)
- **Deployment Platform:** Vercel
- **Repository:** GitHub (Johnobhoy88/loki-interceptor)
- **Branching Strategy:** Feature branches with `claude/` prefix

## Repository Structure

```
loki-interceptor/
├── frontend/               # Next.js frontend application
│   ├── src/
│   │   ├── app/           # Next.js 14 App Router
│   │   ├── components/    # React components
│   │   └── lib/           # Frontend utilities
│   ├── public/            # Static assets
│   ├── package.json
│   └── next.config.js
├── backend/               # Backend API and validation engine
│   ├── core/             # Core engine (validation, correction)
│   ├── modules/          # Compliance modules (FCA, GDPR, Tax, NDA, HR)
│   ├── api/              # API route handlers
│   ├── server.js         # Express server (local dev)
│   └── package.json
├── vercel.json           # Vercel configuration
├── package.json          # Root package.json
└── README.md
```

## Deployment Configuration

### Vercel Configuration

**File:** `vercel.json`

```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "frontend/src/app/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "frontend/$1"
    }
  ],
  "env": {
    "NODE_ENV": "production"
  }
}
```

**Key Settings:**
- Uses `@vercel/next` for Next.js build
- Routes `/api/*` to Next.js API routes
- All other routes to frontend
- Production environment variables

### Environment Variables

**Local Development (.env):**
```bash
# Backend
PORT=3001
NODE_ENV=development

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:3001
NEXT_PUBLIC_ENABLE_CORRECTOR=true
```

**Vercel Production:**
- Set in Vercel dashboard → Settings → Environment Variables
- `NODE_ENV=production`
- `NEXT_PUBLIC_API_URL=https://your-domain.vercel.app`

**Accessing in Code:**

Frontend:
```javascript
const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';
```

Backend:
```javascript
const port = process.env.PORT || 3001;
```

## Git Workflow

### Branch Naming Convention

All Claude-created branches MUST follow pattern:
```
claude/{description}-{session-id}
```

**Examples:**
- `claude/advanced-document-corrector-011CUU58KKXs8YVbXTJSnoGu`
- `claude/add-hmrc-scam-detection-022ABC123XYZ`
- `claude/fix-gdpr-consent-gate-033DEF456UVW`

**Important:** Session ID suffix is required for push authentication!

### Creating a Feature Branch

```bash
# Create and switch to new branch
git checkout -b claude/feature-description-SESSION_ID

# Verify branch
git branch
```

### Committing Changes

**Format:**
```bash
git commit -m "$(cat <<'EOF'
Brief summary (imperative mood)

Detailed description of changes:
- What was changed
- Why it was changed
- Any important notes

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Best Practices:**
1. **Summary line:** Imperative mood, <50 chars
2. **Body:** Explain what and why, not how
3. **Always include:** Claude Code attribution
4. **Co-Author:** Claude credit line

**Good Examples:**
```
Implement enterprise-grade advanced document corrector system

Add HMRC scam detection to Tax UK module

Fix GDPR consent gate to detect bundled consent
```

**Bad Examples:**
```
Updated files
Fixed bug
Changes
```

### Pushing to Remote

**Standard Push:**
```bash
git push -u origin claude/feature-name-SESSION_ID
```

**With Retry Logic (recommended):**
```bash
# Push with exponential backoff retry
for i in 1 2 3 4; do
  git push -u origin claude/feature-name-SESSION_ID && break
  sleep $((2**i))
done
```

**Important Notes:**
- ALWAYS use `-u` flag on first push
- Branch name MUST start with `claude/`
- Session ID suffix REQUIRED for authentication
- Retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s)

### Checking Status

```bash
# View current branch and changes
git status

# View recent commits
git log --oneline -5

# View specific commit
git show <commit-hash>

# View diff
git diff
git diff --staged  # for staged changes
```

## Vercel Deployment

### Automatic Deployments

Vercel automatically deploys:
- **Production:** Pushes to main branch
- **Preview:** Pushes to any other branch (including claude/*)

**Deployment Triggers:**
1. Push to GitHub
2. Vercel detects commit
3. Builds frontend and backend
4. Deploys to URL
5. Sends deployment notification

### Manual Deployment

**Using Vercel CLI:**
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

### Deployment URLs

**Production:**
```
https://loki-interceptor.vercel.app
https://your-custom-domain.com
```

**Preview (per branch):**
```
https://loki-interceptor-git-BRANCH-NAME-username.vercel.app
```

**Example:**
```
https://loki-interceptor-git-claude-advanced-document-corrector-johnobhoy88.vercel.app
```

### Checking Deployment Status

**Vercel Dashboard:**
1. Go to https://vercel.com/dashboard
2. Select loki-interceptor project
3. View deployments list
4. Click deployment for logs

**Via CLI:**
```bash
vercel ls                    # List deployments
vercel logs [deployment-url] # View logs
vercel inspect [url]         # Inspect deployment
```

## Build Process

### Frontend Build

**Location:** `frontend/`

**Build Command:**
```bash
cd frontend
npm install
npm run build
```

**Build Output:**
- `.next/` - Next.js build output
- Static pages pre-rendered
- API routes bundled

**Next.js Configuration:**

File: `frontend/next.config.js`
```javascript
module.exports = {
  reactStrictMode: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:3001/api/:path*'
      }
    ]
  }
}
```

### Backend Build

**Location:** `backend/`

**No Build Required** - Python modules loaded at runtime

**Dependency Installation:**
```bash
cd backend
npm install  # For Express server (local dev only)
```

**Note:** On Vercel, backend runs through Next.js API routes, not Express

## API Routes (Vercel Serverless)

### Route Structure

**Location:** `frontend/src/app/api/`

```
frontend/src/app/api/
├── validate/
│   └── route.js      # POST /api/validate
├── correct/
│   └── route.js      # POST /api/correct
└── health/
    └── route.js      # GET /api/health
```

### Route Implementation

**File:** `frontend/src/app/api/validate/route.js`

```javascript
import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const { text, document_type } = await request.json();

    // Call Python validation engine
    const result = await validateDocument(text, document_type);

    return NextResponse.json(result);
  } catch (error) {
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
```

### Testing API Routes

**Local:**
```bash
curl -X POST http://localhost:3000/api/validate \
  -H "Content-Type: application/json" \
  -d '{"text": "Test document", "document_type": "financial"}'
```

**Production:**
```bash
curl -X POST https://loki-interceptor.vercel.app/api/validate \
  -H "Content-Type: application/json" \
  -d '{"text": "Test document", "document_type": "financial"}'
```

## Local Development

### Starting Development Servers

**Option 1: Separate Servers (Recommended)**

Terminal 1 - Backend:
```bash
cd backend
npm run dev
# Runs on http://localhost:3001
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

**Option 2: Concurrent (Single Terminal)**

```bash
# Root directory
npm run dev
# Runs both frontend and backend concurrently
```

### Verifying Local Setup

```bash
# Check backend health
curl http://localhost:3001/api/health

# Check frontend
curl http://localhost:3000/

# Test validation
curl -X POST http://localhost:3001/api/validate \
  -H "Content-Type: application/json" \
  -d '{"text": "Test", "document_type": "financial"}'
```

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing
- [ ] No console errors in development
- [ ] Environment variables configured
- [ ] Dependencies updated in package.json
- [ ] Build succeeds locally
- [ ] API routes tested
- [ ] Frontend UI tested
- [ ] Validation logic tested
- [ ] Correction logic tested

### Deployment Steps

1. **Commit changes**
   ```bash
   git add .
   git commit -m "Description with Claude attribution"
   ```

2. **Push to GitHub**
   ```bash
   git push -u origin claude/feature-name-SESSION_ID
   ```

3. **Verify Vercel build**
   - Check Vercel dashboard
   - Review build logs
   - Verify deployment URL

4. **Test deployment**
   ```bash
   curl https://deployment-url.vercel.app/api/health
   ```

5. **Merge to main (if needed)**
   - Create pull request
   - Review changes
   - Merge to main
   - Verify production deployment

### Post-Deployment

- [ ] Production URL accessible
- [ ] API endpoints responding
- [ ] Validation working
- [ ] Correction working
- [ ] No errors in Vercel logs
- [ ] Performance acceptable

## Common Issues and Solutions

### Issue: Push Fails with 403 Error

**Cause:** Branch name doesn't include session ID or doesn't start with `claude/`

**Solution:**
```bash
# Rename branch to include session ID
git branch -m claude/feature-name-SESSION_ID

# Push again
git push -u origin claude/feature-name-SESSION_ID
```

### Issue: Vercel Build Fails

**Check:**
1. Build logs in Vercel dashboard
2. Package.json scripts are correct
3. Dependencies are listed
4. Environment variables set

**Common Fixes:**
```bash
# Remove node_modules and reinstall
rm -rf frontend/node_modules
cd frontend && npm install

# Clear Next.js cache
rm -rf frontend/.next
```

### Issue: API Routes 404

**Causes:**
1. Route file not in correct location
2. Incorrect export (must export async function POST/GET)
3. Vercel configuration missing route

**Solution:**
- Verify file is in `frontend/src/app/api/[route]/route.js`
- Check export: `export async function POST(request) { ... }`
- Review `vercel.json` routes configuration

### Issue: Environment Variables Not Working

**Check:**
1. Variables set in Vercel dashboard
2. Variables prefixed with `NEXT_PUBLIC_` for client-side
3. Deployment redeployed after adding variables

**Solution:**
```bash
# Trigger redeploy
vercel --prod

# Or push empty commit
git commit --allow-empty -m "Trigger redeploy for env vars"
git push
```

### Issue: CORS Errors

**Solution:**

Add to API route:
```javascript
export async function POST(request) {
  const response = NextResponse.json(data);
  response.headers.set('Access-Control-Allow-Origin', '*');
  response.headers.set('Access-Control-Allow-Methods', 'POST, OPTIONS');
  response.headers.set('Access-Control-Allow-Headers', 'Content-Type');
  return response;
}
```

## Monitoring and Logs

### Vercel Dashboard

**Accessing Logs:**
1. Go to https://vercel.com/dashboard
2. Select loki-interceptor project
3. Click on deployment
4. View "Build Logs" or "Function Logs"

**Real-time Logs:**
```bash
vercel logs --follow
```

### Log Types

**Build Logs:**
- Show build process
- npm install output
- Next.js build output
- Errors during build

**Function Logs:**
- API route executions
- Runtime errors
- Console.log output
- Request/response info

### Adding Logging

**Frontend/API Routes:**
```javascript
export async function POST(request) {
  console.log('[Validate API] Request received');
  console.log('[Validate API] Body:', await request.json());
  // ... process request
  console.log('[Validate API] Response:', result);
  return NextResponse.json(result);
}
```

**Backend (for local dev):**
```python
import logging
logging.info('Validation started')
logging.error(f'Error: {error}')
```

## Performance Optimization

### Vercel Edge Functions

Consider using Edge Functions for:
- Simple API routes
- Authentication checks
- Rate limiting

**Implementation:**
```javascript
// frontend/src/app/api/validate/route.js
export const runtime = 'edge';  // Use Edge runtime

export async function POST(request) {
  // Your logic
}
```

### Caching

**API Response Caching:**
```javascript
export async function GET(request) {
  return NextResponse.json(data, {
    headers: {
      'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=120'
    }
  });
}
```

### Bundle Size

**Check bundle size:**
```bash
cd frontend
npm run build
# Review output for bundle sizes
```

**Optimize:**
- Use dynamic imports for large components
- Remove unused dependencies
- Enable compression

## Security

### Environment Variables

**Never commit:**
- API keys
- Secrets
- Passwords
- Private tokens

**Always use:**
- Vercel environment variables
- `.env.local` (gitignored)
- Secret management

### API Route Security

**Rate Limiting:**
```javascript
import { Ratelimit } from '@upstash/ratelimit';

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s')
});

export async function POST(request) {
  const ip = request.ip ?? '127.0.0.1';
  const { success } = await ratelimit.limit(ip);

  if (!success) {
    return NextResponse.json(
      { error: 'Too many requests' },
      { status: 429 }
    );
  }

  // Process request
}
```

**Input Validation:**
```javascript
export async function POST(request) {
  const { text, document_type } = await request.json();

  if (!text || typeof text !== 'string') {
    return NextResponse.json(
      { error: 'Invalid text' },
      { status: 400 }
    );
  }

  if (!['financial', 'privacy', 'tax', 'nda', 'employment'].includes(document_type)) {
    return NextResponse.json(
      { error: 'Invalid document_type' },
      { status: 400 }
    );
  }

  // Process valid request
}
```

## Rollback Procedures

### Reverting to Previous Deployment

**Via Vercel Dashboard:**
1. Go to Deployments
2. Find previous working deployment
3. Click "..." menu
4. Select "Promote to Production"

**Via Git:**
```bash
# Revert last commit
git revert HEAD
git push

# Revert to specific commit
git revert <commit-hash>
git push

# Hard reset (use carefully!)
git reset --hard <commit-hash>
git push --force
```

### Emergency Rollback

```bash
# Find last good commit
git log --oneline -10

# Create revert commit
git revert <bad-commit-hash>

# Push immediately
git push origin main
```

## CI/CD Pipeline

### GitHub Actions (Optional)

**File:** `.github/workflows/deploy.yml`

```yaml
name: Deploy to Vercel
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd frontend
          npm install
      - name: Run tests
        run: |
          cd frontend
          npm test
      - name: Build
        run: |
          cd frontend
          npm run build
```

## Deployment Commands Reference

```bash
# Git operations
git status                                    # Check status
git add .                                     # Stage all changes
git commit -m "Message"                       # Commit changes
git push -u origin branch-name                # Push to remote
git branch                                    # List branches
git checkout -b new-branch                    # Create new branch

# Vercel CLI
vercel                                        # Deploy to preview
vercel --prod                                 # Deploy to production
vercel ls                                     # List deployments
vercel logs [url]                             # View logs
vercel env pull                               # Pull env variables
vercel env add                                # Add env variable

# Local development
npm run dev                                   # Start dev servers
npm run build                                 # Build for production
npm test                                      # Run tests

# Debugging
curl [url]/api/health                         # Test API health
curl -X POST [url]/api/validate -d '...'      # Test validation
vercel logs --follow                          # Watch logs
```

## Best Practices

1. **Always use feature branches** - Never commit directly to main
2. **Test locally first** - Verify changes work before pushing
3. **Include session ID** - Required for branch push authentication
4. **Write clear commit messages** - Include what, why, and Claude attribution
5. **Check Vercel logs** - Review deployment logs for errors
6. **Use environment variables** - Never hardcode secrets
7. **Monitor performance** - Check bundle sizes and response times
8. **Implement error handling** - Gracefully handle API errors
9. **Version dependencies** - Keep package.json up to date
10. **Document changes** - Update README for significant features

## When to Use This Skill

Activate this skill when:
- Deploying LOKI to Vercel
- Managing Git branches and commits
- Configuring deployment settings
- Debugging deployment issues
- Setting up CI/CD pipelines
- Managing environment variables
- Monitoring production deployments
- Implementing rollback procedures
- Optimizing deployment performance
- Setting up new deployment environments
