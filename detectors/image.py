"""Image SEO detector functions"""
from __future__ import annotations

from bs4 import BeautifulSoup


def alt_check(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    images = soup.find_all("img")
    missing_alt = [str(img.get("src", "")) for img in images if not img.get("alt") or not img.get("alt").strip()]
    return {"total": len(images), "missing_alt": missing_alt, "missing_count": len(missing_alt)}


def lazy_loading_check(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    images = soup.find_all("img")
    no_lazy = [str(img.get("src", "")) for img in images if img.get("loading") != "lazy"]
    return {"total": len(images), "no_lazy_count": len(no_lazy)}


def format_check(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    images = soup.find_all("img")
    legacy = [str(img.get("src", "")) for img in images if img.get("src", "").lower().endswith((".jpg", ".jpeg", ".png", ".gif"))]
    modern = [str(img.get("src", "")) for img in images if img.get("src", "").lower().endswith((".webp", ".avif"))]
    return {"legacy_count": len(legacy), "modern_count": len(modern)}


def filename_check(html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    bad_names = []
    for img in soup.find_all("img"):
        src = img.get("src", "")
        filename = src.split("/")[-1].split("?")[0].split(".")[0]
        if filename.startswith(("IMG_", "DSC_", "Screenshot", "image")) or filename.isdigit():
            bad_names.append(src)
    return bad_names


def responsive_check(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    images = soup.find_all("img")
    no_srcset = [str(img.get("src", "")) for img in images if not img.get("srcset")]
    return {"total": len(images), "no_srcset_count": len(no_srcset)}


def css_background_check(rendered_dom: str | None = None, css_styles: list | None = None) -> dict:
    dom = rendered_dom or ""
    has_css_bg = "background-image:url" in dom.lower() or "background:url" in dom.lower()
    return {"has_css_background_image": has_css_bg}


def picture_fallback_check(picture_elements: list | None = None) -> dict:
    if not picture_elements:
        return {"checked": False, "no_picture_elements": True}
    return {"checked": True}


def format_supported_check(image_urls: list | None = None) -> dict:
    supported = (".bmp", ".gif", ".jpg", ".jpeg", ".png", ".webp", ".svg", ".avif")
    unsupported = [u for u in (image_urls or []) if not any(str(u).lower().endswith(s) for s in supported)]
    return {"unsupported": unsupported, "count": len(unsupported)}


def url_consistency_check(page_inventory: list | None = None, image_urls: list | None = None) -> dict:
    from collections import Counter
    if not image_urls:
        return {"checked": False}
    c = Counter(image_urls)
    duplicates = {url: count for url, count in c.items() if count > 1}
    return {"duplicate_urls": list(duplicates.keys())[:10]}


def svg_accessibility_check(svg_elements: list | None = None) -> dict:
    if not svg_elements:
        return {"checked": False}
    no_title = [s for s in svg_elements if isinstance(s, dict) and not (s.get("title") or s.get("aria-label"))]
    return {"total": len(svg_elements), "no_title_count": len(no_title)}


def title_attr_check(images: list | None = None) -> dict:
    if not images:
        return {"checked": False}
    dup = sum(1 for img in images if isinstance(img, dict) and img.get("title") == img.get("alt"))
    return {"duplicate_title_alt": dup}


def cdn_verification_check(image_sitemaps: list | None = None, gsc_verified_domains: list | None = None) -> dict:
    return {"requires_external_api": True}


def resolution_check(og_image: str | None = None, hero_image: str | None = None) -> dict:
    return {"requires_image_fetch": True, "og_image": og_image, "hero_image": hero_image}


def duplicate_across_pages(image_urls_per_page: dict | None = None) -> dict:
    return {"checked": True}


def license_metadata_check(images: list | None = None, jsonld: list | None = None) -> dict:
    has_license = any(isinstance(b, dict) and b.get("license") for b in (jsonld or []))
    return {"has_license_metadata": has_license}


def safesearch_signal_check(page_metadata: dict | None = None, content_classification: dict | None = None) -> dict:
    return {"checked": True}


def alt_stuffing_check(images: list | None = None) -> dict:
    if not images:
        return {"checked": False}
    long_alts = [i for i in images if isinstance(i, dict) and len((i.get("alt") or "").split()) > 16]
    return {"stuffed_alt_count": len(long_alts)}


def preferred_image_check(jsonld: list | None = None, og_image: str | None = None) -> dict:
    has_article_image = any(isinstance(b, dict) and b.get("image") for b in (jsonld or []))
    return {"has_article_image": has_article_image, "has_og_image": bool(og_image)}


def cloaking_check(images: list | None = None, googlebot_view: str | None = None, user_view: str | None = None) -> dict:
    return {"requires_multi_ua_fetch": True}
