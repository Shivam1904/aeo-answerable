"""
Citation Gap Analysis Module.

Identifies topics where competitors get cited by AI engines but your brand doesn't,
helping you understand content gaps and opportunities.
"""
from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel
from urllib.parse import urlparse

from ..base import QueryResult


class CompetitorCitation(BaseModel):
    """Citation data for a competitor."""
    url: str
    domain: str
    citation_count: int
    citation_rate: float  # 0.0 to 1.0


class CitationGap(BaseModel):
    """
    A single citation gap - a topic where competitors outperform you.
    
    Attributes:
        topic: The topic/query that was tested
        your_citation_rate: Your citation rate (0.0 to 1.0)
        competitor_citations: List of competitor citation data
        gap_severity: How severe the gap is
        top_competitor: The competitor with highest citation rate
        suggested_action: Recommended action to close the gap
    """
    topic: str
    your_citation_rate: float
    your_citation_count: int
    total_queries: int
    competitor_citations: List[CompetitorCitation]
    gap_severity: Literal["critical", "moderate", "minor", "none"]
    top_competitor: Optional[str]
    suggested_action: str


class CitationGapAnalysis(BaseModel):
    """
    Complete citation gap analysis across multiple topics.
    
    Attributes:
        your_url: Your website URL
        competitor_urls: List of competitor URLs analyzed
        topics_analyzed: Number of topics/queries analyzed
        gaps: List of identified citation gaps
        summary: Overall summary statistics
    """
    your_url: str
    competitor_urls: List[str]
    topics_analyzed: int
    gaps: List[CitationGap]
    summary: Dict[str, Any]


def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    if domain.startswith("www."):
        domain = domain[4:]
    return domain.lower()


def analyze_citation_gap(
    topic: str,
    your_results: List[QueryResult],
    competitor_results: Dict[str, List[QueryResult]],
    your_url: str,
) -> CitationGap:
    """
    Analyze citation gap for a single topic.
    
    Args:
        topic: The topic/query being analyzed
        your_results: QueryResults for your brand
        competitor_results: Dict of competitor URL -> their QueryResults
        your_url: Your website URL
        
    Returns:
        CitationGap with analysis details
    """
    your_domain = extract_domain(your_url)
    
    # Calculate your citation rate
    your_citations = 0
    your_total = 0
    for result in your_results:
        if result.response and not result.error:
            your_total += 1
            # Check if any citation matches your domain
            for citation in result.citations:
                if your_domain in citation.url.lower():
                    your_citations += 1
                    break
    
    your_rate = your_citations / your_total if your_total > 0 else 0.0
    
    # Calculate competitor citation rates
    competitor_data: List[CompetitorCitation] = []
    top_competitor = None
    top_rate = 0.0
    
    for comp_url, comp_results in competitor_results.items():
        comp_domain = extract_domain(comp_url)
        comp_citations = 0
        comp_total = 0
        
        for result in comp_results:
            if result.response and not result.error:
                comp_total += 1
                # Check citations in the response
                response_lower = result.response.lower()
                if comp_domain in response_lower:
                    comp_citations += 1
                # Also check citation objects
                for citation in result.citations:
                    if comp_domain in citation.url.lower():
                        comp_citations += 1
                        break
        
        comp_rate = comp_citations / comp_total if comp_total > 0 else 0.0
        
        competitor_data.append(CompetitorCitation(
            url=comp_url,
            domain=comp_domain,
            citation_count=comp_citations,
            citation_rate=round(comp_rate, 3),
        ))
        
        if comp_rate > top_rate:
            top_rate = comp_rate
            top_competitor = comp_domain
    
    # Determine gap severity
    gap_diff = top_rate - your_rate
    if gap_diff >= 0.5:
        severity = "critical"
    elif gap_diff >= 0.3:
        severity = "moderate"
    elif gap_diff > 0:
        severity = "minor"
    else:
        severity = "none"
    
    # Generate suggested action
    if severity == "critical":
        action = f"Create comprehensive content about '{topic}'. Competitor {top_competitor} dominates this topic."
    elif severity == "moderate":
        action = f"Enhance existing content about '{topic}' with more detailed, authoritative information."
    elif severity == "minor":
        action = f"Consider updating content about '{topic}' to improve citability."
    else:
        action = f"You're well-positioned for '{topic}'. Maintain content freshness."
    
    return CitationGap(
        topic=topic,
        your_citation_rate=round(your_rate, 3),
        your_citation_count=your_citations,
        total_queries=your_total,
        competitor_citations=competitor_data,
        gap_severity=severity,
        top_competitor=top_competitor,
        suggested_action=action,
    )


def analyze_multiple_topics(
    topics: List[str],
    results_by_topic: Dict[str, Dict[str, List[QueryResult]]],
    your_url: str,
    competitor_urls: List[str],
) -> CitationGapAnalysis:
    """
    Analyze citation gaps across multiple topics.
    
    Args:
        topics: List of topics/queries to analyze
        results_by_topic: Nested dict of topic -> url -> results
        your_url: Your website URL
        competitor_urls: List of competitor URLs
        
    Returns:
        Complete CitationGapAnalysis
    """
    gaps = []
    
    for topic in topics:
        topic_results = results_by_topic.get(topic, {})
        your_results = topic_results.get(your_url, [])
        
        competitor_results = {
            comp_url: topic_results.get(comp_url, [])
            for comp_url in competitor_urls
        }
        
        gap = analyze_citation_gap(topic, your_results, competitor_results, your_url)
        gaps.append(gap)
    
    # Calculate summary statistics
    critical_count = sum(1 for g in gaps if g.gap_severity == "critical")
    moderate_count = sum(1 for g in gaps if g.gap_severity == "moderate")
    minor_count = sum(1 for g in gaps if g.gap_severity == "minor")
    
    avg_your_rate = sum(g.your_citation_rate for g in gaps) / len(gaps) if gaps else 0.0
    
    # Find most problematic competitor
    competitor_totals: Dict[str, int] = {}
    for gap in gaps:
        for comp in gap.competitor_citations:
            competitor_totals[comp.domain] = competitor_totals.get(comp.domain, 0) + comp.citation_count
    
    biggest_threat = max(competitor_totals.items(), key=lambda x: x[1])[0] if competitor_totals else None
    
    summary = {
        "critical_gaps": critical_count,
        "moderate_gaps": moderate_count,
        "minor_gaps": minor_count,
        "no_gaps": len(gaps) - critical_count - moderate_count - minor_count,
        "your_average_citation_rate": round(avg_your_rate, 3),
        "biggest_competitor_threat": biggest_threat,
        "total_topics": len(topics),
    }
    
    return CitationGapAnalysis(
        your_url=your_url,
        competitor_urls=competitor_urls,
        topics_analyzed=len(topics),
        gaps=gaps,
        summary=summary,
    )


def generate_gap_topics(brand_name: str, industry: str = "") -> List[str]:
    """
    Generate topics to test for citation gaps.
    
    Args:
        brand_name: Your brand name
        industry: Optional industry for more specific topics
        
    Returns:
        List of query topics to test
    """
    base_topics = [
        f"What is {brand_name}?",
        f"Is {brand_name} reliable?",
        f"What are alternatives to {brand_name}?",
        f"{brand_name} reviews",
        f"{brand_name} pricing",
        f"How does {brand_name} work?",
        f"Best {brand_name} features",
        f"{brand_name} vs competitors",
    ]
    
    if industry:
        industry_topics = [
            f"Best {industry} solutions",
            f"Top {industry} companies",
            f"{industry} comparison",
            f"Leading {industry} providers",
        ]
        base_topics.extend(industry_topics)
    
    return base_topics
