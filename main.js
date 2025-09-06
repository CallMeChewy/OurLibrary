
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const sqlite3 = require('sqlite3');
const fs = require('fs');

let db;

function createWindow () {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    }
  });

  // Start with registration page by default
  win.loadFile('index.html');
}

app.whenReady().then(() => {
  // Read the config file to find the database path
  const configPath = path.join(__dirname, 'Config', 'ourlibrary_config.json');
  const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  const dbPath = path.join(__dirname, config.local_database_path);

  db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
      console.error('Error opening database', err.message);
    } else {
      console.log('Connected to the OurLibrary database.');
    }
  });

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    db.close();
    app.quit();
  }
});

ipcMain.handle('db:initialize', async () => {
  // This is a placeholder, as the database is already initialized when the app starts.
  return { ok: !!db, mode: 'desktop' };
});

ipcMain.handle('db:connect', async () => {
  // This is a placeholder, as the database is already connected.
  return { ok: !!db, mode: 'desktop' };
});

ipcMain.handle('db:getStatus', async () => {
  return new Promise((resolve, reject) => {
    if (!db) {
      return resolve({ ok: false, mode: 'desktop', books: 0 });
    }
    db.get('SELECT COUNT(*) AS n FROM Books', (err, row) => {
      if (err) {
        console.error(err);
        resolve({ ok: true, mode: 'desktop', books: 0 });
      } else {
        resolve({ ok: true, mode: 'desktop', books: row.n });
      }
    });
  });
});

ipcMain.handle('db:query', async (event, sql, params) => {
  return new Promise((resolve, reject) => {
    if (!db) {
      return reject(new Error('Database not connected'));
    }
    db.all(sql, params, (err, rows) => {
      if (err) {
        console.error(err);
        reject(err);
      } else {
        resolve(rows);
      }
    });
  });
});

ipcMain.handle('db:searchBooks', async (event, query) => {
  const sql = `
    SELECT ID, Title, Author, Category_ID, Filename, Thumbnail
    FROM Books
    WHERE Title LIKE ? OR Author LIKE ?
    ORDER BY Title
    LIMIT 200`;
  const params = [`%${query}%`, `%${query}%`];
  return new Promise((resolve, reject) => {
    if (!db) {
      return reject(new Error('Database not connected'));
    }
    db.all(sql, params, (err, rows) => {
      if (err) {
        console.error(err);
        reject(err);
      } else {
        resolve(rows);
      }
    });
  });
});

ipcMain.handle('getGoogleConfig', async () => {
    const configPath = path.join(__dirname, 'Config', 'ourlibrary_google_config.json');
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    return config;
});

ipcMain.handle('updateDatabase', async (event, buffer) => {
    // In a real desktop app, you would handle the database update here.
    // For now, we'll just log it.
    console.log('updateDatabase called, but not implemented in this version.');
    return { ok: true, mode: 'desktop', updated: false };
});
