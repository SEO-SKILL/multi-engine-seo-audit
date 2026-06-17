#!/usr/bin/env python3
"""
GSC OAuth Bootstrap · 一次性拿 refresh token

用法：
  python scripts/gsc_oauth_bootstrap.py path/to/oauth_client.json

oauth_client.json 来自：
  https://console.cloud.google.com/apis/credentials
  → CREATE CREDENTIALS → OAuth client ID
  → Application type: Desktop app
  → DOWNLOAD JSON

跑完会：
  1. 自动开浏览器到 Google 同意页（用 ppmworker@gmail.com 登录授权）
  2. 拿到 refresh token
  3. 输出 3 行 export 命令 + fly secrets set 命令

无需 service account，无需给 GSC 额外加邮箱。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1

    client_json = Path(sys.argv[1])
    if not client_json.exists():
        print(f"✗ 文件不存在：{client_json}")
        return 1

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("✗ 缺依赖。先跑：uv sync")
        return 1

    print("→ 即将打开浏览器，用 ppmworker@gmail.com 同意 webmasters.readonly 权限")
    flow = InstalledAppFlow.from_client_secrets_file(str(client_json), SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

    info = json.loads(client_json.read_text())
    section = info.get("installed") or info.get("web") or {}
    client_id = section.get("client_id", "")
    client_secret = section.get("client_secret", "")

    refresh = creds.refresh_token
    if not refresh:
        print("✗ 没拿到 refresh_token。重跑（加 prompt=consent）")
        return 1

    print("\n✓ 凭证就绪。\n")
    print("=" * 60)
    print("【本地 .env 写入】")
    print(f'GSC_OAUTH_CLIENT_ID={client_id}')
    print(f'GSC_OAUTH_CLIENT_SECRET={client_secret}')
    print(f'GSC_OAUTH_REFRESH_TOKEN={refresh}')
    print("=" * 60)
    print("\n【fly.io 一键推送】")
    print(
        f"fly secrets set \\\n"
        f"  GSC_OAUTH_CLIENT_ID='{client_id}' \\\n"
        f"  GSC_OAUTH_CLIENT_SECRET='{client_secret}' \\\n"
        f"  GSC_OAUTH_REFRESH_TOKEN='{refresh}' \\\n"
        f"  -a multi-engine-seo-audit"
    )
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
