"""
Readability Utility Module.

Provides content extraction using readability algorithms.
"""
from typing import Optional, Tuple

from bs4 import BeautifulSoup


def extract_main_content(soup: BeautifulSoup) -> Tuple[str, bool]:
    """
    Extract main content text from a page using multiple strategies.

    Tries in order:
    1. readability-lxml library (if available)
    2. <main> or <article> tag extraction
    3. <body> fallback

    Args:
        soup: Parsed HTML document.

    Returns:
        Tuple of (extracted_text, extractor_success).
    """
    # Try readability-lxml first
    try:
        from readability import Document
        
        doc = Document(str(soup))
        summary = doc.summary()
        summary_soup = BeautifulSoup(summary, "html.parser")
        text = summary_soup.get_text(separator=" ", strip=True)
        
        if len(text.split()) >= 50:
            return text, True
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback to landmark-based extraction
    return _extract_from_landmarks(soup)


def _extract_from_landmarks(soup: BeautifulSoup) -> Tuple[str, bool]:
    """
    Extract content from semantic landmarks.

    Args:
        soup: Parsed HTML document.

    Returns:
        Tuple of (extracted_text, extractor_success).
    """
    # Try <main> tag
    main = soup.find("main")
    if main:
        text = main.get_text(separator=" ", strip=True)
        if len(text.split()) >= 50:
            return text, True

    # Try <article> tag
    article = soup.find("article")
    if article:
        text = article.get_text(separator=" ", strip=True)
        if len(text.split()) >= 50:
            return text, True

    # Fallback to body
    body = soup.find("body")
    if body:
        text = body.get_text(separator=" ", strip=True)
        return text, len(text.split()) >= 100

    return "", False


def has_main_landmarks(soup: BeautifulSoup) -> dict:
    """
    Check for presence of main content landmarks.

    Args:
        soup: Parsed HTML document.

    Returns:
        Dictionary with landmark presence flags.
    """
    return {
        "has_main_tag": soup.find("main") is not None,
        "has_article_tag": soup.find("article") is not None,
        "has_section_tags": len(soup.find_all("section")) > 0,
    }
