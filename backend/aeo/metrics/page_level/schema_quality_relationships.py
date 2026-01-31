"""
Schema Quality & Relationships Metric (PL-13).

Evaluates the completeness and relationship depth of JSON-LD
structured data.
"""
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from ..base import BaseMetric
from ..utils.schema_parser import (
    extract_json_ld,
    validate_json_ld_syntax,
    extract_schema_relationships,
)


class SchemaQualityRelationshipsMetric(BaseMetric):
    """
    Measures schema completeness and relationship quality.

    High-quality schema graphs with proper relationships are
    more cross-verifiable by AI systems.

    Weight: 4%
    """

    name = "schema_quality_relationships"
    weight = 0.04
    description = "Measures schema completeness and relationship quality"

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute schema quality and relationships score.

        Args:
            soup: BeautifulSoup parsed HTML.
            json_ld: Pre-parsed JSON-LD blocks (optional).

        Returns:
            Metric result with schema quality details.
        """
        soup: BeautifulSoup = kwargs.get("soup")
        json_ld: List[Dict[str, Any]] = kwargs.get("json_ld", [])

        if not soup:
            return self._base_result(0.0, error="No soup provided")

        # Extract JSON-LD if not provided
        if not json_ld:
            json_ld = extract_json_ld(soup)

        if not json_ld:
            return self._base_result(
                0.0,
                schema_blocks=0,
                completeness_score=0.0,
                has_relationships=False,
                note="No JSON-LD found",
            )

        # Validate syntax
        validation = validate_json_ld_syntax(json_ld)
        
        # Extract relationships
        relationships = extract_schema_relationships(json_ld)

        # Calculate completeness score
        completeness = self._calculate_completeness(json_ld, validation)

        # Calculate relationship score
        relationship_score = self._calculate_relationship_score(relationships)

        # Combined score (weighted)
        score = (completeness * 0.6) + (relationship_score * 0.4)

        # Bonus for breadcrumbs
        if relationships["has_breadcrumbs"]:
            score = min(1.0, score + 0.1)

        return self._base_result(
            score=score,
            schema_blocks=len(json_ld),
            completeness_score=round(completeness, 3),
            validation_errors=validation["errors"],
            validation_warnings=validation["warnings"][:3],
            has_relationships=any([
                relationships["has_id"],
                relationships["has_same_as"],
                relationships["has_author"],
                relationships["has_publisher"],
            ]),
            has_breadcrumbs=relationships["has_breadcrumbs"],
            relationship_types=relationships["relationship_types"],
        )

    def _calculate_completeness(
        self, json_ld: List[Dict[str, Any]], validation: Dict[str, Any]
    ) -> float:
        """
        Calculate schema completeness score.

        Args:
            json_ld: JSON-LD blocks.
            validation: Validation results.

        Returns:
            Completeness score between 0 and 1.
        """
        if not json_ld:
            return 0.0

        # Start with base score
        score = 1.0

        # Deduct for errors
        error_count = len(validation["errors"])
        score -= 0.2 * min(error_count, 3)

        # Deduct for warnings (less severe)
        warning_count = len(validation["warnings"])
        score -= 0.05 * min(warning_count, 3)

        # Check for @context (good practice)
        has_context = any("@context" in block for block in json_ld)
        if not has_context:
            score -= 0.1

        return max(0.0, score)

    def _calculate_relationship_score(self, relationships: Dict[str, Any]) -> float:
        """
        Calculate relationship depth score.

        Args:
            relationships: Extracted relationship info.

        Returns:
            Relationship score between 0 and 1.
        """
        score = 0.0

        # Award points for each relationship type
        if relationships["has_id"]:
            score += 0.2
        if relationships["has_same_as"]:
            score += 0.2
        if relationships["has_author"]:
            score += 0.25
        if relationships["has_publisher"]:
            score += 0.15
        if relationships["has_mentions"]:
            score += 0.1
        if relationships["has_breadcrumbs"]:
            score += 0.1

        return min(1.0, score)
