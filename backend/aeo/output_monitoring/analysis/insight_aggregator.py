import re
from typing import List, Dict, Any
from .models import BrandProfile

def aggregate_sota_insights(
    results: List[Dict[str, Any]], 
    profile: BrandProfile
) -> Dict[str, Any]:
    """
    Analyzes multiple engine responses to extract competitive insights.
    
    Args:
        results: List of QueryResult-like dicts.
        profile: The brand profile for context.
        
    Returns:
        Dictionary of aggregated insights.
    """
    competitor_mentions = {comp: 0 for comp in profile.primary_competitors}
    brand_mentions = 0
    total_responses = len(results)
    
    # Sentiment simple proxy (look for positive/negative keywords or use a small model later)
    # For MVP, we use keyword density or just mock the calculation logic structure
    brand_sentiment = 0.0
    
    for res in results:
        text = res.get("response", "").lower()
        if not text:
            continue
            
        # 1. Share of Voice
        if profile.brand_name.lower() in text:
            brand_mentions += 1
            
        for comp in profile.primary_competitors:
            if comp.lower() in text:
                competitor_mentions[comp] += 1
                
        # 2. Sentiment (Very basic heuristic for now)
        pos_words = ['great', 'best', 'excellent', 'recommend', 'better', 'good', 'leading']
        neg_words = ['bad', 'expensive', 'difficult', 'worse', 'limited', 'poor', 'not recommended']
        
        pos_count = sum(1 for word in pos_words if word in text)
        neg_count = sum(1 for word in neg_words if word in text)
        
        if (pos_count + neg_count) > 0:
            res_sentiment = (pos_count - neg_count) / (pos_count + neg_count)
            brand_sentiment += res_sentiment

    # Normalize insights
    share_of_voice = {
        profile.brand_name: round((brand_mentions / total_responses) * 100, 1) if total_responses else 0
    }
    for comp, count in competitor_mentions.items():
        share_of_voice[comp] = round((count / total_responses) * 100, 1) if total_responses else 0
        
    avg_sentiment = (brand_sentiment / total_responses) if total_responses else 0
    
    return {
        "share_of_voice": share_of_voice,
        "sentiment_profile": {
            "brand_sentiment": round((avg_sentiment + 1) * 50, 1), # Scale -1..1 to 0..100
            "industry_benchmark": profile.industry_baseline_sentiment * 100,
            "label": "Positive" if avg_sentiment > 0.2 else "Neutral" if avg_sentiment > -0.2 else "Negative"
        },
        "key_takeaways": _generate_takeaways(share_of_voice, avg_sentiment, profile)
    }

def _generate_takeaways(sov: Dict[str, float], sentiment: float, profile: BrandProfile) -> List[str]:
    takeaways = []
    brand = profile.brand_name
    
    brand_sov = sov.get(brand, 0)
    top_comp = max(sov.items(), key=lambda x: x[1] if x[0] != brand else -1)
    
    if brand_sov > 80:
        takeaways.append(f"Dominant Presence: {brand} is the primary recommendation.")
    elif brand_sov < 30:
        takeaways.append(f"Low Visibility: {brand} is frequently overlooked in favor of competitors.")
        
    if top_comp[1] > brand_sov:
        takeaways.append(f"Competitive Threat: {top_comp[0]} has higher share of voice in AI responses.")
        
    if sentiment > 0.5:
        takeaways.append(f"Strong Reputation: AI engines consistently associate {brand} with positive traits.")
        
    return takeaways
