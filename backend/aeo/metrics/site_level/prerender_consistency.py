"""
Prerender Consistency Metric (SL-03).

Compares content between raw HTML and JavaScript-rendered HTML
to detect JS-only content issues.
"""
from typing import Any, Dict, List

from ..base import BaseMetric


class PrerenderConsistencyMetric(BaseMetric):
    """
    Measures prerender consistency between raw and rendered HTML.

    Some crawlers don't execute JavaScript; SSR/SSG improves
    visibility and ensures content is accessible.

    Weight: 7%
    """

    name = "prerender_consistency"
    weight = 0.07
    description = "Measures prerender consistency between raw and rendered HTML"

    # Thresholds
    CONTENT_RATIO_THRESHOLD = 0.5  # Raw should have at least 50% of rendered content
    HEADING_RATIO_THRESHOLD = 0.5

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute prerender consistency score.

        Args:
            pages: List of page data with raw_word_count and rendered_word_count.

        Returns:
            Metric result with consistency details.
        """
        pages: List[Dict[str, Any]] = kwargs.get("pages", [])

        if not pages:
            return self._base_result(
                1.0,
                pages_analyzed=0,
                note="No pages to analyze",
            )

        total_consistency = 0.0
        pages_analyzed = 0
        js_only_pages: List[str] = []

        for page in pages:
            raw_words = page.get("raw_word_count", 0)
            rendered_words = page.get("rendered_word_count", 0)
            raw_headings = page.get("raw_heading_count", 0)
            rendered_headings = page.get("rendered_heading_count", 0)
            raw_schema = page.get("raw_schema_present", False)
            rendered_schema = page.get("rendered_schema_present", False)
            url = page.get("url", "Unknown")

            # Calculate content ratio
            if rendered_words > 0:
                content_ratio = raw_words / rendered_words
            else:
                content_ratio = 1.0 if raw_words == 0 else 0.0

            # Calculate heading ratio
            if rendered_headings > 0:
                heading_ratio = raw_headings / rendered_headings
            else:
                heading_ratio = 1.0 if raw_headings == 0 else 0.0

            # Check for JS-only critical content
            is_js_only = (
                content_ratio < self.CONTENT_RATIO_THRESHOLD and
                rendered_words > 100
            )

            if is_js_only:
                js_only_pages.append(url)

            # Page consistency score
            page_score = (content_ratio + heading_ratio) / 2
            page_score = min(1.0, page_score)

            # Schema penalty
            if rendered_schema and not raw_schema:
                page_score -= 0.2

            total_consistency += max(0.0, page_score)
            pages_analyzed += 1

        avg_consistency = total_consistency / pages_analyzed if pages_analyzed > 0 else 1.0

        return self._base_result(
            score=avg_consistency,
            pages_analyzed=pages_analyzed,
            js_only_pages=js_only_pages[:5],
            js_only_count=len(js_only_pages),
            critical_content_js_only=len(js_only_pages) > 0,
            recommendation=self._get_recommendation(js_only_pages),
        )

    def _get_recommendation(self, js_only_pages: List[str]) -> str:
        """
        Generate recommendation based on findings.

        Args:
            js_only_pages: List of pages with JS-only content.

        Returns:
            Recommendation string.
        """
        if not js_only_pages:
            return "Content is well-prerendered for non-JS crawlers."
        
        return (
            f"{len(js_only_pages)} page(s) have critical content that only "
            "appears after JavaScript execution. Consider implementing SSR/SSG."
        )
