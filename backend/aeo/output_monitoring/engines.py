"""
Unified LangChain-based Query Engine.

Uses LangChain to provide a consistent interface for multiple LLM providers
(OpenAI, Anthropic, Google Gemini) with built-in retry logic and error handling.

This single module replaces the separate openai_engine.py, anthropic_engine.py,
and gemini_engine.py files, significantly reducing code duplication.
"""
import asyncio
import time
from typing import Optional, Dict, Any, Type
from abc import ABC

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from .base import QueryEngine, QueryResult
from .parser import extract_citations
from .constants import (
    MAX_RETRIES,
    RETRY_DELAY,
    RETRY_MULTIPLIER,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    OPENAI_INPUT_COST_PER_1M,
    OPENAI_OUTPUT_COST_PER_1M,
    ANTHROPIC_INPUT_COST_PER_1M,
    ANTHROPIC_OUTPUT_COST_PER_1M,
    GEMINI_INPUT_COST_PER_1M,
    GEMINI_OUTPUT_COST_PER_1M,
    SEARCHGPT_INPUT_COST_PER_1M,
    SEARCHGPT_OUTPUT_COST_PER_1M,
    BING_COPILOT_INPUT_COST_PER_1M,
    BING_COPILOT_OUTPUT_COST_PER_1M,
)
from .prompts import (
    OPENAI_SYSTEM_PROMPT,
    ANTHROPIC_SYSTEM_PROMPT,
    GEMINI_SYSTEM_PROMPT,
    SEARCHGPT_SYSTEM_PROMPT,
    BING_COPILOT_SYSTEM_PROMPT,
)


# =============================================================================
# ENGINE CONFIGURATION
# =============================================================================
# Centralized configuration for all supported engines
# Using cheapest capable models to minimize costs

ENGINE_CONFIGS: Dict[str, Dict[str, Any]] = {
    "openai": {
        "model": "gpt-4o-mini",  # Cheapest capable OpenAI model
        "input_cost_per_1m": OPENAI_INPUT_COST_PER_1M,
        "output_cost_per_1m": OPENAI_OUTPUT_COST_PER_1M,
        "system_prompt": OPENAI_SYSTEM_PROMPT,
    },
    "anthropic": {
        "model": "claude-3-5-haiku-latest",  # Cheapest capable Anthropic model
        "input_cost_per_1m": ANTHROPIC_INPUT_COST_PER_1M,
        "output_cost_per_1m": ANTHROPIC_OUTPUT_COST_PER_1M,
        "system_prompt": ANTHROPIC_SYSTEM_PROMPT,
    },
    "gemini": {
        "model": "gemini-2.0-flash-lite",  # Cheapest Gemini model
        "input_cost_per_1m": GEMINI_INPUT_COST_PER_1M,
        "output_cost_per_1m": GEMINI_OUTPUT_COST_PER_1M,
        "system_prompt": GEMINI_SYSTEM_PROMPT,
    },
    "searchgpt": {
        "model": "gpt-4o-search-preview",  # OpenAI's search-enabled model
        "input_cost_per_1m": SEARCHGPT_INPUT_COST_PER_1M,
        "output_cost_per_1m": SEARCHGPT_OUTPUT_COST_PER_1M,
        "system_prompt": SEARCHGPT_SYSTEM_PROMPT,
    },
    "bing_copilot": {
        "model": "gpt-4o",  # Azure OpenAI with Bing grounding
        "input_cost_per_1m": BING_COPILOT_INPUT_COST_PER_1M,
        "output_cost_per_1m": BING_COPILOT_OUTPUT_COST_PER_1M,
        "system_prompt": BING_COPILOT_SYSTEM_PROMPT,
        "requires_azure": True,  # Flag to indicate Azure OpenAI is needed
    },
}


class LangChainEngine(QueryEngine):
    """
    Unified LangChain-based query engine.
    
    Supports multiple providers through LangChain's consistent interface:
    - OpenAI (GPT-4o)
    - Anthropic (Claude Sonnet)
    - Google (Gemini Flash)
    
    Benefits over separate engine files:
    - Single codebase for all providers
    - Consistent error handling and retry logic
    - Easy to add new providers
    - LangChain handles provider-specific quirks
    """
    
    def __init__(
        self,
        engine_name: str,
        api_key: str,
        model: Optional[str] = None,
    ):
        """
        Initialize the unified engine.
        
        Args:
            engine_name: Provider name ('openai', 'anthropic', 'gemini')
            api_key: API key for the provider
            model: Optional model override (uses default from config if not specified)
        """
        if engine_name not in ENGINE_CONFIGS:
            raise ValueError(f"Unknown engine: {engine_name}. Supported: {list(ENGINE_CONFIGS.keys())}")
        
        self._engine_name = engine_name
        self._config = ENGINE_CONFIGS[engine_name]
        self._model_name = model or self._config["model"]
        
        # Pricing
        self.INPUT_COST_PER_1M = self._config["input_cost_per_1m"]
        self.OUTPUT_COST_PER_1M = self._config["output_cost_per_1m"]
        
        # System prompt
        self._system_prompt = self._config["system_prompt"]
        
        # Initialize the appropriate LangChain model
        self._llm = self._create_llm(engine_name, api_key, self._model_name)
    
    @property
    def name(self) -> str:
        """Return engine name for QueryResult."""
        return self._engine_name
    
    def _create_llm(self, engine_name: str, api_key: str, model: str) -> BaseChatModel:
        """Create the appropriate LangChain chat model."""
        common_kwargs = {
            "temperature": DEFAULT_TEMPERATURE,
            "max_tokens": DEFAULT_MAX_TOKENS,
            "max_retries": MAX_RETRIES,
        }
        
        if engine_name == "openai":
            return ChatOpenAI(
                api_key=api_key,
                model=model,
                **common_kwargs,
            )
        elif engine_name == "searchgpt":
            # SearchGPT uses OpenAI's search-enabled model
            # The model gpt-4o-search-preview has built-in web search
            return ChatOpenAI(
                api_key=api_key,
                model=model,
                **common_kwargs,
            )
        elif engine_name == "bing_copilot":
            # Bing Copilot uses Azure OpenAI with Bing grounding
            # For now, we use regular OpenAI as fallback
            # To enable full Bing grounding, use Azure OpenAI with data sources
            # See: https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/use-your-data
            return ChatOpenAI(
                api_key=api_key,
                model=model,
                **common_kwargs,
            )
        elif engine_name == "anthropic":
            return ChatAnthropic(
                api_key=api_key,
                model=model,
                **common_kwargs,
            )
        elif engine_name == "gemini":
            return ChatGoogleGenerativeAI(
                google_api_key=api_key,
                model=model,
                temperature=DEFAULT_TEMPERATURE,
                max_output_tokens=DEFAULT_MAX_TOKENS,
                max_retries=MAX_RETRIES,
            )
        else:
            raise ValueError(f"Unknown engine: {engine_name}")
    
    async def query(self, prompt: str, context_url: str) -> QueryResult:
        """
        Execute query against the LLM with automatic retry logic.
        
        LangChain handles retries internally based on max_retries setting.
        
        Args:
            prompt: User query (e.g., "What is ProcureWin?")
            context_url: URL to check for citations
            
        Returns:
            QueryResult with response, citations, cost, etc.
        """
        start_time = time.time()
        
        try:
            # Build messages
            messages = [
                SystemMessage(content=self._system_prompt),
                HumanMessage(content=prompt),
            ]
            
            # LangChain's ainvoke handles async execution
            response = await self._llm.ainvoke(messages)
            
            latency = int((time.time() - start_time) * 1000)
            content = response.content if response.content else ""
            
            # Extract token usage from response metadata
            input_tokens = 0
            output_tokens = 0
            
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                input_tokens = response.usage_metadata.get('input_tokens', 0) or 0
                output_tokens = response.usage_metadata.get('output_tokens', 0) or 0
            elif hasattr(response, 'response_metadata'):
                # Some providers put usage in response_metadata
                usage = response.response_metadata.get('usage', {})
                input_tokens = usage.get('prompt_tokens', 0) or usage.get('input_tokens', 0) or 0
                output_tokens = usage.get('completion_tokens', 0) or usage.get('output_tokens', 0) or 0
            
            total_tokens = input_tokens + output_tokens
            
            # Parse for citations to user's website
            citations = extract_citations(content, context_url)
            
            return QueryResult(
                engine=self.name,
                response=content,
                citations=citations,
                tokens_used=total_tokens,
                cost_usd=self._calculate_cost(input_tokens, output_tokens),
                latency_ms=latency,
            )
            
        except Exception as e:
            return QueryResult(
                engine=self.name,
                response="",
                citations=[],
                tokens_used=0,
                cost_usd=0.0,
                latency_ms=int((time.time() - start_time) * 1000),
                error=str(e),
            )
    
    def estimate_cost(self, prompt: str) -> float:
        """
        Estimate cost before running query.
        
        Args:
            prompt: The query prompt
            
        Returns:
            Estimated cost in USD
        """
        # Rough estimate: ~4 chars per token
        prompt_tokens = len(prompt) // 4
        estimated_output = 500  # Assume 500 tokens output
        return self._calculate_cost(prompt_tokens, estimated_output)
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate actual cost based on token usage.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost in USD
        """
        input_cost = (input_tokens / 1_000_000) * self.INPUT_COST_PER_1M
        output_cost = (output_tokens / 1_000_000) * self.OUTPUT_COST_PER_1M
        return round(input_cost + output_cost, 6)


# =============================================================================
# CONVENIENCE FACTORY FUNCTIONS
# =============================================================================
# These provide backward compatibility and easy instantiation

def create_openai_engine(api_key: str, model: str = "gpt-4o-mini") -> LangChainEngine:
    """Create an OpenAI/ChatGPT engine."""
    return LangChainEngine("openai", api_key, model)


def create_anthropic_engine(api_key: str, model: str = "claude-3-5-haiku-latest") -> LangChainEngine:
    """Create an Anthropic/Claude engine."""
    return LangChainEngine("anthropic", api_key, model)


def create_gemini_engine(api_key: str, model: str = "gemini-2.0-flash-lite") -> LangChainEngine:
    """Create a Google Gemini engine."""
    return LangChainEngine("gemini", api_key, model)


def create_searchgpt_engine(api_key: str, model: str = "gpt-4o-search-preview") -> LangChainEngine:
    """Create an OpenAI SearchGPT engine with web search capabilities."""
    return LangChainEngine("searchgpt", api_key, model)


def create_bing_copilot_engine(api_key: str, model: str = "gpt-4o") -> LangChainEngine:
    """Create a Bing Copilot engine (uses OpenAI API, for full Bing grounding use Azure)."""
    return LangChainEngine("bing_copilot", api_key, model)


# =============================================================================
# BACKWARD COMPATIBILITY ALIASES
# =============================================================================
# These classes provide drop-in replacements for the old separate engines

class OpenAIEngine(LangChainEngine):
    """OpenAI/ChatGPT engine (backward compatible)."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        super().__init__("openai", api_key, model)


class AnthropicEngine(LangChainEngine):
    """Anthropic/Claude engine (backward compatible)."""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-latest"):
        super().__init__("anthropic", api_key, model)


class GeminiEngine(LangChainEngine):
    """Google Gemini engine (backward compatible)."""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-lite"):
        super().__init__("gemini", api_key, model)


class SearchGPTEngine(LangChainEngine):
    """OpenAI SearchGPT engine with web search capabilities."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-search-preview"):
        super().__init__("searchgpt", api_key, model)


class BingCopilotEngine(LangChainEngine):
    """
    Bing Copilot engine.
    
    Note: For full Bing search grounding, use Azure OpenAI with data sources.
    This implementation uses OpenAI API as a fallback.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        super().__init__("bing_copilot", api_key, model)


# =============================================================================
# MULTI-ENGINE HELPER
# =============================================================================

async def query_multiple_engines(
    prompt: str,
    context_url: str,
    engines: list[LangChainEngine],
) -> list[QueryResult]:
    """
    Query multiple engines in parallel.
    
    Args:
        prompt: The query to send
        context_url: URL to check for citations
        engines: List of initialized engine instances
        
    Returns:
        List of QueryResults from all engines
    """
    tasks = [engine.query(prompt, context_url) for engine in engines]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Convert exceptions to error results
    final_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            final_results.append(QueryResult(
                engine=engines[i].name,
                response="",
                citations=[],
                tokens_used=0,
                cost_usd=0.0,
                latency_ms=0,
                error=str(result),
            ))
        else:
            final_results.append(result)
    
    return final_results
