"""
Web Crawler Module.

This module manages the crawling process, including URL queueing,
robots.txt compliance, and fetching logic.
"""
import httpx
from rich import print

from .config import Settings
from .extractor import extract
from .base_crawler import BaseCrawler

class Crawler(BaseCrawler):
    """
    Standard HTTP-based crawler extending BaseCrawler.
    """
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.client = None

    async def _setup(self):
        """Initialize reusable HTTP client."""
        self.client = httpx.AsyncClient(
            timeout=self.settings.timeout, 
            follow_redirects=True, 
            verify=False,
            headers={"User-Agent": self.settings.user_agent}
        )

    async def _teardown(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()

    async def _process_queue_item(self, url: str, depth: int):
        """Fetches a single URL using HTTPX."""
        print(f"[blue]Fetching:[/blue] {url}")
        try:
            resp = await self.client.get(url)
            
            if "text/html" not in resp.headers.get("content-type", ""):
                return

            # Extract Content
            data = extract(resp.text, str(resp.url))
            self.results.append(data)

            # Discover Links
            if len(self.results) < self.settings.max_pages:
                self._extract_links(resp.text, str(resp.url), depth)

        except Exception as e:
            print(f"[red]Failed {url}: {e}[/red]")
            self.errors.append({"url": url, "error": str(e)})
