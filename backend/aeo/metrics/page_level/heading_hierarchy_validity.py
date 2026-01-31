"""
Heading Hierarchy Validity Metric (PL-05).

Checks for proper heading structure: single H1, no skipped levels,
logical nesting order.
"""
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from ..base import BaseMetric


class HeadingHierarchyValidityMetric(BaseMetric):
    """
    Validates heading hierarchy for proper document structure.

    Checks:
    - Exactly one H1 tag
    - No skipped heading levels (H1 → H3 without H2)
    - Logical nesting order

    Weight: 6%
    """

    name = "heading_hierarchy_validity"
    weight = 0.06
    description = "Validates heading hierarchy for proper document structure"

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute heading hierarchy validity score.

        Args:
            soup: BeautifulSoup parsed HTML.

        Returns:
            Metric result with h1_count, skipped_levels, and score.
        """
        soup: BeautifulSoup = kwargs.get("soup")
        if not soup:
            return self._base_result(0.0, error="No soup provided")

        # Find all headings
        h1_tags = soup.find_all("h1")
        h1_count = len(h1_tags)

        # Get all headings in order
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        
        # Track skipped levels
        skipped_levels: List[str] = []
        last_level = 0

        for h in headings:
            current_level = int(h.name[1])
            
            # Check for skipped levels (deeper than +1)
            if current_level > last_level + 1 and last_level > 0:
                heading_text = h.get_text(strip=True)[:40]
                skipped_levels.append(
                    f"H{last_level} → H{current_level} at '{heading_text}...'"
                )
            
            last_level = current_level

        # Calculate score
        score = 1.0

        # Penalize missing H1
        if h1_count == 0:
            score -= 0.3

        # Penalize multiple H1s
        if h1_count > 1:
            score -= 0.2

        # Penalize each skipped level
        score -= 0.1 * len(skipped_levels)

        # Ensure score is in valid range
        score = max(0.0, min(1.0, score))

        return self._base_result(
            score=score,
            h1_count=h1_count,
            total_headings=len(headings),
            skipped_levels=skipped_levels,
            hierarchy_valid=h1_count == 1 and len(skipped_levels) == 0,
        )
