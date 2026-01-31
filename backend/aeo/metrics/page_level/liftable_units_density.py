"""
Liftable Units Density Metric (PL-06).

Counts structured elements (lists, tables, FAQs, definition lists)
that are easy for LLMs to quote and cite accurately.
"""
import re
from typing import Any, Dict

from bs4 import BeautifulSoup

from ..base import BaseMetric


class LiftableUnitsDensityMetric(BaseMetric):
    """
    Measures density of structured, extractable content blocks.

    Counts:
    - Ordered/unordered lists (<ul>, <ol>)
    - Tables (<table>)
    - Definition lists (<dl>)
    - FAQ patterns (heading followed by answer)
    - Step markers (numbered instructions)

    Weight: 8%
    """

    name = "liftable_units_density"
    weight = 0.08
    description = "Measures density of structured, extractable content blocks"

    # Patterns for FAQ-like content
    FAQ_HEADING_PATTERNS = [
        r"^(what|how|why|when|where|who|can|does|is|are|should|will)\b",
        r"\?$",
    ]

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute liftable units density score.

        Args:
            soup: BeautifulSoup parsed HTML.
            extracted_text: Main content text for word count.

        Returns:
            Metric result with unit counts and density score.
        """
        soup: BeautifulSoup = kwargs.get("soup")
        extracted_text: str = kwargs.get("extracted_text", "")
        
        if not soup:
            return self._base_result(0.0, error="No soup provided")

        # Count various structured elements
        lists_count = len(soup.find_all(["ul", "ol"]))
        tables_count = len(soup.find_all("table"))
        definition_lists = len(soup.find_all("dl"))
        
        # Count FAQ patterns
        faq_patterns = self._count_faq_patterns(soup)
        
        # Count step markers (numbered instructions)
        step_markers = self._count_step_markers(soup)

        # Total units
        total_units = (
            lists_count +
            tables_count +
            definition_lists +
            faq_patterns +
            step_markers
        )

        # Calculate word count
        word_count = len(extracted_text.split()) if extracted_text else 1

        # Density per 1000 words
        density_per_1k = (total_units / word_count) * 1000 if word_count > 0 else 0

        # Score calculation: 5+ units/1k words = 1.0, 0 = 0.0
        # Linear scale between 0 and 5
        score = min(1.0, density_per_1k / 5.0)

        return self._base_result(
            score=score,
            lists_count=lists_count,
            tables_count=tables_count,
            definition_lists=definition_lists,
            faq_patterns=faq_patterns,
            step_markers=step_markers,
            total_units=total_units,
            word_count=word_count,
            density_per_1k=round(density_per_1k, 2),
        )

    def _count_faq_patterns(self, soup: BeautifulSoup) -> int:
        """Count FAQ-like heading + answer patterns."""
        count = 0
        headings = soup.find_all(["h2", "h3", "h4", "h5", "h6"])

        for h in headings:
            text = h.get_text(strip=True).lower()
            
            # Check for question patterns
            for pattern in self.FAQ_HEADING_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    # Verify there's content after the heading
                    next_elem = h.find_next_sibling()
                    if next_elem and next_elem.get_text(strip=True):
                        count += 1
                        break

        return count

    def _count_step_markers(self, soup: BeautifulSoup) -> int:
        """Count numbered step/instruction patterns."""
        count = 0

        # Check for ordered lists with step-like content
        for ol in soup.find_all("ol"):
            items = ol.find_all("li")
            if len(items) >= 2:
                count += 1

        # Check for "Step 1", "Step 2" patterns in text
        text = soup.get_text()
        step_matches = re.findall(r"step\s+\d+", text, re.IGNORECASE)
        if len(step_matches) >= 2:
            count += 1

        return count
