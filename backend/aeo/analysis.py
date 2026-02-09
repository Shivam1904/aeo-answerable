"""
AI Gap Analysis Module.

Analyzes AI engine responses to identify why competitors are cited instead of the user
and provides actionable content optimization steps.
"""
import re
from typing import List, Dict, Any, Set
from urllib.parse import urlparse

def generate_action_plan(comparison_results: Dict[str, Any], your_url: str) -> List[Dict[str, Any]]:
    """
    Analyzes competitive query results to generate a prioritized action plan.
    
    Args:
        comparison_results: The 'comparison' list from competitive_query output.
        your_url: The URL of the user's site.
        
    Returns:
        List of action items with priority, title, and description.
    """
    actions = []
    your_data = next((item for item in comparison_results.get('comparison', []) if item['url'] == your_url), None)
    competitors = [item for item in comparison_results.get('comparison', []) if item['url'] != your_url]
    
    if not your_data:
        return actions

    # 1. Identify "Lost" Conversions (Competitor cited, you weren't)
    # We look at the individual engine results
    query = comparison_results.get('query', '')
    
    # Extract keywords from competitor responses where you were NOT cited
    competitor_keywords = _extract_competitor_keywords(competitors)
    
    # 2. Schema Gap
    if your_data['engines_cited'] == 0 and any(c['engines_cited'] > 0 for c in competitors):
        actions.append({
            'type': 'schema',
            'priority': 'high',
            'title': 'Missing Technical Authority (Schema)',
            'description': f"Competitors are being cited for '{query}' but you are not. This often indicates a lack of SearchAction or Product schema that AI engines use for grounding.",
            'fix_action': 'Generate and deploy JSON-LD Schema'
        })

    # 3. Content Narrative Gap
    missing_themes = _identify_missing_themes(your_data, competitors)
    for theme in missing_themes:
        actions.append({
            'type': 'content',
            'priority': 'medium',
            'title': f"Content Gap: {theme}",
            'description': f"AI engines consistently associate this topic with competitors. Adding a dedicated section about '{theme}' to your page will improve your alignment with the model's training data.",
            'fix_action': f'Add {theme} information'
        })

    # 4. Authority Gap
    if your_data['citation_rate'] < 0.3 and any(c['citation_rate'] > 0.6 for c in competitors):
        actions.append({
            'type': 'authority',
            'priority': 'high',
            'title': 'Low Multi-Model Consensus',
            'description': "Your site is only cited by one or zero models, while competitors have consensus across OpenAI and Anthropic. This suggests a need for more direct 'About' page declarations.",
            'fix_action': 'Update Brand Narrative'
        })

    return actions

def _extract_competitor_keywords(competitors: List[Dict[str, Any]]) -> Set[str]:
    """Simple extraction of key thematic nouns from competitor responses."""
    # Placeholder for more complex NLP
    # For now, we'll look for common business terms
    keywords = {"pricing", "features", "security", "enterprise", "integration", "customers", "reviews", "support"}
    detected = set()
    for comp in competitors:
        for res in comp.get('results', []):
            text = res.get('response', '').lower()
            for kw in keywords:
                if kw in text:
                    detected.add(kw)
    return detected

def _identify_missing_themes(your_data: Dict[str, Any], competitors: List[Dict[str, Any]]) -> List[str]:
    """Identifies themes present in competitor responses but missing from user responses."""
    # Simple heuristic: what did competitors get cited for that you didn't?
    themes = ["Pricing Transparency", "Enterprise Security", "Technical Documentation", "Customer Proof"]
    # Real logic would use embeddings or keyword density comparison
    # Returning a mockup for Task 4 phase 1
    return themes[:2] if your_data['citation_rate'] < 0.5 else []
