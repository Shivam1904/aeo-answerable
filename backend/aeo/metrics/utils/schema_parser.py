"""
Schema Parser Utility Module.

Provides utilities for parsing and validating JSON-LD structured data.
"""
import json
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup


def extract_json_ld(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Extract all JSON-LD blocks from a BeautifulSoup object.

    Args:
        soup: Parsed HTML document.

    Returns:
        List of parsed JSON-LD objects.
    """
    json_ld_blocks = []

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            content = script.string
            if content:
                data = json.loads(content)
                # Handle both single objects and arrays
                if isinstance(data, list):
                    json_ld_blocks.extend(data)
                else:
                    json_ld_blocks.append(data)
        except json.JSONDecodeError:
            # Skip invalid JSON-LD blocks
            continue

    return json_ld_blocks


def get_schema_types(json_ld: List[Dict[str, Any]]) -> List[str]:
    """
    Extract all @type values from JSON-LD blocks.

    Args:
        json_ld: List of JSON-LD objects.

    Returns:
        List of schema types found.
    """
    types = []

    def extract_types(obj: Any) -> None:
        if isinstance(obj, dict):
            if "@type" in obj:
                type_val = obj["@type"]
                if isinstance(type_val, list):
                    types.extend(type_val)
                else:
                    types.append(type_val)
            for value in obj.values():
                extract_types(value)
        elif isinstance(obj, list):
            for item in obj:
                extract_types(item)

    for block in json_ld:
        extract_types(block)

    return list(set(types))


def has_schema_type(json_ld: List[Dict[str, Any]], schema_type: str) -> bool:
    """
    Check if a specific schema type exists in the JSON-LD.

    Args:
        json_ld: List of JSON-LD objects.
        schema_type: The schema type to look for.

    Returns:
        True if the type is found.
    """
    types = get_schema_types(json_ld)
    return schema_type in types


def get_schema_property(
    json_ld: List[Dict[str, Any]],
    property_name: str,
    schema_type: Optional[str] = None,
) -> Optional[Any]:
    """
    Get a property value from JSON-LD, optionally filtered by type.

    Args:
        json_ld: List of JSON-LD objects.
        property_name: The property to retrieve.
        schema_type: Optional type filter.

    Returns:
        The property value if found, None otherwise.
    """
    for block in json_ld:
        if schema_type and block.get("@type") != schema_type:
            continue
        if property_name in block:
            return block[property_name]
    return None


def validate_json_ld_syntax(json_ld: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate JSON-LD syntax and structure.

    Args:
        json_ld: List of JSON-LD objects.

    Returns:
        Validation results with errors and warnings.
    """
    errors = []
    warnings = []

    for i, block in enumerate(json_ld):
        # Check for required @type
        if "@type" not in block:
            errors.append(f"Block {i}: Missing @type")

        # Check for @context
        if "@context" not in block:
            warnings.append(f"Block {i}: Missing @context (recommended)")

        # Check for empty required fields based on type
        schema_type = block.get("@type", "")
        
        if schema_type == "Article":
            if not block.get("headline") and not block.get("name"):
                errors.append(f"Block {i}: Article missing headline/name")
            if not block.get("author"):
                warnings.append(f"Block {i}: Article missing author")

        elif schema_type == "Product":
            if not block.get("name"):
                errors.append(f"Block {i}: Product missing name")

        elif schema_type in ("HowTo", "Recipe"):
            if not block.get("name"):
                errors.append(f"Block {i}: {schema_type} missing name")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "blocks_count": len(json_ld),
    }


def extract_schema_relationships(json_ld: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Extract relationship information from JSON-LD.

    Args:
        json_ld: List of JSON-LD objects.

    Returns:
        Dictionary with relationship details.
    """
    relationships = {
        "has_id": False,
        "has_same_as": False,
        "has_author": False,
        "has_publisher": False,
        "has_mentions": False,
        "has_breadcrumbs": False,
        "relationship_types": [],
    }

    for block in json_ld:
        if "@id" in block:
            relationships["has_id"] = True
            if "@id" not in relationships["relationship_types"]:
                relationships["relationship_types"].append("@id")

        if "sameAs" in block:
            relationships["has_same_as"] = True
            if "sameAs" not in relationships["relationship_types"]:
                relationships["relationship_types"].append("sameAs")

        if "author" in block:
            relationships["has_author"] = True
            if "author" not in relationships["relationship_types"]:
                relationships["relationship_types"].append("author")

        if "publisher" in block:
            relationships["has_publisher"] = True
            if "publisher" not in relationships["relationship_types"]:
                relationships["relationship_types"].append("publisher")

        if "mentions" in block:
            relationships["has_mentions"] = True
            if "mentions" not in relationships["relationship_types"]:
                relationships["relationship_types"].append("mentions")

        if block.get("@type") == "BreadcrumbList":
            relationships["has_breadcrumbs"] = True

    return relationships
