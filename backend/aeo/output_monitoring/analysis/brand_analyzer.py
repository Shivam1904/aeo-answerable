import json
import json
import logging
from typing import Dict, Any, Optional

from langchain_core.messages import SystemMessage, HumanMessage

from ..engines import create_openai_engine
from .models import BrandProfile

logger = logging.getLogger(__name__)

BRAND_ANALYSIS_PROMPT = """
You are a SOTA AEO (AI Engine Optimization) Analyst. 
Your goal is to analyze the provided website content and extract a structured "Brand Identity Profile".

Focus on:
1. Identifying the core product/service.
2. Identifying the top 3-5 target personas (be specific, e.g., "Seed-stage SaaS Founders" not just "Business Owners").
3. Identifying the top 3 direct competitors.
4. Extracting key value propositions.

Return the result STRICTLY as a JSON object following this structure:
{{
    "brand_name": "...",
    "industry": "...",
    "tagline": "...",
    "target_audience": ["...", "..."],
    "key_value_props": ["...", "..."],
    "primary_competitors": ["...", "..."],
    "industry_baseline_sentiment": 0.5
}}
"""

async def analyze_brand(
    text: str, 
    api_key: str, 
    model: str = "gpt-4o-mini"
) -> Optional[BrandProfile]:
    """
    Analyzes page text to extract a BrandProfile.
    
    Args:
        text: The extracted page content.
        api_key: OpenAI API key.
        model: Model to use for analysis.
        
    Returns:
        BrandProfile object if successful, else None.
    """
    if not text or len(text) < 100:
        logger.warning("Text too short for brand analysis.")
        return None

    try:
        # Create a dedicated OpenAI engine instance for analysis
        # Using LangChain's underlying chain for structured output if possible, 
        # but manual JSON parsing is safer for simple MVP.
        engine = create_openai_engine(api_key, model=model)
        
        # Build prompt
        messages = [
            SystemMessage(content=BRAND_ANALYSIS_PROMPT),
            HumanMessage(content=f"Analyze this content:\n\n{text[:8000]}") # Clamp text length
        ]
        
        # Use underlying langchain model directly for structured output
        # or just invoke and parse. Since we want "clean" code:
        response = await engine._llm.ainvoke(messages)
        content = response.content
        
        # Simple JSON extraction
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        data = json.loads(content)
        return BrandProfile(**data)
        
    except Exception as e:
        logger.error(f"Brand analysis failed: {str(e)}")
        return None
