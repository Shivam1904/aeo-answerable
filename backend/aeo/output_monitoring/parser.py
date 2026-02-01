"""
Citation Parser Module.

Utilities for detecting citations to a target URL in AI responses.
"""
import re
from typing import List
from urllib.parse import urlparse

from .base import Citation


def extract_citations(response: str, target_url: str) -> List[Citation]:
    """
    Extract citations from AI response.
    
    Detects:
    - Explicit URLs in response
    - Domain mentions (e.g., "according to procurewin.com...")
    - Bracketed citations like [1], [Source]
    
    Args:
        response: The AI-generated response text
        target_url: The URL to check for citations
        
    Returns:
        List of Citation objects found in the response
    """
    citations: List[Citation] = []
    
    if not response or not target_url:
        return citations
    
    # Parse target domain
    parsed = urlparse(target_url)
    target_domain = parsed.netloc.lower()
    
    # Remove 'www.' prefix for matching
    if target_domain.startswith("www."):
        target_domain = target_domain[4:]
    
    # Also match with www prefix
    domains_to_match = [target_domain, f"www.{target_domain}"]
    
    # Pattern 1: Find explicit URLs containing the target domain
    url_pattern = r'https?://[^\s<>"\'\)\]]+' 
    for match in re.finditer(url_pattern, response):
        url = match.group(0).rstrip(".,;:!?)")
        url_domain = urlparse(url).netloc.lower()
        
        # Remove www for comparison
        if url_domain.startswith("www."):
            url_domain = url_domain[4:]
            
        if url_domain == target_domain:
            citations.append(Citation(
                url=url,
                snippet=_extract_snippet(response, match.start()),
                position=match.start()
            ))
    
    # Pattern 2: Find domain mentions (without full URL)
    for domain in domains_to_match:
        # Escape special characters for regex
        escaped_domain = re.escape(domain)
        domain_pattern = rf'\b{escaped_domain}\b'
        
        for match in re.finditer(domain_pattern, response, re.IGNORECASE):
            # Skip if we already found this position (from URL pattern)
            if not any(c.position == match.start() for c in citations):
                citations.append(Citation(
                    url=target_url,
                    snippet=_extract_snippet(response, match.start()),
                    position=match.start()
                ))
    
    # Pattern 3: Find brand name mentions (extract from domain)
    # e.g., "procurewin.com" -> look for "ProcureWin"
    brand_name = target_domain.split('.')[0]
    if len(brand_name) > 3:  # Only if brand name is meaningful
        brand_pattern = rf'\b{re.escape(brand_name)}\b'
        for match in re.finditer(brand_pattern, response, re.IGNORECASE):
            # Skip if position already captured
            if not any(abs(c.position - match.start()) < 10 for c in citations):
                citations.append(Citation(
                    url=target_url,
                    snippet=_extract_snippet(response, match.start()),
                    position=match.start()
                ))
    
    # Sort by position
    citations.sort(key=lambda c: c.position)
    
    return citations


def _extract_snippet(text: str, position: int, radius: int = 75) -> str:
    """
    Extract text snippet around citation position.
    
    Args:
        text: The full text
        position: Position of the citation
        radius: Number of characters before/after to include
        
    Returns:
        Text snippet with ellipsis if truncated
    """
    start = max(0, position - radius)
    end = min(len(text), position + radius)
    
    snippet = text[start:end].strip()
    
    # Add ellipsis if truncated
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
        
    return snippet
