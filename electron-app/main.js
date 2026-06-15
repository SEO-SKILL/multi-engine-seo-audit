// BYDFi SEO Audit — Electron 主进程
// 职责：spawn Flask 后端 → 等 health → 开窗 → 退出时 kill

const { app, BrowserWindow, ipcMain, shell, dialog, Menu } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn, execSync } = require('child_process');
const http = require('http');

const isDev = process.argv.includes('--dev') || !app.isPackaged;
const BACKEND_PORT = 8080;
const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;

// 确定 skill 根目录（开发 = ../，打包 = process.resourcesPath/skill）
function skillRoot() {
  if (isDev) return path.resolve(__dirname, '..');
  return path.join(process.resourcesPath, 'skill');
}

// 检查前置环境（uv + python3）
function preflightCheck() {
  const errors = [];
  try { execSync('which uv', { stdio: 'pipe' }); }
  catch { errors.push('uv (Python 包管理器)'); }
  try { execSync('which python3', { stdio: 'pipe' }); }
  catch { errors.push('python3'); }
  return errors;
}

let backendProcess = null;
let mainWindow = null;
let splashWindow = null;

function createSplash() {
  splashWindow = new BrowserWindow({
    width: 480, height: 320,
    frame: false, transparent: false, resizable: false,
    alwaysOnTop: true, center: true,
    webPreferences: { contextIsolation: true, nodeIntegration: false }
  });
  splashWindow.loadFile(path.join(__dirname, 'splash.html'));
}

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1440, height: 900,
    minWidth: 1100, minHeight: 700,
    title: 'BYDFi SEO Audit',
    icon: path.join(__dirname, 'build', 'icon.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    show: false,
  });

  mainWindow.loadURL(BACKEND_URL);

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    if (splashWindow && !splashWindow.isDestroyed()) splashWindow.close();
  });

  // 外链在系统浏览器打开（避免 Electron 窗口被劫持）
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  mainWindow.on('closed', () => { mainWindow = null; });
}

// 轮询 backend health 直到 200
function waitForBackend(timeoutMs = 60000) {
  const start = Date.now();
  return new Promise((resolve, reject) => {
    const tick = () => {
      http.get(`${BACKEND_URL}/api/health`, (res) => {
        if (res.statusCode === 200) return resolve();
        if (Date.now() - start > timeoutMs) return reject(new Error('backend health timeout'));
        setTimeout(tick, 500);
      }).on('error', () => {
        if (Date.now() - start > timeoutMs) return reject(new Error('backend not reachable'));
        setTimeout(tick, 500);
      });
    };
    tick();
  });
}

function startBackend() {
  const root = skillRoot();
  // 写入 HOST=127.0.0.1 强制内网 + PORT=8080
  const env = { ...process.env, HOST: '127.0.0.1', PORT: String(BACKEND_PORT) };

  // 检查 .env 是否存在（如不存在，从 .env.example 复制）
  const dotenvPath = path.join(root, '.env');
  if (!fs.existsSync(dotenvPath)) {
    const example = path.join(root, '.env.example');
    if (fs.existsSync(example)) {
      fs.copyFileSync(example, dotenvPath);
    } else {
      fs.writeFileSync(dotenvPath, '# 配置 API key — 通过 App 内设置写入\n');
    }
  }

  console.log(`[backend] cwd=${root}`);
  backendProcess = spawn('uv', ['run', 'python', 'web_dashboard.py'], {
    cwd: root,
    env,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  backendProcess.stdout.on('data', (d) => console.log(`[flask] ${d.toString().trim()}`));
  backendProcess.stderr.on('data', (d) => console.log(`[flask err] ${d.toString().trim()}`));
  backendProcess.on('exit', (code) => {
    console.log(`[backend] exited code=${code}`);
    backendProcess = null;
  });
}

function stopBackend() {
  if (backendProcess && !backendProcess.killed) {
    backendProcess.kill('SIGTERM');
    setTimeout(() => {
      if (backendProcess && !backendProcess.killed) backendProcess.kill('SIGKILL');
    }, 3000);
  }
}

// === IPC: settings 读写 .env ===
ipcMain.handle('settings:read', () => {
  const dotenvPath = path.join(skillRoot(), '.env');
  if (!fs.existsSync(dotenvPath)) return {};
  const text = fs.readFileSync(dotenvPath, 'utf8');
  const out = {};
  text.split('\n').forEach((line) => {
    const m = line.match(/^([A-Z_]+)=(.*)$/);
    if (m) out[m[1]] = m[2];
  });
  // 出于安全考虑，只返回是否已配置，不返回完整 key
  return Object.fromEntries(Object.entries(out).map(([k, v]) => [k, v ? `${v.slice(0, 8)}…(${v.length} 字符)` : '']));
});

ipcMain.handle('settings:write', (_e, payload) => {
  const dotenvPath = path.join(skillRoot(), '.env');
  let existing = fs.existsSync(dotenvPath) ? fs.readFileSync(dotenvPath, 'utf8') : '';
  const lines = existing.split('\n');
  const seen = new Set();
  const updated = lines.map((line) => {
    const m = line.match(/^([A-Z_]+)=/);
    if (m && payload[m[1]] && !payload[m[1]].endsWith('…')) {
      seen.add(m[1]);
      return `${m[1]}=${payload[m[1]]}`;
    }
    return line;
  });
  for (const [k, v] of Object.entries(payload)) {
    if (!seen.has(k) && v && !v.endsWith('…')) updated.push(`${k}=${v}`);
  }
  fs.writeFileSync(dotenvPath, updated.join('\n'));
  return { ok: true, restart_required: true };
});

ipcMain.handle('app:restart-backend', () => {
  stopBackend();
  setTimeout(startBackend, 1500);
  return { restarting: true };
});

ipcMain.handle('app:open-settings', () => {
  const settingsWin = new BrowserWindow({
    width: 600, height: 500, resizable: false,
    parent: mainWindow, modal: true,
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true },
  });
  settingsWin.loadFile(path.join(__dirname, 'settings.html'));
  return { opened: true };
});

ipcMain.handle('app:open-deliverables', () => {
  shell.openPath(path.join(skillRoot(), 'deliverables'));
  return { opened: true };
});

// === 应用菜单 ===
function buildMenu() {
  const template = [
    {
      label: 'BYDFi SEO Audit',
      submenu: [
        { label: '关于 BYDFi SEO Audit', role: 'about' },
        { type: 'separator' },
        { label: '设置 API Keys...', accelerator: 'CmdOrCtrl+,', click: () => ipcMain.emit('open-settings-direct') },
        { label: '打开 Deliverables 文件夹', click: () => shell.openPath(path.join(skillRoot(), 'deliverables')) },
        { type: 'separator' },
        { label: '重启后端', click: () => { stopBackend(); setTimeout(startBackend, 1500); } },
        { type: 'separator' },
        { label: '退出', accelerator: 'CmdOrCtrl+Q', click: () => app.quit() },
      ],
    },
    {
      label: '编辑',
      submenu: [
        { role: 'copy' }, { role: 'paste' }, { role: 'selectAll' },
      ],
    },
    {
      label: '视图',
      submenu: [
        { role: 'reload' }, { role: 'forceReload' }, { role: 'toggleDevTools' },
        { type: 'separator' },
        { role: 'resetZoom' }, { role: 'zoomIn' }, { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
      ],
    },
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

ipcMain.on('open-settings-direct', () => {
  const settingsWin = new BrowserWindow({
    width: 600, height: 500, resizable: false,
    parent: mainWindow, modal: true,
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true },
  });
  settingsWin.loadFile(path.join(__dirname, 'settings.html'));
});

app.whenReady().then(async () => {
  buildMenu();

  // 前置环境检查
  const missing = preflightCheck();
  if (missing.length > 0) {
    dialog.showErrorBox(
      '环境检查失败',
      `BYDFi SEO Audit 需要以下工具：\n\n${missing.map(m => '  • ' + m).join('\n')}\n\n安装方法：\n  brew install python uv`
    );
    app.quit();
    return;
  }

  createSplash();
  startBackend();

  try {
    await waitForBackend();
    createMainWindow();
  } catch (e) {
    dialog.showErrorBox('后端启动失败', `Flask backend 未能在 60 秒内启动：\n${e.message}\n\n查看终端日志获取详情。`);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', stopBackend);

app.on('activate', () => {
  if (mainWindow === null && backendProcess) createMainWindow();
});
