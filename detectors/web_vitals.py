"""Web Vitals 4 indicators estimation from static HTML + headers"""
from __future__ import annotations

import re


# === LCP estimate ===
def lcp_estimate(raw_html: str | None = None, http_headers: dict | None = None, **_) -> dict:
    """从 HTML 推断 LCP 风险：hero 图片大小 / render-blocking 资源数"""
    html = raw_html or ""
    headers = http_headers or {}
    # render-blocking <link rel="stylesheet"> 和 <script src> 数量
    blocking_css = len(re.findall(r'<link[^>]+rel\s*=\s*["\']stylesheet["\']', html, re.IGNORECASE))
    blocking_js = len(re.findall(r'<script[^>]+src\s*=\s*["\'][^"\']+["\']\s*(?!\s*(?:async|defer))[^>]*>', html, re.IGNORECASE))
    # hero 图片：第一个 <img>
    first_img = re.search(r"<img[^>]+src=[\"']([^\"']+)[\"'][^>]*>", html, re.IGNORECASE)
    has_priority_hint = first_img and ("fetchpriority" in first_img.group(0).lower() or "preload" in html.lower())
    # 启发式 LCP 评分（满分 1.0）
    score = 1.0
    if blocking_css > 4: score -= 0.2
    if blocking_js > 6: score -= 0.2
    if first_img and not has_priority_hint: score -= 0.15
    score = max(0, score)
    return {
        "blocking_css_count": blocking_css,
        "blocking_js_count": blocking_js,
        "hero_image_has_priority": has_priority_hint,
        "estimated_lcp_score": round(score, 2),
        "suspect_slow_lcp": score < 0.6,
    }


# === CLS check ===
def cls_check(raw_html: str | None = None, **_) -> dict:
    """检测 img/iframe 是否声明 width/height（防 layout shift）"""
    html = raw_html or ""
    imgs = re.findall(r"<img[^>]+>", html, re.IGNORECASE)
    iframes = re.findall(r"<iframe[^>]+>", html, re.IGNORECASE)
    all_media = imgs + iframes
    if not all_media:
        return {"media_count": 0, "all_dimensioned": True}
    with_dim = sum(1 for m in all_media
                   if re.search(r"\bwidth\s*=", m, re.IGNORECASE) and re.search(r"\bheight\s*=", m, re.IGNORECASE))
    return {
        "media_count": len(all_media),
        "dimensioned_count": with_dim,
        "dim_ratio": round(with_dim / max(1, len(all_media)), 2),
        "suspect_layout_shift": with_dim / max(1, len(all_media)) < 0.7,
    }


# === INP estimate ===
def inp_estimate(raw_html: str | None = None, **_) -> dict:
    """从 HTML 推断 INP：第三方 JS 数量 / 大型 inline JS"""
    html = raw_html or ""
    third_party_scripts = len(re.findall(
        r"<script[^>]+src\s*=\s*[\"'](?:https?:)?//(?!(?:[\w-]+\.)?(?:localhost|127\.0))",
        html, re.IGNORECASE))
    inline_scripts = re.findall(r"<script[^>]*>([\s\S]{500,}?)</script>", html, re.IGNORECASE)
    large_inline = len(inline_scripts)
    return {
        "third_party_script_count": third_party_scripts,
        "large_inline_script_count": large_inline,
        "suspect_slow_inp": third_party_scripts > 8 or large_inline > 3,
    }


# === TTFB check ===
def ttfb_check(http_headers: dict | None = None, **_) -> dict:
    """从 response headers 推断服务端响应：server-timing / age / cache-status"""
    headers = http_headers or {}
    server_timing = headers.get("server-timing") or headers.get("Server-Timing", "")
    age = headers.get("age") or headers.get("Age")
    cf_cache_status = headers.get("cf-cache-status") or headers.get("CF-Cache-Status")
    # 是否命中 edge cache
    edge_cached = cf_cache_status in ("HIT", "STALE", "REVALIDATED") or (age and int(age) > 0 if str(age).isdigit() else False)
    # 解析 Server-Timing 中 dur=xxx（毫秒）
    ttfb_ms = None
    m = re.search(r"dur=([\d.]+)", server_timing)
    if m:
        ttfb_ms = float(m.group(1))
    return {
        "edge_cached": bool(edge_cached),
        "cf_cache_status": cf_cache_status,
        "server_timing_dur_ms": ttfb_ms,
        "suspect_slow_ttfb": (ttfb_ms is not None and ttfb_ms > 800) or (cf_cache_status == "MISS" and not edge_cached),
    }
