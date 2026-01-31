"""
Chunk Boundary Integrity Metric (PL-09).

Evaluates how well content splits at natural boundaries when
chunked for RAG retrieval.
"""
import re
from typing import Any, Dict, List

from ..base import BaseMetric


class ChunkBoundaryIntegrityMetric(BaseMetric):
    """
    Measures chunk boundary quality for RAG systems.

    Broken chunks (mid-sentence, mid-list) cause incomplete context
    and inconsistent answers from LLMs.

    Weight: 6%
    """

    name = "chunk_boundary_integrity"
    weight = 0.06
    description = "Measures chunk boundary quality for RAG systems"

    # Chunk sizes to test (tokens approximated as words * 1.3)
    CHUNK_SIZES = [500, 1000, 2000]

    # Sentence ending patterns
    SENTENCE_END_PATTERN = re.compile(r"[.!?]\s*$")
    PARAGRAPH_END_PATTERN = re.compile(r"\n\n\s*$")

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute chunk boundary integrity score.

        Args:
            extracted_text: Main content text.

        Returns:
            Metric result with boundary quality stats.
        """
        extracted_text: str = kwargs.get("extracted_text", "")

        if not extracted_text or len(extracted_text.split()) < 100:
            return self._base_result(
                1.0,
                chunk_sizes_tested=[],
                total_chunks=0,
                clean_boundary_chunks=0,
                integrity_rate=1.0,
                note="Content too short to analyze chunking",
            )

        total_chunks = 0
        clean_boundary_chunks = 0
        broken_examples: List[str] = []

        for chunk_size in self.CHUNK_SIZES:
            chunks = self._split_into_chunks(extracted_text, chunk_size)
            
            for i, chunk in enumerate(chunks[:-1]):  # Skip last chunk
                total_chunks += 1
                
                if self._has_clean_boundary(chunk):
                    clean_boundary_chunks += 1
                else:
                    if len(broken_examples) < 3:
                        last_words = chunk[-50:].strip()
                        broken_examples.append(
                            f"Chunk {i+1} (size {chunk_size}) ends at '...{last_words}'"
                        )

        integrity_rate = (
            clean_boundary_chunks / total_chunks if total_chunks > 0 else 1.0
        )

        return self._base_result(
            score=integrity_rate,
            chunk_sizes_tested=self.CHUNK_SIZES,
            total_chunks=total_chunks,
            clean_boundary_chunks=clean_boundary_chunks,
            integrity_rate=round(integrity_rate, 3),
            broken_examples=broken_examples,
        )

    def _split_into_chunks(self, text: str, target_size: int) -> List[str]:
        """
        Split text into chunks of approximately target_size words.

        Args:
            text: Text to split.
            target_size: Target chunk size in tokens (approx words * 1.3).

        Returns:
            List of text chunks.
        """
        words = text.split()
        word_target = int(target_size / 1.3)  # Convert tokens to words
        chunks = []
        current_chunk: List[str] = []

        for word in words:
            current_chunk.append(word)
            if len(current_chunk) >= word_target:
                chunks.append(" ".join(current_chunk))
                current_chunk = []

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _has_clean_boundary(self, chunk: str) -> bool:
        """
        Check if chunk ends on a clean boundary.

        Args:
            chunk: Text chunk to check.

        Returns:
            True if ends on sentence/paragraph boundary.
        """
        chunk = chunk.rstrip()

        # Check for sentence end
        if self.SENTENCE_END_PATTERN.search(chunk):
            return True

        # Check for paragraph end (newlines before trimming)
        if chunk.endswith("\n"):
            return True

        # Check for list item end (common in structured content)
        if chunk.endswith(":") or chunk.endswith(";"):
            return True

        return False
