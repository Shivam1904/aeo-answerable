"""
Main Content Detectability Metric (PL-02).

Checks for semantic landmarks (<main>, <article>) and validates
that content extractors can successfully isolate meaningful text.
"""
from typing import Any, Dict

from bs4 import BeautifulSoup

from ..base import BaseMetric
from ..utils.readability import extract_main_content, has_main_landmarks


class MainContentDetectabilityMetric(BaseMetric):
    """
    Measures how easily main content can be detected and extracted.

    If extractors can't isolate the article body, RAG systems and
    AI crawlers will ingest navigation, ads, or nothing.

    Weight: 7%
    """

    name = "main_content_detectability"
    weight = 0.07
    description = "Measures how easily main content can be detected and extracted"

    # Minimum word count for successful extraction
    MIN_WORDS = 100

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute main content detectability score.

        Args:
            soup: BeautifulSoup parsed HTML.

        Returns:
            Metric result with landmark flags and extraction success.
        """
        soup: BeautifulSoup = kwargs.get("soup")
        if not soup:
            return self._base_result(0.0, error="No soup provided")

        # Check for semantic landmarks
        landmarks = has_main_landmarks(soup)
        has_landmarks = landmarks["has_main_tag"] or landmarks["has_article_tag"]

        # Try content extraction
        extracted_text, extractor_success = extract_main_content(soup)
        word_count = len(extracted_text.split()) if extracted_text else 0

        # Determine extraction quality
        extraction_quality = "none"
        if word_count >= self.MIN_WORDS:
            extraction_quality = "good"
        elif word_count >= 50:
            extraction_quality = "partial"

        # Calculate score
        if has_landmarks and extractor_success:
            score = 1.0
        elif has_landmarks or extractor_success:
            score = 0.6
        elif word_count >= 50:
            score = 0.3
        else:
            score = 0.0

        return self._base_result(
            score=score,
            has_main_tag=landmarks["has_main_tag"],
            has_article_tag=landmarks["has_article_tag"],
            has_section_tags=landmarks["has_section_tags"],
            extractor_word_count=word_count,
            extractor_success=extractor_success,
            extraction_quality=extraction_quality,
        )
