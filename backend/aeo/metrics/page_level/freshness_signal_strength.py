"""
Freshness Signal Strength Metric (PL-15).

Measures the presence and consistency of date/freshness signals
across visible content, schema, and sitemap.
"""
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from ..base import BaseMetric
from ..utils.schema_parser import extract_json_ld, get_schema_property


class FreshnessSignalStrengthMetric(BaseMetric):
    """
    Measures freshness signal presence and consistency.

    Clear recency cues help AI models pick current information
    over outdated content.

    Weight: 4%
    """

    name = "freshness_signal_strength"
    weight = 0.04
    description = "Measures freshness signal presence and consistency"

    # Date patterns in content
    DATE_PATTERNS = [
        r"(last\s+)?updated[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
        r"(last\s+)?modified[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
        r"published[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
        r"(\d{4}-\d{2}-\d{2})",
        r"(\d{1,2}/\d{1,2}/\d{4})",
        r"([A-Za-z]+\s+\d{1,2},?\s+\d{4})",
    ]

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute freshness signal strength score.

        Args:
            soup: BeautifulSoup parsed HTML.
            json_ld: Pre-parsed JSON-LD blocks (optional).

        Returns:
            Metric result with freshness signal details.
        """
        soup: BeautifulSoup = kwargs.get("soup")
        json_ld: List[Dict[str, Any]] = kwargs.get("json_ld", [])

        if not soup:
            return self._base_result(0.0, error="No soup provided")

        # Extract JSON-LD if not provided
        if not json_ld:
            json_ld = extract_json_ld(soup)

        # Find visible date in content
        visible_date = self._find_visible_date(soup)

        # Find date in schema
        schema_date_modified = get_schema_property(json_ld, "dateModified")
        schema_date_published = get_schema_property(json_ld, "datePublished")

        # Find date in meta tags
        meta_date = self._find_meta_date(soup)

        # Check for time tag
        time_tag = soup.find("time")
        time_tag_date = None
        if time_tag and time_tag.get("datetime"):
            time_tag_date = time_tag.get("datetime")

        # Determine which signals are present
        has_visible = visible_date is not None
        has_schema = schema_date_modified is not None or schema_date_published is not None
        has_meta = meta_date is not None
        has_time_tag = time_tag_date is not None

        # Count signals
        signal_count = sum([has_visible, has_schema, has_meta, has_time_tag])

        # Check consistency (simplified - just check if multiple sources agree)
        dates_consistent = self._check_consistency([
            visible_date, schema_date_modified, schema_date_published,
            meta_date, time_tag_date
        ])

        # Calculate score
        if signal_count == 0:
            score = 0.0
        elif signal_count == 1:
            score = 0.5
        elif signal_count >= 2 and dates_consistent:
            score = 1.0
        elif signal_count >= 2:
            score = 0.75  # Multiple signals but inconsistent

        return self._base_result(
            score=score,
            visible_date=visible_date,
            schema_date_modified=schema_date_modified,
            schema_date_published=schema_date_published,
            meta_date=meta_date,
            time_tag_date=time_tag_date,
            signal_count=signal_count,
            dates_consistent=dates_consistent,
            has_freshness_signals=signal_count > 0,
        )

    def _find_visible_date(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Find visible date in page content.

        Args:
            soup: Parsed HTML.

        Returns:
            Date string if found.
        """
        # Look in common date containers
        date_selectors = [
            {"class_": re.compile(r"date|time|publish|update", re.I)},
            {"class_": re.compile(r"meta|byline|author", re.I)},
        ]

        for selector in date_selectors:
            elements = soup.find_all(**selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                for pattern in self.DATE_PATTERNS:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        return match.group(0)

        return None

    def _find_meta_date(self, soup: BeautifulSoup) -> Optional[str]:
        """
        Find date in meta tags.

        Args:
            soup: Parsed HTML.

        Returns:
            Date string if found.
        """
        date_meta_names = [
            "article:modified_time",
            "article:published_time",
            "og:updated_time",
            "last-modified",
            "date",
        ]

        for name in date_meta_names:
            meta = soup.find("meta", property=name) or soup.find("meta", attrs={"name": name})
            if meta and meta.get("content"):
                return meta.get("content")

        return None

    def _check_consistency(self, dates: List[Optional[str]]) -> bool:
        """
        Check if multiple date signals are consistent.

        Args:
            dates: List of date strings (some may be None).

        Returns:
            True if dates appear consistent.
        """
        valid_dates = [d for d in dates if d]
        
        if len(valid_dates) < 2:
            return True  # Can't check consistency with < 2 dates

        # Simplified check: extract years and compare
        years = []
        for date in valid_dates:
            year_match = re.search(r"20\d{2}", str(date))
            if year_match:
                years.append(int(year_match.group()))

        if len(years) < 2:
            return True

        # Consider consistent if years are within 1 year of each other
        return max(years) - min(years) <= 1
