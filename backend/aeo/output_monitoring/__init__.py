"""
Output Monitoring module.

Tracks what AI engines say about your content by querying multiple
LLM providers and detecting citations to your website.

Uses LangChain for unified LLM access with consistent error handling.
"""
from .base import QueryEngine, QueryResult, Citation
from .engines import (
    LangChainEngine,
    create_openai_engine,
    create_anthropic_engine,
    create_gemini_engine,
    create_searchgpt_engine,
    create_bing_copilot_engine,
    query_multiple_engines,
    ENGINE_CONFIGS,
)
from .parser import extract_citations
from .similarity import (
    calculate_response_similarity,
    calculate_average_similarity,
    score_response_accuracy,
)
from .query_generator import extract_topics, generate_queries

__all__ = [
    # Base classes
    "QueryEngine",
    "QueryResult",
    "Citation",
    # Unified LangChain Engine
    "LangChainEngine",
    "ENGINE_CONFIGS",
    # Factory functions
    "create_openai_engine",
    "create_anthropic_engine",
    "create_gemini_engine",
    "create_searchgpt_engine",
    "create_bing_copilot_engine",
    "query_multiple_engines",
    # Utilities
    "extract_citations",
    "calculate_response_similarity",
    "calculate_average_similarity",
    "score_response_accuracy",
    "extract_topics",
    "generate_queries",
]
