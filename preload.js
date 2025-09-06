
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  dbInitialize: () => ipcRenderer.invoke('db:initialize'),
  dbConnect: () => ipcRenderer.invoke('db:connect'),
  dbGetStatus: () => ipcRenderer.invoke('db:getStatus'),
  dbQuery: (sql, params) => ipcRenderer.invoke('db:query', sql, params),
  searchBooks: (query) => ipcRenderer.invoke('db:searchBooks', query),
  getGoogleConfig: () => ipcRenderer.invoke('getGoogleConfig'),
  updateDatabase: (buffer) => ipcRenderer.invoke('updateDatabase', buffer)
});
