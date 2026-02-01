"""
Topic Extraction and Query Generation Module.

Extracts key topics from page content and generates test queries
that users might ask AI engines about the content.
"""
import re
from typing import List, Dict, Set
from urllib.parse import urlparse

from .prompts import QUERY_TEMPLATES


def extract_topics(
    text: str,
    url: str,
    title: str = "",
    meta_description: str = ""
) -> List[Dict[str, any]]:
    """
    Extract key topics from page content.
    
    Uses multiple signals:
    - Brand/domain name
    - Page title
    - Capitalized phrases (proper nouns)
    - Repeated significant terms
    - Meta description keywords
    
    Args:
        text: Main content text
        url: Page URL
        title: Page title
        meta_description: Meta description if available
        
    Returns:
        List of topic dictionaries with name and confidence score
    """
    topics: Dict[str, float] = {}
    
    # 1. Extract brand name from domain
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    brand_name = domain.split('.')[0]
    
    if len(brand_name) > 2:
        # Capitalize brand name properly
        brand_display = brand_name.capitalize()
        topics[brand_display] = 1.0  # Highest confidence for brand
    
    # 2. Extract from title
    if title:
        title_topics = _extract_noun_phrases(title)
        for topic in title_topics:
            if topic.lower() != brand_name and len(topic) > 3:
                topics[topic] = topics.get(topic, 0) + 0.8
    
    # 3. Extract proper nouns from content
    proper_nouns = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b', text)
    proper_noun_counts: Dict[str, int] = {}
    for noun in proper_nouns:
        if len(noun) > 3 and noun.lower() not in _get_common_words():
            proper_noun_counts[noun] = proper_noun_counts.get(noun, 0) + 1
    
    # Add proper nouns that appear multiple times
    for noun, count in proper_noun_counts.items():
        if count >= 2:
            score = min(0.7, 0.2 + (count * 0.1))
            topics[noun] = max(topics.get(noun, 0), score)
    
    # 4. Extract from meta description
    if meta_description:
        meta_topics = _extract_noun_phrases(meta_description)
        for topic in meta_topics:
            if len(topic) > 3:
                topics[topic] = topics.get(topic, 0) + 0.5
    
    # 5. Find product/service indicators
    product_patterns = [
        r'(?:our|the)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z]?[a-zA-Z]+)?)\s+(?:platform|software|service|tool|solution|product|app)',
        r'([A-Z][a-zA-Z]+(?:\s+[A-Z]?[a-zA-Z]+)?)\s+(?:helps?|enables?|allows?|lets?)',
    ]
    
    for pattern in product_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if len(match) > 3:
                topics[match] = topics.get(match, 0) + 0.6
    
    # Sort by confidence and return top topics
    sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
    
    return [
        {"name": name, "confidence": round(score, 2)}
        for name, score in sorted_topics[:15]
    ]


def generate_queries(
    topics: List[Dict[str, any]],
    query_types: List[str] | None = None,
    max_queries: int = 20
) -> List[Dict[str, any]]:
    """
    Generate test queries from extracted topics.
    
    Args:
        topics: List of topic dictionaries from extract_topics()
        query_types: Types of queries to generate (default: all)
        max_queries: Maximum number of queries to return
        
    Returns:
        List of query dictionaries with query text and metadata
    """
    if query_types is None:
        query_types = ["definition", "benefits", "how_to", "features"]
    
    queries = []
    
    for topic in topics[:5]:  # Use top 5 topics
        topic_name = topic["name"]
        confidence = topic["confidence"]
        
        for query_type in query_types:
            if query_type in QUERY_TEMPLATES:
                # Use first template for each type
                template = QUERY_TEMPLATES[query_type][0]
                query_text = template.format(topic=topic_name)
                
                queries.append({
                    "query": query_text,
                    "topic": topic_name,
                    "type": query_type,
                    "priority": round(confidence * _get_type_weight(query_type), 2)
                })
    
    # Sort by priority and limit
    queries.sort(key=lambda x: x["priority"], reverse=True)
    return queries[:max_queries]


def _extract_noun_phrases(text: str) -> List[str]:
    """
    Extract noun phrases from text using simple patterns.
    """
    # Pattern for capitalized phrases
    phrases = re.findall(r'\b[A-Z][a-zA-Z]*(?:\s+[A-Z]?[a-zA-Z]+)*\b', text)
    
    # Filter out common words and short phrases
    common = _get_common_words()
    filtered = [
        p for p in phrases 
        if p.lower() not in common and len(p) > 3
    ]
    
    return list(set(filtered))


def _get_type_weight(query_type: str) -> float:
    """Get priority weight for query type."""
    weights = {
        "definition": 1.0,
        "benefits": 0.9,
        "features": 0.85,
        "how_to": 0.8,
        "pricing": 0.7,
        "comparison": 0.6,
        "reviews": 0.5,
    }
    return weights.get(query_type, 0.5)


def _get_common_words() -> Set[str]:
    """Get set of common words to filter out."""
    return {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
        'can', 'had', 'her', 'was', 'one', 'our', 'out', 'has',
        'his', 'how', 'its', 'let', 'may', 'new', 'now', 'old',
        'see', 'way', 'who', 'boy', 'did', 'get', 'put', 'say',
        'she', 'too', 'use', 'this', 'that', 'with', 'have', 'from',
        'they', 'been', 'call', 'come', 'could', 'find', 'first',
        'into', 'like', 'long', 'look', 'make', 'many', 'more',
        'most', 'number', 'other', 'over', 'part', 'people', 'than',
        'then', 'these', 'time', 'very', 'when', 'which', 'will',
        'your', 'about', 'after', 'also', 'back', 'because', 'being',
        'here', 'home', 'just', 'know', 'last', 'made', 'much',
        'only', 'some', 'take', 'them', 'want', 'well', 'what',
        'year', 'years', 'january', 'february', 'march', 'april',
        'june', 'july', 'august', 'september', 'october', 'november',
        'december', 'monday', 'tuesday', 'wednesday', 'thursday',
        'friday', 'saturday', 'sunday', 'today', 'tomorrow', 'yesterday',
        'introduction', 'conclusion', 'overview', 'summary', 'more',
        'information', 'learn', 'read', 'click', 'here', 'contact',
        'privacy', 'policy', 'terms', 'conditions', 'copyright',
    }
