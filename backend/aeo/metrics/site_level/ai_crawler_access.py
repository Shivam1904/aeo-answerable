"""
AI Crawler Access Hygiene Metric (SL-01).

Checks robots.txt and HTTP headers for AI bot accessibility.
"""
import re
from typing import Any, Dict, List, Set

from ..base import BaseMetric


class AICrawlerAccessMetric(BaseMetric):
    """
    Measures AI crawler access configuration.

    If AI bots are blocked, content cannot be ingested for
    RAG or answer generation.

    Weight: 6%
    """

    name = "ai_crawler_access"
    weight = 0.06
    description = "Measures AI crawler access configuration"

    # Known AI bot user agents
    AI_BOT_USER_AGENTS = [
        "GPTBot",
        "ChatGPT-User",
        "anthropic-ai",
        "Claude-Web",
        "PerplexityBot",
        "YouBot",
        "Bytespider",
        "CCBot",
        "Google-Extended",
        "FacebookBot",
    ]

    def compute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Compute AI crawler access score.

        Args:
            robots_txt: Content of robots.txt file.
            pages: List of page data (for header checks).
            base_url: Base URL of the site.

        Returns:
            Metric result with access configuration details.
        """
        robots_txt: str = kwargs.get("robots_txt", "")
        pages: List[Dict[str, Any]] = kwargs.get("pages", [])

        # Parse robots.txt
        allowed_bots, blocked_bots = self._parse_robots_txt(robots_txt)

        # Check for overly restrictive rules
        has_disallow_all = self._has_disallow_all(robots_txt)

        # Calculate access score
        important_bots = ["GPTBot", "anthropic-ai", "Google-Extended"]
        important_allowed = sum(1 for b in important_bots if b in allowed_bots)
        important_blocked = sum(1 for b in important_bots if b in blocked_bots)

        # Score calculation
        if has_disallow_all:
            score = 0.0
        elif important_blocked >= 2:
            score = 0.3
        elif important_blocked == 1:
            score = 0.6
        elif important_allowed >= 2:
            score = 1.0
        else:
            # Default: no explicit rules = assume accessible
            score = 0.8

        return self._base_result(
            score=score,
            robots_txt_exists=bool(robots_txt),
            ai_bots_allowed=list(allowed_bots),
            ai_bots_blocked=list(blocked_bots),
            has_disallow_all=has_disallow_all,
            recommendation=self._get_recommendation(blocked_bots, has_disallow_all),
        )

    def _parse_robots_txt(self, content: str) -> tuple[Set[str], Set[str]]:
        """
        Parse robots.txt for AI bot rules.

        Args:
            content: robots.txt content.

        Returns:
            Tuple of (allowed_bots, blocked_bots).
        """
        allowed: Set[str] = set()
        blocked: Set[str] = set()

        if not content:
            return allowed, blocked

        current_agent = None
        lines = content.split("\n")

        for line in lines:
            line = line.strip().lower()

            if line.startswith("user-agent:"):
                agent = line.split(":", 1)[1].strip()
                current_agent = agent

            elif line.startswith("disallow:") and current_agent:
                path = line.split(":", 1)[1].strip()
                
                # Check if this affects AI bots
                for bot in self.AI_BOT_USER_AGENTS:
                    if current_agent == "*" or bot.lower() in current_agent:
                        if path == "/" or path == "/*":
                            blocked.add(bot)

            elif line.startswith("allow:") and current_agent:
                path = line.split(":", 1)[1].strip()
                
                for bot in self.AI_BOT_USER_AGENTS:
                    if current_agent == "*" or bot.lower() in current_agent:
                        if path == "/" or path == "/*":
                            allowed.add(bot)

        return allowed, blocked

    def _has_disallow_all(self, content: str) -> bool:
        """
        Check for blanket disallow rules.

        Args:
            content: robots.txt content.

        Returns:
            True if disallow all detected.
        """
        if not content:
            return False

        # Pattern for "User-agent: *" followed by "Disallow: /"
        pattern = r"user-agent:\s*\*[\s\S]*?disallow:\s*/\s*$"
        return bool(re.search(pattern, content, re.IGNORECASE | re.MULTILINE))

    def _get_recommendation(
        self, blocked_bots: Set[str], has_disallow_all: bool
    ) -> str:
        """
        Generate recommendation based on findings.

        Args:
            blocked_bots: Set of blocked bot names.
            has_disallow_all: Whether blanket disallow exists.

        Returns:
            Recommendation string.
        """
        if has_disallow_all:
            return "robots.txt blocks all crawlers. Consider allowing AI bots for better visibility."
        
        if blocked_bots:
            bots_str = ", ".join(list(blocked_bots)[:3])
            return f"Consider allowing these AI bots: {bots_str}"
        
        return "AI crawler access looks good."
