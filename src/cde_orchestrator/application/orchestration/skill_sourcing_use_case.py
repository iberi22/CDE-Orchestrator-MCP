"""
Skill Sourcing Use Case

Downloads and adapts skills from external repositories:
- awesome-claude-skills (GitHub)
- Custom skill repos
- Curated skill collections

Transforms external formats to CDE-compatible skill markdown.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional
import re
import asyncio
import aiohttp
from datetime import datetime


@dataclass
class ExternalSkill:
    """Represents a skill from external repository."""
    name: str
    description: str
    source_url: str
    content: str
    tags: List[str]
    category: str
    rating: Optional[float] = None


@dataclass
class SkillAdaptation:
    """Result of adapting external skill to CDE format."""
    skill_name: str
    file_path: str
    content: str
    metadata: Dict[str, Any]
    adaptations_made: List[str]


class SkillSourcingUseCase:
    """
    Sources skills from external repositories and adapts them to CDE format.

    Supports:
    - awesome-claude-skills (GitHub)
    - Custom GitHub repos
    - Direct URLs to skill files
    """

    AWESOME_CLAUDE_SKILLS_REPO = "https://api.github.com/repos/travisvn/awesome-claude-skills"
    AWESOME_CLAUDE_SKILLS_RAW = "https://raw.githubusercontent.com/travisvn/awesome-claude-skills/main"

    # Category mappings from external format to CDE format
    CATEGORY_MAPPING = {
        "coding": "engineering",
        "writing": "documentation",
        "analysis": "research",
        "productivity": "general",
        "research": "research",
        "development": "engineering"
    }

    def __init__(self, skills_base_path: Optional[Path] = None):
        """
        Initialize skill sourcing.

        Args:
            skills_base_path: Base path for .copilot/skills/ directory
        """
        self.skills_base_path = skills_base_path or Path(".copilot/skills")

    async def execute(
        self,
        skill_query: str,
        source: str = "awesome-claude-skills",
        destination: str = "base"
    ) -> Dict[str, Any]:
        """
        Search and download skill from external repository.

        Args:
            skill_query: Search query (e.g., "web scraping", "redis optimization")
            source: Repository source ("awesome-claude-skills", "custom-url")
            destination: Where to save ("base" or "ephemeral")

        Returns:
            {
                "status": "success",
                "skills_found": int,
                "skills_downloaded": [SkillAdaptation],
                "destination_path": str
            }
        """
        # 1. Search for matching skills
        external_skills = await self._search_skills(skill_query, source)

        if not external_skills:
            return {
                "status": "not_found",
                "skills_found": 0,
                "skills_downloaded": [],
                "message": f"No skills found matching '{skill_query}' in {source}"
            }

        # 2. Adapt skills to CDE format
        adapted_skills = []
        for ext_skill in external_skills[:3]:  # Top 3 matches
            adaptation = self._adapt_skill_to_cde_format(ext_skill)
            adapted_skills.append(adaptation)

        # 3. Save to destination
        destination_path = self.skills_base_path / destination
        destination_path.mkdir(parents=True, exist_ok=True)

        saved_files = []
        for adaptation in adapted_skills:
            file_path = destination_path / f"{adaptation.skill_name}.md"
            file_path.write_text(adaptation.content, encoding="utf-8")
            saved_files.append(str(file_path))

        return {
            "status": "success",
            "skills_found": len(external_skills),
            "skills_downloaded": [
                {
                    "name": a.skill_name,
                    "path": a.file_path,
                    "adaptations": a.adaptations_made,
                    "metadata": a.metadata
                }
                for a in adapted_skills
            ],
            "destination_path": str(destination_path),
            "saved_files": saved_files
        }

    async def _search_skills(
        self, query: str, source: str
    ) -> List[ExternalSkill]:
        """
        Search for skills in external repository.

        Args:
            query: Search query
            source: Repository name

        Returns:
            List of matching external skills
        """
        if source == "awesome-claude-skills":
            return await self._search_awesome_claude_skills(query)
        else:
            # Support for custom sources in future
            return []

    async def _search_awesome_claude_skills(self, query: str) -> List[ExternalSkill]:
        """
        Search awesome-claude-skills repository.

        Strategy:
        1. Fetch README.md from repo
        2. Parse skill links and descriptions
        3. Score skills by relevance to query
        4. Download top matches
        """
        external_skills = []

        try:
            async with aiohttp.ClientSession() as session:
                # 1. Fetch README
                readme_url = f"{self.AWESOME_CLAUDE_SKILLS_RAW}/README.md"
                async with session.get(readme_url) as response:
                    if response.status != 200:
                        return []

                    readme_content = await response.text()

                # 2. Parse skill entries
                # Pattern: [Skill Name](path/to/skill.md) - Description
                pattern = r'\[([^\]]+)\]\(([^\)]+\.md)\)\s*-?\s*(.+)?'
                matches = re.finditer(pattern, readme_content, re.MULTILINE)

                # 3. Score and filter by relevance
                query_lower = query.lower()
                for match in matches:
                    skill_name = match.group(1).strip()
                    skill_path = match.group(2).strip()
                    skill_desc = match.group(3).strip() if match.group(3) else ""

                    # Simple relevance scoring
                    relevance = 0
                    if query_lower in skill_name.lower():
                        relevance += 10
                    if query_lower in skill_desc.lower():
                        relevance += 5

                    # Token overlap
                    query_tokens = set(query_lower.split())
                    name_tokens = set(skill_name.lower().split())
                    desc_tokens = set(skill_desc.lower().split())

                    overlap = len(query_tokens & (name_tokens | desc_tokens))
                    relevance += overlap * 2

                    if relevance > 3:  # Threshold
                        # 4. Download skill content
                        skill_url = f"{self.AWESOME_CLAUDE_SKILLS_RAW}/{skill_path}"
                        async with session.get(skill_url) as skill_response:
                            if skill_response.status == 200:
                                content = await skill_response.text()

                                external_skills.append(ExternalSkill(
                                    name=skill_name,
                                    description=skill_desc,
                                    source_url=skill_url,
                                    content=content,
                                    tags=self._extract_tags(skill_name, skill_desc),
                                    category=self._infer_category(skill_name, skill_desc),
                                    rating=relevance / 20.0  # Normalize to 0-1
                                ))

                # Sort by rating
                external_skills.sort(key=lambda s: s.rating or 0, reverse=True)

        except Exception as e:
            print(f"Error searching awesome-claude-skills: {e}")
            return []

        return external_skills

    def _extract_tags(self, name: str, description: str) -> List[str]:
        """Extract relevant tags from skill name and description."""
        text = f"{name} {description}".lower()
        tags = []

        # Common tag patterns
        tag_keywords = [
            "python", "javascript", "typescript", "react", "vue", "angular",
            "api", "rest", "graphql", "database", "sql", "nosql",
            "testing", "debugging", "refactoring", "optimization",
            "web", "frontend", "backend", "fullstack",
            "ai", "ml", "llm", "gpt", "claude",
            "devops", "docker", "kubernetes", "aws", "azure"
        ]

        for keyword in tag_keywords:
            if keyword in text:
                tags.append(keyword)

        return tags[:5]  # Limit to 5 tags

    def _infer_category(self, name: str, description: str) -> str:
        """Infer skill category from name and description."""
        text = f"{name} {description}".lower()

        # Category detection patterns
        if any(kw in text for kw in ["code", "programming", "develop", "implement"]):
            return "engineering"
        elif any(kw in text for kw in ["write", "document", "spec", "guide"]):
            return "documentation"
        elif any(kw in text for kw in ["research", "analyze", "investigate"]):
            return "research"
        elif any(kw in text for kw in ["manage", "plan", "organize"]):
            return "project-management"
        else:
            return "general"

    def _adapt_skill_to_cde_format(self, external_skill: ExternalSkill) -> SkillAdaptation:
        """
        Adapt external skill format to CDE-compatible markdown.

        CDE Skill Format:
        ```
        ---
        skill_name: "Skill Name"
        category: "engineering"
        tags: ["tag1", "tag2"]
        source: "awesome-claude-skills"
        imported: "2025-11-02"
        ---

        # Skill: [Name]

        ## Overview
        [Description]

        ## When to Use
        [Use cases]

        ## Tools & Context
        [Required tools]

        ## Examples
        [Code examples]

        ## Best Practices
        [Guidelines]

        ## Common Pitfalls
        [Warnings]
        ```
        """
        adaptations_made = []

        # 1. Parse existing content structure
        content_sections = self._parse_external_content(external_skill.content)

        # 2. Build CDE-compatible frontmatter
        frontmatter = f"""---
skill_name: "{external_skill.name}"
category: "{external_skill.category}"
tags: {external_skill.tags}
source: "awesome-claude-skills"
source_url: "{external_skill.source_url}"
imported: "{datetime.now().strftime('%Y-%m-%d')}"
rating: {external_skill.rating or 0.0}
---

"""
        adaptations_made.append("Added CDE frontmatter")

        # 3. Build main content
        main_content = f"# Skill: {external_skill.name}\n\n"
        main_content += f"## Overview\n\n{external_skill.description}\n\n"

        # Add parsed sections
        if "when_to_use" in content_sections:
            main_content += f"## When to Use\n\n{content_sections['when_to_use']}\n\n"
            adaptations_made.append("Preserved 'When to Use' section")

        if "tools" in content_sections:
            main_content += f"## Tools & Context\n\n{content_sections['tools']}\n\n"
            adaptations_made.append("Preserved 'Tools' section")

        if "examples" in content_sections:
            main_content += f"## Examples\n\n{content_sections['examples']}\n\n"
            adaptations_made.append("Preserved 'Examples' section")

        if "best_practices" in content_sections:
            main_content += f"## Best Practices\n\n{content_sections['best_practices']}\n\n"
            adaptations_made.append("Preserved 'Best Practices' section")

        # 4. Add remaining content as-is
        if "raw" in content_sections:
            main_content += f"\n## Additional Content\n\n{content_sections['raw']}\n"
            adaptations_made.append("Preserved raw content")

        # 5. Add metadata footer
        footer = f"""
---

**Source**: [awesome-claude-skills]({external_skill.source_url})
**Imported**: {datetime.now().strftime('%Y-%m-%d')}
**CDE Adaptation**: Automated import with structure preservation
"""

        full_content = frontmatter + main_content + footer

        # 6. Sanitize filename
        skill_filename = re.sub(r'[^a-z0-9-]', '-', external_skill.name.lower())
        skill_filename = re.sub(r'-+', '-', skill_filename).strip('-')

        return SkillAdaptation(
            skill_name=skill_filename,
            file_path=f".copilot/skills/base/{skill_filename}.md",
            content=full_content,
            metadata={
                "original_name": external_skill.name,
                "source": "awesome-claude-skills",
                "rating": external_skill.rating,
                "tags": external_skill.tags,
                "category": external_skill.category
            },
            adaptations_made=adaptations_made
        )

    def _parse_external_content(self, content: str) -> Dict[str, str]:
        """Parse external skill content into structured sections."""
        sections = {}

        # Common section patterns
        patterns = {
            "when_to_use": r'(?:## When to Use|## Use Cases?)(.*?)(?=##|$)',
            "tools": r'(?:## Tools?|## Context|## Requirements?)(.*?)(?=##|$)',
            "examples": r'(?:## Examples?|## Usage)(.*?)(?=##|$)',
            "best_practices": r'(?:## Best Practices|## Guidelines)(.*?)(?=##|$)'
        }

        for section_key, pattern in patterns.items():
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                sections[section_key] = match.group(1).strip()

        # Store remaining content
        sections["raw"] = content

        return sections
