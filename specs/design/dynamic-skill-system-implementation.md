# Dynamic Skill Management System - Implementation Guide

> **Type**: Technical Implementation
> **Status**: Ready for Development
> **Estimated Effort**: 8 weeks
> **Dependencies**: `gemini-cli`, `beautifulsoup4`, `aiohttp`, `tiktoken`

---

## 🎯 Quick Start

```bash
# Install dependencies
pip install aiohttp beautifulsoup4 tiktoken lxml aiofiles

# Initialize skill system
python -m cde_orchestrator.skills.init

# Run tests
pytest tests/skills/ -v
```

---

## 📂 File Structure

```
src/cde_orchestrator/skills/
├── __init__.py
├── models.py              # Pydantic models
├── detector.py            # SkillRequirementDetector
├── manager.py             # SkillManager (orchestrator)
├── sourcer.py             # SkillSourcer (external repos)
├── generator.py           # SkillGenerator (AI-powered)
├── updater.py             # SkillUpdater (background job)
├── researcher.py          # WebResearcher (web scraping + Gemini)
├── distiller.py           # SkillDistiller (ephemeral → base)
└── storage.py             # SkillStorage (file-based)

.copilot/skills/
├── base/                  # Persistent, generic skills
│   ├── web-research.md
│   ├── code-generation.md
│   └── skill-management.md
└── ephemeral/             # Temporary, task-specific
    └── [auto-cleaned after 24h]

tests/skills/
├── test_detector.py
├── test_generator.py
├── test_sourcer.py
└── test_integration.py
```

---

## 💻 Core Implementation

### 1. Models (`models.py`)

```python
# src/cde_orchestrator/skills/models.py
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class SkillType(str, Enum):
    """Skill lifecycle types."""
    BASE = "base"           # Persistent, accumulative
    EPHEMERAL = "ephemeral" # Task-specific, temporary


class ComplexityLevel(str, Enum):
    """Task complexity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SkillRequirement(BaseModel):
    """Result of task analysis by SkillRequirementDetector."""
    needs_skill: bool
    complexity: ComplexityLevel
    domain: str  # e.g., "database", "web", "infrastructure"
    knowledge_gaps: List[str]  # e.g., ["redis pub/sub", "fastapi websockets"]
    suggested_sources: List[str]  # External repos to check
    confidence: float = Field(ge=0.0, le=1.0, default=0.8)


class SkillMetadata(BaseModel):
    """Metadata extracted from skill frontmatter."""
    name: str
    skill_type: SkillType
    domain: str
    tools: List[str]
    version: str = "1.0.0"

    # Lifecycle tracking (NO TTL - Smart Reuse Instead)
    created_at: datetime
    last_used: datetime
    last_verified: datetime
    archived_at: Optional[datetime] = None
    generation_count: int = 0  # How many times regenerated

    # Context-based staleness detection
    context_hash: str  # Fingerprint of dependencies
    previous_version_id: Optional[str] = None

    # Dependency tracking
    update_checks: Dict[str, Any] = Field(default_factory=dict)
    # {
    #   "tool_versions": {"redis": "7.2.4", ...},
    #   "library_versions": {"redis-py": "5.0.1", ...},
    #   "source_code_hash": "abc123...",
    #   "last_check": "2025-11-01T18:45:00Z",
    #   "breaking_changes_found": False
    # }

    # Status (new: smart reuse replaces TTL)
    status: str = "active"  # active, stale, archived
    created: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    expires: Optional[datetime] = None  # For ephemeral skills
    task_id: Optional[str] = None       # Link to specific task


class UpdateNote(BaseModel):
    """Single update entry in skill history."""
    date: datetime
    version: str
    changes: List[str]  # e.g., ["Redis 7.2.4 released", "Added SINTERCARD example"]
    references: List[str]  # URLs to docs/issues/PRs


class SkillTemplate(BaseModel):
    """Template extracted from external skill repositories."""
    name: str
    domain: str
    source_url: str
    code_examples: List[str]
    patterns: List[Dict[str, str]]  # {"name": "Cache-Aside", "code": "..."}
    known_issues: List[Dict[str, str]]  # {"issue": "...", "workaround": "..."}
    tools: List[str]


class BaseSkill(BaseModel):
    """Persistent skill that grows with learnings."""
    metadata: SkillMetadata
    content: str  # Full markdown content
    update_history: List[UpdateNote] = []
    file_path: Path
    token_count: int = 0

    @validator("metadata")
    def validate_base_type(cls, v):
        if v.skill_type != SkillType.BASE:
            raise ValueError("BaseSkill must have type=BASE")
        return v

    def append_update_note(self, note: UpdateNote):
        """Add update without modifying core content."""
        self.update_history.append(note)
        self.metadata.last_updated = datetime.now()

        # Append formatted note to content
        note_md = self._format_update_note(note)

        # Find or create update history section
        if "## 📅 Update History" not in self.content:
            self.content += "\n\n---\n\n## 📅 Update History\n\n"

        # Insert after "## 📅 Update History" header
        insert_pos = self.content.find("## 📅 Update History") + len("## 📅 Update History\n\n")
        self.content = (
            self.content[:insert_pos] +
            note_md + "\n\n" +
            self.content[insert_pos:]
        )

    def _format_update_note(self, note: UpdateNote) -> str:
        """Format update note as markdown."""
        lines = [f"### {note.date.strftime('%Y-%m-%d')} (v{note.version})"]
        for change in note.changes:
            lines.append(f"- {change}")

        if note.references:
            lines.append("\n**References:**")
            for ref in note.references:
                lines.append(f"- {ref}")

        return "\n".join(lines)


class EphemeralSkill(BaseModel):
    """
    Task-specific skill with smart reuse (NO TTL).

    Persists indefinitely, reused if context unchanged.
    Archives after 6 months without use, never deleted.
    """
    metadata: SkillMetadata
    content: str
    task_context: str  # Original user request
    parent_base_skill: Optional[str] = None  # Link to base skill
    file_path: Path
    token_count: int = 0
    size_bytes: int = 0

    @validator("metadata")
    def validate_ephemeral_type(cls, v):
        if v.skill_type != SkillType.EPHEMERAL:
            raise ValueError("EphemeralSkill must have type=EPHEMERAL")
        # NO TTL - set defaults for tracking instead
        if not v.created_at:
            v.created_at = datetime.now()
        if not v.last_used:
            v.last_used = datetime.now()
        if not v.last_verified:
            v.last_verified = datetime.now()
        return v

    async def is_stale(self, current_context_hash: str) -> bool:
        """
        Check if skill needs regeneration (context-based, not time-based).

        Returns True if:
        - Context hash changed (dependencies updated)
        - Breaking changes detected
        - Source code changed
        """
        # Primary: Context hash mismatch
        if current_context_hash != self.metadata.context_hash:
            return True

        # Secondary: Breaking changes in dependencies
        if self.metadata.update_checks.get("breaking_changes_found"):
            return True

        # Tertiary: Long time since verification
        last_verify = self.metadata.last_verified
        days_since = (datetime.now() - last_verify).days
        if days_since > 30:
            # Re-verify even if hash matches (in case of external changes)
            return True

        return False


class ResearchResult(BaseModel):
    """Result from web research."""
    query: str
    source: str  # "official_docs", "github", "stackoverflow"
    title: str
    url: str
    snippet: str
    date: Optional[datetime] = None
    relevance_score: float = Field(ge=0.0, le=1.0)


class ResearchResults(BaseModel):
    """Aggregated research from multiple sources."""
    docs: List[ResearchResult] = []
    issues: List[ResearchResult] = []
    discussions: List[ResearchResult] = []
    qa: List[ResearchResult] = []

    def filter_by_date(self, since: str):
        """Keep only recent results (e.g., since='2024-01-01')."""
        cutoff = datetime.fromisoformat(since)

        self.docs = [r for r in self.docs if r.date and r.date >= cutoff]
        self.issues = [r for r in self.issues if r.date and r.date >= cutoff]
        self.discussions = [r for r in self.discussions if r.date and r.date >= cutoff]
        self.qa = [r for r in self.qa if r.date and r.date >= cutoff]

    def top_k(self, k: int = 5) -> List[ResearchResult]:
        """Get top K most relevant results across all sources."""
        all_results = self.docs + self.issues + self.discussions + self.qa
        sorted_results = sorted(all_results, key=lambda r: r.relevance_score, reverse=True)
        return sorted_results[:k]
```

### 2. Skill Requirement Detector (`detector.py`)

```python
# src/cde_orchestrator/skills/detector.py
import re
from typing import List

from .models import ComplexityLevel, SkillRequirement


class SkillRequirementDetector:
    """
    Analyzes tasks to determine if specialized skills are needed.

    Uses heuristics based on:
    - Task complexity (keywords, patterns)
    - Domain detection (technology mentions)
    - Knowledge gap identification
    """

    COMPLEXITY_PATTERNS = {
        ComplexityLevel.HIGH: [
            r"implement .+ (cache|caching|queue|database|db)",
            r"optimize .+ (performance|speed|latency)",
            r"migrate .+ to .+",
            r"integrate .+ with .+",
            r"security (audit|review|hardening)",
            r"scale .+ to handle .+",
            r"distributed .+",
            r"real-?time .+",
            r"pub/sub",
            r"event-driven",
        ],
        ComplexityLevel.MEDIUM: [
            r"refactor .+",
            r"add .+ feature",
            r"fix .+ (bug|issue)",
            r"improve .+",
            r"setup .+ environment",
            r"configure .+",
            r"deploy .+",
        ],
        ComplexityLevel.LOW: [
            r"rename .+",
            r"format .+",
            r"update .+ (comment|docstring)",
            r"change .+ color",
            r"move .+ file",
        ],
    }

    DOMAIN_PATTERNS = {
        "database": [
            r"\b(sql|nosql|postgres|postgresql|mysql|mongodb|mongo|redis|dynamodb|cassandra|elasticsearch)\b",
            r"\b(cache|caching|query|transaction|index|migration)\b",
        ],
        "web": [
            r"\b(react|vue|angular|nextjs|svelte|fastapi|django|flask|express|api|rest|graphql|websocket)\b",
            r"\b(frontend|backend|fullstack|http|https|cors|authentication|auth)\b",
        ],
        "infrastructure": [
            r"\b(docker|kubernetes|k8s|terraform|ansible|aws|gcp|azure|cloud|devops|ci/cd|jenkins|github actions)\b",
            r"\b(container|orchestration|deployment|scaling|load balancer)\b",
        ],
        "ml": [
            r"\b(machine learning|ml|neural|model|training|inference|pytorch|tensorflow|scikit-learn|pandas|numpy)\b",
            r"\b(dataset|feature engineering|hyperparameter|embeddings|transformer)\b",
        ],
        "security": [
            r"\b(auth|authentication|authorization|oauth|jwt|saml|encryption|ssl|tls|certificate)\b",
            r"\b(vulnerability|penetration test|xss|csrf|sql injection|firewall)\b",
        ],
    }

    TOOL_PATTERNS = {
        # Database tools
        "redis": r"\bredis\b",
        "postgres": r"\b(postgres|postgresql)\b",
        "mongodb": r"\b(mongo|mongodb)\b",
        # Web frameworks
        "fastapi": r"\bfastapi\b",
        "react": r"\breact\b",
        "nextjs": r"\bnextjs\b",
        # Infrastructure
        "docker": r"\bdocker\b",
        "kubernetes": r"\b(kubernetes|k8s)\b",
        "terraform": r"\bterraform\b",
        # Languages
        "python": r"\bpython\b",
        "typescript": r"\b(typescript|ts)\b",
        "rust": r"\brust\b",
    }

    def analyze_task(self, task: str) -> SkillRequirement:
        """
        Analyze task and determine skill requirements.

        Args:
            task: User's task description

        Returns:
            SkillRequirement with needs_skill, complexity, domain, etc.
        """
        task_lower = task.lower()

        # Detect complexity
        complexity = self._detect_complexity(task_lower)

        # Detect domain
        domain = self._detect_domain(task_lower)

        # Extract tools mentioned
        tools = self._extract_tools(task_lower)

        # Identify knowledge gaps (tools + patterns not in base skills)
        knowledge_gaps = self._identify_knowledge_gaps(task_lower, tools)

        # Suggest external sources
        suggested_sources = self._suggest_sources(domain)

        # Determine if skill is needed
        needs_skill = complexity in [ComplexityLevel.MEDIUM, ComplexityLevel.HIGH]

        # Calculate confidence
        confidence = self._calculate_confidence(complexity, domain, knowledge_gaps)

        return SkillRequirement(
            needs_skill=needs_skill,
            complexity=complexity,
            domain=domain,
            knowledge_gaps=knowledge_gaps,
            suggested_sources=suggested_sources,
            confidence=confidence,
        )

    def _detect_complexity(self, task: str) -> ComplexityLevel:
        """Detect task complexity from patterns."""
        for level in [ComplexityLevel.HIGH, ComplexityLevel.MEDIUM, ComplexityLevel.LOW]:
            for pattern in self.COMPLEXITY_PATTERNS[level]:
                if re.search(pattern, task, re.IGNORECASE):
                    return level

        # Default to MEDIUM if no match
        return ComplexityLevel.MEDIUM

    def _detect_domain(self, task: str) -> str:
        """Detect primary domain from tool mentions."""
        domain_scores = {}

        for domain, patterns in self.DOMAIN_PATTERNS.items():
            score = sum(
                1 for pattern in patterns
                if re.search(pattern, task, re.IGNORECASE)
            )
            domain_scores[domain] = score

        # Return domain with highest score, or "general" if no match
        if not domain_scores or max(domain_scores.values()) == 0:
            return "general"

        return max(domain_scores, key=domain_scores.get)

    def _extract_tools(self, task: str) -> List[str]:
        """Extract mentioned tools from task description."""
        tools = []

        for tool, pattern in self.TOOL_PATTERNS.items():
            if re.search(pattern, task, re.IGNORECASE):
                tools.append(tool)

        return tools

    def _identify_knowledge_gaps(self, task: str, tools: List[str]) -> List[str]:
        """
        Identify knowledge gaps.

        For now, returns tools + key phrases. In production, would check
        against existing skill database.
        """
        gaps = tools.copy()

        # Extract key action phrases
        key_phrases = [
            "pub/sub", "caching", "authentication", "real-time",
            "distributed", "scaling", "migration", "optimization"
        ]

        for phrase in key_phrases:
            if phrase in task:
                gaps.append(phrase)

        return list(set(gaps))  # Remove duplicates

    def _suggest_sources(self, domain: str) -> List[str]:
        """Suggest external skill repositories to check."""
        base_sources = [
            "https://github.com/travisvn/awesome-claude-skills",
            "https://github.com/anthropics/skills",
        ]

        # Domain-specific sources
        domain_sources = {
            "database": ["https://github.com/search?q=redis+skill"],
            "web": ["https://github.com/search?q=fastapi+skill"],
            "infrastructure": ["https://github.com/search?q=docker+skill"],
        }

        return base_sources + domain_sources.get(domain, [])

    def _calculate_confidence(
        self,
        complexity: ComplexityLevel,
        domain: str,
        gaps: List[str]
    ) -> float:
        """
        Calculate confidence score for skill requirement detection.

        Higher confidence if:
        - High complexity
        - Specific domain (not "general")
        - Multiple knowledge gaps
        """
        confidence = 0.5  # Base

        if complexity == ComplexityLevel.HIGH:
            confidence += 0.3
        elif complexity == ComplexityLevel.MEDIUM:
            confidence += 0.15

        if domain != "general":
            confidence += 0.1

        if len(gaps) >= 3:
            confidence += 0.1

        return min(confidence, 1.0)
```

### 3. Skill Sourcer (`sourcer.py`)

```python
# src/cde_orchestrator/skills/sourcer.py
import re
from pathlib import Path
from typing import List, Optional

import aiohttp
from bs4 import BeautifulSoup

from .models import SkillTemplate


class SkillSourcer:
    """
    Scrapes external skill repositories to extract skill templates.

    Primary sources:
    - awesome-claude-skills
    - anthropics/skills
    - obra/superpowers
    """

    SOURCES = [
        {
            "name": "awesome-claude-skills",
            "url": "https://github.com/travisvn/awesome-claude-skills",
            "readme": "https://raw.githubusercontent.com/travisvn/awesome-claude-skills/main/README.md",
        },
        {
            "name": "anthropics-skills",
            "url": "https://github.com/anthropics/skills",
            "readme": "https://raw.githubusercontent.com/anthropics/skills/main/README.md",
        },
    ]

    async def search_templates(self, domain: str) -> List[SkillTemplate]:
        """
        Search all sources for domain-relevant skill templates.

        Args:
            domain: e.g., "database", "web", "infrastructure"

        Returns:
            List of SkillTemplate objects
        """
        templates = []

        async with aiohttp.ClientSession() as session:
            for source in self.SOURCES:
                try:
                    source_templates = await self._scrape_source(session, source, domain)
                    templates.extend(source_templates)
                except Exception as e:
                    print(f"Error scraping {source['name']}: {e}")

        return templates

    async def _scrape_source(
        self,
        session: aiohttp.ClientSession,
        source: dict,
        domain: str
    ) -> List[SkillTemplate]:
        """Scrape single source repository."""
        templates = []

        # Fetch README
        async with session.get(source["readme"]) as resp:
            readme_content = await resp.text()

        # Parse skill links
        skill_links = self._extract_skill_links(readme_content, domain)

        # Download each skill
        for link in skill_links[:5]:  # Limit to 5 per source
            try:
                template = await self._download_and_parse_skill(session, link)
                if template:
                    templates.append(template)
            except Exception as e:
                print(f"Error downloading skill {link}: {e}")

        return templates

    def _extract_skill_links(self, readme: str, domain: str) -> List[str]:
        """
        Extract GitHub links to skill files from README.

        Looks for patterns like:
        - [skill-name](https://github.com/.../skill-name)
        """
        links = []

        # Parse markdown links
        link_pattern = r'\[([^\]]+)\]\((https://github\.com/[^\)]+)\)'
        matches = re.findall(link_pattern, readme)

        for name, url in matches:
            # Filter by domain keywords
            name_lower = name.lower()
            if any(keyword in name_lower for keyword in self._domain_keywords(domain)):
                # Convert to raw content URL
                raw_url = self._convert_to_raw_url(url)
                links.append(raw_url)

        return links

    def _domain_keywords(self, domain: str) -> List[str]:
        """Get keywords for domain filtering."""
        keywords = {
            "database": ["sql", "redis", "mongo", "cache", "db"],
            "web": ["api", "react", "fastapi", "web", "http"],
            "infrastructure": ["docker", "k8s", "deploy", "cloud"],
            "ml": ["ml", "model", "training", "neural"],
            "security": ["auth", "security", "encrypt"],
        }
        return keywords.get(domain, [])

    def _convert_to_raw_url(self, github_url: str) -> str:
        """
        Convert GitHub URL to raw content URL.

        Example:
        https://github.com/anthropics/skills/tree/main/mcp-builder
        → https://raw.githubusercontent.com/anthropics/skills/main/mcp-builder/SKILL.md
        """
        # Replace github.com with raw.githubusercontent.com
        raw_url = github_url.replace("github.com", "raw.githubusercontent.com")

        # Remove /tree/ or /blob/
        raw_url = raw_url.replace("/tree/", "/")
        raw_url = raw_url.replace("/blob/", "/")

        # Append /SKILL.md
        if not raw_url.endswith(".md"):
            raw_url += "/SKILL.md"

        return raw_url

    async def _download_and_parse_skill(
        self,
        session: aiohttp.ClientSession,
        url: str
    ) -> Optional[SkillTemplate]:
        """Download SKILL.md and parse into template."""
        async with session.get(url) as resp:
            if resp.status != 200:
                return None

            content = await resp.text()

        # Parse skill content
        return self._parse_skill_content(content, url)

    def _parse_skill_content(self, content: str, source_url: str) -> Optional[SkillTemplate]:
        """
        Extract structure from SKILL.md content.

        Looks for:
        - Frontmatter (YAML)
        - Code examples (```code blocks)
        - Patterns (## Pattern sections)
        - Known issues (## Known Issues sections)
        """
        # Extract YAML frontmatter
        metadata = self._extract_frontmatter(content)

        if not metadata:
            return None

        # Extract code blocks
        code_examples = self._extract_code_blocks(content)

        # Extract patterns
        patterns = self._extract_patterns(content)

        # Extract known issues
        known_issues = self._extract_known_issues(content)

        return SkillTemplate(
            name=metadata.get("name", "unknown"),
            domain=metadata.get("domain", "general"),
            source_url=source_url,
            code_examples=code_examples,
            patterns=patterns,
            known_issues=known_issues,
            tools=metadata.get("tools", []),
        )

    def _extract_frontmatter(self, content: str) -> Optional[dict]:
        """Extract YAML frontmatter from skill file."""
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None

        yaml_content = match.group(1)

        # Simple YAML parsing (in production, use PyYAML)
        metadata = {}
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Parse arrays
                if value.startswith('[') and value.endswith(']'):
                    value = [v.strip().strip('"\'') for v in value[1:-1].split(',')]

                metadata[key] = value

        return metadata

    def _extract_code_blocks(self, content: str) -> List[str]:
        """Extract all code blocks from markdown."""
        pattern = r'```(?:\w+)?\n(.*?)```'
        matches = re.findall(pattern, content, re.DOTALL)
        return [match.strip() for match in matches]

    def _extract_patterns(self, content: str) -> List[dict]:
        """Extract pattern sections (## Pattern Name)."""
        patterns = []

        # Find all ## headers
        sections = re.split(r'\n## ', content)

        for section in sections:
            lines = section.split('\n', 1)
            if len(lines) < 2:
                continue

            header = lines[0].strip()
            body = lines[1].strip()

            # Look for pattern-like sections
            if any(keyword in header.lower() for keyword in ['pattern', 'approach', 'strategy']):
                # Extract first code block as example
                code_match = re.search(r'```(?:\w+)?\n(.*?)```', body, re.DOTALL)
                code = code_match.group(1).strip() if code_match else ""

                patterns.append({
                    "name": header,
                    "description": body[:200],  # First 200 chars
                    "code": code,
                })

        return patterns

    def _extract_known_issues(self, content: str) -> List[dict]:
        """Extract known issues section."""
        issues = []

        # Find "Known Issues" section
        match = re.search(
            r'## Known Issues.*?\n(.*?)(?=\n##|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )

        if not match:
            return issues

        issues_section = match.group(1)

        # Parse list items
        for line in issues_section.split('\n'):
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                # Extract issue and potential workaround
                issue_text = line[2:].strip()

                # Check for workaround pattern (e.g., "Issue: ... → Workaround: ...")
                if '→' in issue_text or 'workaround' in issue_text.lower():
                    parts = re.split(r'[→:]', issue_text, 1)
                    issue = parts[0].strip()
                    workaround = parts[1].strip() if len(parts) > 1 else ""
                else:
                    issue = issue_text
                    workaround = ""

                issues.append({"issue": issue, "workaround": workaround})

        return issues
```

### 4. Skill Generator (`generator.py`)

```python
# src/cde_orchestrator/skills/generator.py
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from .models import EphemeralSkill, SkillMetadata, SkillTemplate, SkillType
from .researcher import WebResearcher
from .sourcer import SkillSourcer


class SkillGenerator:
    """
    Generates ephemeral skills on-demand using:
    1. External skill templates
    2. Web research
    3. LLM generation (Gemini/Claude)
    """

    def __init__(
        self,
        sourcer: SkillSourcer,
        researcher: WebResearcher,
        skills_dir: Path,
    ):
        self.sourcer = sourcer
        self.researcher = researcher
        self.skills_dir = skills_dir
        self.ephemeral_dir = skills_dir / "ephemeral"
        self.ephemeral_dir.mkdir(parents=True, exist_ok=True)

    async def generate_skill(
        self,
        task: str,
        domain: str,
        knowledge_gaps: List[str],
        parent_base_skill: Optional[str] = None,
    ) -> EphemeralSkill:
        """
        Generate ephemeral skill for specific task.

        Steps:
        1. Source external templates
        2. Research each knowledge gap
        3. Find known issues
        4. Generate skill via LLM (Gemini)
        5. Save to ephemeral directory
        """
        task_id = str(uuid.uuid4())[:8]

        # Step 1: Source templates
        templates = await self.sourcer.search_templates(domain)

        # Step 2: Research knowledge gaps
        research_results = await self._research_knowledge_gaps(knowledge_gaps)

        # Step 3: Find known issues
        known_issues = await self._find_known_issues(knowledge_gaps)

        # Step 4: Generate skill content
        skill_content = await self._generate_via_llm(
            task=task,
            domain=domain,
            templates=templates,
            research=research_results,
            issues=known_issues,
        )

        # Step 5: Create metadata
        metadata = SkillMetadata(
            name=f"{domain}-{task_id}",
            skill_type=SkillType.EPHEMERAL,
            domain=domain,
            tools=knowledge_gaps,
            version="1.0.0",
            created=datetime.now(),
            last_updated=datetime.now(),
            expires=datetime.now() + timedelta(hours=24),
            task_id=task_id,
        )

        # Step 6: Save to file
        file_path = self.ephemeral_dir / f"{metadata.name}.md"
        file_path.write_text(skill_content, encoding="utf-8")

        # Step 7: Create EphemeralSkill object
        skill = EphemeralSkill(
            metadata=metadata,
            content=skill_content,
            task_context=task,
            parent_base_skill=parent_base_skill,
            file_path=file_path,
            token_count=self._estimate_tokens(skill_content),
        )

        return skill

    async def _research_knowledge_gaps(self, gaps: List[str]) -> Dict[str, List[dict]]:
        """Research each knowledge gap via web."""
        results = {}

        for gap in gaps:
            query = f"{gap} best practices latest 2025"
            research = await self.researcher.research(
                query=query,
                sources=["official_docs", "github", "stackoverflow"]
            )

            # Get top 3 results
            top_results = research.top_k(k=3)
            results[gap] = [
                {
                    "title": r.title,
                    "url": r.url,
                    "snippet": r.snippet,
                }
                for r in top_results
            ]

        return results

    async def _find_known_issues(self, tools: List[str]) -> List[dict]:
        """Search for known issues related to tools."""
        all_issues = []

        for tool in tools:
            issues = await self.researcher.search_github_issues(
                query=f"{tool} bug issue",
                labels=["bug", "breaking-change"],
                limit=5,
            )

            all_issues.extend(issues)

        return all_issues

    async def _generate_via_llm(
        self,
        task: str,
        domain: str,
        templates: List[SkillTemplate],
        research: Dict[str, List[dict]],
        issues: List[dict],
    ) -> str:
        """
        Generate skill content using LLM (Gemini CLI).

        In production, this would call Gemini CLI with a structured prompt.
        For now, returns template-based content.
        """
        # Build context for LLM
        context = {
            "task": task,
            "domain": domain,
            "templates": [self._template_to_dict(t) for t in templates],
            "research": research,
            "known_issues": issues,
        }

        # Create prompt for Gemini
        prompt = self._build_generation_prompt(context)

        # Call Gemini CLI (background execution)
        # In production:
        # skill_content = await self._call_gemini(prompt)

        # For now, return template-based skill
        return self._template_based_skill(context)

    def _build_generation_prompt(self, context: dict) -> str:
        """Build prompt for LLM skill generation."""
        return f"""
Generate a Claude skill for the following task:

**Task:** {context['task']}
**Domain:** {context['domain']}

**External Templates Found:**
{json.dumps(context['templates'], indent=2)}

**Research Results:**
{json.dumps(context['research'], indent=2)}

**Known Issues:**
{json.dumps(context['known_issues'], indent=2)}

Create a comprehensive skill in markdown format with:
1. YAML frontmatter (name, domain, tools, expires)
2. Task context section
3. Implementation patterns with code examples
4. Known issues and workarounds
5. References to research sources

Format:
---
skill_type: ephemeral
domain: {context['domain']}
tools: [...]
---

# [Skill Title]

## Task Context
...

## Implementation
...

## Known Issues
...

## References
...
"""

    def _template_based_skill(self, context: dict) -> str:
        """Generate skill from templates (fallback)."""
        task = context['task']
        domain = context['domain']

        # Use first template as base
        templates = context['templates']
        base_template = templates[0] if templates else None

        skill_md = f"""---
skill_type: ephemeral
domain: {domain}
task_id: {str(uuid.uuid4())[:8]}
created: {datetime.now().isoformat()}
expires: {(datetime.now() + timedelta(hours=24)).isoformat()}
---

# {domain.title()} Implementation for Task

## Task Context

**User Request:** {task}

## Implementation Patterns

"""

        # Add code examples from template
        if base_template and base_template.code_examples:
            skill_md += "### Pattern 1: Basic Setup\n\n"
            skill_md += f"```python\n{base_template.code_examples[0]}\n```\n\n"

        # Add research findings
        skill_md += "## Research Findings\n\n"
        for gap, results in context['research'].items():
            skill_md += f"### {gap.title()}\n\n"
            for result in results:
                skill_md += f"- [{result['title']}]({result['url']})\n"
                skill_md += f"  {result['snippet'][:200]}...\n\n"

        # Add known issues
        if context['known_issues']:
            skill_md += "## Known Issues\n\n"
            for issue in context['known_issues'][:3]:
                skill_md += f"- {issue.get('title', 'Issue')}\n"
                skill_md += f"  URL: {issue.get('url', '')}\n\n"

        skill_md += "\n---\n\n**Note:** This ephemeral skill expires in 24 hours.\n"

        return skill_md

    def _template_to_dict(self, template: SkillTemplate) -> dict:
        """Convert SkillTemplate to dict for JSON serialization."""
        return {
            "name": template.name,
            "domain": template.domain,
            "source": template.source_url,
            "patterns": template.patterns,
            "known_issues": template.known_issues,
        }

    def _estimate_tokens(self, content: str) -> int:
        """Rough token estimation (4 chars ≈ 1 token)."""
        return len(content) // 4
```

---

## 🔌 Integration with CDE Workflow

### Hook into `cde_startFeature`

```python
# src/server.py (modifications)

from cde_orchestrator.skills.detector import SkillRequirementDetector
from cde_orchestrator.skills.manager import SkillManager

# Initialize skill system
skill_detector = SkillRequirementDetector()
skill_manager = SkillManager(skills_dir=Path(".copilot/skills"))

@app.tool()
@tool_handler
def cde_startFeature(user_prompt: str) -> str:
    """Start new feature with dynamic skill loading."""

    # Step 1: Detect skill requirements
    skill_req = skill_detector.analyze_task(user_prompt)

    # Step 2: Load or generate skills
    skills_context = ""
    if skill_req.needs_skill:
        skills = await skill_manager.get_or_create_skills(
            domain=skill_req.domain,
            knowledge_gaps=skill_req.knowledge_gaps,
            task=user_prompt,
        )

        # Format skills for context
        skills_context = skill_manager.format_skills_for_prompt(skills)

    # Step 3: Generate feature ID and load workflow
    feature_id = str(uuid.uuid4())
    workflow_type = workflow_manager.detect_workflow_type(user_prompt)
    initial_phase = workflow_manager.get_initial_phase()

    # Step 4: Prepare context with skills
    context = {
        "USER_PROMPT": user_prompt,
        "FEATURE_ID": feature_id,
        "WORKFLOW_TYPE": workflow_type,
        "SKILLS_CONTEXT": skills_context,  # <-- New!
    }

    # Step 5: Load prompt recipe
    poml_recipe_path = Path(initial_phase.prompt_recipe)
    final_prompt = prompt_manager.load_and_prepare(poml_recipe_path, context)

    # ... rest of implementation
```

### New MCP Tools

```python
@app.tool()
def cde_listSkills(skill_type: Optional[str] = None) -> str:
    """
    List all available skills.

    Args:
        skill_type: Filter by 'base' or 'ephemeral'

    Returns:
        JSON: {"skills": [{"name": "...", "domain": "...", "version": "..."}]}
    """
    skills = skill_manager.list_skills(skill_type=skill_type)

    return json.dumps({
        "skills": [
            {
                "name": s.metadata.name,
                "type": s.metadata.skill_type,
                "domain": s.metadata.domain,
                "tools": s.metadata.tools,
                "version": s.metadata.version,
                "updated": s.metadata.last_updated.isoformat(),
            }
            for s in skills
        ]
    }, indent=2)


@app.tool()
def cde_getSkill(skill_name: str) -> str:
    """
    Retrieve full content of a skill.

    Returns:
        Markdown content of the skill
    """
    skill = skill_manager.get_skill(skill_name)

    if not skill:
        return json.dumps({"error": "skill_not_found"}, indent=2)

    return skill.content


@app.tool()
async def cde_refreshSkills() -> str:
    """
    Trigger immediate skill update check.

    Returns:
        JSON: {"updated": 3, "skipped": 5, "errors": 0}
    """
    from cde_orchestrator.skills.updater import SkillUpdater

    updater = SkillUpdater(skill_manager=skill_manager)
    results = await updater.update_outdated_skills()

    return json.dumps(results, indent=2)
```

---

## 🧪 Testing Strategy

### Unit Tests

```python
# tests/skills/test_detector.py
import pytest
from cde_orchestrator.skills.detector import SkillRequirementDetector
from cde_orchestrator.skills.models import ComplexityLevel

def test_detect_high_complexity():
    detector = SkillRequirementDetector()

    task = "Implement Redis caching with pub/sub for real-time notifications"
    req = detector.analyze_task(task)

    assert req.needs_skill == True
    assert req.complexity == ComplexityLevel.HIGH
    assert req.domain == "database"
    assert "redis" in req.knowledge_gaps
    assert "pub/sub" in req.knowledge_gaps


def test_detect_low_complexity_no_skill():
    detector = SkillRequirementDetector()

    task = "Rename the user model file"
    req = detector.analyze_task(task)

    assert req.needs_skill == False
    assert req.complexity == ComplexityLevel.LOW


@pytest.mark.parametrize("task,expected_domain", [
    ("Setup PostgreSQL database with connection pooling", "database"),
    ("Build React dashboard with real-time updates", "web"),
    ("Deploy to Kubernetes with autoscaling", "infrastructure"),
])
def test_domain_detection(task, expected_domain):
    detector = SkillRequirementDetector()

    req = detector.analyze_task(task)

    assert req.domain == expected_domain
```

### Integration Tests

```python
# tests/skills/test_integration.py
import pytest
from pathlib import Path
from cde_orchestrator.skills.manager import SkillManager
from cde_orchestrator.skills.detector import SkillRequirementDetector

@pytest.mark.asyncio
async def test_full_skill_workflow(tmp_path):
    """Test complete workflow: detect → generate → load → distill."""

    skills_dir = tmp_path / ".copilot" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: Detect requirement
    detector = SkillRequirementDetector()
    task = "Implement Redis caching for FastAPI endpoints"
    req = detector.analyze_task(task)

    assert req.needs_skill == True

    # Step 2: Generate skill
    manager = SkillManager(skills_dir=skills_dir)
    skills = await manager.get_or_create_skills(
        domain=req.domain,
        knowledge_gaps=req.knowledge_gaps,
        task=task,
    )

    assert len(skills) > 0
    ephemeral = skills[0]
    assert ephemeral.metadata.skill_type == "ephemeral"
    assert ephemeral.file_path.exists()

    # Step 3: Load skill
    loaded = manager.get_skill(ephemeral.metadata.name)
    assert loaded is not None
    assert loaded.content == ephemeral.content

    # Step 4: Distill to base (simulated task completion)
    await manager.distill_ephemeral(ephemeral.metadata.name)

    # Check base skill was updated
    base_skills = manager.list_skills(skill_type="base")
    assert any(s.metadata.domain == req.domain for s in base_skills)
```

---

## 📊 Monitoring

### Prometheus Metrics

```python
# src/cde_orchestrator/skills/metrics.py
from prometheus_client import Counter, Histogram, Gauge

skill_generations = Counter(
    'dsms_skill_generations_total',
    'Total skills generated',
    ['domain', 'complexity']
)

skill_generation_duration = Histogram(
    'dsms_skill_generation_duration_seconds',
    'Time to generate skill',
    buckets=[1, 5, 10, 30, 60, 120]
)

skill_hits = Counter(
    'dsms_skill_hits_total',
    'Skills loaded during execution',
    ['skill_name', 'type']
)

skill_cache_size = Gauge(
    'dsms_skill_cache_size_bytes',
    'Total size of skill files'
)

research_api_calls = Counter(
    'dsms_research_api_calls_total',
    'API calls for research',
    ['provider']  # gemini, github, stackoverflow
)
```

### Usage in Code

```python
# In generator.py
from .metrics import skill_generations, skill_generation_duration

async def generate_skill(self, ...):
    with skill_generation_duration.time():
        # ... generation logic
        skill = EphemeralSkill(...)

        skill_generations.labels(
            domain=domain,
            complexity=complexity
        ).inc()

        return skill
```

---

## 🚀 Deployment

### Installation

```bash
# Install dependencies
pip install -r requirements-skills.txt

# Initialize skill directories
mkdir -p .copilot/skills/base
mkdir -p .copilot/skills/ephemeral

# Setup base skills (seed with defaults)
python -m cde_orchestrator.skills.init --seed
```

### Background Job (Skill Updater)

```python
# Add to src/server.py
import asyncio
from cde_orchestrator.skills.updater import SkillUpdater

async def skill_update_job():
    """Background job to update skills daily."""
    updater = SkillUpdater(skill_manager=skill_manager)

    while True:
        try:
            await updater.update_outdated_skills()
        except Exception as e:
            logger.error(f"Skill update job failed: {e}")

        # Run daily
        await asyncio.sleep(86400)

# Start background task
asyncio.create_task(skill_update_job())
```

---

## ✅ Acceptance Criteria

### Phase 1 Complete When:

- [ ] `SkillRequirementDetector` correctly identifies 90%+ of test cases
- [ ] `SkillSourcer` successfully scrapes awesome-claude-skills
- [ ] `WebResearcher` retrieves relevant docs/issues
- [ ] Base skills exist for top 5 domains

### Phase 2 Complete When:

- [ ] `SkillGenerator` creates valid ephemeral skills
- [ ] Generated skills pass manual review (code runs, references are valid)
- [ ] Ephemeral cleanup job removes expired skills

### Phase 3 Complete When:

- [ ] `SkillUpdater` detects and updates outdated skills
- [ ] Update notes include version changes + references
- [ ] Skills remain under 5000 tokens

### Phase 4 Complete When:

- [ ] MCP tools (`cde_listSkills`, etc.) are functional
- [ ] Skills auto-load during `cde_startFeature`
- [ ] Metrics dashboard shows skill usage stats

---

**Status:** ✅ Ready for Implementation
**Next Action:** Create feature branch `feature/dynamic-skill-system` and begin Phase 1
