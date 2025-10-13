const { app, BrowserWindow, ipcMain, Menu } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const Store = require('electron-store');

const store = new Store({ encryptionKey: 'loki-interceptor-key' });

let mainWindow;
let pythonProcess;

function resolvePythonPath() {
  const venvPath = process.platform === 'win32'
    ? path.join(__dirname, '../backend/venv/Scripts/python.exe')
    : path.join(__dirname, '../backend/venv/bin/python');
  if (fs.existsSync(venvPath)) return venvPath;
  // fallbacks
  return process.platform === 'win32' ? 'python' : 'python3';
}

async function isBackendOnline() {
  try {
    const controller = new AbortController();
    const t = setTimeout(() => controller.abort(), 1000);
    const res = await fetch('http://127.0.0.1:5002/health', { signal: controller.signal });
    clearTimeout(t);
    return res.ok;
  } catch (e) {
    return false;
  }
}

async function startPythonBackend() {
  // Skip starting if backend already online
  if (await isBackendOnline()) {
    console.log('Backend already running on port 5002');
    return;
  }

  // Check if we're in development or production
  const isDev = !app.isPackaged;

  if (isDev) {
    const pythonPath = resolvePythonPath();
    const scriptPath = path.join(__dirname, '../backend/server.py');
    pythonProcess = spawn(pythonPath, [scriptPath], { stdio: ['ignore', 'pipe', 'pipe'] });
  } else {
    const backendPath = path.join(process.resourcesPath, 'loki_backend.exe');
    pythonProcess = spawn(backendPath, [], { stdio: ['ignore', 'pipe', 'pipe'] });
  }

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Backend Error: ${data}`);
  });

  pythonProcess.on('exit', (code, signal) => {
    console.log(`Backend exited with code ${code} signal ${signal}`);
  });

  setTimeout(() => {
    console.log('Backend started on port 5002');
  }, 3000);
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      cache: false  // Disable cache for development
    },
    title: 'LOKI Interceptor EXPERIMENTAL V2',
    backgroundColor: '#1a1a2e'
  });

  mainWindow.loadFile(path.join(__dirname, '../frontend/index.html'));

  // Clear cache on load
  mainWindow.webContents.session.clearCache();

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// IPC handlers for config management
ipcMain.handle('save-api-key', async (event, provider, key) => {
  store.set(`api_keys.${provider}`, key);
  return { success: true };
});

ipcMain.handle('get-api-key', async (event, provider) => {
  return store.get(`api_keys.${provider}`, '');
});

ipcMain.handle('get-backend-status', async () => {
  try {
    const response = await fetch('http://127.0.0.1:5002/health');
    const data = await response.json();
    return { online: true, ...data };
  } catch (error) {
    return { online: false, error: error.message };
  }
});

app.whenReady().then(() => {
  // Set explicit Edit menu with clipboard roles before creating window
  try {
    const isMac = process.platform === 'darwin';
    const template = [
      ...(isMac ? [{ role: 'appMenu' }] : []),
      {
        label: 'Edit',
        submenu: [
          { role: 'undo' },
          { role: 'redo' },
          { type: 'separator' },
          { role: 'cut' },
          { role: 'copy' },
          { role: 'paste' },
          { role: 'pasteAndMatchStyle' },
          { role: 'delete' },
          { role: 'selectAll' },
        ],
      },
      { role: 'viewMenu' },
    ];
    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
  } catch (e) {
    console.warn('Failed to set application menu:', e);
  }

  startPythonBackend();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (pythonProcess) {
    try { pythonProcess.kill(); } catch {}
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Add right-click context menu with clipboard actions for text inputs
app.on('browser-window-created', (_event, win) => {
  win.webContents.on('context-menu', (event, params) => {
    const { editFlags } = params;
    const menu = Menu.buildFromTemplate([
      { role: 'cut', enabled: editFlags.canCut },
      { role: 'copy', enabled: editFlags.canCopy },
      { role: 'paste', enabled: editFlags.canPaste },
      { type: 'separator' },
      { role: 'selectAll' },
    ]);
    menu.popup({ window: win });
  });
});

app.on('before-quit', () => {
  if (pythonProcess) {
    try { pythonProcess.kill(); } catch {}
  }
});
