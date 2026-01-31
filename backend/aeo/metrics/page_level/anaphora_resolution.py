"""
Anaphora Resolution Score Metric (PL-08).

Measures pronoun usage and potential resolution issues that
could cause ambiguity when content is chunked.
"""
import re
from typing import Any, Dict, List

from ..base import BaseMetric


class AnaphoraResolutionMetric(BaseMetric):
    """
    Measures pronoun clarity and resolution potential.

    Pronouns with unclear or distant antecedents create
    ambiguous chunks that harm LLM understanding.

    Weight: 7%
    """

    name = "anaphora_resolution"
    weight = 0.07
    description = "Measures pronoun clarity and resolution potential"

    # Pronouns to analyze
    PRONOUNS = [
        "it", "its", "itself",
        "this", "that", "these", "those",
        "they", "them", "their", "theirs",
        "he", "him", "his", "himself",
        "she", "her", "hers", "herself",
    ]

    # Maximum acceptable pronoun density
    MAX_PRONOUN_DENSITY = 0.08  # 8% of words
    
    # Ideal pronoun density
    IDEAL_PRONOUN_DENSITY = 0.03  # 3% of words

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute anaphora resolution score.

        Args:
            extracted_text: Main content text.

        Returns:
            Metric result with pronoun stats.
        """
        extracted_text: str = kwargs.get("extracted_text", "")

        if not extracted_text:
            return self._base_result(0.0, error="No text provided")

        words = extracted_text.lower().split()
        total_words = len(words)

        if total_words < 50:
            return self._base_result(
                1.0,
                total_pronouns=0,
                pronoun_density=0.0,
                note="Content too short to analyze",
            )

        # Count pronouns
        pronoun_count = sum(1 for w in words if w.strip(".,;:!?") in self.PRONOUNS)
        pronoun_density = pronoun_count / total_words

        # Find potentially problematic pronouns (at paragraph starts)
        paragraph_start_pronouns = self._find_paragraph_start_pronouns(extracted_text)

        # Find distant pronouns (far from likely antecedent)
        ambiguous_examples = self._find_ambiguous_pronouns(extracted_text)

        # Calculate resolution rate estimate
        # Higher density = more potential issues
        resolution_rate = max(0.0, 1.0 - (pronoun_density / self.MAX_PRONOUN_DENSITY))

        # Calculate score
        if pronoun_density <= self.IDEAL_PRONOUN_DENSITY:
            score = 1.0
        elif pronoun_density >= self.MAX_PRONOUN_DENSITY:
            score = 0.5  # Not zero, just not great
        else:
            # Linear interpolation
            excess = pronoun_density - self.IDEAL_PRONOUN_DENSITY
            range_size = self.MAX_PRONOUN_DENSITY - self.IDEAL_PRONOUN_DENSITY
            score = 1.0 - (0.5 * (excess / range_size))

        # Additional penalty for paragraph-start pronouns
        if paragraph_start_pronouns > 3:
            score -= 0.1

        score = max(0.0, min(1.0, score))

        return self._base_result(
            score=score,
            total_pronouns=pronoun_count,
            word_count=total_words,
            pronoun_density=round(pronoun_density, 4),
            paragraph_start_pronouns=paragraph_start_pronouns,
            resolution_rate=round(resolution_rate, 3),
            ambiguous_examples=ambiguous_examples[:3],
        )

    def _find_paragraph_start_pronouns(self, text: str) -> int:
        """
        Count pronouns at the start of paragraphs.

        These are particularly problematic for chunked retrieval.

        Args:
            text: Full text content.

        Returns:
            Count of paragraph-starting pronouns.
        """
        count = 0
        paragraphs = text.split("\n\n")

        for para in paragraphs:
            para = para.strip()
            if para:
                first_word = para.split()[0].lower().strip(".,;:!?") if para.split() else ""
                if first_word in self.PRONOUNS:
                    count += 1

        return count

    def _find_ambiguous_pronouns(self, text: str) -> List[str]:
        """
        Find examples of potentially ambiguous pronoun usage.

        Args:
            text: Full text content.

        Returns:
            List of example snippets.
        """
        examples = []
        sentences = re.split(r"[.!?]\s+", text)

        for sentence in sentences:
            words = sentence.lower().split()
            
            # Check if sentence starts with ambiguous pronoun
            if words and words[0].strip(".,;:!?") in ["it", "this", "that"]:
                preview = sentence[:60].strip()
                examples.append(f"'{preview}...'")

                if len(examples) >= 5:
                    break

        return examples
