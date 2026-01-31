"""
Utils Module for AEO Metrics.

Provides shared utilities for tokenization, schema parsing, and content extraction.
"""
from .tokenizer import count_tokens, estimate_context_usage
from .schema_parser import (
    extract_json_ld,
    get_schema_types,
    has_schema_type,
    get_schema_property,
    validate_json_ld_syntax,
    extract_schema_relationships,
)
from .readability import extract_main_content, has_main_landmarks


__all__ = [
    # Tokenizer
    "count_tokens",
    "estimate_context_usage",
    # Schema parser
    "extract_json_ld",
    "get_schema_types",
    "has_schema_type",
    "get_schema_property",
    "validate_json_ld_syntax",
    "extract_schema_relationships",
    # Readability
    "extract_main_content",
    "has_main_landmarks",
]
