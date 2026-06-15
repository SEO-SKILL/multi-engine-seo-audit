"""Schema.org JSON-LD 相关 detector functions"""
from __future__ import annotations

import json

from bs4 import BeautifulSoup


def extract_jsonld(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    blocks = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            blocks.append(data)
        except (json.JSONDecodeError, TypeError):
            continue
    return blocks


def has_ssr_jsonld(raw_html: str, rendered_html: str | None) -> dict:
    raw_blocks = extract_jsonld(raw_html)
    rendered_blocks = extract_jsonld(rendered_html) if rendered_html else []
    return {
        "raw_count": len(raw_blocks),
        "rendered_count": len(rendered_blocks),
        "csr_only": len(raw_blocks) == 0 and len(rendered_blocks) > 0,
        "raw_types": [b.get("@type") for b in raw_blocks if isinstance(b, dict)],
        "rendered_types": [b.get("@type") for b in rendered_blocks if isinstance(b, dict)],
    }


def check_aggregaterating_grounded(jsonld_blocks: list[dict], visible_text: str) -> list[dict]:
    """检测 AggregateRating 是否对应页面可见评分"""
    issues = []
    for block in jsonld_blocks:
        if not isinstance(block, dict):
            continue
        ar = block.get("aggregateRating")
        if not ar:
            continue
        rating_value = str(ar.get("ratingValue", ""))
        review_count = str(ar.get("reviewCount", ""))
        # 检查可见文本是否出现这些值
        if rating_value and rating_value not in visible_text:
            issues.append({
                "field": "aggregateRating.ratingValue",
                "value": rating_value,
                "reason": "页面可见内容找不到该评分值",
            })
        if review_count and review_count not in visible_text:
            issues.append({
                "field": "aggregateRating.reviewCount",
                "value": review_count,
                "reason": "页面可见内容找不到该评论数",
            })
    return issues


def ssr_vs_csr_diff(raw_html: str, rendered_dom: str | None = None) -> dict:
    return has_ssr_jsonld(raw_html, rendered_dom)


def field_grounding(jsonld_parsed: list | None = None, visible_text: str | None = None, dom_screenshot: str | None = None) -> dict:
    issues = check_aggregaterating_grounded(jsonld_parsed or [], visible_text or "")
    return {"issues": issues, "has_ungrounded_fields": len(issues) > 0}


def aggregaterating_review_grounding(jsonld_parsed: list | None = None, visible_text: str | None = None, dom_components: list | None = None) -> dict:
    has_visible_review = any("review" in str(c).lower() for c in (dom_components or []))
    issues = check_aggregaterating_grounded(jsonld_parsed or [], visible_text or "")
    return {"has_visible_review": has_visible_review, "schema_issues": issues}


def copyrightnotice_consistency(jsonld_parsed: list | None = None, visible_text: str | None = None, page_footer: str | None = None) -> dict:
    email = get_jsonld_field(jsonld_parsed or [], "copyrightNotice.email")
    if not email:
        return {"has_copyright_email": False}
    in_footer = email in (page_footer or "") or email in (visible_text or "")
    return {"email": email, "consistent_with_footer": in_footer}


def relatedlink_topic_match(jsonld_parsed: list | None = None, page_topic_classification: str | None = None, related_link_targets: list | None = None) -> dict:
    related_links = []
    for b in (jsonld_parsed or []):
        if isinstance(b, dict) and b.get("relatedLink"):
            rls = b["relatedLink"] if isinstance(b["relatedLink"], list) else [b["relatedLink"]]
            related_links.extend(rls)
    return {"related_link_count": len(related_links), "requires_llm_check": True}


def related_link_topic_match(jsonld_parsed: list | None = None, page_topic_classification: str | None = None, related_link_targets: list | None = None) -> dict:
    return relatedlink_topic_match(jsonld_parsed, page_topic_classification, related_link_targets)


def deprecated_types_check(jsonld_parsed: list | None = None) -> dict:
    deprecated = []
    for b in (jsonld_parsed or []):
        if isinstance(b, dict) and b.get("@type") in ("FAQPage", "HowTo"):
            deprecated.append(b["@type"])
    return {"deprecated_types_used": deprecated}


def deprecated_faqpage_check(jsonld: list | None = None) -> dict:
    """FAQ 富结果 2026-05 弃用 — 检测 FAQPage schema 仍存在则触发"""
    has_faqpage = any(isinstance(b, dict) and b.get("@type") == "FAQPage" for b in (jsonld or []))
    return {
        "has_faqpage_schema": has_faqpage,
        "suspect_deprecated_faqpage": has_faqpage,  # FAQ 弃用了，still 用就触发提示
    }


def deprecated_howto_check(jsonld: list | None = None) -> dict:
    has_howto = any(isinstance(b, dict) and b.get("@type") == "HowTo" for b in (jsonld or []))
    return {
        "has_howto_schema": has_howto,
        "suspect_deprecated_howto": has_howto,
    }


def breadcrumb_position_check(jsonld: list | None = None) -> dict:
    for b in (jsonld or []):
        if isinstance(b, dict) and b.get("@type") == "BreadcrumbList":
            items = b.get("itemListElement", [])
            positions = [i.get("position") for i in items if isinstance(i, dict)]
            sequential = positions == list(range(1, len(positions) + 1))
            return {"positions": positions, "sequential": sequential}
    return {"checked": False}


def breadcrumblist_check(jsonld_parsed: list | None = None, page_url: str | None = None, page_hierarchy: list | None = None) -> dict:
    has = any(isinstance(b, dict) and b.get("@type") == "BreadcrumbList" for b in (jsonld_parsed or []))
    return {"has_breadcrumblist": has}


def syntax_validate(jsonld_raw: str | None = None) -> dict:
    if not jsonld_raw:
        return {"checked": False}
    try:
        json.loads(jsonld_raw)
        return {"valid": True}
    except json.JSONDecodeError as e:
        return {"valid": False, "error": str(e)}


def multiple_products_check(jsonld: list | None = None) -> dict:
    products = [b for b in (jsonld or []) if isinstance(b, dict) and b.get("@type") == "Product"]
    has_itemlist = any(isinstance(b, dict) and b.get("@type") == "ItemList" for b in (jsonld or []))
    return {"product_count": len(products), "has_itemlist": has_itemlist, "needs_itemlist": len(products) > 1 and not has_itemlist}


def organization_check(jsonld: list | None = None) -> dict:
    org = next((b for b in (jsonld or []) if isinstance(b, dict) and b.get("@type") in ("Organization", "Corporation")), None)
    if not org:
        return {"has_organization": False}
    required = ["name", "url", "logo"]
    missing = [r for r in required if not org.get(r)]
    return {"has_organization": True, "missing_fields": missing, "complete": not missing}


def sameas_check(jsonld: list | None = None) -> dict:
    for b in (jsonld or []):
        if isinstance(b, dict) and b.get("sameAs"):
            sas = b["sameAs"] if isinstance(b["sameAs"], list) else [b["sameAs"]]
            return {"sameas_count": len(sas), "sameas": sas[:5]}
    return {"sameas_count": 0}


def website_name_check(jsonld_parsed: list | None = None) -> dict:
    has = any(isinstance(b, dict) and b.get("@type") in ("WebSite", "Organization") for b in (jsonld_parsed or []))
    return {"has_website_or_org": has}


def sitelinks_searchbox_check(jsonld_parsed: list | None = None) -> dict:
    has_searchbox = any(isinstance(b, dict) and b.get("potentialAction", {}).get("@type") == "SearchAction" for b in (jsonld_parsed or []) if isinstance(b, dict))
    return {"has_sitelinks_searchbox": has_searchbox}


def newsarticle_completeness(jsonld: list | None = None) -> dict:
    for b in (jsonld or []):
        if isinstance(b, dict) and b.get("@type") in ("NewsArticle", "Article"):
            required = ["headline", "author", "datePublished", "publisher", "image"]
            missing = [r for r in required if not b.get(r)]
            return {"missing_fields": missing, "complete": not missing}
    return {"has_article": False}


def product_completeness(jsonld: list | None = None) -> dict:
    for b in (jsonld or []):
        if isinstance(b, dict) and b.get("@type") == "Product":
            required = ["name", "offers"]
            missing = [r for r in required if not b.get(r)]
            return {"missing_fields": missing}
    return {"has_product": False}


def brand_consistency(jsonld: list | None = None, visible_brand: str | None = None) -> dict:
    for b in (jsonld or []):
        if isinstance(b, dict) and b.get("brand"):
            brand_in_schema = b["brand"].get("name") if isinstance(b["brand"], dict) else b["brand"]
            if visible_brand and brand_in_schema != visible_brand:
                return {"consistent": False, "schema": brand_in_schema, "visible": visible_brand}
    return {"consistent": True}


def gtin_check(jsonld: list | None = None) -> dict:
    has_gtin = any(isinstance(b, dict) and (b.get("gtin") or b.get("mpn")) for b in (jsonld or []))
    return {"has_gtin_or_mpn": has_gtin}


def adult_consideration_check(jsonld: list | None = None, product_category: str | None = None) -> dict:
    has_field = any(isinstance(b, dict) and "hasAdultConsideration" in b for b in (jsonld or []))
    return {"has_field": has_field}


def get_jsonld_field(blocks: list[dict], path: str) -> str | None:
    """提取 JSON-LD 字段，如 'author.name' / 'copyrightNotice.email'"""
    parts = path.split(".")
    for block in blocks:
        if not isinstance(block, dict):
            continue
        cur = block
        for part in parts:
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                cur = None
                break
        if cur is not None:
            return str(cur)
    return None
