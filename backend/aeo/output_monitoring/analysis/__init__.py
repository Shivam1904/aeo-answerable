"""
Analysis module for Output Monitoring.

Provides advanced analysis capabilities for AI engine responses:
- Brand Sentiment Analysis
- Citation Gap Analysis
- Content Recommendations
- Schema Suggestions
"""

from .sentiment import (
    SentimentResult,
    analyze_sentiment,
    analyze_brand_sentiment,
)

from .citation_gaps import (
    CitationGap,
    CitationGapAnalysis,
    CompetitorCitation,
    analyze_citation_gap,
    analyze_multiple_topics,
    generate_gap_topics,
)

from .recommendations import (
    ContentRecommendation,
    ContentRecommendationReport,
    generate_recommendations_from_gaps,
    generate_quick_wins,
    generate_content_report,
)

from .schema_suggestions import (
    SchemaSuggestion,
    SchemaAnalysisReport,
    analyze_content_for_schema,
    generate_schema_report,
)

__all__ = [
    # Sentiment Analysis
    "SentimentResult",
    "analyze_sentiment",
    "analyze_brand_sentiment",
    # Citation Gap Analysis
    "CitationGap",
    "CitationGapAnalysis",
    "CompetitorCitation",
    "analyze_citation_gap",
    "analyze_multiple_topics",
    "generate_gap_topics",
    # Content Recommendations
    "ContentRecommendation",
    "ContentRecommendationReport",
    "generate_recommendations_from_gaps",
    "generate_quick_wins",
    "generate_content_report",
    # Schema Suggestions
    "SchemaSuggestion",
    "SchemaAnalysisReport",
    "analyze_content_for_schema",
    "generate_schema_report",
]
