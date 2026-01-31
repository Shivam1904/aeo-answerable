"""
Content Extractor Module.

This module provides functionality to parse raw HTML and transform it into
"Agent-Readable" text. It handles boilerplate removal, heading extraction,
and semantic content cleaning.
"""
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

from bs4 import BeautifulSoup, Tag

from .auditor import ContentAuditor
from .chunker import ContentChunker

def extract(html: str, url: str) -> Dict[str, Any]:
    """
    Main entry point to extract content from a raw HTML string.

    Args:
        html (str): The raw HTML content of the page.
        url (str): The URL of the page (used for metadata).

    Returns:
        Dict[str, Any]: A dictionary containing the cleaned content and metadata.
        Structure:
        {
            "url": str,
            "title": str,
            "description": str,
            "headings": List[Dict],
            "main_content": str,
            "audits": Dict,
            "chunks": Dict,
            "metadata": Dict
        }
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # Metadata extraction
    title_tag = soup.find('title')
    title = title_tag.get_text().strip() if title_tag else "Untitled"
    
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    description = desc_tag.get('content', '') if desc_tag else ""

    # 1. Remove Boilerplate
    _remove_boilerplate(soup)

    # 2. Extract Headings
    headings = _extract_headings(soup)

    # 3. Extract Main Content
    main_content = _extract_main_content(soup)

    # 4. Run Audits
    auditor = ContentAuditor()
    structure_audit = auditor.audit_structure(soup)
    clarity_audit = auditor.audit_clarity(main_content)

    # 5. Run Chunking
    chunker = ContentChunker()
    semantic_chunks = chunker.chunk_semantic(soup)
    sliding_chunks = chunker.chunk_sliding(main_content)
    chunk_delta = chunker.compare_strategies(semantic_chunks, sliding_chunks)

    return {
        "url": url,
        "title": title,
        "description": description,
        "headings": headings,
        "main_content": main_content,
        "audits": {
            "structure": structure_audit,
            "clarity": clarity_audit,
        },
        "chunks": {
            "semantic": semantic_chunks,
            "sliding": sliding_chunks,
            "consistency_score": chunk_delta
        },
        "metadata": {
            "word_count": len(main_content.split()),
            "extraction_method": "semantic",
            "crawled_at": datetime.utcnow().isoformat()
        }
    }

def _remove_boilerplate(soup: BeautifulSoup) -> None:
    """
    Removes navigational elements, ads, and scripts from the DOM in-place.
    
    Args:
        soup (BeautifulSoup): The parsed HTML object.
    """
    # Tags to remove
    for tag in soup(['script', 'style', 'noscript', 'iframe', 'svg', 'nav', 'header', 'footer', 'aside']):
        tag.decompose()
    
    # Classes/IDs to remove using regex
    params = [
        {'class': re.compile(r'sidebar|popup|modal|cookie|advertisement|ad-container')},
        {'id': re.compile(r'sidebar|popup|modal')}
    ]
    for p in params:
        for tag in soup.find_all(**p): # type: ignore
            tag.decompose()

def _extract_headings(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """
    Extracts all H1-H6 headings to build a document skeleton.

    Args:
        soup (BeautifulSoup): The clean HTML object.

    Returns:
        List[Dict[str, Any]]: List of heading objects with text, level, and ID.
    """
    headings = []
    for tag in soup.find_all(re.compile(r'^h[1-6]$')):
        text = tag.get_text().strip()
        if text:
            headings.append({
                "text": text,
                "level": int(tag.name[1]), # type: ignore
                "id": tag.get('id')
            })
    return headings

def _extract_main_content(soup: BeautifulSoup) -> str:
    """
    Isolates the main content area and converts it to text/markdown.

    Args:
        soup (BeautifulSoup): The clean HTML object.

    Returns:
        str: The extracted markdown-like content.
    """
    # Heuristic: Find content container
    content = soup.find('main') or soup.find('article') or soup.find('body')
    
    if not content:
        return ""

    if isinstance(content, Tag):
        return _dom_to_markdown(content)
    return ""

def _dom_to_markdown(element: Tag) -> str:
    """
    Recursively converts DOM elements into a semantic text representation.

    Args:
        element (Tag): The DOM element to process.

    Returns:
        str: The generated text string.
    """
    text_parts = []
    
    for child in element.children:
        if child.name is None: # Text node
            t = str(child).strip()
            if t: text_parts.append(t)
        
        elif child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = int(child.name[1]) # type: ignore
            text_parts.append(f"\n\n{'#' * level} {child.get_text().strip()}\n\n")
        
        elif child.name == 'p':
            text_parts.append(f"\n\n{child.get_text().strip()}\n\n")
        
        elif child.name == 'li':
            text_parts.append(f"\n- {child.get_text().strip()}")
        
        elif child.name in ['div', 'section', 'article']:
             if isinstance(child, Tag):
                text_parts.append(_dom_to_markdown(child))
        
        # Recurse for others
        elif hasattr(child, 'children'):
             if isinstance(child, Tag):
                text_parts.append(_dom_to_markdown(child))
    
    return " ".join(text_parts).replace("  ", " ").replace("\n ", "\n")
