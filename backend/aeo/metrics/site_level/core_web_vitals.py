"""
Core Web Vitals / Render Latency Metric (SL-04).

Measures site performance via Core Web Vitals metrics.
"""
from typing import Any, Dict, List, Optional

from ..base import BaseMetric


class CoreWebVitalsMetric(BaseMetric):
    """
    Measures Core Web Vitals performance.

    Performance affects crawl success, timeouts, and overall
    extractability for AI systems.

    Weight: 4%
    """

    name = "core_web_vitals"
    weight = 0.04
    description = "Measures Core Web Vitals performance"

    # Core Web Vitals thresholds (Google's standards)
    LCP_THRESHOLDS = {"good": 2500, "poor": 4000}  # milliseconds
    CLS_THRESHOLDS = {"good": 0.1, "poor": 0.25}
    INP_THRESHOLDS = {"good": 200, "poor": 500}  # milliseconds

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute Core Web Vitals score.

        Args:
            pages: List of page data with performance metrics.

        Returns:
            Metric result with CWV details.
        """
        pages: List[Dict[str, Any]] = kwargs.get("pages", [])

        # Aggregate metrics from pages
        lcp_values = []
        cls_values = []
        inp_values = []

        for page in pages:
            perf = page.get("performance", {})
            if "lcp" in perf:
                lcp_values.append(perf["lcp"])
            if "cls" in perf:
                cls_values.append(perf["cls"])
            if "inp" in perf:
                inp_values.append(perf["inp"])

        # Calculate averages
        avg_lcp = sum(lcp_values) / len(lcp_values) if lcp_values else None
        avg_cls = sum(cls_values) / len(cls_values) if cls_values else None
        avg_inp = sum(inp_values) / len(inp_values) if inp_values else None

        # Rate each metric
        lcp_rating = self._rate_metric(avg_lcp, self.LCP_THRESHOLDS)
        cls_rating = self._rate_metric(avg_cls, self.CLS_THRESHOLDS)
        inp_rating = self._rate_metric(avg_inp, self.INP_THRESHOLDS)

        # Calculate overall score
        scores = []
        if lcp_rating:
            scores.append(self._rating_to_score(lcp_rating))
        if cls_rating:
            scores.append(self._rating_to_score(cls_rating))
        if inp_rating:
            scores.append(self._rating_to_score(inp_rating))

        if not scores:
            # No performance data available
            return self._base_result(
                0.7,  # Neutral score when no data
                data_source="none",
                note="No performance data available. Consider integrating CrUX or Lighthouse.",
            )

        overall_score = sum(scores) / len(scores)

        return self._base_result(
            score=overall_score,
            data_source="page_metrics",
            lcp_ms=round(avg_lcp) if avg_lcp else None,
            lcp_rating=lcp_rating,
            cls=round(avg_cls, 3) if avg_cls else None,
            cls_rating=cls_rating,
            inp_ms=round(avg_inp) if avg_inp else None,
            inp_rating=inp_rating,
            pages_with_metrics=len(lcp_values),
        )

    def _rate_metric(
        self, value: Optional[float], thresholds: Dict[str, float]
    ) -> Optional[str]:
        """
        Rate a metric value against thresholds.

        Args:
            value: Metric value.
            thresholds: Dict with 'good' and 'poor' thresholds.

        Returns:
            Rating string or None.
        """
        if value is None:
            return None

        if value <= thresholds["good"]:
            return "good"
        elif value >= thresholds["poor"]:
            return "poor"
        else:
            return "needs-improvement"

    def _rating_to_score(self, rating: Optional[str]) -> float:
        """
        Convert rating to numeric score.

        Args:
            rating: Rating string.

        Returns:
            Score between 0 and 1.
        """
        if rating == "good":
            return 1.0
        elif rating == "needs-improvement":
            return 0.5
        elif rating == "poor":
            return 0.0
        return 0.5  # Default for unknown
