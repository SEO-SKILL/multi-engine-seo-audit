"""
Google Search Console API 集成
认证优先级：service-account JSON > OAuth refresh token > ADC > 跳过

支持的 env：
- GSC_SERVICE_ACCOUNT_JSON: service account JSON 字符串（推荐 server 部署）
- GSC_OAUTH_CLIENT_ID / GSC_OAUTH_CLIENT_SECRET / GSC_OAUTH_REFRESH_TOKEN: OAuth 三件套（个人账号）
- GOOGLE_APPLICATION_CREDENTIALS: 指向 JSON 文件路径
- ADC 文件：~/.config/gcloud/application_default_credentials.json
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

_ADC_PATH = Path.home() / ".config" / "gcloud" / "application_default_credentials.json"
_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

_log = logging.getLogger(__name__)
_credentials_cache: Any = None


def is_configured() -> bool:
    return bool(
        os.environ.get("GSC_SERVICE_ACCOUNT_JSON")
        or (
            os.environ.get("GSC_OAUTH_CLIENT_ID")
            and os.environ.get("GSC_OAUTH_CLIENT_SECRET")
            and os.environ.get("GSC_OAUTH_REFRESH_TOKEN")
        )
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        or _ADC_PATH.exists()
    )


def _load_credentials() -> Any:
    """按优先级加载凭证。返回 google-auth Credentials，None 表示未配置。"""
    global _credentials_cache
    if _credentials_cache is not None:
        return _credentials_cache
    if not is_configured():
        return None

    try:
        from google.auth import default as _adc_default
        from google.oauth2 import service_account
        from google.oauth2.credentials import Credentials as OAuthCredentials
    except ImportError as e:
        _log.warning("google-auth not installed: %s", e)
        return None

    # 1. Service Account JSON（env 字符串）
    sa_json = os.environ.get("GSC_SERVICE_ACCOUNT_JSON")
    if sa_json:
        try:
            info = json.loads(sa_json)
            _credentials_cache = service_account.Credentials.from_service_account_info(
                info, scopes=_SCOPES
            )
            return _credentials_cache
        except Exception as e:
            _log.warning("GSC_SERVICE_ACCOUNT_JSON parse failed: %s", e)

    # 2. OAuth refresh token（个人账号路径）
    refresh = os.environ.get("GSC_OAUTH_REFRESH_TOKEN")
    client_id = os.environ.get("GSC_OAUTH_CLIENT_ID")
    client_secret = os.environ.get("GSC_OAUTH_CLIENT_SECRET")
    if refresh and client_id and client_secret:
        creds = OAuthCredentials(
            token=None,
            refresh_token=refresh,
            client_id=client_id,
            client_secret=client_secret,
            token_uri="https://oauth2.googleapis.com/token",
            scopes=_SCOPES,
        )
        # quota_project 必须设：Google 后端对 ADC client_id 拒绝无 quota_project 的请求
        quota_project = os.environ.get("GSC_QUOTA_PROJECT") or os.environ.get("GOOGLE_CLOUD_PROJECT")
        if quota_project:
            creds = creds.with_quota_project(quota_project)
        _credentials_cache = creds
        return _credentials_cache

    # 3. GOOGLE_APPLICATION_CREDENTIALS 文件路径
    gac = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if gac and Path(gac).exists():
        try:
            _credentials_cache = service_account.Credentials.from_service_account_file(
                gac, scopes=_SCOPES
            )
            return _credentials_cache
        except Exception:
            pass  # fall through to ADC

    # 4. ADC（本地 gcloud auth application-default login）
    try:
        creds, _ = _adc_default(scopes=_SCOPES)
        _credentials_cache = creds
        return _credentials_cache
    except Exception as e:
        _log.warning("ADC load failed: %s", e)
        return None


def _build_service() -> Any:
    creds = _load_credentials()
    if creds is None:
        return None
    try:
        from googleapiclient.discovery import build
        return build("searchconsole", "v1", credentials=creds, cache_discovery=False)
    except ImportError as e:
        _log.warning("google-api-python-client not installed: %s", e)
        return None


def _property_for_url(url: str) -> str:
    """从 URL 推断 GSC property（domain property 或 URL-prefix）。
    简单实现：用 origin (https://host) 作为 property。
    """
    from urllib.parse import urlparse
    p = urlparse(url)
    if not p.scheme or not p.netloc:
        return url
    return f"{p.scheme}://{p.netloc}/"


async def url_inspection(url: str) -> dict[str, Any]:
    """调用 URL Inspection API。返回 dict 含 indexStatusResult / coverageState 等。
    失败/未配置时返回 {"skipped": True, "reason": ...}
    """
    if not is_configured():
        return {"skipped": True, "reason": "gsc_not_configured"}

    service = _build_service()
    if service is None:
        return {"skipped": True, "reason": "gsc_lib_missing"}

    site_url = _property_for_url(url)
    try:
        req = service.urlInspection().index().inspect(
            body={"inspectionUrl": url, "siteUrl": site_url}
        )
        result = req.execute()
        inspection = result.get("inspectionResult", {})
        index_status = inspection.get("indexStatusResult", {})
        mobile = inspection.get("mobileUsabilityResult", {})
        rich = inspection.get("richResultsResult", {})
        return {
            "coverage_state": index_status.get("coverageState"),
            "indexing_state": index_status.get("indexingState"),
            "verdict": index_status.get("verdict"),
            "last_crawl_time": index_status.get("lastCrawlTime"),
            "robots_txt_state": index_status.get("robotsTxtState"),
            "page_fetch_state": index_status.get("pageFetchState"),
            "user_canonical": index_status.get("userCanonical"),
            "google_canonical": index_status.get("googleCanonical"),
            "mobile_usability_verdict": mobile.get("verdict"),
            "rich_results_verdict": rich.get("verdict"),
            "raw": inspection,
        }
    except Exception as e:
        msg = str(e)
        if "403" in msg or "permission" in msg.lower():
            return {"skipped": True, "reason": "gsc_no_permission", "detail": msg[:200]}
        if "404" in msg or "not found" in msg.lower():
            return {"skipped": True, "reason": "gsc_property_not_found", "detail": msg[:200]}
        return {"skipped": True, "reason": "gsc_api_error", "detail": msg[:200]}


async def search_analytics(
    property_url: str, *, dimensions: list[str] | None = None, days: int = 28, row_limit: int = 100
) -> dict:
    """调 Search Analytics query API。"""
    if not is_configured():
        return {"skipped": True, "reason": "gsc_not_configured"}

    service = _build_service()
    if service is None:
        return {"skipped": True, "reason": "gsc_lib_missing"}

    from datetime import date, timedelta
    end = date.today()
    start = end - timedelta(days=days)
    body = {
        "startDate": start.isoformat(),
        "endDate": end.isoformat(),
        "dimensions": dimensions or ["query"],
        "rowLimit": row_limit,
    }
    try:
        result = service.searchanalytics().query(
            siteUrl=property_url, body=body
        ).execute()
        return {
            "property": property_url,
            "days": days,
            "rows": result.get("rows", []),
            "response_aggregation_type": result.get("responseAggregationType"),
        }
    except Exception as e:
        return {"skipped": True, "reason": "gsc_api_error", "detail": str(e)[:200]}


def reset_cache() -> None:
    """测试用：清掉凭证缓存。"""
    global _credentials_cache
    _credentials_cache = None
