"""
llms.txt Presence/Quality Metric (SL-02).

Checks for the presence and quality of the llms.txt file
that provides guidance to AI assistants.
"""
import re
from typing import Any, Dict, List

from ..base import BaseMetric


class LlmsTxtQualityMetric(BaseMetric):
    """
    Measures llms.txt file presence and quality.

    llms.txt provides curated entry points and guidance
    for AI assistants visiting the site.

    Weight: 3%
    """

    name = "llms_txt_quality"
    weight = 0.03
    description = "Measures llms.txt file presence and quality"

    # Expected sections in llms.txt
    EXPECTED_SECTIONS = [
        "title",
        "description",
        "url",
        "contact",
    ]

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute llms.txt quality score.

        Args:
            llms_txt: Content of llms.txt file.
            base_url: Base URL of the site.

        Returns:
            Metric result with llms.txt quality details.
        """
        llms_txt: str = kwargs.get("llms_txt", "")
        base_url: str = kwargs.get("base_url", "")

        if not llms_txt:
            return self._base_result(
                0.0,
                file_exists=False,
                valid_structure=False,
                note="No llms.txt file found at /.well-known/llms.txt",
            )

        # Validate structure
        structure = self._validate_structure(llms_txt)

        # Count linked pages
        linked_pages = self._count_linked_pages(llms_txt)

        # Check for description
        has_description = bool(re.search(r"^#\s*.+$", llms_txt, re.MULTILINE))

        # Calculate quality score
        quality_score = 0.0

        if structure["is_valid"]:
            quality_score += 0.4

        if has_description:
            quality_score += 0.2

        if linked_pages >= 3:
            quality_score += 0.3
        elif linked_pages >= 1:
            quality_score += 0.15

        # Bonus for comprehensive content
        if len(llms_txt) > 500:
            quality_score += 0.1

        quality_score = min(1.0, quality_score)

        return self._base_result(
            score=quality_score,
            file_exists=True,
            valid_structure=structure["is_valid"],
            structure_issues=structure["issues"],
            has_description=has_description,
            linked_pages_count=linked_pages,
            content_length=len(llms_txt),
        )

    def _validate_structure(self, content: str) -> Dict[str, Any]:
        """
        Validate llms.txt markdown structure.

        Args:
            content: llms.txt file content.

        Returns:
            Validation results.
        """
        issues: List[str] = []
        
        # Check for title (first line should be # Title)
        lines = content.strip().split("\n")
        if not lines or not lines[0].startswith("#"):
            issues.append("Missing title (expected # Title on first line)")

        # Check for some prose/description
        non_header_lines = [l for l in lines if l.strip() and not l.startswith("#")]
        if len(non_header_lines) < 2:
            issues.append("Very little descriptive content")

        # Check for markdown links
        has_links = bool(re.search(r"\[.+\]\(.+\)", content))
        if not has_links:
            issues.append("No markdown links found")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
        }

    def _count_linked_pages(self, content: str) -> int:
        """
        Count linked pages in llms.txt.

        Args:
            content: llms.txt file content.

        Returns:
            Number of linked pages.
        """
        # Find all markdown links
        links = re.findall(r"\[.+?\]\((.+?)\)", content)
        
        # Filter to internal/relevant links
        page_links = [l for l in links if not l.startswith("mailto:")]
        
        return len(page_links)
