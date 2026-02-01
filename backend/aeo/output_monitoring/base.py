"""
Base classes for Output Monitoring module.

Provides the abstract base class for AI query engines and
data models for citations and query results.
"""
from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel


class Citation(BaseModel):
    """
    A citation detected in an AI response.
    
    Attributes:
        url: The URL or domain mentioned
        snippet: Text snippet around the citation
        position: Character position in response
    """
    url: str
    snippet: str
    position: int


class QueryResult(BaseModel):
    """
    Result from a query engine.
    
    Attributes:
        engine: Engine identifier (e.g., 'openai', 'anthropic')
        response: The AI-generated response text
        citations: List of detected citations to target URL
        tokens_used: Total tokens consumed
        cost_usd: Cost of the query in USD
        latency_ms: Response latency in milliseconds
        error: Error message if query failed
    """
    engine: str
    response: str
    citations: List[Citation]
    tokens_used: int
    cost_usd: float
    latency_ms: int
    error: Optional[str] = None


class QueryEngine(ABC):
    """
    Abstract base class for AI query engines.
    
    Each engine (OpenAI, Anthropic, etc.) inherits from this,
    similar to how each metric inherits from BaseMetric.
    
    Each engine must define:
        - name: Unique identifier (e.g., 'openai', 'anthropic')
        - query(): Async method to execute a query
        - estimate_cost(): Method to estimate cost before running
    """
    
    name: str = ""
    
    @abstractmethod
    async def query(self, prompt: str, context_url: str) -> QueryResult:
        """
        Execute query against AI engine.
        
        Args:
            prompt: User query (e.g., "What is ProcureWin?")
            context_url: URL to check for citations
            
        Returns:
            QueryResult with response, citations, cost, etc.
        """
        pass
    
    @abstractmethod
    def estimate_cost(self, prompt: str) -> float:
        """
        Estimate cost before running query.
        
        Args:
            prompt: The query prompt
            
        Returns:
            Estimated cost in USD
        """
        pass
