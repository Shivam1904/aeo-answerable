"""
Content Recommendations Module.

Generates actionable content recommendations to improve AI citability
based on citation gap analysis and sentiment data.
"""
from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel

from .citation_gaps import CitationGap, CitationGapAnalysis
from .sentiment import SentimentResult


class ContentRecommendation(BaseModel):
    """
    A single content recommendation.
    
    Attributes:
        title: Suggested content title
        content_type: Type of content to create
        target_queries: Queries this content should answer
        priority: How important this recommendation is
        estimated_impact: Expected improvement in citations
        reasoning: Why this content is recommended
        outline: Suggested content outline/sections
        keywords: Important keywords to include
    """
    title: str
    content_type: Literal["blog_post", "faq_page", "guide", "landing_page", "comparison", "case_study"]
    target_queries: List[str]
    priority: Literal["high", "medium", "low"]
    estimated_impact: str
    reasoning: str
    outline: List[str]
    keywords: List[str]


class ContentRecommendationReport(BaseModel):
    """
    Complete content recommendation report.
    
    Attributes:
        brand: Brand name
        total_recommendations: Number of recommendations generated
        high_priority_count: Count of high-priority recommendations
        recommendations: List of content recommendations
        quick_wins: Easy-to-implement improvements
    """
    brand: str
    total_recommendations: int
    high_priority_count: int
    recommendations: List[ContentRecommendation]
    quick_wins: List[str]


# =============================================================================
# CONTENT TYPE TEMPLATES
# =============================================================================

CONTENT_TYPE_TEMPLATES = {
    "blog_post": {
        "outline": [
            "Introduction - Hook and problem statement",
            "Background - Context and why this matters",
            "Main Content - Key points with examples",
            "Expert Insights - Quotes or data",
            "Conclusion - Summary and call to action",
        ],
        "ideal_for": ["thought leadership", "industry trends", "how-to guides"],
    },
    "faq_page": {
        "outline": [
            "Common Questions Section",
            "Getting Started Questions",
            "Technical Questions",
            "Pricing/Plan Questions",
            "Support Questions",
        ],
        "ideal_for": ["product questions", "customer support", "seo"],
    },
    "guide": {
        "outline": [
            "Executive Summary",
            "Step-by-Step Instructions",
            "Best Practices",
            "Common Mistakes to Avoid",
            "Resources and Next Steps",
        ],
        "ideal_for": ["educational content", "complex topics", "tutorials"],
    },
    "landing_page": {
        "outline": [
            "Hero Section - Value proposition",
            "Problem/Solution Section",
            "Features and Benefits",
            "Social Proof - Testimonials/logos",
            "Call to Action",
        ],
        "ideal_for": ["product launches", "campaigns", "conversions"],
    },
    "comparison": {
        "outline": [
            "Overview of Options",
            "Feature Comparison Table",
            "Pros and Cons of Each",
            "Use Case Recommendations",
            "Final Verdict",
        ],
        "ideal_for": ["vs competitors", "product comparisons", "buying guides"],
    },
    "case_study": {
        "outline": [
            "Client Background",
            "Challenge/Problem",
            "Solution Implemented",
            "Results and Metrics",
            "Key Takeaways",
        ],
        "ideal_for": ["proof points", "enterprise sales", "credibility"],
    },
}


def generate_recommendations_from_gaps(
    gaps: List[CitationGap],
    brand_name: str,
) -> List[ContentRecommendation]:
    """
    Generate content recommendations from citation gaps.
    
    Args:
        gaps: List of citation gaps from analysis
        brand_name: Your brand name
        
    Returns:
        List of content recommendations
    """
    recommendations = []
    
    # Sort gaps by severity
    critical_gaps = [g for g in gaps if g.gap_severity == "critical"]
    moderate_gaps = [g for g in gaps if g.gap_severity == "moderate"]
    minor_gaps = [g for g in gaps if g.gap_severity == "minor"]
    
    # Generate recommendations for critical gaps
    for gap in critical_gaps:
        rec = _create_recommendation_for_gap(gap, brand_name, "high")
        recommendations.append(rec)
    
    # Generate recommendations for moderate gaps
    for gap in moderate_gaps[:5]:  # Limit to top 5
        rec = _create_recommendation_for_gap(gap, brand_name, "medium")
        recommendations.append(rec)
    
    # Generate recommendations for minor gaps
    for gap in minor_gaps[:3]:  # Limit to top 3
        rec = _create_recommendation_for_gap(gap, brand_name, "low")
        recommendations.append(rec)
    
    return recommendations


def _create_recommendation_for_gap(
    gap: CitationGap,
    brand_name: str,
    priority: Literal["high", "medium", "low"],
) -> ContentRecommendation:
    """Create a content recommendation for a specific gap."""
    topic = gap.topic
    
    # Determine content type based on topic
    content_type = _determine_content_type(topic)
    template = CONTENT_TYPE_TEMPLATES[content_type]
    
    # Generate title
    title = _generate_title(topic, brand_name, content_type)
    
    # Generate keywords
    keywords = _extract_keywords(topic, brand_name)
    
    # Calculate estimated impact
    if priority == "high":
        impact = f"Could increase citation rate by 30-50% for '{topic}' queries"
    elif priority == "medium":
        impact = f"Could improve visibility for '{topic}' related queries"
    else:
        impact = f"May help with '{topic}' search visibility"
    
    # Generate reasoning
    if gap.top_competitor and gap.competitor_citations:
        top_rate = gap.competitor_citations[0].citation_rate if gap.competitor_citations else 0
        reasoning = f"Competitor '{gap.top_competitor}' currently dominates this topic with {top_rate*100:.0f}% citation rate. Creating authoritative content can close this gap."
    else:
        reasoning = f"Your current citation rate for '{topic}' is only {gap.your_citation_rate*100:.0f}%. New content can establish authority."
    
    return ContentRecommendation(
        title=title,
        content_type=content_type,
        target_queries=[topic] + _generate_related_queries(topic),
        priority=priority,
        estimated_impact=impact,
        reasoning=reasoning,
        outline=template["outline"],
        keywords=keywords,
    )


def _determine_content_type(topic: str) -> str:
    """Determine best content type for a topic."""
    topic_lower = topic.lower()
    
    if "vs" in topic_lower or "alternative" in topic_lower or "comparison" in topic_lower:
        return "comparison"
    elif "how" in topic_lower or "guide" in topic_lower or "tutorial" in topic_lower:
        return "guide"
    elif "what is" in topic_lower or "explain" in topic_lower:
        return "blog_post"
    elif "pricing" in topic_lower or "cost" in topic_lower or "plan" in topic_lower:
        return "landing_page"
    elif "review" in topic_lower or "experience" in topic_lower:
        return "case_study"
    elif "?" in topic or "how" in topic_lower:
        return "faq_page"
    else:
        return "blog_post"


def _generate_title(topic: str, brand_name: str, content_type: str) -> str:
    """Generate a compelling title for the content."""
    topic_clean = topic.replace("?", "").strip()
    
    if content_type == "comparison":
        return f"{brand_name} vs Alternatives: Comprehensive Comparison Guide"
    elif content_type == "guide":
        return f"Complete Guide: {topic_clean}"
    elif content_type == "faq_page":
        return f"Frequently Asked Questions About {brand_name}"
    elif content_type == "landing_page":
        return f"{brand_name} - {topic_clean.title()}"
    elif content_type == "case_study":
        return f"How Companies Succeed with {brand_name}: Case Studies"
    else:
        return f"{topic_clean}: Everything You Need to Know"


def _extract_keywords(topic: str, brand_name: str) -> List[str]:
    """Extract keywords from topic."""
    # Remove common words
    stop_words = {"what", "is", "the", "a", "an", "how", "to", "do", "does", "are", "?"}
    words = topic.lower().split()
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Add brand name
    keywords.insert(0, brand_name.lower())
    
    # Add common variations
    keywords.extend([
        f"{brand_name.lower()} review",
        f"{brand_name.lower()} features",
        f"best {keywords[-1]}" if keywords else f"best {brand_name.lower()}",
    ])
    
    return list(set(keywords))[:10]


def _generate_related_queries(topic: str) -> List[str]:
    """Generate related queries for a topic."""
    related = []
    topic_clean = topic.replace("?", "").strip()
    
    if "what is" in topic.lower():
        base = topic_clean.replace("What is", "").replace("what is", "").strip()
        related = [
            f"How does {base} work?",
            f"Is {base} worth it?",
            f"{base} benefits",
        ]
    elif "vs" in topic.lower() or "alternative" in topic.lower():
        related = [
            f"Best alternatives comparison",
            f"Which one should I choose?",
            f"Detailed feature comparison",
        ]
    else:
        related = [
            f"{topic_clean} explained",
            f"{topic_clean} for beginners",
            f"Best practices for {topic_clean}",
        ]
    
    return related[:3]


def generate_quick_wins(
    gaps: List[CitationGap],
    brand_name: str,
) -> List[str]:
    """
    Generate quick-win improvements that can be done immediately.
    
    Args:
        gaps: Citation gap analysis
        brand_name: Your brand name
        
    Returns:
        List of quick-win suggestions
    """
    quick_wins = []
    
    # Check for brand-related issues
    brand_queries = [g for g in gaps if brand_name.lower() in g.topic.lower()]
    if brand_queries and any(g.your_citation_rate < 0.3 for g in brand_queries):
        quick_wins.append(
            f"Add a comprehensive 'About {brand_name}' page with clear value proposition, history, and key facts"
        )
    
    # Check for FAQ opportunities
    question_queries = [g for g in gaps if "?" in g.topic or "how" in g.topic.lower()]
    if question_queries:
        quick_wins.append(
            "Create an FAQ section answering common questions directly with clear, concise answers"
        )
    
    # Check for comparison opportunities
    comparison_queries = [g for g in gaps if "vs" in g.topic.lower() or "alternative" in g.topic.lower()]
    if comparison_queries:
        quick_wins.append(
            "Create a comparison page that honestly compares your solution to alternatives"
        )
    
    # General recommendations
    quick_wins.extend([
        "Add structured data (Schema.org) to help AI engines understand your content",
        "Ensure your homepage clearly states what your company does in the first paragraph",
        "Include specific facts, numbers, and statistics that AI can cite",
        "Update any outdated content with current information and dates",
    ])
    
    return quick_wins[:6]  # Limit to 6 quick wins


def generate_content_report(
    gaps: List[CitationGap],
    brand_name: str,
) -> ContentRecommendationReport:
    """
    Generate a complete content recommendation report.
    
    Args:
        gaps: Citation gap analysis results
        brand_name: Your brand name
        
    Returns:
        Complete content recommendation report
    """
    recommendations = generate_recommendations_from_gaps(gaps, brand_name)
    quick_wins = generate_quick_wins(gaps, brand_name)
    
    high_priority = sum(1 for r in recommendations if r.priority == "high")
    
    return ContentRecommendationReport(
        brand=brand_name,
        total_recommendations=len(recommendations),
        high_priority_count=high_priority,
        recommendations=recommendations,
        quick_wins=quick_wins,
    )
