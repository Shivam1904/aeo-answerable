"""
Heading Predictive Power Metric (PL-04).

Measures semantic similarity between headings and their
following content blocks.
"""
import re
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup, Tag

from ..base import BaseMetric


class HeadingPredictivePowerMetric(BaseMetric):
    """
    Measures how well headings predict their content.

    Headings act as retrieval anchors; if they don't match
    their content semantically, retrieval quality suffers.

    Weight: 10%
    """

    name = "heading_predictive_power"
    weight = 0.10
    description = "Measures how well headings predict their content"

    # Similarity threshold for "good" heading
    GOOD_SIMILARITY_THRESHOLD = 0.3
    EXCELLENT_SIMILARITY_THRESHOLD = 0.5

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute heading predictive power score.

        Uses word overlap as a simple similarity measure.
        For production, consider using sentence-transformers.

        Args:
            soup: BeautifulSoup parsed HTML.

        Returns:
            Metric result with heading similarity stats.
        """
        soup: BeautifulSoup = kwargs.get("soup")
        if not soup:
            return self._base_result(0.0, error="No soup provided")

        # Extract heading-content pairs
        pairs = self._extract_heading_content_pairs(soup)

        if not pairs:
            return self._base_result(
                1.0,
                headings_analyzed=0,
                avg_similarity=1.0,
                note="No headings with content found",
            )

        similarities = []
        low_similarity_headings: List[str] = []

        for heading_text, content_text in pairs:
            similarity = self._calculate_similarity(heading_text, content_text)
            similarities.append(similarity)

            if similarity < self.GOOD_SIMILARITY_THRESHOLD:
                low_similarity_headings.append(heading_text)

        avg_similarity = sum(similarities) / len(similarities)

        # Score based on average similarity
        if avg_similarity >= self.EXCELLENT_SIMILARITY_THRESHOLD:
            score = 1.0
        elif avg_similarity >= self.GOOD_SIMILARITY_THRESHOLD:
            # Scale between 0.7 and 1.0
            normalized = (avg_similarity - self.GOOD_SIMILARITY_THRESHOLD) / (
                self.EXCELLENT_SIMILARITY_THRESHOLD - self.GOOD_SIMILARITY_THRESHOLD
            )
            score = 0.7 + (0.3 * normalized)
        else:
            # Scale between 0.0 and 0.7
            normalized = avg_similarity / self.GOOD_SIMILARITY_THRESHOLD
            score = 0.7 * normalized

        # AGGRESSIVE REPORTING:
        # If score is not perfect (< 0.9) and we have no explicit failures,
        # fallback to showing the absolute lowest similarity headings as "weak".
        if score < 0.9 and not low_similarity_headings:
             # Sort pairs by similarity score
             sorted_pairs = sorted(zip(pairs, similarities), key=lambda x: x[1])
             # Take bottom 3
             low_similarity_headings = [p[0][0] for p in sorted_pairs[:3]]


        return self._base_result(
            score=score,
            headings_analyzed=len(pairs),
            avg_similarity=round(avg_similarity, 3),
            low_similarity_headings=low_similarity_headings[:5],
            similarity_distribution={
                "excellent": sum(1 for s in similarities if s >= self.EXCELLENT_SIMILARITY_THRESHOLD),
                "good": sum(1 for s in similarities if self.GOOD_SIMILARITY_THRESHOLD <= s < self.EXCELLENT_SIMILARITY_THRESHOLD),
                "poor": sum(1 for s in similarities if s < self.GOOD_SIMILARITY_THRESHOLD),
            },
        )

    def _extract_heading_content_pairs(
        self, soup: BeautifulSoup
    ) -> List[Tuple[str, str]]:
        """
        Extract heading text and following content pairs.

        Args:
            soup: Parsed HTML.

        Returns:
            List of (heading_text, content_text) tuples.
        """
        pairs = []
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

        for heading in headings:
            heading_text = heading.get_text(strip=True)
            if not heading_text or len(heading_text) < 3:
                continue

            content = self._get_following_content(heading, word_limit=100)
            if content and len(content.split()) >= 10:
                pairs.append((heading_text, content))

        return pairs

    def _get_following_content(self, heading: Tag, word_limit: int = 100) -> str:
        """
        Get content text following a heading.

        Args:
            heading: Heading tag.
            word_limit: Maximum words to collect.

        Returns:
            Content text string.
        """
        text_parts = []
        word_count = 0
        current = heading.find_next_sibling()

        while current and word_count < word_limit:
            if isinstance(current, Tag):
                if current.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    break
                text = current.get_text(strip=True)
                if text:
                    text_parts.append(text)
                    word_count += len(text.split())
            current = current.find_next_sibling()

        return " ".join(text_parts)

    def _calculate_similarity(self, heading: str, content: str) -> float:
        """
        Calculate semantic similarity using word overlap.

        For production, replace with embedding-based similarity.

        Args:
            heading: Heading text.
            content: Content text.

        Returns:
            Similarity score between 0 and 1.
        """
        # Normalize text
        heading_words = set(self._normalize_words(heading))
        content_words = set(self._normalize_words(content))

        if not heading_words:
            return 0.0

        # Calculate Jaccard-like overlap
        # Weight content overlap more since content has more words
        heading_in_content = sum(1 for w in heading_words if w in content_words)
        
        # Score based on what percentage of heading words appear in content
        coverage = heading_in_content / len(heading_words)

        return coverage

    def _normalize_words(self, text: str) -> List[str]:
        """
        Normalize text to word list for comparison.

        Args:
            text: Input text.

        Returns:
            List of normalized words.
        """
        # Remove punctuation and lowercase
        text = re.sub(r"[^\w\s]", "", text.lower())
        words = text.split()

        # Remove stopwords
        stopwords = {
            "a", "an", "the", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "to", "of", "in", "for", "on", "with", "at", "by",
            "from", "as", "into", "through", "during", "before", "after",
            "above", "below", "between", "under", "again", "further",
            "then", "once", "here", "there", "when", "where", "why",
            "how", "all", "each", "few", "more", "most", "other", "some",
            "such", "no", "nor", "not", "only", "own", "same", "so",
            "than", "too", "very", "just", "and", "but", "if", "or",
            "because", "until", "while", "this", "that", "these", "those",
        }

        return [w for w in words if w not in stopwords and len(w) > 2]
