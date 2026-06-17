# 同事使用指南 · 怎么跑 SEO 审计

4 套使用方式 —— 选适合你的。

## 🎯 我是哪一类？

| 你是 | 推荐方式 | 装机时间 |
|------|---------|---------|
| 任何角色（最快体验） | **☁️ 云端 Dashboard** | 0 分钟 |
| 内容运营 / 法务 / 产品 | **A · 桌面 App** | 5 分钟 |
| SEO 运营 / 增长 | **B · Web Dashboard（本地）** | 10 分钟 |
| 前端 / 工程 / 数据 | **C · CLI + API** | 5 分钟 |

---

## ☁️ 云端 Dashboard（推荐先用这个）

直接打开浏览器：**https://multi-engine-seo-audit.fly.dev**

- ✅ 无需安装、无需配 API key（已托管）
- ✅ 任何设备都能用，团队共享
- ✅ 7×24 在线（auto-scale，闲时停机省费）
- ⚠️ 仅适合临时审计 / 演示；隐私敏感页面请用本地版（A/B）

---

## A · 桌面 App（零技术门槛）

**适合**：完全不写代码的同事

### 第一次装机（5 分钟）

```bash
# 1. 一行命令装齐 Python 环境（macOS 自带 zsh 终端打开粘贴）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.12 uv node

# 2. clone 仓库
gh auth login  # 用浏览器登录 GitHub
gh repo clone SEO-SKILL/multi-engine-seo-audit
cd multi-engine-seo-audit

# 3. 一键打 dmg
bash install.sh
cd electron-app && npm install && npm run build:mac

# 4. 装到 Applications
open dist/
# 双击 .dmg → 拖到 Applications → 完成
```

### 之后每次用

1. **Launchpad 搜「SEO」** → 双击启动
2. 等 splash 加载（~10 秒后自动弹主窗口）
3. **菜单栏 → Multi-Engine SEO Audit → 设置 API Keys**（首次必须填）
4. 顶部输入框填要审计的 URL → 选 locale → 点 🔍 一键深度诊断
5. 或点 🚀 跑核心 8 页 一键批量

### API Key 在哪填

App 菜单栏：Multi-Engine SEO Audit → **设置 API Keys...**（⌘ + ,）

向 Kelly 申请共享 key 或自己去 [console.anthropic.com](https://console.anthropic.com) 申请。

---

## B · Web Dashboard（浏览器用）

**适合**：会装命令行工具但不写 Python 的同事

### 第一次装机（10 分钟）

```bash
# 1. 装 brew + python + uv（如未装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.12 uv

# 2. clone + 一键安装
gh repo clone SEO-SKILL/multi-engine-seo-audit
cd multi-engine-seo-audit
bash install.sh

# 3. 编辑 .env 填 ANTHROPIC_API_KEY
nano .env  # 把 sk-ant-... 粘贴到 ANTHROPIC_API_KEY=

# 4. 启动
uv run python web_dashboard.py
```

### 之后每次用

```bash
cd ~/multi-engine-seo-audit       # 或你 clone 的位置
uv run python web_dashboard.py    # 后台启动
```

浏览器打开 **http://localhost:8080** 开始审计。

---

## C · CLI + API（工程师）

**适合**：要把审计接入脚本 / CI / 数据 pipeline

### 单页审计

```bash
curl -X POST https://multi-engine-seo-audit.fly.dev/api/audit \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/en/price/btc",
    "locale": "en",
    "no_cache": true
  }' | jq
```

返回 JSON 含：`score`, `verdict`, `findings[]`, `composite{}`, `action_plan[]`。

### 批量审计 8 页

```bash
curl https://multi-engine-seo-audit.fly.dev/api/batch | jq '.results[] | {label, score, blockers, highs}'
```

### 自定义批量

```bash
curl -X POST http://localhost:8080/api/batch \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      {"url":"https://example.com/en/futures", "locale":"en", "label":"Futures"},
      {"url":"https://example.com/ja",         "locale":"ja", "label":"Homepage JA"}
    ]
  }' | jq
```

### 导出 Markdown 报告

```bash
RUN_ID=$(curl -X POST localhost:8080/api/audit -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com/en", "locale":"en"}' | jq -r .run_id)

curl -X POST localhost:8080/api/export-markdown \
  -H "Content-Type: application/json" \
  -d "{\"run_id\":\"$RUN_ID\"}" | jq -r .markdown > report.md
```

### 接入 Cron（每周自动跑）

```bash
# crontab -e 加一行：每周一早 9 点跑批量审计 + 发飞书
0 9 * * 1 cd ~/multi-engine-seo-audit && uv run python web_dashboard.py & \
          sleep 20 && curl -s localhost:8080/api/batch > weekly-$(date +\%Y\%m\%d).json
```

---

## 🆘 常见问题

### Q: API key 怎么申请 / 共用？

向 Kelly 申请团队共享 key（推荐），或自己注册：
- Anthropic：https://console.anthropic.com
- Google AI（兜底）：https://aistudio.google.com/apikey

### Q: 装机失败 / brew 报错

```bash
# 看 brew 是否在 PATH
echo $PATH | grep -o '/opt/homebrew/bin\|/usr/local/bin'

# 如果没有：
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

### Q: 跑 audit 时报「API key invalid」

```bash
# 检查 .env
cat .env | grep ANTHROPIC

# 重启 dashboard 让它重新加载
pkill -f web_dashboard.py
uv run python web_dashboard.py
```

### Q: 8080 端口被占用

```bash
# 找出占用进程
lsof -iTCP:8080 -sTCP:LISTEN

# 杀掉
pkill -f web_dashboard.py

# 或换端口
PORT=8081 uv run python web_dashboard.py
```

### Q: dashboard 上的 finding 不会渲染中文标签

刷新浏览器（Cmd+R）—— 第一次拉规则 mapping 可能稍慢。

### Q: 怎么知道我跑的 audit 结果靠不靠谱

跑同一个 URL 至少 2 次（勾选 🔄 强制重跑 绕过 cache）。如果两次结果一致 → 可信。
如果差异大 → LLM judge 的随机性，建议看 hard rule 触发的 finding。

---

## 📖 进阶文档

- [SKILL.md](SKILL.md) — 完整能力清单（所有 agent / 所有规则）
- [PRD.md](PRD.md) — 产品需求文档
- [deliverables/](deliverables/) — 针对内部业务的 patch 包（私有）

## 🐛 出问题找谁

- 工具 bug / 规则误报：在 GitHub repo 开 Issue
- API key / 共享账号：找 Kelly
- 业务问题（KO 韩文页 / Price schema）：见 [Issues](https://github.com/SEO-SKILL/multi-engine-seo-audit/issues)
