from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class BrandProfile(BaseModel):
    """
    Structured brand identity profile extracted from page content.
    """
    brand_name: str = Field(..., description="The official name of the brand or product.")
    industry: str = Field(..., description="The primary industry or category (e.g., 'SaaS', 'Ecommerce').")
    tagline: Optional[str] = Field(None, description="The brand's tagline or core mission statement.")
    target_audience: List[str] = Field(default_factory=list, description="Top 3-5 target personas.")
    key_value_props: List[str] = Field(default_factory=list, description="Main benefits or features.")
    primary_competitors: List[str] = Field(default_factory=list, description="Top 3 direct competitors.")
    industry_baseline_sentiment: float = Field(default=0.5, description="General sentiment of this industry (0-1).")

class AnalysisResult(BaseModel):
    """
    Container for brand profile and generated queries.
    """
    profile: BrandProfile
    suggested_queries: List[Dict] = Field(default_factory=list)
