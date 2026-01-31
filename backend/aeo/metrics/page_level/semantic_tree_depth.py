"""
Semantic Tree Depth Metric (PL-03).

Measures the maximum and average depth of text-containing nodes
in the main content area.
"""
from typing import Any, Dict, List, Tuple

from bs4 import BeautifulSoup, Tag

from ..base import BaseMetric


class SemanticTreeDepthMetric(BaseMetric):
    """
    Measures DOM nesting depth for main content nodes.

    Deep nesting harms content segmentation and can cause
    broken chunks during RAG processing.

    Weight: 5%
    """

    name = "semantic_tree_depth"
    weight = 0.05
    description = "Measures DOM nesting depth for main content nodes"

    # Maximum acceptable depths
    MAX_DEPTH_THRESHOLD = 15
    AVG_DEPTH_THRESHOLD = 8

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute semantic tree depth score.

        Args:
            soup: BeautifulSoup parsed HTML.

        Returns:
            Metric result with max_depth, avg_depth, and score.
        """
        soup: BeautifulSoup = kwargs.get("soup")
        if not soup:
            return self._base_result(0.0, error="No soup provided")

        # Find main content container
        main_content = soup.find("main") or soup.find("article") or soup.find("body")
        if not main_content:
            return self._base_result(0.0, error="No main content found")

        # Collect depths of text-containing nodes
        depths = self._collect_text_node_depths(main_content)

        if not depths:
            return self._base_result(1.0, max_depth=0, avg_depth=0.0, deep_nodes_count=0)

        max_depth = max(depths)
        avg_depth = sum(depths) / len(depths)
        deep_nodes_count = sum(1 for d in depths if d > self.MAX_DEPTH_THRESHOLD)

        # Calculate score
        score = 1.0

        # Penalize excessive max depth
        if max_depth > self.MAX_DEPTH_THRESHOLD:
            excess = max_depth - self.MAX_DEPTH_THRESHOLD
            score -= 0.05 * excess

        # Penalize high average depth
        if avg_depth > self.AVG_DEPTH_THRESHOLD:
            excess = avg_depth - self.AVG_DEPTH_THRESHOLD
            score -= 0.03 * excess

        score = max(0.0, min(1.0, score))

        return self._base_result(
            score=score,
            max_depth=max_depth,
            avg_depth=round(avg_depth, 2),
            deep_nodes_count=deep_nodes_count,
            total_text_nodes=len(depths),
        )

    def _collect_text_node_depths(
        self, element: Tag, current_depth: int = 0
    ) -> List[int]:
        """
        Recursively collect depths of text-containing nodes.

        Args:
            element: Current DOM element.
            current_depth: Current nesting depth.

        Returns:
            List of depths for text-containing nodes.
        """
        depths = []

        for child in element.children:
            if isinstance(child, Tag):
                # Skip non-content tags
                if child.name in ["script", "style", "nav", "header", "footer"]:
                    continue

                # Check if this tag has direct text content
                direct_text = child.find(string=True, recursive=False)
                if direct_text and direct_text.strip():
                    depths.append(current_depth + 1)

                # Recurse into children
                depths.extend(
                    self._collect_text_node_depths(child, current_depth + 1)
                )

        return depths
