"""
Base Metric Module.

Provides the abstract base class for all AEO metrics and a registry
for automatic metric discovery.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type


class BaseMetric(ABC):
    """
    Abstract base class for all AEO metrics.

    Each metric must define:
        - name: Unique identifier (snake_case)
        - weight: Score contribution (0.0 to 1.0)
        - description: Human-readable explanation
        - compute(): Method that returns metric results
    """

    name: str = ""
    weight: float = 0.0
    description: str = ""

    @abstractmethod
    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute the metric and return results.

        Returns:
            Dict containing at minimum:
                - metric: str (metric name)
                - score: float (0.0 to 1.0)
                - weight: float (the metric's weight)
                - Additional metric-specific fields
        """
        pass

    def _base_result(self, score: float, **extras: Any) -> Dict[str, Any]:
        """
        Create a standardized result dictionary.

        Args:
            score: The computed score (0.0 to 1.0).
            **extras: Additional metric-specific data.

        Returns:
            Standardized result dictionary.
        """
        return {
            "metric": self.name,
            "score": round(max(0.0, min(1.0, score)), 3),
            "weight": self.weight,
            **extras,
        }


class MetricRegistry:
    """
    Registry for automatic metric discovery and instantiation.
    """

    _page_metrics: List[Type[BaseMetric]] = []
    _site_metrics: List[Type[BaseMetric]] = []

    @classmethod
    def register_page_metric(cls, metric_class: Type[BaseMetric]) -> Type[BaseMetric]:
        """Decorator to register a page-level metric."""
        cls._page_metrics.append(metric_class)
        return metric_class

    @classmethod
    def register_site_metric(cls, metric_class: Type[BaseMetric]) -> Type[BaseMetric]:
        """Decorator to register a site-level metric."""
        cls._site_metrics.append(metric_class)
        return metric_class

    @classmethod
    def get_page_metrics(cls) -> List[Type[BaseMetric]]:
        """Get all registered page-level metrics."""
        return cls._page_metrics.copy()

    @classmethod
    def get_site_metrics(cls) -> List[Type[BaseMetric]]:
        """Get all registered site-level metrics."""
        return cls._site_metrics.copy()

    @classmethod
    def clear(cls) -> None:
        """Clear all registered metrics (useful for testing)."""
        cls._page_metrics.clear()
        cls._site_metrics.clear()
