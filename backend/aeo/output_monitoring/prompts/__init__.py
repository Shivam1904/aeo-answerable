"""
Prompts module for Output Monitoring.

This module contains all system prompts and query templates
used by the output monitoring engines.
"""

from .system_prompts import (
    OPENAI_SYSTEM_PROMPT,
    ANTHROPIC_SYSTEM_PROMPT,
    GEMINI_SYSTEM_PROMPT,
    SEARCHGPT_SYSTEM_PROMPT,
    BING_COPILOT_SYSTEM_PROMPT,
)

from .query_templates import QUERY_TEMPLATES

__all__ = [
    # System Prompts
    "OPENAI_SYSTEM_PROMPT",
    "ANTHROPIC_SYSTEM_PROMPT",
    "GEMINI_SYSTEM_PROMPT",
    "SEARCHGPT_SYSTEM_PROMPT",
    "BING_COPILOT_SYSTEM_PROMPT",
    # Query Templates
    "QUERY_TEMPLATES",
]
