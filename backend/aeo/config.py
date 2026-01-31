"""
Configuration Module.

This module defines the runtime configuration settings for the AEO crawler.
Uses Pydantic for validation and environment variable loading.
"""
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
    """
    start_url: str = ""
    max_pages: int = 200
    mode: str = "fast"
    concurrency: int = 5
    timeout: int = 15
    respect_robots: bool = True
    user_agent: str = "AEO-Answerable-Bot/0.1 (+https://github.com/shivam/aeo-answerable)"

    class Config:
        env_prefix = "AEO_"
