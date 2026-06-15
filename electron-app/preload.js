// Preload script — 安全的 IPC 桥
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('bydfiAudit', {
  readSettings: () => ipcRenderer.invoke('settings:read'),
  writeSettings: (payload) => ipcRenderer.invoke('settings:write', payload),
  restartBackend: () => ipcRenderer.invoke('app:restart-backend'),
  openSettings: () => ipcRenderer.invoke('app:open-settings'),
  openDeliverables: () => ipcRenderer.invoke('app:open-deliverables'),
});
