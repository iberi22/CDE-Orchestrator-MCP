"""
Web Research Use Case

Performs intelligent web research to:
1. Update skills with latest documentation
2. Find breaking changes and deprecations
3. Discover best practices and patterns
4. Gather up-to-date library/tool information

Uses LLM CLI adapters for summarization and synthesis.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import aiofiles
from bs4 import BeautifulSoup

from cde_orchestrator.infrastructure.circuit_breaker import circuit_breaker


@dataclass(frozen=True)
class ResearchSource:
    """Represents a researched source."""

    url: str
    title: str
    content: str
    relevance_score: float
    source_type: str  # "docs", "blog", "github", "stackoverflow"
    date_published: Optional[str] = None


@dataclass
class ResearchInsight:
    """Key insight from research."""

    category: str  # "breaking_change", "best_practice", "deprecation", "new_feature"
    summary: str
    details: str
    sources: List[str]
    confidence: float


@dataclass
class SkillUpdate:
    """Result of skill research and update."""

    skill_name: str
    version_before: str
    version_after: str
    insights: List[ResearchInsight]
    update_note: str
    sources_cited: List[str]


class WebResearchUseCase:
    """
    Performs web research to keep skills current and accurate.

    Research Strategy:
    1. Identify topics to research (from skill metadata)
    2. Search multiple sources (official docs, GitHub, blogs, SO)
    3. Extract and rank insights
    4. Synthesize findings using LLM
    5. Generate structured update note
    """

    # Trusted sources for different types of content
    TRUSTED_SOURCES = {
        "python": [
            "https://docs.python.org",
            "https://peps.python.org",
            "https://realpython.com",
        ],
        "javascript": [
            "https://developer.mozilla.org",
            "https://tc39.es",
            "https://nodejs.org/docs",
        ],
        "react": ["https://react.dev", "https://github.com/facebook/react"],
        "redis": ["https://redis.io/docs", "https://github.com/redis/redis"],
        "fastapi": [
            "https://fastapi.tiangolo.com",
            "https://github.com/tiangolo/fastapi",
        ],
    }

    # Search engines (rate-limited, use sparingly)
    SEARCH_APIS = {
        "duckduckgo": "https://api.duckduckgo.com/?q={query}&format=json",
        "github": "https://api.github.com/search/repositories?q={query}",
    }

    def __init__(self, llm_cli_adapter: Optional[Any] = None) -> None:
        """
        Initialize web research use case.

        Args:
            llm_cli_adapter: LLM CLI adapter for summarization (optional)
        """
        self.llm_adapter = llm_cli_adapter

    async def execute(
        self,
        skill_name: str,
        topics: List[str],
        max_sources: int = 10,
        skill_file_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Research and update a skill with latest information.

        Args:
            skill_name: Name of skill to research
            topics: Topics to research (e.g., ["redis 7.x", "redis caching best practices"])
            max_sources: Maximum sources to fetch per topic
            skill_file_path: Path to skill file (optional, for version detection)

        Returns:
            {
                "status": "success",
                "skill_name": str,
                "insights": [ResearchInsight],
                "update_note": str,
                "sources": [str]
            }
        """
        all_insights = []
        all_sources = []

        # 1. Research each topic
        for topic in topics:
            print(f"🔍 Researching: {topic}")
            sources = await self._research_topic(topic, max_sources=max_sources)
            all_sources.extend(sources)

            # 2. Extract insights from sources
            insights = await self._extract_insights(topic, sources)
            all_insights.extend(insights)

        # 3. Deduplicate and rank insights
        unique_insights = self._deduplicate_insights(all_insights)
        ranked_insights = self._rank_insights(unique_insights)

        # 4. Generate update note
        update_note = await self._generate_update_note(
            skill_name, ranked_insights, all_sources
        )

        # 5. Detect version changes (if skill file provided)
        version_info = {}
        if skill_file_path and skill_file_path.exists():
            version_info = await self._detect_version_changes(
                skill_file_path, ranked_insights
            )

        return {
            "status": "success",
            "skill_name": skill_name,
            "insights": [
                {
                    "category": i.category,
                    "summary": i.summary,
                    "details": i.details,
                    "sources": i.sources,
                    "confidence": i.confidence,
                }
                for i in ranked_insights
            ],
            "update_note": update_note,
            "sources": len(all_sources),  # Count of sources consulted
            "version_info": version_info,
        }

    async def _research_topic(
        self, topic: str, max_sources: int = 10
    ) -> List[ResearchSource]:
        """
        Research a specific topic across multiple sources.

        Args:
            topic: Topic to research
            max_sources: Max sources to return

        Returns:
            List of research sources
        """
        sources = []

        # 1. Check trusted sources first
        tool_name = self._extract_tool_name(topic)
        if tool_name and tool_name in self.TRUSTED_SOURCES:
            trusted_urls = self.TRUSTED_SOURCES[tool_name]
            for url in trusted_urls[:3]:  # Top 3 trusted sources
                source = await self._fetch_source(url, topic)
                if source:
                    sources.append(source)

        # 2. Search GitHub for recent issues/discussions
        github_sources = await self._search_github(topic, max_results=3)
        sources.extend(github_sources)

        # 3. Web search for additional sources (if needed)
        if len(sources) < max_sources:
            web_sources = await self._web_search(
                topic, max_results=max_sources - len(sources)
            )
            sources.extend(web_sources)

        return sources[:max_sources]

    def _extract_tool_name(self, topic: str) -> Optional[str]:
        """Extract tool/library name from topic string."""
        topic_lower = topic.lower()

        # Check against known tools
        for tool in self.TRUSTED_SOURCES.keys():
            if tool in topic_lower:
                return tool

        return None

    @circuit_breaker(
        name="web_research_fetch",
        failure_threshold=5,
        timeout=60.0,
        expected_exception=aiohttp.ClientError,
    )
    async def _fetch_source(self, url: str, topic: str) -> Optional[ResearchSource]:
        """
        Fetch content from URL and extract relevant information.

        Args:
            url: URL to fetch
            topic: Topic for relevance scoring

        Returns:
            ResearchSource or None
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status != 200:
                        return None

                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    # Extract title
                    title = soup.find("title")
                    title_text = title.get_text() if title else "Unknown"

                    # Extract main content (heuristic)
                    content_blocks = []
                    for tag in ["article", "main", "div.content", "div.documentation"]:
                        element = soup.select_one(tag)
                        if element:
                            content_blocks.append(
                                element.get_text(separator=" ", strip=True)
                            )

                    if not content_blocks:
                        # Fallback to all paragraphs
                        content_blocks = [
                            p.get_text(strip=True) for p in soup.find_all("p")
                        ]

                    content = " ".join(content_blocks[:50])  # Limit content

                    # Calculate relevance
                    relevance = self._calculate_relevance(content, topic)

                    # Detect source type
                    source_type = self._detect_source_type(url)

                    return ResearchSource(
                        url=url,
                        title=title_text,
                        content=content[:2000],  # Limit to 2000 chars
                        relevance_score=relevance,
                        source_type=source_type,
                    )

        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def _calculate_relevance(self, content: str, topic: str) -> float:
        """Calculate relevance score (0.0-1.0) of content to topic."""
        content_lower = content.lower()
        topic_tokens = set(topic.lower().split())

        # Count token occurrences
        matches = sum(1 for token in topic_tokens if token in content_lower)

        # Normalize to 0-1
        relevance = min(matches / max(len(topic_tokens), 1), 1.0)

        return relevance

    def _detect_source_type(self, url: str) -> str:
        """Detect source type from URL."""
        if "github.com" in url:
            return "github"
        elif "stackoverflow.com" in url:
            return "stackoverflow"
        elif any(domain in url for domain in ["docs", "documentation", "readthedocs"]):
            return "docs"
        else:
            return "blog"

    @circuit_breaker(
        name="github_search_api",
        failure_threshold=3,
        timeout=120.0,
        expected_exception=aiohttp.ClientError,
    )
    async def _search_github(
        self, topic: str, max_results: int = 3
    ) -> List[ResearchSource]:
        """Search GitHub for repositories and issues related to topic."""
        sources = []

        try:
            query = topic.replace(" ", "+")
            search_url = f"https://api.github.com/search/repositories?q={query}&sort=updated&per_page={max_results}"

            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        for item in data.get("items", []):
                            sources.append(
                                ResearchSource(
                                    url=item["html_url"],
                                    title=item["name"],
                                    content=item.get("description", ""),
                                    relevance_score=0.7,  # GitHub results assumed relevant
                                    source_type="github",
                                )
                            )

        except Exception as e:
            print(f"Error searching GitHub: {e}")

        return sources

    @circuit_breaker(
        name="duckduckgo_api",
        failure_threshold=3,
        timeout=90.0,
        expected_exception=aiohttp.ClientError,
    )
    async def _web_search(
        self, topic: str, max_results: int = 5
    ) -> List[ResearchSource]:
        """Perform web search using DuckDuckGo API."""
        sources = []

        try:
            query = topic.replace(" ", "+")
            search_url = f"https://api.duckduckgo.com/?q={query}&format=json"

            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Extract related topics
                        for result in data.get("RelatedTopics", [])[:max_results]:
                            if isinstance(result, dict) and "FirstURL" in result:
                                sources.append(
                                    ResearchSource(
                                        url=result["FirstURL"],
                                        title=result.get("Text", "")[:100],
                                        content=result.get("Text", ""),
                                        relevance_score=0.5,
                                        source_type="web",
                                    )
                                )

        except Exception as e:
            print(f"Error in web search: {e}")

        return sources

    async def _extract_insights(
        self, topic: str, sources: List[ResearchSource]
    ) -> List[ResearchInsight]:
        """Extract key insights from research sources."""
        insights = []

        # Pattern matching for common insight types
        patterns = {
            "breaking_change": [
                r"breaking change",
                r"deprecated",
                r"no longer supported",
                r"removed in version",
                r"migration required",
            ],
            "best_practice": [
                r"best practice",
                r"recommended approach",
                r"should use",
                r"prefer.*over",
                r"best way to",
            ],
            "new_feature": [
                r"new feature",
                r"now supports",
                r"added support",
                r"introducing",
                r"released.*version",
            ],
            "deprecation": [
                r"deprecated",
                r"will be removed",
                r"legacy",
                r"no longer maintained",
            ],
        }

        for source in sources:
            content = source.content.lower()

            for category, pattern_list in patterns.items():
                for pattern in pattern_list:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Extract context around match
                        start = max(0, match.start() - 100)
                        end = min(len(content), match.end() + 100)
                        context = content[start:end]

                        insights.append(
                            ResearchInsight(
                                category=category,
                                summary=context[:100],
                                details=context,
                                sources=[source.url],
                                confidence=source.relevance_score,
                            )
                        )

        return insights

    def _deduplicate_insights(
        self, insights: List[ResearchInsight]
    ) -> List[ResearchInsight]:
        """Remove duplicate insights based on similarity."""
        unique = []
        seen_summaries = set()

        for insight in insights:
            summary_key = insight.summary[:50].lower().strip()
            if summary_key not in seen_summaries:
                unique.append(insight)
                seen_summaries.add(summary_key)

        return unique

    def _rank_insights(self, insights: List[ResearchInsight]) -> List[ResearchInsight]:
        """Rank insights by importance and confidence."""
        # Priority: breaking_change > deprecation > new_feature > best_practice
        category_priority = {
            "breaking_change": 4,
            "deprecation": 3,
            "new_feature": 2,
            "best_practice": 1,
        }

        sorted_insights = sorted(
            insights,
            key=lambda i: (category_priority.get(i.category, 0), i.confidence),
            reverse=True,
        )

        return sorted_insights[:10]  # Top 10

    async def _generate_update_note(
        self,
        skill_name: str,
        insights: List[ResearchInsight],
        sources: List[ResearchSource],
    ) -> str:
        """Generate structured update note from insights."""
        note = f"## 📅 Update Log - {datetime.now().strftime('%Y-%m-%d')}\n\n"
        note += f"### Research Summary for '{skill_name}'\n\n"

        # Group by category
        by_category: Dict[str, List[ResearchInsight]] = {}
        for insight in insights:
            by_category.setdefault(insight.category, []).append(insight)

        # Format each category
        category_labels = {
            "breaking_change": "🔴 Breaking Changes",
            "deprecation": "⚠️ Deprecations",
            "new_feature": "✨ New Features",
            "best_practice": "💡 Best Practices",
        }

        for category, label in category_labels.items():
            if category in by_category:
                note += f"#### {label}\n\n"
                for insight in by_category[category][:3]:  # Top 3 per category
                    note += f"- {insight.summary}\n"
                    note += f"  - Sources: {', '.join(insight.sources[:2])}\n\n"

        # Add sources (deduplicate by URL since ResearchSource is frozen/hashable now)
        note += "\n#### 📚 Sources Consulted\n\n"
        unique_urls = list(set(source.url for source in sources))
        for i, url in enumerate(unique_urls[:10], 1):
            note += f"{i}. {url}\n"

        note += f"\n---\n*Auto-generated by CDE Web Research | {datetime.now().isoformat()}*\n"

        return note

    async def _detect_version_changes(
        self, skill_file: Path, insights: List[ResearchInsight]
    ) -> Dict[str, Any]:
        """Detect version changes from skill file and insights."""
        # Read current skill content
        async with aiofiles.open(skill_file, "r", encoding="utf-8") as f:
            content = await f.read()

        # Extract version mentions
        version_pattern = r"version[:\s]+(\d+\.\d+(?:\.\d+)?)"
        versions_in_skill = re.findall(version_pattern, content, re.IGNORECASE)

        # Extract versions from insights
        versions_in_insights = []
        for insight in insights:
            versions = re.findall(r"\d+\.\d+(?:\.\d+)?", insight.details)
            versions_in_insights.extend(versions)

        return {
            "current_versions": list(set(versions_in_skill)),
            "discovered_versions": list(set(versions_in_insights)),
        }
