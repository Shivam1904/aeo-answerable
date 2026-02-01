"""
Rendered Crawler Module.

This module uses Playwright to crawl pages, executing JavaScript before extraction.
"""
from rich import print
from playwright.async_api import async_playwright

from .config import Settings
from .extractor import extract
from .base_crawler import BaseCrawler

class RenderedCrawler(BaseCrawler):
    """
    Playwright-based crawler extending BaseCrawler.
    """
    def __init__(self, settings: Settings):
        super().__init__(settings)
        self.playwright = None
        self.browser = None
        self.context = None

    async def _setup(self):
        """Initialize Playwright browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch()
        self.context = await self.browser.new_context(user_agent=self.settings.user_agent)

    async def _teardown(self):
        """Close browser resources."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def _process_queue_item(self, url: str, depth: int):
        """Navigates to a URL using Playwright."""
        print(f"[magenta]Rendering:[/magenta] {url}")
        
        page = await self.context.new_page()
        try:
            # Goto and wait for network idle to ensure JS has likely run
            await page.goto(url, wait_until="domcontentloaded", timeout=self.settings.timeout * 1000)

            # Get the fully rendered HTML
            content = await page.content()
            current_url = page.url

            # Extract Content
            data = extract(content, current_url)
            self.results.append(data)

            # Discover Links
            if len(self.results) < self.settings.max_pages:
                self._extract_links(content, current_url, depth)

        except Exception as e:
            print(f"[red]Failed {url}: {e}[/red]")
            self.errors.append({"url": url, "error": str(e)})
        finally:
            await page.close()
