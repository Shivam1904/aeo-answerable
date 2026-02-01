"""
Content Extractor Module.

This module provides functionality to parse raw HTML and transform it into
"Agent-Readable" text. It handles boilerplate removal, heading extraction,
semantic content cleaning, and AEO metrics computation.
"""
import re
from datetime import datetime
from typing import List, Dict, Any
import copy

from bs4 import BeautifulSoup, Tag

from .chunker import ContentChunker
from .metrics import compute_page_metrics
from .metrics.utils.schema_parser import extract_json_ld


def extract(html: str, url: str) -> Dict[str, Any]:
    """
    Main entry point to extract content from a raw HTML string.

    Args:
        html: The raw HTML content of the page.
        url: The URL of the page (used for metadata).

    Returns:
        Dictionary containing cleaned content, metrics, and metadata.
    """
    # Parse HTML - keep a clean copy for metrics
    soup = BeautifulSoup(html, "html.parser")
    
    # Metadata extraction (before boilerplate removal)
    title_tag = soup.find("title")
    title = title_tag.get_text().strip() if title_tag else "Untitled"
    
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = desc_tag.get("content", "") if desc_tag else ""

    # Extract JSON-LD before modification
    json_ld = extract_json_ld(soup)

    # Create a copy for boilerplate removal without re-parsing
    clean_soup = copy.copy(soup)
    _remove_boilerplate(clean_soup)

    # Extract Headings
    headings = _extract_headings(clean_soup)

    # Extract Main Content
    main_content = _extract_main_content(clean_soup)

    # Run new AEO metrics (using original soup for full analysis)
    metrics_result = compute_page_metrics(
        html=html,
        soup=soup,
        extracted_text=main_content,
        url=url,
        json_ld=json_ld,
    )

    # Run Chunking
    chunker = ContentChunker()
    semantic_chunks = chunker.chunk_semantic(clean_soup)
    sliding_chunks = chunker.chunk_sliding(main_content)
    chunk_delta = chunker.compare_strategies(semantic_chunks, sliding_chunks)

    return {
        "url": url,
        "title": title,
        "description": description,
        "headings": headings,
        "main_content": main_content,
        # New metrics structure
        "metrics": metrics_result["metrics"],
        "page_score": metrics_result["page_score"],
        # Legacy audits for backward compatibility
        "audits": _convert_metrics_to_legacy_audits(metrics_result["metrics"]),
        "chunks": {
            "semantic": semantic_chunks,
            "sliding": sliding_chunks,
            "consistency_score": chunk_delta,
        },
        "metadata": {
            "word_count": len(main_content.split()),
            "extraction_method": "semantic",
            "crawled_at": datetime.utcnow().isoformat(),
        },
    }


def _convert_metrics_to_legacy_audits(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Convert new metrics format to legacy audit format for backward compatibility."""
    structure = metrics.get("heading_hierarchy_validity", {})
    clarity = metrics.get("anaphora_resolution", {})
    
    return {
        "structure": {
            "score": structure.get("score", 0),
            "h1_found": structure.get("h1_count", 0) == 1,
            "h1_count": structure.get("h1_count", 0),
            "skipped_levels": structure.get("skipped_levels", []),
        },
        "clarity": {
            "score": clarity.get("score", 0),
            "pronoun_density": clarity.get("pronoun_density", 0),
            "flags": [],
        },
    }


def _remove_boilerplate(soup: BeautifulSoup) -> None:
    """
    Removes navigational elements, ads, and scripts from the DOM in-place.
    
    Args:
        soup: The parsed HTML object.
    """
    # Tags to remove
    for tag in soup(["script", "style", "noscript", "iframe", "svg", "nav", "header", "footer", "aside"]):
        tag.decompose()
    
    # Classes/IDs to remove using regex
    params = [
        {"class": re.compile(r"sidebar|popup|modal|cookie|advertisement|ad-container")},
        {"id": re.compile(r"sidebar|popup|modal")},
    ]
    for p in params:
        for tag in soup.find_all(**p):  # type: ignore
            tag.decompose()


def _extract_headings(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Extracts all H1-H6 headings to build a document skeleton.

    Args:
        soup: The clean HTML object.

    Returns:
        List of heading objects with text, level, and ID.
    """
    headings = []
    for tag in soup.find_all(re.compile(r"^h[1-6]$")):
        text = tag.get_text().strip()
        if text:
            headings.append({
                "text": text,
                "level": int(tag.name[1]),  # type: ignore
                "id": tag.get("id"),
            })
    return headings


def _extract_main_content(soup: BeautifulSoup) -> str:
    """
    Isolates the main content area and converts it to text/markdown.

    Args:
        soup: The clean HTML object.

    Returns:
        The extracted markdown-like content.
    """
    content = soup.find("main") or soup.find("article") or soup.find("body")
    
    if not content:
        return ""

    if isinstance(content, Tag):
        return _dom_to_markdown(content)
    return ""


def _dom_to_markdown(element: Tag) -> str:
    """
    Recursively converts DOM elements into a semantic text representation.

    Args:
        element: The DOM element to process.

    Returns:
        The generated text string.
    """
    text_parts = []
    
    for child in element.children:
        if child.name is None:  # Text node
            t = str(child).strip()
            if t:
                text_parts.append(t)
        
        elif child.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            level = int(child.name[1])  # type: ignore
            text_parts.append(f"\n\n{'#' * level} {child.get_text().strip()}\n\n")
        
        elif child.name == "p":
            text_parts.append(f"\n\n{child.get_text().strip()}\n\n")
        
        elif child.name == "li":
            text_parts.append(f"\n- {child.get_text().strip()}")
        
        elif child.name in ["div", "section", "article"]:
            if isinstance(child, Tag):
                text_parts.append(_dom_to_markdown(child))
        
        # Recurse for others
        elif hasattr(child, "children"):
            if isinstance(child, Tag):
                text_parts.append(_dom_to_markdown(child))
    
    return " ".join(text_parts).replace("  ", " ").replace("\n ", "\n")
