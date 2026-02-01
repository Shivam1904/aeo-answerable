"""
Configuration Module.

This module defines the runtime configuration settings for the AEO crawler.
Uses Pydantic for validation and environment variable loading.
"""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings managed by Pydantic.
    
    Attributes:
        start_url (str): The seed URL for the crawl.
        max_pages (int): Maximum number of pages to crawl.
        mode (str): Crawling mode ('fast' or 'rendered').
        concurrency (int): Max concurrent requests (async).
        timeout (int): Request timeout in seconds.
        respect_robots (bool): Whether to respect robots.txt rules.
        user_agent (str): User-Agent string to identify the bot.
        
    Output Monitoring API Keys:
        openai_api_key: OpenAI API key for ChatGPT queries
        anthropic_api_key: Anthropic API key for Claude queries
        gemini_api_key: Google AI API key for Gemini queries
    """
    # Crawler settings
    start_url: str = ""
    max_pages: int = 200
    mode: str = "fast"
    concurrency: int = 5
    timeout: int = 15
    respect_robots: bool = True
    user_agent: str = "AEO-Answerable-Bot/0.1 (+https://github.com/shivam/aeo-answerable)"
    
    # Output Monitoring API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    # SearchGPT uses OpenAI API key (same key, different model)
    # Bing Copilot can use OpenAI key or Azure OpenAI key
    azure_openai_api_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    
    # Output Monitoring Settings
    output_monitoring_daily_budget_usd: float = 10.0

    class Config:
        env_prefix = "AEO_"
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings instance (cached for performance)
    """
    return Settings()
