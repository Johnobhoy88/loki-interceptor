# 🚀 LOKI Interceptor - Vercel Deployment Guide

## ⚠️ Important: Hybrid Deployment Architecture

**Vercel Limitation**: Vercel's Python runtime has a 50MB size limit and limited serverless execution time. The full LOKI backend (~200MB with all dependencies) **cannot** run on Vercel.

**Solution**: Deploy frontend on Vercel, backend elsewhere.

---

## 🏗️ Deployment Architecture

```
┌─────────────────────────────────────────────┐
│           Vercel (Frontend + Demo API)      │
│  - React 18 + TypeScript UI                 │
│  - Static assets                            │
│  - Lightweight demo API (/api/*)            │
└─────────────┬───────────────────────────────┘
              │
              │ API Calls
              ▼
┌─────────────────────────────────────────────┐
│     Backend (Railway/Render/AWS/etc.)       │
│  - Full FastAPI backend                     │
│  - 507 compliance gates                     │
│  - Database (PostgreSQL)                    │
│  - Redis cache                              │
│  - All Python dependencies                  │
└─────────────────────────────────────────────┘
```

---

## 📋 Quick Deployment Options

### **Option 1: Vercel Frontend + Railway Backend** (Recommended)

**Best for**: Production deployments, full features

#### Step 1: Deploy Backend to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy backend
railway up

# Get your backend URL
railway domain
# Example: https://loki-backend-production.up.railway.app
```

#### Step 2: Deploy Frontend to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Set environment variable
vercel env add BACKEND_API_URL
# Enter your Railway URL from Step 1

# Deploy to production
vercel --prod
```

---

### **Option 2: Vercel Frontend + Render Backend**

#### Step 1: Deploy Backend to Render

1. Go to [render.com](https://render.com)
2. Connect your GitHub repo
3. Create new **Web Service**
4. Configure:
   - **Environment**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.api.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Starter ($7/month) or Free

5. Add environment variables:
   - `ANTHROPIC_API_KEY`
   - `DATABASE_URL` (if using PostgreSQL)
   - `REDIS_URL` (if using Redis)

6. Deploy and get URL: `https://loki-backend.onrender.com`

#### Step 2: Deploy Frontend to Vercel

Same as Option 1, Step 2.

---

### **Option 3: All-in-One Docker Deployment**

Deploy the entire stack together using Docker:

**Platforms**: AWS ECS, Google Cloud Run, DigitalOcean App Platform, Fly.io

```bash
# Build and deploy with docker-compose
docker-compose -f docker-compose.yml up -d

# Or build individual containers
docker build -t loki-backend -f backend/Dockerfile .
docker build -t loki-frontend -f frontend/Dockerfile .
```

See `DEPLOYMENT_GUIDE.md` for detailed Docker instructions.

---

## 🔧 Vercel Configuration

### 1. Environment Variables

Set these in Vercel dashboard:

```bash
# Required
BACKEND_API_URL=https://your-backend-url.com

# Optional (if backend needs them)
ANTHROPIC_API_KEY=your_key_here
NODE_ENV=production
```

### 2. Build Settings

**Framework Preset**: Other
**Build Command**: `cd frontend && npm install && npm run build`
**Output Directory**: `frontend/dist`
**Install Command**: `npm install`

### 3. Root Directory

Leave as `/` (root)

---

## 📦 What Runs on Vercel?

### ✅ Deployed to Vercel:
- React frontend (static files)
- Demo API endpoints:
  - `GET /` - API info
  - `GET /health` - Health check
  - `GET /api/v1/modules` - Module list
  - `GET /api/v1/stats` - Platform stats
  - `POST /api/v1/validate` - Demo/proxy endpoint

### ❌ NOT on Vercel (too large):
- Full FastAPI backend
- Database (PostgreSQL)
- Redis cache
- Celery workers
- Heavy Python dependencies (SQLAlchemy, etc.)
- Claude AI integration (requires long-running processes)

---

## 🚀 Step-by-Step Deployment

### Prerequisites

- GitHub account
- Vercel account (free)
- Railway/Render account (for backend)

### 1. Prepare Repository

```bash
# Ensure you have the latest code
git pull origin claude/multi-agent-deployment-011CV2gmxXPjiQ9goRPJgJko

# Verify files exist
ls api/index.py
ls requirements-vercel.txt
ls vercel.json
```

### 2. Deploy Backend (Railway Example)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Add environment variables
railway variables set ANTHROPIC_API_KEY=your_key_here

# Deploy
railway up

# Get URL
railway domain
# Copy this URL: https://loki-backend-production-xxxx.up.railway.app
```

### 3. Deploy Frontend (Vercel)

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy to preview
vercel

# Add environment variable
vercel env add BACKEND_API_URL production
# Paste your Railway URL from step 2

# Deploy to production
vercel --prod

# Your app is live! 🎉
# Example: https://loki-interceptor.vercel.app
```

### 4. Update Frontend API Client

Edit `frontend/src/services/api-client.ts`:

```typescript
const API_BASE_URL = process.env.VITE_BACKEND_API_URL ||
                     import.meta.env.VITE_BACKEND_API_URL ||
                     'https://your-railway-url.up.railway.app';
```

Rebuild and redeploy:
```bash
vercel --prod
```

---

## 🔍 Testing Deployment

### Test Demo API (Vercel)

```bash
# Health check
curl https://your-app.vercel.app/health

# Get modules
curl https://your-app.vercel.app/api/v1/modules

# Get stats
curl https://your-app.vercel.app/api/v1/stats
```

### Test Full Backend (Railway/Render)

```bash
# Health check
curl https://your-backend.up.railway.app/api/health

# Validate document (requires API key)
curl -X POST https://your-backend.up.railway.app/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Test document",
    "document_type": "financial",
    "modules": ["fca_uk"]
  }'
```

---

## 💰 Cost Estimates

### Vercel (Frontend)
- **Hobby Plan**: $0/month (Free)
  - 100GB bandwidth
  - Unlimited requests
  - Perfect for frontend

### Railway (Backend)
- **Starter Plan**: $5/month
  - 512MB RAM, 1 vCPU
  - Good for demo/development
- **Pro Plan**: $20+/month
  - Scalable resources
  - Recommended for production

### Render (Alternative Backend)
- **Free Plan**: $0/month
  - Spins down after inactivity
  - Good for demo
- **Starter Plan**: $7/month
  - Always on
  - 512MB RAM

### Total Cost (Production)
- **Vercel (Free) + Railway ($5)** = $5/month minimum
- **Vercel (Free) + Railway Pro ($20)** = $20/month recommended

---

## 🐛 Troubleshooting

### Issue: "Module not found" on Vercel

**Solution**: You're trying to import backend modules that don't exist on Vercel.

The `api/index.py` should be lightweight (already fixed in this guide).

### Issue: "Function exceeded timeout"

**Solution**: Vercel functions timeout after 10 seconds (Hobby) or 60 seconds (Pro).

Backend should handle long-running tasks, not Vercel.

### Issue: "Bundle too large"

**Solution**: Use `requirements-vercel.txt` (minimal dependencies) instead of `requirements.txt`.

```bash
# In vercel.json, ensure it uses the right file
# This is already configured correctly
```

### Issue: CORS errors

**Solution**: Add your Vercel URL to backend CORS settings:

```python
# In backend/api/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app.vercel.app",  # Add this
        "https://*.vercel.app",          # And this
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📚 Additional Resources

- [Vercel Python Runtime Docs](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Railway Deployment Docs](https://docs.railway.app/deploy/deployments)
- [Render Deployment Guide](https://render.com/docs/deploy-fastapi)
- [LOKI Full Deployment Guide](./DEPLOYMENT_GUIDE.md)

---

## ✅ Deployment Checklist

### Before Deployment

- [ ] Backend deployed to Railway/Render/AWS
- [ ] Backend URL obtained
- [ ] Environment variables configured
- [ ] Database provisioned (if needed)
- [ ] Redis provisioned (if needed)
- [ ] API keys secured

### Vercel Deployment

- [ ] `vercel.json` configured
- [ ] `requirements-vercel.txt` uses minimal dependencies
- [ ] `api/index.py` is lightweight
- [ ] Frontend build works locally (`npm run build`)
- [ ] Environment variables set in Vercel dashboard
- [ ] Custom domain configured (optional)

### Post-Deployment

- [ ] Test demo API endpoints
- [ ] Test full backend endpoints
- [ ] Verify frontend loads
- [ ] Check API connectivity
- [ ] Monitor logs for errors
- [ ] Set up monitoring/alerts

---

## 🎉 Success!

Your LOKI Interceptor PLATINUM Edition is now deployed!

- **Frontend**: `https://your-app.vercel.app`
- **Backend**: `https://your-backend.up.railway.app`
- **Status**: Production Ready ✅

---

**Questions?** Check `DEPLOYMENT_GUIDE.md` or open an issue on GitHub.

**🛡️ LOKI Interceptor PLATINUM Edition**
**Professional Compliance, Intelligent Protection**
