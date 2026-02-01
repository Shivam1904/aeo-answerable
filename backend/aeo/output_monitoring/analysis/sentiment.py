"""
Brand Sentiment Analysis Module.

Analyzes AI engine responses to determine sentiment towards a brand,
including positive/negative language detection and recommendation scoring.
"""
import re
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel

from ..base import QueryResult


class SentimentResult(BaseModel):
    """
    Result of sentiment analysis on an AI response.
    
    Attributes:
        overall_sentiment: Overall sentiment classification
        sentiment_score: Numeric score from -1.0 (negative) to 1.0 (positive)
        positive_phrases: Phrases indicating positive sentiment
        negative_phrases: Phrases indicating negative sentiment
        neutral_phrases: Factual/neutral phrases
        brand_mentions: Number of times the brand was mentioned
        recommendation_type: Whether the response recommends, warns against, or is neutral
        confidence: Confidence in the sentiment assessment (0.0 to 1.0)
    """
    overall_sentiment: Literal["positive", "neutral", "negative"]
    sentiment_score: float  # -1.0 to 1.0
    positive_phrases: List[str]
    negative_phrases: List[str]
    neutral_phrases: List[str]
    brand_mentions: int
    recommendation_type: Literal["recommended", "neutral", "cautioned", "warned_against"]
    confidence: float


# =============================================================================
# SENTIMENT LEXICONS
# =============================================================================
# Word lists for sentiment detection

POSITIVE_INDICATORS = [
    # Strong positive
    "excellent", "outstanding", "exceptional", "best", "leading", "top-rated",
    "highly recommended", "trusted", "reliable", "innovative", "cutting-edge",
    "award-winning", "industry-leading", "premier", "superior", "world-class",
    # Moderate positive
    "good", "great", "effective", "useful", "helpful", "popular", "well-known",
    "respected", "reputable", "professional", "quality", "solid", "strong",
    "recommended", "valuable", "beneficial", "successful", "proven",
    # Action positive
    "recommend", "suggest trying", "worth considering", "consider using",
    "a good choice", "a great option", "highly regarded", "well-reviewed",
]

NEGATIVE_INDICATORS = [
    # Strong negative
    "avoid", "stay away", "not recommended", "poor", "terrible", "worst",
    "unreliable", "untrustworthy", "scam", "fraud", "deceptive", "misleading",
    "dangerous", "risky", "problematic", "controversial", "criticized",
    # Moderate negative
    "issues", "problems", "concerns", "drawbacks", "limitations", "weaknesses",
    "complaints", "negative reviews", "mixed reviews", "questionable",
    "outdated", "expensive", "overpriced", "lacking", "insufficient",
    # Caution indicators
    "be careful", "exercise caution", "do your research", "buyer beware",
    "some concerns", "not without issues", "has faced criticism",
]

RECOMMENDATION_PHRASES = {
    "recommended": [
        "recommend", "highly recommend", "suggest", "consider using",
        "good choice", "great option", "worth trying", "top pick",
        "you should try", "check out", "one of the best",
    ],
    "cautioned": [
        "be careful", "exercise caution", "do your research",
        "consider alternatives", "weigh the options", "not for everyone",
        "depends on your needs", "has some issues",
    ],
    "warned_against": [
        "avoid", "stay away", "not recommended", "don't use",
        "better alternatives", "look elsewhere", "skip this",
        "wouldn't recommend", "save your money",
    ],
}


def analyze_sentiment(text: str, brand_name: str = "") -> SentimentResult:
    """
    Analyze sentiment of a text response towards a brand.
    
    Uses lexicon-based sentiment analysis with contextual awareness.
    
    Args:
        text: The AI response text to analyze
        brand_name: The brand name to focus on (optional)
        
    Returns:
        SentimentResult with detailed sentiment breakdown
    """
    if not text:
        return SentimentResult(
            overall_sentiment="neutral",
            sentiment_score=0.0,
            positive_phrases=[],
            negative_phrases=[],
            neutral_phrases=[],
            brand_mentions=0,
            recommendation_type="neutral",
            confidence=0.0,
        )
    
    text_lower = text.lower()
    
    # Count brand mentions
    brand_mentions = 0
    if brand_name:
        brand_mentions = text_lower.count(brand_name.lower())
    
    # Extract positive phrases
    positive_phrases = []
    positive_score = 0
    for indicator in POSITIVE_INDICATORS:
        if indicator.lower() in text_lower:
            # Find the sentence containing this indicator
            sentences = _split_sentences(text)
            for sentence in sentences:
                if indicator.lower() in sentence.lower():
                    positive_phrases.append(sentence.strip()[:150])
                    positive_score += 1
                    break
    
    # Extract negative phrases
    negative_phrases = []
    negative_score = 0
    for indicator in NEGATIVE_INDICATORS:
        if indicator.lower() in text_lower:
            sentences = _split_sentences(text)
            for sentence in sentences:
                if indicator.lower() in sentence.lower():
                    negative_phrases.append(sentence.strip()[:150])
                    negative_score += 1
                    break
    
    # Determine recommendation type
    recommendation_type = "neutral"
    for rec_type, phrases in RECOMMENDATION_PHRASES.items():
        for phrase in phrases:
            if phrase.lower() in text_lower:
                recommendation_type = rec_type
                break
        if recommendation_type != "neutral":
            break
    
    # Calculate overall sentiment score (-1.0 to 1.0)
    total_indicators = positive_score + negative_score
    if total_indicators > 0:
        sentiment_score = (positive_score - negative_score) / max(total_indicators, 1)
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
    else:
        sentiment_score = 0.0
    
    # Determine overall sentiment
    if sentiment_score > 0.2:
        overall_sentiment = "positive"
    elif sentiment_score < -0.2:
        overall_sentiment = "negative"
    else:
        overall_sentiment = "neutral"
    
    # Calculate confidence based on number of indicators found
    confidence = min(1.0, total_indicators / 5)  # Max confidence at 5+ indicators
    
    # Extract neutral/factual phrases (sentences without strong sentiment)
    neutral_phrases = []
    sentences = _split_sentences(text)
    for sentence in sentences[:5]:  # Limit to first 5 sentences
        sentence_lower = sentence.lower()
        has_positive = any(p.lower() in sentence_lower for p in POSITIVE_INDICATORS[:10])
        has_negative = any(n.lower() in sentence_lower for n in NEGATIVE_INDICATORS[:10])
        if not has_positive and not has_negative and len(sentence.strip()) > 20:
            neutral_phrases.append(sentence.strip()[:150])
    
    return SentimentResult(
        overall_sentiment=overall_sentiment,
        sentiment_score=round(sentiment_score, 3),
        positive_phrases=positive_phrases[:5],  # Limit to 5
        negative_phrases=negative_phrases[:5],
        neutral_phrases=neutral_phrases[:3],
        brand_mentions=brand_mentions,
        recommendation_type=recommendation_type,
        confidence=round(confidence, 3),
    )


def analyze_brand_sentiment(
    results: List[QueryResult],
    brand_name: str,
) -> Dict[str, any]:
    """
    Analyze brand sentiment across multiple AI engine responses.
    
    Args:
        results: List of QueryResults from different engines
        brand_name: The brand name to analyze
        
    Returns:
        Aggregated sentiment analysis across all engines
    """
    if not results:
        return {
            "brand": brand_name,
            "overall_sentiment": "neutral",
            "average_score": 0.0,
            "engines_positive": 0,
            "engines_neutral": 0,
            "engines_negative": 0,
            "total_brand_mentions": 0,
            "recommendation_summary": "neutral",
            "per_engine_results": [],
        }
    
    per_engine_results = []
    total_score = 0.0
    total_mentions = 0
    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
    recommendation_counts = {"recommended": 0, "neutral": 0, "cautioned": 0, "warned_against": 0}
    
    for result in results:
        if result.error or not result.response:
            continue
            
        sentiment = analyze_sentiment(result.response, brand_name)
        per_engine_results.append({
            "engine": result.engine,
            "sentiment": sentiment.overall_sentiment,
            "score": sentiment.sentiment_score,
            "recommendation": sentiment.recommendation_type,
            "brand_mentions": sentiment.brand_mentions,
            "positive_phrases": sentiment.positive_phrases,
            "negative_phrases": sentiment.negative_phrases,
        })
        
        total_score += sentiment.sentiment_score
        total_mentions += sentiment.brand_mentions
        sentiment_counts[sentiment.overall_sentiment] += 1
        recommendation_counts[sentiment.recommendation_type] += 1
    
    # Calculate averages
    num_valid = len(per_engine_results)
    avg_score = total_score / num_valid if num_valid > 0 else 0.0
    
    # Determine overall sentiment
    if avg_score > 0.2:
        overall = "positive"
    elif avg_score < -0.2:
        overall = "negative"
    else:
        overall = "neutral"
    
    # Determine recommendation summary
    if recommendation_counts["warned_against"] > 0:
        rec_summary = "warned_against"
    elif recommendation_counts["cautioned"] > recommendation_counts["recommended"]:
        rec_summary = "cautioned"
    elif recommendation_counts["recommended"] > 0:
        rec_summary = "recommended"
    else:
        rec_summary = "neutral"
    
    return {
        "brand": brand_name,
        "overall_sentiment": overall,
        "average_score": round(avg_score, 3),
        "engines_positive": sentiment_counts["positive"],
        "engines_neutral": sentiment_counts["neutral"],
        "engines_negative": sentiment_counts["negative"],
        "total_brand_mentions": total_mentions,
        "recommendation_summary": rec_summary,
        "per_engine_results": per_engine_results,
    }


def _split_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    # Simple sentence splitting on common punctuation
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]
