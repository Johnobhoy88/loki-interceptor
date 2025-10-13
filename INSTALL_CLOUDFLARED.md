# Installing Cloudflared for LOKI Experimental V2

To enable Cloudflare tunneling, you need to download `cloudflared.exe` and place it in the project root.

## Quick Install Steps

### 1. Download Cloudflared
Go to: https://github.com/cloudflare/cloudflared/releases

### 2. Find Windows Version
Look for the latest release and download:
```
cloudflared-windows-amd64.exe
```

Direct link (latest): https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe

### 3. Rename the File
Rename `cloudflared-windows-amd64.exe` to:
```
cloudflared.exe
```

### 4. Place in Project Root
Move `cloudflared.exe` to:
```
C:\Users\jpmcm.DESKTOP-CQ0CL93\OneDrive\Desktop\HighlandAI\LOKI_EXPERIMENTAL_V2\
```

The file should be in the same directory as:
- launch_experimental.bat
- launch_experimental_cloudflare.bat
- TEST_DOCUMENTS.md

### 5. Verify Installation
Open Command Prompt in the project directory and run:
```
cloudflared.exe --version
```

You should see output like:
```
cloudflared version 2024.10.0 (built 2024-10-01-1234 UTC)
```

## File Structure After Installation

```
LOKI_EXPERIMENTAL_V2/
├── backend/
├── electron/
├── frontend/
├── cloudflared.exe          ← Place here
├── launch_experimental.bat
├── launch_experimental_cloudflare.bat
├── TEST_DOCUMENTS.md
└── LAUNCHER_GUIDE.md
```

## Testing

1. Double-click `launch_experimental_cloudflare.bat`
2. A Cloudflare window will open showing a URL like:
   ```
   https://abc-def-ghi.trycloudflare.com
   ```
3. Copy that URL and test it in a browser
4. The LOKI interface should load

## Troubleshooting

### "cloudflared.exe not found"
- Make sure the file is named exactly `cloudflared.exe` (not cloudflared-windows-amd64.exe)
- Make sure it's in the root directory of LOKI_EXPERIMENTAL_V2

### Tunnel fails to start
- Check if port 5002 is already in use:
  ```
  netstat -ano | findstr :5002
  ```
- Kill any processes using port 5002:
  ```
  taskkill /F /PID [process_id]
  ```

### "This app has been blocked by your administrator"
- Right-click cloudflared.exe → Properties → Unblock
- Or run as administrator

### Tunnel works but website won't load
- Make sure backend is running (check for "Running on http://127.0.0.1:5002")
- Wait 10-15 seconds after tunnel starts for DNS propagation
- Try accessing the tunnel URL from a different device/network

## Alternative: Using NPX (No Download Required)

If you don't want to download cloudflared.exe, you can use npx:

Edit `launch_experimental_cloudflare.bat` line 30 to:
```batch
start "Cloudflare Tunnel" cmd /k "npx cloudflared tunnel --url http://localhost:5002"
```

This will download cloudflared on first run (slower, but no manual download needed).

## Security Notes

- Cloudflare tunnel URLs are publicly accessible
- Use only for demos/testing, not production
- URLs expire when tunnel closes
- New URL generated each launch (no hardcoded URLs)
- No account/login required for quick tunnels

## File Size

cloudflared.exe is approximately 50-60 MB. If you're committing to git, consider adding to .gitignore:

```
# .gitignore
cloudflared.exe
```

But for easy distribution, you may want to include it in the repo.
