"""
Schema Coverage by Intent Metric (PL-12).

Checks if the page has the appropriate schema type for its
detected content intent.
"""
import re
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup

from ..base import BaseMetric
from ..utils.schema_parser import extract_json_ld, get_schema_types


class SchemaCoverageByIntentMetric(BaseMetric):
    """
    Measures schema type appropriateness for page intent.

    "Right schema for the job" improves machine interpretation
    and rich result eligibility.

    Weight: 6%
    """

    name = "schema_coverage_by_intent"
    weight = 0.06
    description = "Measures schema type appropriateness for page intent"

    # Intent detection patterns and expected schema types
    INTENT_PATTERNS: List[Tuple[str, List[str], List[str]]] = [
        # (intent_name, content_patterns, expected_schema_types)
        (
            "article",
            [r"publish", r"author", r"posted", r"written\s+by", r"article", r"blog"],
            ["Article", "NewsArticle", "BlogPosting"],
        ),
        (
            "product",
            [r"price", r"\$\d+", r"add\s+to\s+cart", r"buy\s+now", r"product", r"shop"],
            ["Product", "Offer"],
        ),
        (
            "how-to",
            [r"step\s+\d+", r"how\s+to", r"tutorial", r"guide", r"instructions"],
            ["HowTo", "Article"],
        ),
        (
            "faq",
            [r"faq", r"frequently\s+asked", r"questions?\s+and\s+answers?"],
            ["FAQPage", "Question"],
        ),
        (
            "recipe",
            [r"ingredients?", r"servings?", r"cook\s+time", r"prep\s+time", r"recipe"],
            ["Recipe"],
        ),
        (
            "event",
            [r"event", r"date:", r"location:", r"register", r"tickets?"],
            ["Event"],
        ),
        (
            "local-business",
            [r"hours:", r"address:", r"phone:", r"contact\s+us", r"location"],
            ["LocalBusiness", "Organization"],
        ),
    ]

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute schema coverage by intent score.

        Args:
            soup: BeautifulSoup parsed HTML.
            extracted_text: Main content text.
            json_ld: Pre-parsed JSON-LD blocks (optional).

        Returns:
            Metric result with intent/schema match status.
        """
        soup: BeautifulSoup = kwargs.get("soup")
        extracted_text: str = kwargs.get("extracted_text", "")
        json_ld: List[Dict[str, Any]] = kwargs.get("json_ld", [])

        if not soup:
            return self._base_result(0.0, error="No soup provided")

        # Extract JSON-LD if not provided
        if not json_ld:
            json_ld = extract_json_ld(soup)

        # Detect page intent
        detected_intent, confidence = self._detect_intent(extracted_text, soup)
        expected_types = self._get_expected_types(detected_intent)

        # Get actual schema types
        found_types = get_schema_types(json_ld)

        # Check for match
        intent_match = any(t in found_types for t in expected_types)

        # Calculate score
        if not detected_intent:
            # Can't determine intent - neutral score
            score = 0.7
        elif intent_match:
            score = 1.0
        elif found_types:
            # Has schema, but wrong type
            score = 0.5
        else:
            # No schema at all
            score = 0.0

        return self._base_result(
            score=score,
            detected_intent=detected_intent or "unknown",
            intent_confidence=round(confidence, 3),
            expected_schema_types=expected_types,
            found_schema_types=found_types,
            intent_schema_match=intent_match,
        )

    def _detect_intent(
        self, text: str, soup: BeautifulSoup
    ) -> Tuple[Optional[str], float]:
        """
        Detect the page's content intent.

        Args:
            text: Content text.
            soup: Parsed HTML.

        Returns:
            Tuple of (intent_name, confidence_score).
        """
        if not text:
            return None, 0.0

        text_lower = text.lower()
        title_text = ""
        title_tag = soup.find("title")
        if title_tag:
            title_text = title_tag.get_text().lower()

        combined_text = f"{title_text} {text_lower}"

        best_intent = None
        best_score = 0.0

        for intent_name, patterns, _ in self.INTENT_PATTERNS:
            matches = 0
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    matches += 1

            # Score based on percentage of patterns matched
            if patterns:
                score = matches / len(patterns)
                if score > best_score:
                    best_score = score
                    best_intent = intent_name

        # Require at least 20% confidence to declare intent
        if best_score < 0.2:
            return None, 0.0

        return best_intent, best_score

    def _get_expected_types(self, intent: Optional[str]) -> List[str]:
        """
        Get expected schema types for an intent.

        Args:
            intent: Detected intent name.

        Returns:
            List of expected schema type names.
        """
        if not intent:
            return []

        for intent_name, _, expected_types in self.INTENT_PATTERNS:
            if intent_name == intent:
                return expected_types

        return []
