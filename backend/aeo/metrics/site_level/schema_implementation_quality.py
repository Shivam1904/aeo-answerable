"""
Schema Implementation Quality (Technical) Metric (SL-06).

Validates JSON-LD syntax and schema.org compliance across the site.
"""
from typing import Any, Dict, List

from ..base import BaseMetric


class SchemaImplementationQualityMetric(BaseMetric):
    """
    Measures schema implementation quality across the site.

    Invalid schema is effectively nonexistent to machines;
    proper validation ensures rich result eligibility.

    Weight: 2%
    """

    name = "schema_implementation_quality"
    weight = 0.02
    description = "Measures schema implementation quality across the site"

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute schema implementation quality score.

        Args:
            pages: List of page data with schema validation results.

        Returns:
            Metric result with schema quality details.
        """
        pages: List[Dict[str, Any]] = kwargs.get("pages", [])

        if not pages:
            return self._base_result(
                0.5,
                pages_checked=0,
                note="No pages to analyze",
            )

        pages_with_schema = 0
        valid_schema_count = 0
        total_errors: List[str] = []
        total_warnings: List[str] = []
        rich_results_eligible = 0

        for page in pages:
            schema_data = page.get("schema", {})
            
            if schema_data.get("has_schema"):
                pages_with_schema += 1
                
                validation = schema_data.get("validation", {})
                
                if validation.get("valid", False):
                    valid_schema_count += 1
                
                errors = validation.get("errors", [])
                total_errors.extend([f"{page.get('url', 'Unknown')}: {e}" for e in errors[:2]])
                
                warnings = validation.get("warnings", [])
                total_warnings.extend(warnings[:2])
                
                if schema_data.get("rich_results_eligible", False):
                    rich_results_eligible += 1

        # Calculate rates
        pages_count = len(pages)
        schema_coverage = pages_with_schema / pages_count if pages_count > 0 else 0
        
        valid_syntax_pct = (
            valid_schema_count / pages_with_schema 
            if pages_with_schema > 0 
            else 1.0
        )

        # Calculate score
        score = 0.0
        
        # Schema coverage (having schema at all)
        score += 0.3 * schema_coverage
        
        # Syntax validity
        score += 0.4 * valid_syntax_pct
        
        # Rich results eligibility bonus
        if pages_with_schema > 0:
            rich_rate = rich_results_eligible / pages_with_schema
            score += 0.3 * rich_rate

        return self._base_result(
            score=score,
            pages_checked=pages_count,
            pages_with_schema=pages_with_schema,
            schema_coverage=round(schema_coverage, 3),
            valid_syntax_pct=round(valid_syntax_pct, 3),
            valid_schema_count=valid_schema_count,
            schema_errors=total_errors[:5],
            schema_warnings=total_warnings[:5],
            rich_results_eligible=rich_results_eligible,
        )
