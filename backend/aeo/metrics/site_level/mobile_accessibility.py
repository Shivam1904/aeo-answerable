"""
Mobile & Accessibility Optimization Metric (SL-05).

Checks for mobile-friendly configuration and accessibility features.
"""
from typing import Any, Dict, List

from ..base import BaseMetric


class MobileAccessibilityMetric(BaseMetric):
    """
    Measures mobile and accessibility optimization.

    Accessibility improvements also improve machine readability;
    alt text feeds multimodal AI understanding.

    Weight: 3%
    """

    name = "mobile_accessibility"
    weight = 0.03
    description = "Measures mobile and accessibility optimization"

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute mobile and accessibility optimization score.

        Args:
            pages: List of page data with accessibility info.

        Returns:
            Metric result with accessibility details.
        """
        pages: List[Dict[str, Any]] = kwargs.get("pages", [])

        if not pages:
            return self._base_result(
                0.7,
                pages_analyzed=0,
                note="No pages to analyze",
            )

        # Aggregate accessibility metrics
        viewport_count = 0
        main_landmark_count = 0
        nav_landmark_count = 0
        total_images = 0
        images_with_alt = 0

        for page in pages:
            a11y = page.get("accessibility", {})
            
            if a11y.get("has_viewport_meta"):
                viewport_count += 1
            if a11y.get("has_main_landmark"):
                main_landmark_count += 1
            if a11y.get("has_nav_landmark"):
                nav_landmark_count += 1
            
            total_images += a11y.get("images_total", 0)
            images_with_alt += a11y.get("images_with_alt", 0)

        pages_count = len(pages)

        # Calculate rates
        viewport_rate = viewport_count / pages_count
        main_rate = main_landmark_count / pages_count
        nav_rate = nav_landmark_count / pages_count
        alt_coverage = images_with_alt / total_images if total_images > 0 else 1.0

        # Calculate score
        score = 0.0
        
        # Viewport meta (required for mobile)
        score += 0.25 * viewport_rate
        
        # Main landmark
        score += 0.25 * main_rate
        
        # Nav landmark
        score += 0.15 * nav_rate
        
        # Alt text coverage
        score += 0.35 * alt_coverage

        # Determine critical issues
        critical_issues: List[str] = []
        
        if viewport_rate < 0.5:
            critical_issues.append("Many pages missing viewport meta tag")
        if main_rate < 0.5:
            critical_issues.append("Many pages missing <main> landmark")
        if alt_coverage < 0.5:
            critical_issues.append(f"Low alt text coverage ({alt_coverage:.0%})")

        return self._base_result(
            score=score,
            pages_analyzed=pages_count,
            viewport_coverage=round(viewport_rate, 3),
            main_landmark_coverage=round(main_rate, 3),
            nav_landmark_coverage=round(nav_rate, 3),
            images_total=total_images,
            images_with_alt=images_with_alt,
            alt_coverage=round(alt_coverage, 3),
            critical_issues=critical_issues,
        )
