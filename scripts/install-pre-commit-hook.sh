#!/usr/bin/env bash
# 安装 git pre-commit hook，让 Platform 内容仓库 commit 前自动跑 gate
# 用法: 在 Platform 内容仓库内运行此脚本

set -e

SKILL_DIR="$HOME/.claude/skills/seo-audit"
HOOK_PATH=".git/hooks/pre-commit"

if [ ! -d ".git" ]; then
  echo "❌ 当前目录不是 git 仓库"
  exit 1
fi

cat > "$HOOK_PATH" << 'EOF'
#!/usr/bin/env bash
# Multi-Engine SEO Audit pre-commit hook
SKILL_DIR="$HOME/.claude/skills/seo-audit"

# 找到所有 staged 的 MD/HTML 文件
files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(md|html)$' || true)

if [ -z "$files" ]; then
  exit 0
fi

failed=0
for f in $files; do
  echo "🔍 SEO Audit: $f"
  cd "$SKILL_DIR"
  if ! uv run python cli.py gate "$OLDPWD/$f" 2>&1; then
    failed=1
  fi
  cd "$OLDPWD"
done

if [ $failed -ne 0 ]; then
  echo ""
  echo "❌ SEO Gate failed for one or more files. Fix issues above before committing."
  echo "   Bypass (use carefully): git commit --no-verify"
  exit 1
fi

echo "✅ All files passed SEO Gate."
EOF

chmod +x "$HOOK_PATH"
echo "✅ Installed pre-commit hook at $HOOK_PATH"
echo "   现在每次 commit 前会自动跑 Multi-Engine SEO Audit Skill gate 命令"
echo "   如需绕过: git commit --no-verify"
