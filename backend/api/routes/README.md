# API Routes Integration Guide

## Adding correction_v2 Routes to Main API

To integrate the new correction v2 endpoints into your FastAPI application, add the following to `/home/user/loki-interceptor/backend/api/main.py`:

### Step 1: Import the Router

Add this import at the top of `main.py`:

```python
from .routes import validation, correction, correction_v2, history, modules, stats, websocket
```

### Step 2: Include the Router

Add this after the existing router includes:

```python
# Include v2 correction router
app.include_router(
    correction_v2.router,
    prefix="/api/v2",
    tags=["Correction V2"]
)
```

### Complete Example

```python
# ... existing imports ...
from .routes import validation, correction, correction_v2, history, modules, stats, websocket

# ... existing code ...

# Include routers
app.include_router(
    validation.router,
    prefix="/api/v1",
    tags=["Validation"]
)

app.include_router(
    correction.router,
    prefix="/api/v1",
    tags=["Correction"]
)

# NEW: Add V2 Correction Router
app.include_router(
    correction_v2.router,
    prefix="/api/v2",
    tags=["Correction V2"]
)

app.include_router(
    history.router,
    prefix="/api/v1",
    tags=["History"]
)

# ... rest of routers ...
```

## Available Endpoints

After integration, the following endpoints will be available:

### Advanced Correction
- `POST /api/v2/correct/advanced` - Advanced correction with full pipeline control

### Batch Processing
- `POST /api/v2/correct/batch` - Submit batch correction job
- `GET /api/v2/correct/batch/{batch_id}` - Get batch status

### Async Scheduling
- `POST /api/v2/correct/schedule` - Schedule async correction job
- `GET /api/v2/correct/jobs/{job_id}` - Get job status

### Streaming
- `WS /api/v2/correct/stream` - WebSocket streaming corrections

### Export
- `GET /api/v2/correct/export/{job_id}` - Export result in various formats

### Utilities
- `GET /api/v2/correct/quota` - Get quota information
- `POST /api/v2/correct/webhook/test` - Test webhook
- `GET /api/v2/correct/versions` - Get algorithm versions

## Testing the Integration

```bash
# Start the API server
cd /home/user/loki-interceptor/backend/api
uvicorn main:app --reload --port 8000

# Access Swagger documentation
open http://localhost:8000/api/docs

# Test advanced correction endpoint
curl -X POST http://localhost:8000/api/v2/correct/advanced \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Test document with compliance issues.",
    "export_format": "json",
    "auto_apply": true
  }'
```

## Monitoring Dashboard Integration

To add monitoring endpoints, create a new monitoring router:

```python
# backend/api/routes/monitoring.py
from fastapi import APIRouter
from ...monitoring.correction_dashboard import get_dashboard

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_data():
    dashboard = get_dashboard()
    return await dashboard.get_dashboard_data()

@router.get("/performance")
async def get_performance_report(hours: int = 24):
    dashboard = get_dashboard()
    return await dashboard.get_performance_report(hours)
```

Then include it in `main.py`:

```python
from .routes import monitoring

app.include_router(
    monitoring.router,
    prefix="/api/v2/monitoring",
    tags=["Monitoring"]
)
```
