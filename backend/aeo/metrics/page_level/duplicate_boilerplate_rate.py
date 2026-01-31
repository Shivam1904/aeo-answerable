"""
Duplicate/Boilerplate Repetition Rate Metric (PL-10).

Measures the percentage of content that appears to be repeated
boilerplate across the page.
"""
import hashlib
import re
from typing import Any, Dict, List, Set

from bs4 import BeautifulSoup

from ..base import BaseMetric


class DuplicateBoilerplateRateMetric(BaseMetric):
    """
    Measures duplicate/boilerplate content rate.

    Boilerplate (nav, footers, cookie banners) pollutes embeddings
    and harms retrieval precision in RAG systems.

    Weight: 5%
    """

    name = "duplicate_boilerplate_rate"
    weight = 0.05
    description = "Measures duplicate/boilerplate content rate"

    # Common boilerplate patterns
    BOILERPLATE_PATTERNS = [
        r"cookie\s*(policy|consent|notice)",
        r"privacy\s*policy",
        r"terms\s*(of|and)\s*(service|use)",
        r"subscribe\s*to\s*(our|the)\s*newsletter",
        r"follow\s*us\s*on",
        r"all\s*rights\s*reserved",
        r"©\s*\d{4}",
        r"sign\s*up\s*for",
        r"share\s*(this|on)",
    ]

    # Minimum block length to consider (words)
    MIN_BLOCK_LENGTH = 10

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute duplicate/boilerplate rate score.

        Args:
            soup: BeautifulSoup parsed HTML.
            extracted_text: Main content text.

        Returns:
            Metric result with duplicate block stats.
        """
        soup: BeautifulSoup = kwargs.get("soup")
        extracted_text: str = kwargs.get("extracted_text", "")

        if not soup:
            return self._base_result(0.0, error="No soup provided")

        # Extract text blocks from the page
        blocks = self._extract_text_blocks(soup)
        
        if not blocks:
            return self._base_result(
                1.0,
                total_blocks=0,
                duplicate_blocks=0,
                boilerplate_blocks=0,
                duplicate_content_pct=0.0,
            )

        # Find duplicates and boilerplate
        duplicate_blocks = self._find_duplicate_blocks(blocks)
        boilerplate_blocks = self._find_boilerplate_blocks(blocks)

        # Combine unique problematic blocks
        problematic_indices: Set[int] = duplicate_blocks | boilerplate_blocks
        
        # Calculate duplicate content percentage by word count
        total_words = sum(len(b.split()) for b in blocks)
        problem_words = sum(
            len(blocks[i].split()) for i in problematic_indices
        )
        
        duplicate_pct = problem_words / total_words if total_words > 0 else 0.0

        # Examples of problematic content
        examples: List[str] = []
        for i in list(problematic_indices)[:3]:
            preview = blocks[i][:50].strip()
            examples.append(f"{preview}...")

        # Score: 0% problems = 1.0, 50%+ problems = 0.0
        score = max(0.0, 1.0 - (duplicate_pct * 2))

        return self._base_result(
            score=score,
            total_blocks=len(blocks),
            duplicate_blocks=len(duplicate_blocks),
            boilerplate_blocks=len(boilerplate_blocks),
            duplicate_content_pct=round(duplicate_pct, 3),
            duplicate_examples=examples,
        )

    def _extract_text_blocks(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract text blocks from semantic containers.

        Args:
            soup: Parsed HTML.

        Returns:
            List of text blocks.
        """
        blocks = []
        
        # Find all paragraph-like containers
        containers = soup.find_all(["p", "div", "li", "td", "section"])
        
        for container in containers:
            text = container.get_text(strip=True)
            words = text.split()
            
            if len(words) >= self.MIN_BLOCK_LENGTH:
                blocks.append(text)

        return blocks

    def _find_duplicate_blocks(self, blocks: List[str]) -> Set[int]:
        """
        Find indices of duplicate blocks using hash comparison.

        Args:
            blocks: List of text blocks.

        Returns:
            Set of indices that are duplicates.
        """
        seen_hashes: Dict[str, int] = {}
        duplicates: Set[int] = set()

        for i, block in enumerate(blocks):
            # Normalize and hash
            normalized = " ".join(block.lower().split())
            block_hash = hashlib.md5(normalized.encode()).hexdigest()

            if block_hash in seen_hashes:
                duplicates.add(i)
                duplicates.add(seen_hashes[block_hash])
            else:
                seen_hashes[block_hash] = i

        return duplicates

    def _find_boilerplate_blocks(self, blocks: List[str]) -> Set[int]:
        """
        Find indices of boilerplate blocks using pattern matching.

        Args:
            blocks: List of text blocks.

        Returns:
            Set of indices that are boilerplate.
        """
        boilerplate: Set[int] = set()

        for i, block in enumerate(blocks):
            block_lower = block.lower()
            
            for pattern in self.BOILERPLATE_PATTERNS:
                if re.search(pattern, block_lower, re.IGNORECASE):
                    boilerplate.add(i)
                    break

        return boilerplate
