#!/usr/bin/env bash
# Multi-Engine SEO Audit · 一键安装脚本
# 用法：bash install.sh
#
# 这个脚本会：
# 1. 检查 / 安装 Homebrew（如未装）
# 2. 装 python@3.12 + uv + node（如未装）
# 3. uv sync 安装 Python 依赖
# 4. 引导填 .env 里的 API key
# 5. 启动 dashboard

set -e

ORANGE='\033[0;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${ORANGE}${BOLD}╔══════════════════════════════════════════════════╗${NC}"
echo -e "${ORANGE}${BOLD}║    Multi-Engine SEO Audit · 一键安装             ║${NC}"
echo -e "${ORANGE}${BOLD}╚══════════════════════════════════════════════════╝${NC}"
echo ""

# === Step 1: 检查 macOS ===
if [[ "$(uname)" != "Darwin" ]]; then
  echo -e "${RED}✗ 当前脚本只支持 macOS。Windows 同事请用 WSL 或联系工程。${NC}"
  exit 1
fi

# === Step 2: Homebrew ===
echo -e "${BOLD}[1/5]${NC} 检查 Homebrew..."
if ! command -v brew &> /dev/null; then
  echo -e "  ${ORANGE}!${NC} brew 未装，开始安装（约 3-5 分钟）..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
  echo -e "  ${GREEN}✓${NC} brew $(brew --version | head -1)"
fi

# === Step 3: python + uv + node ===
echo -e "${BOLD}[2/5]${NC} 检查 Python / uv / Node..."
NEED_INSTALL=()
command -v python3 &> /dev/null || NEED_INSTALL+=("python@3.12")
command -v uv &> /dev/null || NEED_INSTALL+=("uv")
command -v node &> /dev/null || NEED_INSTALL+=("node")

if [ ${#NEED_INSTALL[@]} -gt 0 ]; then
  echo -e "  ${ORANGE}!${NC} 需要安装: ${NEED_INSTALL[*]}"
  brew install "${NEED_INSTALL[@]}"
else
  echo -e "  ${GREEN}✓${NC} 全部已装"
fi

# === Step 4: uv sync ===
echo -e "${BOLD}[3/5]${NC} 安装 Python 依赖（uv sync）..."
if [ -f pyproject.toml ]; then
  uv sync --quiet
  echo -e "  ${GREEN}✓${NC} 依赖装好"
else
  echo -e "  ${RED}✗${NC} 当前目录无 pyproject.toml — 请先 cd 到 repo 根目录"
  exit 1
fi

# === Step 5: .env 配置引导 ===
echo -e "${BOLD}[4/5]${NC} 配置 API Key..."
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
  else
    cat > .env << 'EOF'
# Multi-Engine SEO Audit · API Keys
# 填入你的 API key（向团队 leader 申请共享 key 或自己申请）

# 主 LLM judge（必填）· 申请：https://console.anthropic.com
ANTHROPIC_API_KEY=

# Gemini fallback（可选 · Anthropic 配额满时兜底）· 申请：https://aistudio.google.com/apikey
GOOGLE_AI_API_KEY=

# 飞书告警 webhook（可选）
LARK_WEBHOOK=
EOF
  fi
  echo -e "  ${ORANGE}!${NC} 已创建 .env 模板"
  echo -e "  ${BOLD}请编辑 .env 填入 ANTHROPIC_API_KEY 后再启动${NC}"
  echo -e "  ${ORANGE}（向 Kelly 申请共享 key，或自己去 console.anthropic.com 申请）${NC}"
else
  if grep -q "ANTHROPIC_API_KEY=sk-ant" .env 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} .env 已含 Anthropic key"
  else
    echo -e "  ${ORANGE}!${NC} .env 存在但 ANTHROPIC_API_KEY 似乎未填"
  fi
fi

# === Step 6: 启动选项 ===
echo -e "${BOLD}[5/5]${NC} 启动方式选择"
echo ""
echo "  方式 A · Web Dashboard（推荐 SEO/运营/法务同事）"
echo "    ${BOLD}uv run python web_dashboard.py${NC}"
echo "    → 浏览器打开 http://localhost:8080"
echo ""
echo "  方式 B · Electron 桌面 App（推荐非技术同事）"
echo "    ${BOLD}cd electron-app && npm install && npm run dev${NC}"
echo "    → 自动弹窗口，不用记 URL"
echo ""
echo "  方式 C · CLI 单页（推荐工程师）"
echo "    ${BOLD}curl -X POST localhost:8080/api/audit \\${NC}"
echo "    ${BOLD}     -H 'Content-Type: application/json' \\${NC}"
echo "    ${BOLD}     -d '{\"url\":\"<目标 URL>\",\"locale\":\"en\"}'${NC}"
echo ""
echo -e "${GREEN}${BOLD}✓ 安装完成${NC}"
echo ""
echo -e "${ORANGE}下一步：${NC}"
echo "  1. ${BOLD}编辑 .env 填 ANTHROPIC_API_KEY${NC}（向 Kelly 申请共享 key）"
echo "  2. 跑 ${BOLD}uv run python web_dashboard.py${NC} 启动"
echo "  3. 浏览器打开 http://localhost:8080 开始审计"
echo ""
