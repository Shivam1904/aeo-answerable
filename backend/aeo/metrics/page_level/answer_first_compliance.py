"""
Answer-First Compliance Metric (PL-07).

Checks if sections begin with direct answers/definitions
rather than introductory fluff.
"""
import re
from typing import Any, Dict, List, Tuple

from bs4 import BeautifulSoup, Tag

from ..base import BaseMetric


class AnswerFirstComplianceMetric(BaseMetric):
    """
    Measures answer-first writing pattern compliance.

    Sections where the first sentence directly answers/defines
    the heading's intent are easier to extract and cite.

    Weight: 7%
    """

    name = "answer_first_compliance"
    weight = 0.07
    description = "Measures answer-first writing pattern compliance"

    # Patterns indicating answer-first content
    ANSWER_PATTERNS = [
        r"^[A-Z][^.]*\s+is\s+",              # "X is..."
        r"^[A-Z][^.]*\s+are\s+",             # "X are..."
        r"^[A-Z][^.]*\s+means\s+",           # "X means..."
        r"^[A-Z][^.]*\s+refers?\s+to\s+",    # "X refers to..."
        r"^To\s+[a-z]+\s+",                  # "To do X..."
        r"^The\s+[a-z]+\s+(is|are)\s+",      # "The X is..."
        r"^Yes[,.]",                          # "Yes, ..."
        r"^No[,.]",                           # "No, ..."
        r"^\d+",                              # Starts with number
    ]

    # Patterns indicating fluff/non-answer starts
    FLUFF_PATTERNS = [
        r"^(Many|Most|Some)\s+people\s+(wonder|ask|think)",
        r"^In\s+this\s+(article|post|guide)",
        r"^(Have\s+you\s+ever|Did\s+you\s+know)",
        r"^(Let's|Let\s+us)\s+(take\s+a\s+look|explore|dive)",
        r"^(Before|First)\s+we\s+(begin|start|dive)",
        r"^(As\s+you\s+may\s+know|Obviously)",
    ]

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute answer-first compliance score.

        Args:
            soup: BeautifulSoup parsed HTML.

        Returns:
            Metric result with compliance stats.
        """
        soup: BeautifulSoup = kwargs.get("soup")
        if not soup:
            return self._base_result(0.0, error="No soup provided")

        # Get heading-content pairs
        sections = self._extract_sections(soup)

        if not sections:
            return self._base_result(
                1.0,
                sections_analyzed=0,
                compliant_sections=0,
                compliance_rate=1.0,
                note="No sections with headings found",
            )

        compliant_count = 0
        non_compliant_examples: List[str] = []

        for heading_text, first_sentences in sections:
            if self._is_answer_first(first_sentences):
                compliant_count += 1
            else:
                if len(non_compliant_examples) < 3:
                    preview = first_sentences[:60].strip()
                    non_compliant_examples.append(
                        f"'{heading_text}' section starts with '{preview}...'"
                    )

        compliance_rate = compliant_count / len(sections) if sections else 1.0

        return self._base_result(
            score=compliance_rate,
            sections_analyzed=len(sections),
            compliant_sections=compliant_count,
            compliance_rate=round(compliance_rate, 3),
            non_compliant_examples=non_compliant_examples,
        )

    def _extract_sections(
        self, soup: BeautifulSoup
    ) -> List[Tuple[str, str]]:
        """
        Extract heading + first sentences pairs.

        Args:
            soup: Parsed HTML.

        Returns:
            List of (heading_text, first_sentences) tuples.
        """
        sections = []
        headings = soup.find_all(["h2", "h3", "h4", "h5", "h6"])

        for heading in headings:
            heading_text = heading.get_text(strip=True)
            if not heading_text:
                continue

            # Get text content after heading
            first_sentences = self._get_following_text(heading)
            if first_sentences:
                sections.append((heading_text, first_sentences))

        return sections

    def _get_following_text(self, heading: Tag) -> str:
        """
        Get the first 1-2 sentences following a heading.

        Args:
            heading: Heading tag element.

        Returns:
            First sentences as string.
        """
        text_parts = []
        current = heading.find_next_sibling()
        word_count = 0

        while current and word_count < 50:
            if isinstance(current, Tag):
                if current.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    break
                text = current.get_text(strip=True)
                if text:
                    text_parts.append(text)
                    word_count += len(text.split())
            current = current.find_next_sibling()

        return " ".join(text_parts)[:200]

    def _is_answer_first(self, text: str) -> bool:
        """
        Determine if text follows answer-first pattern.

        Args:
            text: First sentences of section.

        Returns:
            True if answer-first pattern detected.
        """
        if not text:
            return True  # Empty sections don't count against

        # Check for fluff patterns (negative signal)
        for pattern in self.FLUFF_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return False

        # Check for answer patterns (positive signal)
        for pattern in self.ANSWER_PATTERNS:
            if re.search(pattern, text):
                return True

        # Default: neither clearly good nor bad
        return True
