#!/usr/bin/env bash
# 安装 Platform SEO Audit 的 cron 任务（daily-pull + watch + quarterly review）

set -e

SKILL_DIR="$HOME/.claude/skills/seo-audit"
CRON_FILE=$(mktemp)

# 保留现有 cron
crontab -l 2>/dev/null > "$CRON_FILE" || true

# 移除旧 Platform SEO 任务
sed -i.bak '/# Platform-SEO-Audit/d' "$CRON_FILE"

# 添加新任务
cat >> "$CRON_FILE" << EOF

# Platform-SEO-Audit Daily Rule Sync (每日 06:00 UTC)
0 6 * * * cd $SKILL_DIR && uv run python3 -c "import asyncio; from agents.rule_sync import run_sync; asyncio.run(run_sync())" >> $SKILL_DIR/logs/daily-sync.log 2>&1

# Platform-SEO-Audit Weekly Watch (每周一 08:00 UTC)
0 8 * * 1 cd $SKILL_DIR && uv run python scripts/batch_audit.py >> $SKILL_DIR/logs/weekly-watch.log 2>&1

# Platform-SEO-Audit Quarterly Feedback Review (每季度第一天)
0 9 1 1,4,7,10 * cd $SKILL_DIR && uv run python3 -c "from agents.feedback import quarterly_review; import json; print(json.dumps(quarterly_review(), indent=2))" >> $SKILL_DIR/logs/quarterly-review.log 2>&1
EOF

mkdir -p "$SKILL_DIR/logs"
crontab "$CRON_FILE"
rm "$CRON_FILE"

echo "✅ Cron tasks installed:"
crontab -l | grep Platform-SEO-Audit
echo ""
echo "Logs: $SKILL_DIR/logs/"
