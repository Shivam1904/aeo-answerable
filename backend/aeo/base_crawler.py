"""
Base Crawler Module.

Shared logic for standard and rendered crawlers.
"""
import asyncio
import urllib.robotparser
from typing import List, Set, Dict, Any, Optional
from urllib.parse import urlparse, urljoin
from collections import deque
from bs4 import BeautifulSoup
from rich import print
import httpx

from .config import Settings

class BaseCrawler:
    """
    Base class for web crawlers.
    Handles queue management, robots.txt, and link discovery.
    Subclasses must implement _process_queue_item.
    """
    def __init__(self, settings: Settings):
        self.settings = settings
        self.visited: Set[str] = set()
        self.queue: deque = deque()
        self.results: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, str]] = []
        self.rp = urllib.robotparser.RobotFileParser()

    async def scan(self) -> Dict[str, Any]:
        """
        Executes the crawling process starting from the seed URL.
        """
        if not self.settings.start_url:
            raise ValueError("Start URL is required")

        await self._setup_robots_txt()
        self.queue.append((self.settings.start_url, 0))

        # Setup resources (e.g. browser context) if needed by subclass
        await self._setup()

        try:
            while self.queue and len(self.results) < self.settings.max_pages:
                url, depth = self.queue.popleft()
                
                if url in self.visited:
                    continue
                self.visited.add(url)
                
                if not self._should_crawl(url):
                    continue

                await self._process_queue_item(url, depth)
        finally:
            await self._teardown()

        return {
            "summary": {"scanned_count": len(self.results), "errors": len(self.errors)},
            "pages": self.results,
            "errors": self.errors
        }

    async def _setup(self):
        """Hook for setup (e.g. launching browser)."""
        pass

    async def _teardown(self):
        """Hook for cleanup."""
        pass

    async def _process_queue_item(self, url: str, depth: int):
        """Must be implemented by subclass."""
        raise NotImplementedError

    async def _setup_robots_txt(self):
        """Fetches and parses robots.txt if configured."""
        if not self.settings.respect_robots:
            return

        parsed = urlparse(self.settings.start_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        print(f"[dim]Fetching robots.txt from {robots_url}...[/dim]")
        try:
            async with httpx.AsyncClient(verify=False) as client:
                resp = await client.get(robots_url, timeout=5)
                if resp.status_code == 200:
                    self.rp.parse(resp.text.splitlines())
                else:
                    self.rp.allow_all = True
        except Exception as e:
            print(f"[yellow]Could not fetch robots.txt: {e} - defaulting to ALLOW ALL[/yellow]")
            self.rp.allow_all = True

    def _should_crawl(self, url: str) -> bool:
        """Checks robots.txt rules for a given URL."""
        if self.settings.respect_robots and not self.rp.can_fetch(self.settings.user_agent, url):
            print(f"[dim]Skipped (robots.txt): {url}[/dim]")
            return False
        return True

    def _extract_links(self, html: str, base_url: str, depth: int):
        """
        Parses HTML to find new links to crawl.
        """
        soup = BeautifulSoup(html, 'html.parser')
        base_domain = urlparse(base_url).netloc

        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            
            # Domain check
            if parsed.netloc != base_domain:
                continue
                
            # Fragment check
            full_url = full_url.split('#')[0]

            # Normalization: Strip trailing slash
            if full_url.endswith('/'):
                full_url = full_url[:-1]

            if full_url not in self.visited:
                self.queue.append((full_url, depth + 1))
