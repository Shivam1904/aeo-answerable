"""
Tokenizer Utility Module.

Provides token counting functionality using tiktoken for accurate
LLM context window estimation.
"""
from typing import Optional

# Lazy import to avoid startup overhead
_encoding = None


def get_encoding():
    """Get or create the tiktoken encoding instance."""
    global _encoding
    if _encoding is None:
        try:
            import tiktoken
            _encoding = tiktoken.get_encoding("cl100k_base")
        except ImportError:
            # Fallback to simple word-based estimation
            return None
    return _encoding


def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a text string.

    Uses tiktoken with cl100k_base encoding (GPT-4/Claude compatible).
    Falls back to word count * 1.3 if tiktoken is not available.

    Args:
        text: The text to tokenize.

    Returns:
        Estimated token count.
    """
    if not text:
        return 0

    encoding = get_encoding()
    if encoding is not None:
        return len(encoding.encode(text))

    # Fallback: rough estimation based on words
    words = len(text.split())
    return int(words * 1.3)


def estimate_context_usage(text: str, max_context: int = 128000) -> float:
    """
    Estimate what percentage of a model's context window the text uses.

    Args:
        text: The text to measure.
        max_context: Maximum context window size (default: 128k for GPT-4).

    Returns:
        Percentage of context used (0.0 to 1.0+).
    """
    tokens = count_tokens(text)
    return tokens / max_context
