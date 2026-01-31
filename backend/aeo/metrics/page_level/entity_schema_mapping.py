"""
Entity-Schema Mapping Metric (PL-11).

Measures how well named entities in content are backed by
structured data (JSON-LD).
"""
import re
from typing import Any, Dict, List, Set

from bs4 import BeautifulSoup

from ..base import BaseMetric
from ..utils.schema_parser import extract_json_ld


class EntitySchemaMappingMetric(BaseMetric):
    """
    Measures entity-to-schema mapping coverage.

    Entities backed by structured data are easier for AI
    systems to trust and cross-verify.

    Weight: 10%
    """

    name = "entity_schema_mapping"
    weight = 0.10
    description = "Measures entity-to-schema mapping coverage"

    # Simple entity patterns (for basic NER without spacy)
    ENTITY_PATTERNS = [
        # Capitalized multi-word names (Person, Org, Product)
        r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b",
        # Quoted terms (often product names, titles)
        r'"([^"]+)"',
        # Monetary values
        r"\$[\d,]+(?:\.\d{2})?",
        # Percentages with context
        r"\d+(?:\.\d+)?%",
    ]

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute entity-schema mapping score.

        Args:
            soup: BeautifulSoup parsed HTML.
            extracted_text: Main content text.
            json_ld: Pre-parsed JSON-LD blocks (optional).

        Returns:
            Metric result with entity mapping stats.
        """
        soup: BeautifulSoup = kwargs.get("soup")
        extracted_text: str = kwargs.get("extracted_text", "")
        json_ld: List[Dict[str, Any]] = kwargs.get("json_ld", [])

        if not soup:
            return self._base_result(0.0, error="No soup provided")

        # Extract JSON-LD if not provided
        if not json_ld:
            json_ld = extract_json_ld(soup)

        # Extract entities from text
        text_entities = self._extract_entities(extracted_text)

        if not text_entities:
            return self._base_result(
                1.0,
                entities_found=[],
                entities_in_schema=[],
                mapping_rate=1.0,
                note="No significant entities found in content",
            )

        # Extract entities from schema
        schema_entities = self._extract_schema_entities(json_ld)

        # Match entities
        matched_entities = self._match_entities(text_entities, schema_entities)

        mapping_rate = len(matched_entities) / len(text_entities) if text_entities else 0.0
        unmapped = [e for e in text_entities if e not in matched_entities]

        # Score scales with mapping rate
        # 50%+ mapped = good, 80%+ = excellent
        if mapping_rate >= 0.8:
            score = 1.0
        elif mapping_rate >= 0.5:
            score = 0.6 + (0.4 * ((mapping_rate - 0.5) / 0.3))
        else:
            score = mapping_rate * 1.2  # Up to 0.6 for <50%

        score = min(1.0, score)

        return self._base_result(
            score=score,
            entities_found=list(text_entities)[:10],
            entities_in_schema=list(matched_entities)[:10],
            schema_entities=list(schema_entities)[:10],
            mapping_rate=round(mapping_rate, 3),
            unmapped_entities=unmapped[:5],
        )

    def _extract_entities(self, text: str) -> Set[str]:
        """
        Extract named entities from text using patterns.

        For production, use spacy NER.

        Args:
            text: Content text.

        Returns:
            Set of entity strings.
        """
        entities: Set[str] = set()

        for pattern in self.ENTITY_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if len(match) > 2 and len(match) < 50:
                    entities.add(match.strip())

        # Filter common false positives
        stop_entities = {
            "The", "This", "That", "However", "Therefore",
            "For Example", "In Addition", "As A Result",
        }
        entities = {e for e in entities if e not in stop_entities}

        return entities

    def _extract_schema_entities(self, json_ld: List[Dict[str, Any]]) -> Set[str]:
        """
        Extract entity names/values from JSON-LD.

        Args:
            json_ld: List of JSON-LD objects.

        Returns:
            Set of entity strings from schema.
        """
        entities: Set[str] = set()

        def extract_values(obj: Any, depth: int = 0) -> None:
            if depth > 5:
                return

            if isinstance(obj, dict):
                # Extract name-like properties
                for key in ["name", "headline", "title", "author", "brand", "manufacturer"]:
                    if key in obj:
                        val = obj[key]
                        if isinstance(val, str):
                            entities.add(val)
                        elif isinstance(val, dict) and "name" in val:
                            entities.add(val["name"])

                for value in obj.values():
                    extract_values(value, depth + 1)

            elif isinstance(obj, list):
                for item in obj:
                    extract_values(item, depth + 1)

        for block in json_ld:
            extract_values(block)

        return entities

    def _match_entities(
        self, text_entities: Set[str], schema_entities: Set[str]
    ) -> Set[str]:
        """
        Find text entities that match schema entities.

        Uses fuzzy matching for flexibility.

        Args:
            text_entities: Entities from content.
            schema_entities: Entities from JSON-LD.

        Returns:
            Set of matched entity strings.
        """
        matched: Set[str] = set()

        text_lower = {e.lower(): e for e in text_entities}
        schema_lower = {e.lower() for e in schema_entities}

        for lower_text, original in text_lower.items():
            # Exact match
            if lower_text in schema_lower:
                matched.add(original)
                continue

            # Substring match (entity contained in schema entity)
            for schema_ent in schema_lower:
                if lower_text in schema_ent or schema_ent in lower_text:
                    matched.add(original)
                    break

        return matched
