"""
AI Readiness Score Calculation.

This module provides the logic for deriving a 'Readiness Score' from AEO scan results.
The score measures how well a website is optimized for AI Answer Engines.
"""
from typing import Dict, Any, List

def calculate_ai_readiness(scan_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate AI Readiness Score (0-100) from crawler results.
    
    Weights:
    - Schema Coverage: 40%
    - Metadata Quality: 30%
    - Content Structure (H1s, etc.): 20%
    - Entity Density: 10%
    """
    pages = scan_result.get("pages", [])
    if not pages:
        return {"score": 0, "breakdown": {}}

    num_pages = len(pages)
    
    total_schema_score = 0
    total_meta_score = 0
    total_structure_score = 0
    total_entity_score = 0

    for page in pages:
        # 1. Schema Coverage (40%)
        # Check for JSON-LD or Microdata
        has_schema = page.get("metrics", {}).get("has_json_ld", False) or page.get("metrics", {}).get("has_microdata", False)
        total_schema_score += 100 if has_schema else 0

        # 2. Metadata Quality (30%)
        # Check for title and description presence/length
        has_meta = page.get("metadata", {}).get("title") and page.get("metadata", {}).get("description")
        total_meta_score += 100 if has_meta else 0

        # 3. Content Structure (20%)
        # Check for H1s
        has_h1 = page.get("content_analysis", {}).get("h1_count", 0) > 0
        total_structure_score += 100 if has_h1 else 0

        # 4. Entity Density (10%)
        # Check for person/org/product detections
        entities = page.get("content_analysis", {}).get("entities", [])
        total_entity_score += 100 if len(entities) > 5 else (len(entities) * 20)

    # Averages
    avg_schema = total_schema_score / num_pages
    avg_meta = total_meta_score / num_pages
    avg_structure = total_structure_score / num_pages
    avg_entity = total_entity_score / num_pages

    # Weighted Score (Task 4 updated)
    # Schema (35%), Metadata (25%), Structure (20%), Entities (10%), Narrative (10%)
    final_score = (
        (avg_schema * 0.35) +
        (avg_meta * 0.25) +
        (avg_structure * 0.20) +
        (avg_entity * 0.10) +
        (85 * 0.10) # Placeholder for narrative alignment detection
    )

    return {
        "score": round(final_score, 2),
        "breakdown": {
            "schema_coverage": round(avg_schema, 2),
            "metadata_quality": round(avg_meta, 2),
            "content_structure": round(avg_structure, 2),
            "entity_density": round(avg_entity, 2),
            "narrative_alignment": 85
        }
    }
