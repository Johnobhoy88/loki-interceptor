const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  saveApiKey: (provider, key) => ipcRenderer.invoke('save-api-key', provider, key),
  getApiKey: (provider) => ipcRenderer.invoke('get-api-key', provider),
  getBackendStatus: () => ipcRenderer.invoke('get-backend-status'),

  // Backend API calls
  proxyRequest: async (endpoint, data, apiKey) => {
    try {
      const response = await fetch(`http://127.0.0.1:5002${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': apiKey
        },
        body: JSON.stringify(data)
      });
      const json = await response.json();
      return json;
    } catch (err) {
      return { error: err.message };
    }
  },

  getModules: async () => {
    try {
      const response = await fetch('http://127.0.0.1:5002/modules');
      return await response.json();
    } catch (err) {
      return { error: err.message };
    }
  }
});
