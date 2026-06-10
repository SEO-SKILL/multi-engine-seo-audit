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
