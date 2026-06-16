# Multi-Engine SEO Audit · 桌面 App（Electron）

把 SEO audit skill 包装成本地桌面应用，给 Platform 内部同事（SEO / 内容运营 / 法务 / 工程）一键使用。

## 🎯 给同事用：直接装 .dmg

```
1. 双击 Platform-SEO-Audit-1.0.0.dmg
2. 拖拽 Multi-Engine SEO Audit.app 到 Applications
3. 首次启动会弹「无法验证开发者」 → 右键打开 → 仍要打开
4. App 自动启动 → 设置菜单填入 API key → 开始审计
```

**前置**（首次安装需要）：
```bash
# 一行命令装齐 Python 环境
brew install python uv
```

## 🛠 开发 / 自己构建

### 安装依赖

```bash
cd electron-app
npm install
```

### 开发模式（热启动）

```bash
npm run dev
# 自动 spawn Flask backend + 打开 BrowserWindow
```

### 打包发布

```bash
# macOS Apple Silicon (.dmg)
npm run build:mac

# macOS Intel
npm run build:mac-intel

# Windows
npm run build:win

# 产物在 dist/ 目录
```

## 📦 架构

```
┌──────────────────────────────────────────────┐
│  Electron App (Multi-Engine SEO Audit)              │
│  ┌────────────────────────────────────────┐  │
│  │ Main Process (main.js)                 │  │
│  │ - 启动时 spawn Flask backend           │  │
│  │ - 等 /api/health → 显示主窗口          │  │
│  │ - 退出时 kill backend                  │  │
│  │ - IPC: 读写 .env / 重启 / 打开文件夹   │  │
│  └────────┬───────────────────────────────┘  │
│           ▼                                  │
│  ┌────────────────────────────────────────┐  │
│  │ BrowserWindow → http://127.0.0.1:8080  │  │
│  │ (现有 dashboard UI · 442 规则)         │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
         │ child_process.spawn
         ▼
┌──────────────────────────────────────────────┐
│  Flask Backend (uv run python web_dashboard) │
│  - 22 agents + 442 rules                     │
│  - 127.0.0.1 only (不暴露公网)               │
└──────────────────────────────────────────────┘
```

## 🔐 安全设计

- **后端只绑 127.0.0.1**（main.js 强制 `HOST=127.0.0.1`）
- **API key 仅保存本地 .env**（不上传任何服务器）
- **Settings UI 默认隐藏 key 字符**（点 👁 才显示）
- **外链系统浏览器打开**（不被 Electron 窗口劫持）

## 📁 文件结构

```
electron-app/
├── package.json         ← npm + electron-builder 配置
├── main.js              ← 主进程（生命周期 + IPC）
├── preload.js           ← 安全的 IPC 桥（contextBridge）
├── splash.html          ← 启动等待页（橙色 logo 动画）
├── settings.html        ← API key 配置 UI
├── build/
│   └── icon.png         ← App icon（可换 Platform 真 logo）
└── README.md            ← 本文档
```

## ⚙️ 菜单功能

| 菜单项 | 快捷键 | 作用 |
|--------|--------|------|
| 设置 API Keys... | ⌘, | 弹 Settings 窗口配置 LLM API |
| 打开 Deliverables 文件夹 | — | 直接 Finder 打开 patch 包目录 |
| 重启后端 | — | 修改 .env / 规则后重启 Flask |
| 重新加载 | ⌘R | 刷新 dashboard UI |
| 切换 DevTools | ⌥⌘I | 调试用 |
| 退出 | ⌘Q | 自动 kill Flask 进程 |

## 🐛 常见问题

**Q: 启动时报「环境检查失败」？**
A: 装 brew + python + uv：`brew install python uv`

**Q: 后端启动失败 / 60 秒超时？**
A: 终端启动 dashboard 看错误：`uv run python web_dashboard.py`，常见原因：
   - 8080 端口被占用 → 换端口或 kill 占用进程
   - venv 损坏 → `rm -rf .venv && uv sync`
   - rules YAML 语法错误 → 看 stderr

**Q: 如何替换 App icon？**
A: 替换 `build/icon.png`（512×512 PNG），macOS 还需 `build/icon.icns`（用 [iconutil](https://developer.apple.com/library/archive/documentation/GraphicsAnimation/Conceptual/HighResolutionOSX/Optimizing/Optimizing.html)）

**Q: 如何给非技术同事？**
A: 跑 `npm run build:mac` 产出 .dmg，扔飞书私聊给同事，告知首次需要装 brew/python/uv 一次。

## 🔮 未来增强（如需）

- [ ] 内嵌 Python 运行时（pyinstaller 打包，免去同事装 uv）
- [ ] macOS 代码签名 + 公证（避免「无法验证开发者」警告）
- [ ] Auto-update（electron-updater）
- [ ] 跨平台 Windows .exe 测试
- [ ] keytar 集成（API key 存入系统钥匙串）
