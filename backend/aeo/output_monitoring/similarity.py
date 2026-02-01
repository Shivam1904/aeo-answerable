"""
Similarity Analysis Module.

Provides semantic similarity scoring between AI engine responses
and accuracy scoring against source content.
"""
from typing import List, Dict, Tuple
import re
from difflib import SequenceMatcher


def calculate_response_similarity(responses: List[str]) -> Dict[str, float]:
    """
    Calculate pairwise similarity between AI responses.
    
    Uses a combination of:
    - Token overlap (Jaccard similarity)
    - Sequence matching (for structure)
    
    Args:
        responses: List of response texts from different engines
        
    Returns:
        Dictionary with pairwise similarity scores (0.0 to 1.0)
        Keys are formatted as "engine1-engine2"
    """
    if len(responses) < 2:
        return {}
    
    similarities = {}
    
    for i in range(len(responses)):
        for j in range(i + 1, len(responses)):
            # Calculate token-based similarity (Jaccard)
            tokens1 = set(_tokenize(responses[i]))
            tokens2 = set(_tokenize(responses[j]))
            
            if not tokens1 or not tokens2:
                jaccard = 0.0
            else:
                intersection = len(tokens1 & tokens2)
                union = len(tokens1 | tokens2)
                jaccard = intersection / union if union > 0 else 0.0
            
            # Calculate sequence similarity
            seq_ratio = SequenceMatcher(None, responses[i], responses[j]).ratio()
            
            # Weighted average (60% semantic, 40% structural)
            similarity = 0.6 * jaccard + 0.4 * seq_ratio
            
            similarities[f"{i}-{j}"] = round(similarity, 4)
    
    return similarities


def calculate_average_similarity(responses: List[str]) -> float:
    """
    Calculate average pairwise similarity across all responses.
    
    Args:
        responses: List of response texts
        
    Returns:
        Average similarity score (0.0 to 1.0)
    """
    similarities = calculate_response_similarity(responses)
    if not similarities:
        return 0.0
    return round(sum(similarities.values()) / len(similarities), 4)


def score_response_accuracy(
    response: str,
    source_content: str
) -> Dict[str, any]:
    """
    Score how accurately the AI response reflects the source content.
    
    Checks for:
    - Fact coverage: How many key terms from source appear in response
    - Potential hallucinations: Response claims not supported by source
    
    Args:
        response: The AI-generated response
        source_content: The actual website content
        
    Returns:
        Dictionary with accuracy score and details
    """
    if not response or not source_content:
        return {
            "accuracy_score": 0.0,
            "fact_coverage": 0.0,
            "key_terms_found": [],
            "key_terms_missing": [],
            "potential_hallucinations": []
        }
    
    # Extract key terms from source (nouns, proper nouns, numbers)
    source_terms = _extract_key_terms(source_content)
    response_terms = _extract_key_terms(response)
    
    # Calculate fact coverage
    found_terms = [t for t in source_terms if t.lower() in response.lower()]
    missing_terms = [t for t in source_terms if t.lower() not in response.lower()]
    
    fact_coverage = len(found_terms) / len(source_terms) if source_terms else 0.0
    
    # Detect potential hallucinations (terms in response not in source)
    # Focus on specific entities (capitalized words, numbers)
    potential_hallucinations = []
    for term in response_terms:
        # Check if it's a specific entity (capitalized or number)
        if term[0].isupper() or term[0].isdigit():
            if term.lower() not in source_content.lower():
                # Could be a hallucination
                potential_hallucinations.append(term)
    
    # Calculate accuracy score
    # Penalize for potential hallucinations
    hallucination_penalty = min(0.3, len(potential_hallucinations) * 0.05)
    accuracy_score = max(0.0, fact_coverage - hallucination_penalty)
    
    return {
        "accuracy_score": round(accuracy_score, 4),
        "fact_coverage": round(fact_coverage, 4),
        "key_terms_found": found_terms[:20],  # Limit for response size
        "key_terms_missing": missing_terms[:10],
        "potential_hallucinations": potential_hallucinations[:10]
    }


def _tokenize(text: str) -> List[str]:
    """
    Tokenize text into words, removing punctuation and lowercasing.
    """
    # Remove punctuation and split
    words = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'must', 'shall',
        'can', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
        'from', 'as', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'between', 'under', 'again', 'further',
        'then', 'once', 'here', 'there', 'when', 'where', 'why',
        'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some',
        'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
        'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or',
        'because', 'until', 'while', 'it', 'its', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'we', 'they'
    }
    return [w for w in words if w not in stop_words and len(w) > 2]


def _extract_key_terms(text: str) -> List[str]:
    """
    Extract key terms (nouns, proper nouns, numbers) from text.
    """
    # Find capitalized words (likely proper nouns)
    proper_nouns = re.findall(r'\b[A-Z][a-zA-Z]+\b', text)
    
    # Find numbers and measurements
    numbers = re.findall(r'\b\d+(?:\.\d+)?(?:\s*(?:%|percent|dollars?|USD|GB|MB|TB|users?|customers?))?\b', text, re.IGNORECASE)
    
    # Get significant words (longer than 5 chars, appear to be meaningful)
    words = re.findall(r'\b[a-zA-Z]{6,}\b', text)
    
    # Combine and deduplicate
    all_terms = list(set(proper_nouns + numbers + words[:50]))
    
    return all_terms[:100]  # Limit to top 100 terms
