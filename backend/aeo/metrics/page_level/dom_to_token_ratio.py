"""
DOM-to-Token Ratio Metric (PL-01).

Measures the ratio of meaningful text tokens to total HTML tokens,
indicating content efficiency for LLM context windows.
"""
from typing import Any, Dict

from bs4 import BeautifulSoup

from ..base import BaseMetric
from ..utils.tokenizer import count_tokens


class DOMToTokenRatioMetric(BaseMetric):
    """
    Measures content efficiency via DOM-to-token ratio.

    High HTML bloat wastes LLM context window and may cause
    truncation of answer-relevant text.

    Weight: 8%
    """

    name = "dom_to_token_ratio"
    weight = 0.08
    description = "Measures content efficiency via DOM-to-token ratio"

    # Thresholds for scoring
    EXCELLENT_RATIO = 0.5  # 50% of tokens are content = perfect
    POOR_RATIO = 0.1      # 10% of tokens are content = 0 score

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute DOM-to-token ratio score.

        Args:
            html: Raw HTML string.
            extracted_text: Main content text.

        Returns:
            Metric result with token counts and ratio.
        """
        html: str = kwargs.get("html", "")
        extracted_text: str = kwargs.get("extracted_text", "")

        if not html:
            return self._base_result(0.0, error="No HTML provided")

        # Count tokens in raw HTML
        html_tokens = count_tokens(html)

        # Count tokens in extracted text
        text_tokens = count_tokens(extracted_text) if extracted_text else 0

        # Calculate ratio
        if html_tokens == 0:
            ratio = 0.0
        else:
            ratio = text_tokens / html_tokens

        # Calculate score (linear scale)
        # ratio >= 0.5 = 1.0, ratio <= 0.1 = 0.0
        if ratio >= self.EXCELLENT_RATIO:
            score = 1.0
        elif ratio <= self.POOR_RATIO:
            score = 0.0
        else:
            # Linear interpolation
            score = (ratio - self.POOR_RATIO) / (self.EXCELLENT_RATIO - self.POOR_RATIO)

        return self._base_result(
            score=score,
            html_tokens=html_tokens,
            text_tokens=text_tokens,
            ratio=round(ratio, 4),
            efficiency_rating=self._get_rating(ratio),
        )

    def _get_rating(self, ratio: float) -> str:
        """Get human-readable efficiency rating."""
        if ratio >= 0.4:
            return "excellent"
        elif ratio >= 0.25:
            return "good"
        elif ratio >= 0.15:
            return "fair"
        else:
            return "poor"
