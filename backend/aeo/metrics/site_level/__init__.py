"""
Site-Level Metrics Module.

Contains all metrics computed across a site for access, rendering,
and policy scoring.
"""
from typing import List, Type

from ..base import BaseMetric

# Import all site-level metric classes
from .ai_crawler_access import AICrawlerAccessMetric
from .llms_txt_quality import LlmsTxtQualityMetric
from .prerender_consistency import PrerenderConsistencyMetric
from .core_web_vitals import CoreWebVitalsMetric
from .mobile_accessibility import MobileAccessibilityMetric
from .schema_implementation_quality import SchemaImplementationQualityMetric


# Ordered list of all site-level metrics
SITE_LEVEL_METRICS: List[Type[BaseMetric]] = [
    AICrawlerAccessMetric,
    LlmsTxtQualityMetric,
    PrerenderConsistencyMetric,
    CoreWebVitalsMetric,
    MobileAccessibilityMetric,
    SchemaImplementationQualityMetric,
]

__all__ = [
    "SITE_LEVEL_METRICS",
    "AICrawlerAccessMetric",
    "LlmsTxtQualityMetric",
    "PrerenderConsistencyMetric",
    "CoreWebVitalsMetric",
    "MobileAccessibilityMetric",
    "SchemaImplementationQualityMetric",
]
