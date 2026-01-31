"""
Author & E-E-A-T Signals Metric (PL-16).

Measures the presence of author attribution, credentials,
and trust markers.
"""
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from ..base import BaseMetric
from ..utils.schema_parser import extract_json_ld, has_schema_type


class AuthorEEATSignalsMetric(BaseMetric):
    """
    Measures author and E-E-A-T signal presence.

    Author credentials and editorial markers help trust ranking
    and citation likelihood on sensitive topics.

    Weight: 3%
    """

    name = "author_eeat_signals"
    weight = 0.03
    description = "Measures author and E-E-A-T signal presence"

    # Credential patterns
    CREDENTIAL_PATTERNS = [
        r"\b(MD|PhD|Dr\.|M\.D\.|Ph\.D\.)\b",
        r"\b(MBA|JD|CPA|CFA|RN|LPN)\b",
        r"\b(Professor|Expert|Specialist|Consultant)\b",
        r"\b(certified|licensed|accredited)\b",
    ]

    # Editorial/review patterns
    EDITORIAL_PATTERNS = [
        r"fact[- ]?check",
        r"medically\s+reviewed",
        r"reviewed\s+by",
        r"edited\s+by",
        r"verified\s+by",
        r"expert\s+review",
    ]

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute author and E-E-A-T signals score.

        Args:
            soup: BeautifulSoup parsed HTML.
            extracted_text: Main content text.
            json_ld: Pre-parsed JSON-LD blocks (optional).

        Returns:
            Metric result with E-E-A-T signal details.
        """
        soup: BeautifulSoup = kwargs.get("soup")
        extracted_text: str = kwargs.get("extracted_text", "")
        json_ld: List[Dict[str, Any]] = kwargs.get("json_ld", [])

        if not soup:
            return self._base_result(0.0, error="No soup provided")

        # Extract JSON-LD if not provided
        if not json_ld:
            json_ld = extract_json_ld(soup)

        # Find author byline
        byline_info = self._find_author_byline(soup)
        has_byline = byline_info["found"]
        author_name = byline_info["name"]

        # Check for credentials
        credentials = self._find_credentials(soup, extracted_text)

        # Check for Person schema
        has_person_schema = has_schema_type(json_ld, "Person")

        # Check for author in Article schema
        has_schema_author = self._has_schema_author(json_ld)

        # Check for editorial/fact-check markers
        has_editorial = self._has_editorial_markers(soup, extracted_text)

        # Calculate score
        score = 0.0

        if has_byline:
            score += 0.3
        if author_name:
            score += 0.1
        if credentials:
            score += 0.25
        if has_person_schema or has_schema_author:
            score += 0.2
        if has_editorial:
            score += 0.15

        score = min(1.0, score)

        return self._base_result(
            score=score,
            has_author_byline=has_byline,
            author_name=author_name,
            has_credentials=len(credentials) > 0,
            credentials=credentials[:3],
            has_person_schema=has_person_schema,
            has_schema_author=has_schema_author,
            has_editorial_markers=has_editorial,
        )

    def _find_author_byline(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Find author byline in content.

        Args:
            soup: Parsed HTML.

        Returns:
            Dict with found status and author name.
        """
        result = {"found": False, "name": None}

        # Check for common byline patterns
        byline_selectors = [
            {"class_": re.compile(r"author|byline|writer", re.I)},
            {"rel": "author"},
            {"itemprop": "author"},
        ]

        for selector in byline_selectors:
            element = soup.find(**selector)
            if element:
                text = element.get_text(strip=True)
                if text and len(text) < 100:
                    result["found"] = True
                    # Extract name (remove "by " prefix if present)
                    name = re.sub(r"^(by|written by|author:?)\s*", "", text, flags=re.I)
                    if name and len(name) > 2:
                        result["name"] = name[:50]
                    break

        return result

    def _find_credentials(
        self, soup: BeautifulSoup, text: str
    ) -> List[str]:
        """
        Find credential mentions.

        Args:
            soup: Parsed HTML.
            text: Content text.

        Returns:
            List of found credentials.
        """
        credentials = []
        combined_text = f"{soup.get_text()} {text}"

        for pattern in self.CREDENTIAL_PATTERNS:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            credentials.extend(matches)

        # Deduplicate and clean
        return list(set(c.strip() for c in credentials if c.strip()))

    def _has_schema_author(self, json_ld: List[Dict[str, Any]]) -> bool:
        """
        Check if any schema block has an author property.

        Args:
            json_ld: JSON-LD blocks.

        Returns:
            True if author found in schema.
        """
        for block in json_ld:
            if "author" in block:
                return True
        return False

    def _has_editorial_markers(
        self, soup: BeautifulSoup, text: str
    ) -> bool:
        """
        Check for editorial/fact-check markers.

        Args:
            soup: Parsed HTML.
            text: Content text.

        Returns:
            True if editorial markers found.
        """
        combined_text = f"{soup.get_text()} {text}"

        for pattern in self.EDITORIAL_PATTERNS:
            if re.search(pattern, combined_text, re.IGNORECASE):
                return True

        return False
