"""
AEO Metrics Module.

This module provides a modular system for computing Answer Engine Optimization
metrics at both page-level and site-level granularity.
"""
from typing import Dict, Any, List

from .base import MetricRegistry
from .page_level import PAGE_LEVEL_METRICS
from .site_level import SITE_LEVEL_METRICS


def compute_page_metrics(
    html: str,
    soup: Any,
    extracted_text: str,
    url: str,
    json_ld: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Compute all page-level metrics for a single page.

    Args:
        html: Raw HTML string.
        soup: Parsed BeautifulSoup object.
        extracted_text: Main content text extracted from page.
        url: The page URL.
        json_ld: Parsed JSON-LD structured data blocks.

    Returns:
        Dictionary with metric results and weighted score.
    """
    results = {}
    weighted_sum = 0.0
    total_weight = 0.0

    for metric_cls in PAGE_LEVEL_METRICS:
        metric = metric_cls()
        try:
            result = metric.compute(
                html=html,
                soup=soup,
                extracted_text=extracted_text,
                url=url,
                json_ld=json_ld,
            )
            results[metric.name] = result
            weighted_sum += result["score"] * result["weight"]
            total_weight += result["weight"]
        except Exception as e:
            results[metric.name] = {
                "metric": metric.name,
                "error": str(e),
                "score": 0.0,
                "weight": metric.weight,
            }
            total_weight += metric.weight

    overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0

    return {
        "metrics": results,
        "page_score": round(overall_score, 3),
        "total_weight": round(total_weight, 3),
    }


def compute_site_metrics(
    pages: List[Dict[str, Any]],
    robots_txt: str,
    llms_txt: str,
    base_url: str,
) -> Dict[str, Any]:
    """
    Compute all site-level metrics across a crawled site.

    Args:
        pages: List of page data dictionaries from crawl.
        robots_txt: Content of robots.txt file.
        llms_txt: Content of llms.txt file (empty if not found).
        base_url: The base URL of the site.

    Returns:
        Dictionary with metric results and weighted score.
    """
    results = {}
    weighted_sum = 0.0
    total_weight = 0.0

    for metric_cls in SITE_LEVEL_METRICS:
        metric = metric_cls()
        try:
            result = metric.compute(
                pages=pages,
                robots_txt=robots_txt,
                llms_txt=llms_txt,
                base_url=base_url,
            )
            results[metric.name] = result
            weighted_sum += result["score"] * result["weight"]
            total_weight += result["weight"]
        except Exception as e:
            results[metric.name] = {
                "metric": metric.name,
                "error": str(e),
                "score": 0.0,
                "weight": metric.weight,
            }
            total_weight += metric.weight

    overall_score = weighted_sum / total_weight if total_weight > 0 else 0.0

    return {
        "metrics": results,
        "site_score": round(overall_score, 3),
        "total_weight": round(total_weight, 3),
    }


__all__ = [
    "compute_page_metrics",
    "compute_site_metrics",
    "MetricRegistry",
    "PAGE_LEVEL_METRICS",
    "SITE_LEVEL_METRICS",
]
