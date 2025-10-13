# LOKI Experimental V2 - Launcher Guide

## Available Launchers

### 1. Local Development (Recommended for testing)
**File:** `launch_experimental.bat`

**Use when:**
- Working locally on your machine
- Testing new features
- Development work

**Access:**
- Local only: http://localhost:5002
- Fast startup
- No internet required

**How to launch:**
```
Double-click: launch_experimental.bat
```

---

### 2. Cloudflare Public Access
**File:** `launch_experimental_cloudflare.bat`

**Use when:**
- Need to share with remote users
- Accessing from other devices
- Demo presentations
- Client testing

**Access:**
- Local: http://localhost:5002
- Public: https://xxxxx.trycloudflare.com (changes each launch)

**How to launch:**
```
Double-click: launch_experimental_cloudflare.bat
```

**Important:**
1. Cloudflare window will open showing a unique URL
2. Copy the URL (ends with .trycloudflare.com)
3. Share that URL with remote users
4. URL changes every time you restart the tunnel

**Example Cloudflare output:**
```
2025-10-13T10:30:00Z INF +--------------------------------------------------------------------------------------------+
2025-10-13T10:30:00Z INF |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
2025-10-13T10:30:00Z INF |  https://abc-def-ghi-jkl.trycloudflare.com                                                |
2025-10-13T10:30:00Z INF +--------------------------------------------------------------------------------------------+
```

Copy: `https://abc-def-ghi-jkl.trycloudflare.com`

---

## Troubleshooting

### Cloudflare not installed?
Download from: https://github.com/cloudflare/cloudflared/releases

Install to project root or add to PATH

### Port already in use?
Stop other LOKI instances:
```
taskkill /F /IM python.exe
```

### Backend not starting?
Check Python is installed:
```
python --version
```

### Electron not launching?
Install dependencies:
```
cd electron
npm install
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│  LOKI EXPERIMENTAL V2                   │
├─────────────────────────────────────────┤
│                                         │
│  Backend: http://localhost:5002         │
│  ├─ Flask API                           │
│  ├─ 5 Compliance Modules                │
│  └─ Document Validation Engine          │
│                                         │
│  Frontend: Electron App                 │
│  ├─ Document Validator                  │
│  ├─ Prompt Interceptor                  │
│  ├─ Analytics Dashboard                 │
│  └─ Module Configuration                │
│                                         │
│  Cloudflare Tunnel (optional)           │
│  └─ Public HTTPS access                 │
│                                         │
└─────────────────────────────────────────┘
```

---

## Demo Build (Port 5001)

The original demo build runs on port 5001:
- Location: `LOKI_INTERCEPTOR_CLAUDEV1`
- Launcher: `launch_loki.bat`
- Port: 5001

Both can run simultaneously without conflicts.

---

## Module Status

All modules loaded and operational:

1. **FCA UK Compliance** - 25 gates (Financial promotions, Consumer Duty)
2. **GDPR UK Compliance** - 15 gates (Data protection, Privacy)
3. **UK/EU NDA Compliance** - 14 gates (Confidentiality agreements)
4. **UK Tax Compliance** - 15 gates (IR35, PAYE, Tax structures)
5. **HR Scottish Compliance** - 16 gates (Employment law, Working time)

Total: **85 compliance gates**

---

## Test Documents

Sample test documents available in: `TEST_DOCUMENTS.md`

Each module has:
- Full test document (triggers CRITICAL findings)
- Quick test sample (triggers LOW-MEDIUM findings)

Copy/paste into Document Validator to test.
