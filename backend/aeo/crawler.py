"""
Web Crawler Module.

This module manages the crawling process, including URL queueing,
robots.txt compliance, and fetching logic.
"""
import httpx
import asyncio
import urllib.robotparser
from typing import List, Set, Dict, Any
from urllib.parse import urlparse, urljoin
from collections import deque
from bs4 import BeautifulSoup
from rich import print

from .config import Settings
from .extractor import extract

class Crawler:
    """
    A simple web crawler that fetches pages and processes them using the Extractor.
    
    Attributes:
        settings (Settings): Configuration settings.
        visited (Set[str]): Set of visited URLs to prevent loops.
        queue (deque): Queue of URLs to visit (Breadth-First Search).
        results (List[Dict]): List of extracted page data.
        errors (List[Dict]): List of crawling errors.
        rp (RobotFileParser): Parser for robots.txt rules.
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
        
        Returns:
            Dict[str, Any]: A summary report containing all scanned pages and errors.
        """
        if not self.settings.start_url:
            raise ValueError("Start URL is required")

        await self._setup_robots_txt()
        self.queue.append((self.settings.start_url, 0))

        async with httpx.AsyncClient(timeout=self.settings.timeout, follow_redirects=True, verify=False) as client:
            while self.queue and len(self.results) < self.settings.max_pages:
                url, depth = self.queue.popleft()
                
                if url in self.visited:
                    continue
                self.visited.add(url)
                
                if not self._should_crawl(url):
                    continue

                print(f"[blue]Fetching:[/blue] {url}")
                await self._process_url(client, url, depth)

        return {
            "summary": {"scanned_count": len(self.results), "errors": len(self.errors)},
            "pages": self.results,
            "errors": self.errors
        }

    async def _setup_robots_txt(self):
        """Fetches and parses robots.txt if configured."""
        if not self.settings.respect_robots:
            return

        parsed = urlparse(self.settings.start_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        print(f"[dim]Fetching robots.txt from {robots_url}...[/dim]")
        try:
            # specifically use a clean client for robots to avoid context reuse issues
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

    async def _process_url(self, client: httpx.AsyncClient, url: str, depth: int):
        """Fetches a single URL, extracts content, and discovers links."""
        try:
            resp = await client.get(url, headers={"User-Agent": self.settings.user_agent})
            
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

    def _extract_links(self, html: str, base_url: str, depth: int):
        """
        Parses HTML to find new links to crawl.
        
        Args:
            html (str): Page HTML.
            base_url (str): The URL of the page (for relative link resolution).
            depth (int): Current depth in the crawl tree.
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

            # Normalization: Strip trailing slash for consistency
            if full_url.endswith('/'):
                full_url = full_url[:-1]

            if full_url not in self.visited:
                self.queue.append((full_url, depth + 1))
