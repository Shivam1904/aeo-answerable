"""
Citation & Source Attribution Density Metric (PL-14).

Measures how well factual claims are backed by citations
and source attributions.
"""
import re
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from ..base import BaseMetric


class CitationSourceDensityMetric(BaseMetric):
    """
    Measures citation and source attribution coverage.

    Attributed facts are easier for AI systems to trust
    and reuse in generated answers.

    Weight: 4%
    """

    name = "citation_source_density"
    weight = 0.04
    description = "Measures citation and source attribution coverage"

    # Patterns indicating factual claims
    FACTUAL_PATTERNS = [
        r"\d+%",                           # Percentages
        r"\$[\d,]+",                        # Dollar amounts
        r"\d{4}",                           # Years
        r"studies?\s+(show|found|indicate)",
        r"according\s+to",
        r"research\s+(shows?|suggests?)",
        r"\d+\s+(million|billion|thousand)",
    ]

    # Patterns indicating citations/attributions
    CITATION_PATTERNS = [
        r"source:",
        r"citation:",
        r"\[\d+\]",                         # Footnote markers
        r"\(\d{4}\)",                       # Year citations
        r"according\s+to\s+[A-Z]",          # Named source
        r"per\s+[A-Z]",
    ]

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute citation and source attribution score.

        Args:
            soup: BeautifulSoup parsed HTML.
            extracted_text: Main content text.

        Returns:
            Metric result with citation stats.
        """
        soup: BeautifulSoup = kwargs.get("soup")
        extracted_text: str = kwargs.get("extracted_text", "")

        if not soup:
            return self._base_result(0.0, error="No soup provided")

        # Count factual claims
        factual_claims = self._count_factual_claims(extracted_text)

        # Count citations in text
        text_citations = self._count_text_citations(extracted_text)

        # Count citation links
        citation_links = self._count_citation_links(soup)

        # Count cite tags
        cite_tags = len(soup.find_all("cite"))

        total_citations = text_citations + citation_links + cite_tags

        # Calculate attribution rate
        if factual_claims == 0:
            attribution_rate = 1.0  # No claims to attribute
        else:
            # Assume each citation can support multiple claims
            attribution_rate = min(1.0, total_citations / (factual_claims * 0.5))

        # Score based on attribution rate
        score = attribution_rate

        return self._base_result(
            score=score,
            factual_claims_detected=factual_claims,
            text_citations=text_citations,
            citation_links=citation_links,
            cite_tags=cite_tags,
            total_citations=total_citations,
            attribution_rate=round(attribution_rate, 3),
        )

    def _count_factual_claims(self, text: str) -> int:
        """
        Count sentences that appear to contain factual claims.

        Args:
            text: Content text.

        Returns:
            Number of detected factual claims.
        """
        if not text:
            return 0

        count = 0
        sentences = re.split(r"[.!?]\s+", text)

        for sentence in sentences:
            for pattern in self.FACTUAL_PATTERNS:
                if re.search(pattern, sentence, re.IGNORECASE):
                    count += 1
                    break  # Only count once per sentence

        return count

    def _count_text_citations(self, text: str) -> int:
        """
        Count citation patterns in text.

        Args:
            text: Content text.

        Returns:
            Number of citation patterns found.
        """
        if not text:
            return 0

        count = 0
        for pattern in self.CITATION_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            count += len(matches)

        return count

    def _count_citation_links(self, soup: BeautifulSoup) -> int:
        """
        Count links that appear to be citations/sources.

        Args:
            soup: Parsed HTML.

        Returns:
            Number of citation-like links.
        """
        count = 0
        links = soup.find_all("a", href=True)

        for link in links:
            href = link.get("href", "")
            text = link.get_text(strip=True).lower()

            # Check for external links (likely sources)
            if href.startswith("http") and not self._is_navigation_link(href, text):
                # Check for source-like text
                if any(word in text for word in ["source", "study", "research", "report", "data"]):
                    count += 1
                # Check for citation-like patterns
                elif re.match(r"^\[\d+\]$", text):
                    count += 1
                elif re.match(r"^\d+$", text):  # Footnote number
                    count += 1

        return count

    def _is_navigation_link(self, href: str, text: str) -> bool:
        """
        Check if a link is likely navigation rather than citation.

        Args:
            href: Link URL.
            text: Link text.

        Returns:
            True if likely navigation.
        """
        nav_patterns = [
            "home", "about", "contact", "menu", "navigation",
            "twitter", "facebook", "instagram", "linkedin",
            "share", "comment", "reply",
        ]

        text_lower = text.lower()
        href_lower = href.lower()

        for pattern in nav_patterns:
            if pattern in text_lower or pattern in href_lower:
                return True

        return False
