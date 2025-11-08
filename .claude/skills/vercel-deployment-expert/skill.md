# Vercel Deployment Expert Skill

## Overview
Complete expertise in Vercel serverless platform deployment, configuration, monitoring, and troubleshooting. Specialized in Python Flask applications like LOKI.

## Core Knowledge Areas

### 1. Vercel Platform Architecture

**Serverless Functions:**
- Python runtime (3.9, 3.11, 3.12)
- Function limits: 10s timeout (Hobby), 60s (Pro)
- Memory limits: 1024MB (Hobby), 3008MB (Pro)
- Cold start optimization
- Function regions and edge network

**Build System:**
- Build time limits: 45 minutes
- Build cache optimization
- Custom build commands
- Environment variable injection
- Dependency caching

**Routing & Networking:**
- Edge Network (global CDN)
- Route configuration (vercel.json)
- Rewrites and redirects
- Headers and CORS
- Static file serving

### 2. LOKI-Specific Deployment

**Application Structure:**
```
LOKI_EXPERIMENTAL_V2/
├── api/
│   └── index.py           # WSGI entry point for Vercel
├── backend/
│   ├── server.py          # Flask application
│   ├── core/              # Core engines
│   └── modules/           # Compliance modules
├── frontend/              # Static HTML/CSS/JS
├── vercel.json           # Vercel configuration
└── requirements.txt      # Python dependencies
```

**Deployment Flow:**
1. Git push to GitHub main branch
2. Vercel detects push via webhook
3. Vercel clones repository
4. Installs Python dependencies (requirements.txt)
5. Builds function from api/index.py
6. Deploys to edge network
7. Updates production URL

**Critical Files:**

`api/index.py` - WSGI wrapper:
```python
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ROOT_DIR, '..'))
sys.path.append(PROJECT_ROOT)

BACKEND_DIR = os.path.join(PROJECT_ROOT, 'backend')
sys.path.append(BACKEND_DIR)

from backend.server import app as flask_app

# Expose WSGI callable for Vercel
app = flask_app
```

`vercel.json` - Configuration:
```json
{
  "version": 2,
  "routes": [
    { "src": "/api/(.*)", "dest": "/api/index.py" },
    { "src": "/(.*)\\.(css|js|png|jpg|svg|ico|txt|map)", "dest": "/frontend/$1.$2" },
    { "src": "/(.*)", "dest": "/api/index.py" }
  ]
}
```

### 3. Common Deployment Issues

**Issue 1: Module Import Errors**
```
ModuleNotFoundError: No module named 'modules.xxx'
```
**Cause:** Missing `__init__.py` or `module.py` files
**Fix:** Ensure all package directories have `__init__.py` and LOKI modules have `module.py`

**Issue 2: Build Timeout**
```
Build exceeded maximum duration
```
**Cause:** Too many dependencies or large files
**Fix:** Optimize requirements.txt, use .vercelignore, consider Vercel Pro

**Issue 3: Function Timeout**
```
Task timed out after 10.00 seconds
```
**Cause:** Long-running operation in serverless function
**Fix:** Optimize code, add caching, increase timeout (Pro plan), or use background jobs

**Issue 4: Cold Start Latency**
```
First request takes 3-5 seconds
```
**Cause:** Python interpreter startup and module imports
**Fix:** Minimize imports, lazy load heavy modules, implement warming

**Issue 5: Memory Limit**
```
Function exceeded memory limit
```
**Cause:** Loading large data in memory
**Fix:** Stream responses, use pagination, optimize data structures

### 4. Optimization Strategies

**Build Optimization:**
1. **Minimize dependencies** - Only include what's needed
2. **Use .vercelignore** - Exclude unnecessary files
3. **Cache dependencies** - Vercel caches node_modules and pip packages
4. **Parallel builds** - Vercel builds functions in parallel

**Runtime Optimization:**
1. **Module-level imports** - Import at top, not in functions
2. **Lazy loading** - Import heavy modules only when needed
3. **Connection pooling** - Reuse database connections
4. **Response caching** - Cache expensive operations
5. **Edge caching** - Use CDN for static content

**Cold Start Optimization:**
1. **Minimize dependencies** - Fewer imports = faster start
2. **Precompute data** - Generate at build time if possible
3. **Warm functions** - Ping function every 5 minutes
4. **Use global scope** - Initialize once outside handler

**Cost Optimization:**
1. **Function duration** - Optimize code to run faster
2. **Caching** - Reduce function invocations
3. **Static files** - Serve from CDN not function
4. **Right-sizing** - Use appropriate memory/timeout limits

### 5. Configuration Best Practices

**vercel.json Advanced Configuration:**
```json
{
  "version": 2,
  "name": "loki-interceptor",
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "maxDuration": 30,
        "memory": 1024,
        "runtime": "python3.9"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/health",
      "dest": "/api/index.py",
      "headers": {
        "Cache-Control": "no-cache"
      }
    },
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    },
    {
      "src": "/static/(.*)",
      "dest": "/frontend/$1",
      "headers": {
        "Cache-Control": "public, max-age=31536000, immutable"
      }
    }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "SAMEORIGIN"
        },
        {
          "key": "Strict-Transport-Security",
          "value": "max-age=31536000"
        }
      ]
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.9"
  },
  "regions": ["iad1"]
}
```

**Environment Variables:**
- Always use environment variables for secrets
- Set in Vercel dashboard or vercel CLI
- Never commit .env files
- Use different values for preview/production

**Security Headers:**
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-DNS-Prefetch-Control", "value": "on" },
        { "key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains; preload" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" },
        { "key": "X-Frame-Options", "value": "SAMEORIGIN" },
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "Referrer-Policy", "value": "origin-when-cross-origin" }
      ]
    }
  ]
}
```

### 6. Monitoring & Debugging

**Using Vercel MCP Server:**
```python
# Get latest deployment
deployments = get_deployments(project_id="loki-interceptor", limit=1)

# Get deployment logs
logs = get_deployment_logs(deployment_id="dpl_xxx")

# Get runtime logs
runtime_logs = get_deployment_logs(
    deployment_id="dpl_xxx",
    follow=True,
    since=1234567890
)
```

**Key Metrics to Monitor:**
1. Deployment frequency and duration
2. Function execution time (p50, p95, p99)
3. Error rate (4xx, 5xx)
4. Cold start frequency and duration
5. Memory usage
6. Cache hit rate
7. Build time

**Log Analysis Patterns:**
- `ERROR` - Critical failures
- `WARNING` - Potential issues
- `ModuleNotFoundError` - Import problems
- `Task timed out` - Timeout issues
- `Memory limit exceeded` - Memory problems

### 7. Deployment Strategies

**Preview Deployments:**
- Automatic on PR creation
- Unique URL per PR
- Test changes before merging
- Share with stakeholders

**Production Deployments:**
- Automatic on main branch push
- Can configure custom branch
- Use deployment protection (manual approve)
- Immediate rollback available

**Rollback Strategy:**
1. Identify last known good deployment
2. Use Vercel dashboard to promote deployment
3. Or redeploy previous git commit
4. Monitor after rollback
5. Fix issue and redeploy

**Blue-Green Deployment:**
1. Deploy to preview (green)
2. Test thoroughly
3. Promote to production
4. Keep previous version (blue) for rollback

### 8. Troubleshooting Checklist

**Deployment Failed:**
- [ ] Check build logs for errors
- [ ] Verify requirements.txt is correct
- [ ] Check for syntax errors
- [ ] Verify all imports are correct
- [ ] Check file sizes (<50MB per function)
- [ ] Verify vercel.json is valid JSON

**Function Errors:**
- [ ] Check runtime logs
- [ ] Verify environment variables
- [ ] Check for module import errors
- [ ] Verify database connection
- [ ] Check API rate limits
- [ ] Test locally first

**Performance Issues:**
- [ ] Check function execution time
- [ ] Identify slow operations
- [ ] Add caching where appropriate
- [ ] Optimize database queries
- [ ] Consider increasing memory/timeout
- [ ] Profile code to find bottlenecks

**Module Loading Issues:**
- [ ] Verify __init__.py in all packages
- [ ] Check module.py exists for LOKI modules
- [ ] Verify import paths match directory structure
- [ ] Check for circular imports
- [ ] Test imports locally

### 9. LOKI Module Loading

**Expected Module Structure:**
```
backend/modules/{module_name}/
├── __init__.py              # Makes it a package
├── module.py                # Module loader (required by engine)
└── gates/
    ├── __init__.py          # Makes gates a package
    └── gate_name.py         # Individual gate implementations
```

**module.py Template:**
```python
from .gates.gate1 import Gate1
from .gates.gate2 import Gate2

class ModuleNameModule:
    def __init__(self):
        self.name = "Module Name"
        self.version = "1.0.0"
        self.gates = {
            'gate1': Gate1(),
            'gate2': Gate2(),
        }

    def execute(self, text, document_type):
        results = {'module': self.name, 'gates': {}}
        for gate_name, gate in self.gates.items():
            try:
                results['gates'][gate_name] = gate.check(text, document_type)
            except Exception as e:
                results['gates'][gate_name] = {
                    'status': 'ERROR',
                    'message': str(e)
                }
        return results
```

**Engine Loading (server.py):**
```python
engine = AsyncLOKIEngine(max_workers=4)

# Load with error handling
modules_to_load = ['hr_scottish', 'gdpr_uk', 'uk_employment']
for module_name in modules_to_load:
    try:
        engine.load_module(module_name)
        print(f"✓ Loaded: {module_name}")
    except Exception as e:
        print(f"⚠ Failed to load {module_name}: {e}")
```

### 10. Quick Reference

**Vercel CLI Commands:**
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod

# View logs
vercel logs

# List deployments
vercel ls

# Promote deployment to production
vercel promote <deployment-url>

# Set environment variable
vercel env add API_KEY

# Pull environment variables
vercel env pull .env.local
```

**Useful Vercel URLs:**
- Dashboard: https://vercel.com/dashboard
- Deployments: https://vercel.com/{team}/{project}/deployments
- Settings: https://vercel.com/{team}/{project}/settings
- Logs: https://vercel.com/{team}/{project}/{deployment}/logs

**Common Fix Patterns:**
1. **Module not found** → Add `__init__.py` and `module.py`
2. **Build timeout** → Optimize requirements.txt
3. **Function timeout** → Add caching or increase limit
4. **Cold start slow** → Minimize imports
5. **Memory exceeded** → Optimize data structures
6. **CORS error** → Update CORS config in server.py

---

**Master these concepts to deploy and manage LOKI efficiently on Vercel.**
