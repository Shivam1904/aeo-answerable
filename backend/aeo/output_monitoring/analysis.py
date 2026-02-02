
import json
from aeo.config import Settings
from aeo.output_monitoring.engines import create_openai_engine

async def analyze_response_metrics(
    query: str,
    response_text: str, 
    brand_name: str,
    product_bio: str = ""
) -> dict:
    """
    Analyzes an LLM response to extract AEO metrics:
    - Share of Voice
    - Sentiment
    - Recommendation Strength
    - Rank
    - Hallucinations
    """
    settings = Settings()
    if not settings.openai_api_key:
        return {}
        
    engine = create_openai_engine(settings.openai_api_key, model="gpt-4o-mini")
    
    prompt = f"""
    Analyze the following AI response to a user query about "{brand_name}".
    
    User Query: "{query}"
    
    AI Response:
    \"\"\"{response_text}\"\"\"
    
    Brand Context (Bio):
    "{product_bio}"
    
    Provide a JSON analysis with exactly these keys:
    1. "share_of_voice": (0-100) estimated percentage of text related to {brand_name}.
    2. "sentiment_score": (-100 to 100) overall sentiment for {brand_name}.
    3. "recommendation": One of ["Winner", "Top Contender", "Alternative", "Not Recommended", "Neutral"].
    4. "rank": (Evaluate if a list exists. If yes, what number is {brand_name}? If not in list use -1. If no list, use 0).
    5. "key_attributes": Array of objects {{ "name": "attribute_name", "sentiment": "Positive"|"Negative"|"Neutral" }}.
    6. "hallucinations": Array of strings listing any potential factual errors about {brand_name} based on the Bio (if Bio provided).
    
    Return ONLY valid JSON.
    """
    
    # We use a dummy URL since we don't need citation checking for this meta-analysis
    result = await engine.query(prompt, context_url="http://ignore.com")
    
    try:
        # Clean up code blocks if present
        content = result.response
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        data = json.loads(content.strip())
        return data
    except Exception as e:
        print(f"Analysis failed: {e}")
        return {}
