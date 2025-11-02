---
author: Auto-Generated
created: '2025-11-02'
description: '``` ┌─────────────────────────────────────────────────────────────┐'
llm_summary: "User guide for Onboarding System: Technical Implementation Guide.\n\
  \  > **Status**: Implementation Ready > **Design Doc**: `specs/design/onboarding-system-redesign.md`\
  \ > **Target**: Sprint 1-4 (8 weeks) > **Priority**: \U0001F534 CRITICAL | Operation\
  \ | Target | Current | Status |\n  Reference when working with guide documentation."
status: draft
tags:
- architecture
- documentation
- implementation
- mcp
- migration
- onboarding
title: 'Onboarding System: Technical Implementation Guide'
type: design
updated: '2025-11-02'
---

# Onboarding System: Technical Implementation Guide

> **Status**: Implementation Ready
> **Design Doc**: `specs/design/onboarding-system-redesign.md`
> **Target**: Sprint 1-4 (8 weeks)
> **Priority**: 🔴 CRITICAL

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [File Structure](#file-structure)
3. [Core Components](#core-components)
4. [Implementation Roadmap](#implementation-roadmap)
5. [Testing Strategy](#testing-strategy)
6. [Migration Guide](#migration-guide)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     MCP Server Layer                        │
│                    (cde_onboardingProject)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│               Onboarding Orchestrator                       │
│          (Multi-phase execution & validation)               │
└─┬────────┬─────────┬─────────────┬────────────┬────────────┘
  │        │         │             │            │
  ▼        ▼         ▼             ▼            ▼
┌───────┐ ┌────────┐ ┌──────────┐ ┌─────────┐ ┌──────────┐
│ Repo  │ │ Consti │ │ Structure│ │ Cleanup │ │Validator │
│Analyst│ │ tution │ │ Builder  │ │ Manager │ │          │
└───┬───┘ └────────┘ └──────────┘ └─────────┘ └──────────┘
    │
    ├──> Cache Layer (SQLite)
    ├──> Git Integration
    └──> Token Estimator (tiktoken)
```

---

## File Structure

```
src/cde_orchestrator/
├── onboarding/                     # NEW: Onboarding subsystem
│   ├── __init__.py
│   ├── analyzer.py                # IntelligentRepoAnalyzer
│   ├── constitution.py            # ConstitutionGenerator
│   ├── orchestrator.py            # OnboardingOrchestrator
│   ├── validator.py               # OnboardingValidator
│   ├── cache.py                   # OnboardingCache
│   ├── cleanup.py                 # CleanupManager
│   ├── structure.py               # StructureBuilder
│   ├── models.py                  # Pydantic models
│   └── templates/                 # Constitution & doc templates
│       ├── constitution.md.j2
│       ├── readme.md.j2
│       └── ...
├── onboarding_analyzer.py         # DEPRECATED: To be removed
├── repo_ingest.py                 # DEPRECATED: To be replaced
└── ...

tests/
├── onboarding/                     # NEW: Onboarding tests
│   ├── test_analyzer.py
│   ├── test_constitution.py
│   ├── test_orchestrator.py
│   ├── test_validator.py
│   ├── test_cache.py
│   └── fixtures/                  # Test repositories
│       ├── simple_python/
│       ├── complex_web_app/
│       └── legacy_project/
```

---

## Core Components

### 1. IntelligentRepoAnalyzer

```python
# src/cde_orchestrator/onboarding/analyzer.py
"""
Async repository analyzer with GitIngest-inspired patterns.
"""
from pathlib import Path
from typing import Set, Dict, List
import asyncio
import tiktoken
from pydantic import BaseModel

class AnalysisConfig(BaseModel):
    """Configuration for repository analysis."""
    max_file_size: int = 1_000_000
    include_patterns: Set[str] = {"*.py", "*.md", "*.yml", "*.json", "*.toml"}
    exclude_patterns: Set[str] = {
        "*.pyc", "__pycache__", "node_modules", ".git",
        "*.egg-info", "venv", "env", ".venv"
    }
    analyze_branches: bool = True
    max_commits: int = 100
    include_submodules: bool = False
    estimate_tokens: bool = True
    detect_dependencies: bool = True
    max_file_content_size: int = 100_000  # For content analysis

class FileEntry(BaseModel):
    """Represents a file in the repository."""
    path: Path
    size: int
    lines: int
    extension: str
    content_snippet: str = ""  # First N chars for analysis

class FileTree(BaseModel):
    """Repository file tree structure."""
    root: Path
    files: List[FileEntry]
    total_files: int
    total_size: int
    total_lines: int

class TechStack(BaseModel):
    """Detected technology stack."""
    languages: Dict[str, int]  # language -> file count
    frameworks: List[str]
    package_managers: List[str]
    build_tools: List[str]
    primary_language: str

class GitInsights(BaseModel):
    """Git repository insights."""
    total_commits: int
    active_branches: int
    contributors: int
    commit_frequency: float  # commits per day
    recent_activity: str  # "high", "medium", "low"
    oldest_commit: str
    newest_commit: str

class TokenEstimate(BaseModel):
    """Token estimation for LLM context."""
    total: int
    by_file_type: Dict[str, int]
    model: str = "cl100k_base"  # OpenAI tokenizer
    fits_in_context: bool
    recommended_chunk_size: int

class RepositoryIntelligence(BaseModel):
    """Complete repository intelligence."""
    project_path: Path
    file_tree: FileTree
    tech_stack: TechStack
    git_insights: GitInsights
    token_estimate: TokenEstimate
    documentation_coverage: float
    test_coverage_estimate: float
    recommended_templates: List[str]
    analysis_timestamp: str

class IntelligentRepoAnalyzer:
    """
    Async repository analyzer combining:
    - GitIngest's file processing
    - Git history analysis
    - Tech stack detection
    - Token estimation
    """

    def __init__(self, cache: Optional['OnboardingCache'] = None):
        self.cache = cache
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    async def analyze_async(
        self,
        project_path: Path,
        config: AnalysisConfig = AnalysisConfig()
    ) -> RepositoryIntelligence:
        """
        Perform deep async analysis of repository.

        Steps:
        1. Check cache
        2. Build file tree (async)
        3. Detect tech stack
        4. Analyze git history
        5. Estimate tokens
        6. Generate insights
        7. Cache results
        """
        # Check cache first
        if self.cache:
            cached = await self.cache.get(project_path, config)
            if cached:
                return cached

        # Parallel execution of independent analyses
        file_tree, tech_stack, git_insights = await asyncio.gather(
            self._build_file_tree(project_path, config),
            self._detect_tech_stack(project_path),
            self._analyze_git_history(project_path, config)
        )

        # Token estimation (depends on file_tree)
        token_estimate = await self._estimate_tokens(file_tree, config)

        # Coverage estimates
        doc_coverage = self._estimate_documentation_coverage(file_tree)
        test_coverage = self._estimate_test_coverage(file_tree)

        # Recommend templates
        templates = self._recommend_templates(tech_stack, file_tree)

        intelligence = RepositoryIntelligence(
            project_path=project_path,
            file_tree=file_tree,
            tech_stack=tech_stack,
            git_insights=git_insights,
            token_estimate=token_estimate,
            documentation_coverage=doc_coverage,
            test_coverage_estimate=test_coverage,
            recommended_templates=templates,
            analysis_timestamp=datetime.now(timezone.utc).isoformat()
        )

        # Cache for future use
        if self.cache:
            await self.cache.set(project_path, config, intelligence)

        return intelligence

    async def _build_file_tree(
        self,
        project_path: Path,
        config: AnalysisConfig
    ) -> FileTree:
        """Build file tree with async I/O."""
        files: List[FileEntry] = []
        total_size = 0
        total_lines = 0

        # Use pathspec for .gitignore handling
        gitignore_spec = self._load_gitignore(project_path)

        # Async directory traversal
        async def process_file(file_path: Path):
            try:
                # Check patterns
                rel_path = file_path.relative_to(project_path)
                if not self._should_include(rel_path, config, gitignore_spec):
                    return None

                stat = file_path.stat()
                if stat.st_size > config.max_file_size:
                    return None

                # Read file content (async)
                content = await self._read_file_async(file_path, config.max_file_content_size)
                lines = content.count('\n')

                return FileEntry(
                    path=rel_path,
                    size=stat.st_size,
                    lines=lines,
                    extension=file_path.suffix,
                    content_snippet=content[:500] if content else ""
                )
            except Exception as e:
                logger.warning(f"Error processing {file_path}: {e}")
                return None

        # Gather all file processing tasks
        tasks = []
        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                tasks.append(process_file(file_path))

        # Execute in parallel with concurrency limit
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful results
        for result in results:
            if isinstance(result, FileEntry):
                files.append(result)
                total_size += result.size
                total_lines += result.lines

        return FileTree(
            root=project_path,
            files=files,
            total_files=len(files),
            total_size=total_size,
            total_lines=total_lines
        )

    async def _detect_tech_stack(self, project_path: Path) -> TechStack:
        """Detect technology stack from project files."""
        languages = Counter()
        frameworks = set()
        package_managers = set()
        build_tools = set()

        # File extension -> language mapping
        EXT_MAP = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
            '.java': 'Java', '.go': 'Go', '.rs': 'Rust',
            '.rb': 'Ruby', '.php': 'PHP', '.cs': 'C#'
        }

        # Detect from files
        for file in project_path.rglob("*"):
            if file.is_file():
                ext = file.suffix
                if ext in EXT_MAP:
                    languages[EXT_MAP[ext]] += 1

        # Detect package managers & frameworks
        if (project_path / "package.json").exists():
            package_managers.add("npm")
            # TODO: Detect React/Vue/Angular from package.json

        if (project_path / "requirements.txt").exists():
            package_managers.add("pip")

        if (project_path / "pyproject.toml").exists():
            package_managers.add("poetry")
            build_tools.add("poetry")

        if (project_path / "Cargo.toml").exists():
            package_managers.add("cargo")

        primary = languages.most_common(1)[0][0] if languages else "Unknown"

        return TechStack(
            languages=dict(languages),
            frameworks=list(frameworks),
            package_managers=list(package_managers),
            build_tools=list(build_tools),
            primary_language=primary
        )

    async def _analyze_git_history(
        self,
        project_path: Path,
        config: AnalysisConfig
    ) -> GitInsights:
        """Analyze Git history for project insights."""
        # Similar to existing logic but async
        # Use asyncio.create_subprocess_exec for git commands
        pass

    async def _estimate_tokens(
        self,
        file_tree: FileTree,
        config: AnalysisConfig
    ) -> TokenEstimate:
        """Estimate token count using tiktoken."""
        total_tokens = 0
        by_file_type = Counter()

        for file in file_tree.files:
            if file.content_snippet:
                tokens = len(self.tokenizer.encode(file.content_snippet))
                # Extrapolate from snippet to full file
                if len(file.content_snippet) < file.size:
                    ratio = file.size / len(file.content_snippet)
                    tokens = int(tokens * ratio)

                total_tokens += tokens
                by_file_type[file.extension] += tokens

        # Check if fits in typical context windows
        fits_in_context = total_tokens < 200_000  # Claude 3.5 Sonnet
        chunk_size = min(total_tokens // 5, 50_000) if total_tokens > 200_000 else total_tokens

        return TokenEstimate(
            total=total_tokens,
            by_file_type=dict(by_file_type),
            fits_in_context=fits_in_context,
            recommended_chunk_size=chunk_size
        )

    def _estimate_documentation_coverage(self, file_tree: FileTree) -> float:
        """Estimate documentation coverage."""
        doc_files = sum(1 for f in file_tree.files if f.extension in {'.md', '.rst', '.txt'})
        code_files = sum(1 for f in file_tree.files if f.extension not in {'.md', '.rst', '.txt'})

        if code_files == 0:
            return 0.0

        # Heuristic: Good docs = 1 doc file per 10 code files
        return min(doc_files / (code_files / 10), 1.0)

    def _estimate_test_coverage(self, file_tree: FileTree) -> float:
        """Estimate test coverage."""
        test_files = sum(1 for f in file_tree.files if 'test' in f.path.name.lower())
        code_files = sum(1 for f in file_tree.files if f.extension in {'.py', '.js', '.ts'})

        if code_files == 0:
            return 0.0

        # Heuristic: Good coverage = 1 test file per 2-3 code files
        return min(test_files / (code_files / 2.5), 1.0)
```

### 2. ConstitutionGenerator

```python
# src/cde_orchestrator/onboarding/constitution.py
"""
Generates project constitutions based on repository intelligence.
"""

class ConstitutionTemplate(BaseModel):
    """Template for constitution generation."""
    name: str
    applicable_to: List[str]  # project types
    core_values: List[str]
    code_standards: Dict[str, Any]
    testing_requirements: Dict[str, Any]

class ConstitutionGenerator:
    """
    Generates tailored project constitutions.
    """

    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir)
        )

    async def generate(
        self,
        intelligence: RepositoryIntelligence,
        existing_constitution: Optional[Path] = None
    ) -> Constitution:
        """
        Generate constitution based on:
        - Tech stack
        - Project size
        - Team size (from git)
        - Existing patterns (if re-onboarding)
        """
        # Select appropriate template
        template = self._select_template(intelligence)

        # Customize for tech stack
        customized = self._customize_for_tech_stack(template, intelligence.tech_stack)

        # Adjust for team size
        team_size = self._estimate_team_size(intelligence.git_insights)
        customized = self._adjust_for_team_size(customized, team_size)

        # Preserve existing if present
        if existing_constitution and existing_constitution.exists():
            customized = self._merge_with_existing(customized, existing_constitution)

        return customized

    def render_markdown(self, constitution: Constitution) -> str:
        """Render constitution to markdown using Jinja2."""
        template = self.jinja_env.get_template("constitution.md.j2")
        return template.render(constitution=constitution)
```

### 3. OnboardingOrchestrator

```python
# src/cde_orchestrator/onboarding/orchestrator.py
"""
Multi-phase onboarding orchestrator.
"""

class OnboardingPhase(StrEnum):
    """Onboarding phases."""
    INTELLIGENCE = "intelligence"
    CONSTITUTION = "constitution"
    STRUCTURE = "structure"
    CLEANUP = "cleanup"
    VALIDATION = "validation"

class OnboardingProgress(BaseModel):
    """Tracks onboarding progress."""
    current_phase: OnboardingPhase
    completed_phases: List[OnboardingPhase]
    failed_phases: List[OnboardingPhase]
    start_time: datetime
    estimated_completion: datetime
    progress_percentage: float

class OnboardingOrchestrator:
    """
    Orchestrates multi-phase onboarding with validation.
    """

    def __init__(
        self,
        analyzer: IntelligentRepoAnalyzer,
        constitution_gen: ConstitutionGenerator,
        structure_builder: StructureBuilder,
        cleanup_manager: CleanupManager,
        validator: OnboardingValidator,
        cache: OnboardingCache
    ):
        self.analyzer = analyzer
        self.constitution_gen = constitution_gen
        self.structure_builder = structure_builder
        self.cleanup_manager = cleanup_manager
        self.validator = validator
        self.cache = cache

    async def execute_onboarding(
        self,
        project_path: Path,
        mode: OnboardingMode = OnboardingMode.FULL,
        config: AnalysisConfig = AnalysisConfig()
    ) -> OnboardingResult:
        """
        Execute complete onboarding process.
        """
        progress = OnboardingProgress(
            current_phase=OnboardingPhase.INTELLIGENCE,
            completed_phases=[],
            failed_phases=[],
            start_time=datetime.now(timezone.utc),
            estimated_completion=datetime.now(timezone.utc) + timedelta(seconds=30),
            progress_percentage=0.0
        )

        try:
            # Phase 1: Intelligence Gathering
            intelligence = await self._phase_intelligence(project_path, config, progress)

            # Phase 2: Constitution
            constitution = await self._phase_constitution(intelligence, progress)

            # Phase 3: Structure
            structure_result = await self._phase_structure(project_path, intelligence, progress)

            # Phase 4: Cleanup
            cleanup_result = await self._phase_cleanup(project_path, intelligence, progress)

            # Phase 5: Validation
            validation = await self._phase_validation(project_path, progress)

            return OnboardingResult(
                status=OnboardingStatus.SUCCESS,
                intelligence=intelligence,
                constitution=constitution,
                structure_result=structure_result,
                cleanup_result=cleanup_result,
                validation=validation,
                progress=progress,
                health_score=validation.health_score
            )

        except Exception as e:
            logger.exception("Onboarding failed")
            return OnboardingResult(
                status=OnboardingStatus.FAILED,
                error=str(e),
                progress=progress
            )

    async def _phase_intelligence(
        self,
        project_path: Path,
        config: AnalysisConfig,
        progress: OnboardingProgress
    ) -> RepositoryIntelligence:
        """Phase 1: Gather repository intelligence."""
        progress.current_phase = OnboardingPhase.INTELLIGENCE
        progress.progress_percentage = 0.2

        intelligence = await self.analyzer.analyze_async(project_path, config)

        progress.completed_phases.append(OnboardingPhase.INTELLIGENCE)
        return intelligence

    # ... similar methods for other phases
```

---

## Implementation Roadmap

### Week 1-2: Sprint 1

**Goal**: Foundation with async analysis

```python
# Priority tasks
1. Setup new package structure
2. Implement IntelligentRepoAnalyzer (async)
3. Add tiktoken integration
4. Create basic caching layer
5. Write comprehensive tests
```

### Week 3-4: Sprint 2

**Goal**: Constitution generation

```python
# Priority tasks
1. Implement ConstitutionGenerator
2. Create Jinja2 templates
3. Add tech-stack detection
4. Test on diverse projects
```

### Week 5-6: Sprint 3

**Goal**: Orchestration & validation

```python
# Priority tasks
1. Build OnboardingOrchestrator
2. Implement multi-phase execution
3. Add progress tracking
4. Create rollback mechanism
```

### Week 7-8: Sprint 4

**Goal**: Quality & polish

```python
# Priority tasks
1. Implement OnboardingValidator
2. Add health scoring
3. Create repair mode
4. Documentation & examples
```

---

## Testing Strategy

### Unit Tests

```python
# tests/onboarding/test_analyzer.py
@pytest.mark.asyncio
async def test_analyzer_basic_repo():
    """Test analysis of simple Python project."""
    analyzer = IntelligentRepoAnalyzer()

    intelligence = await analyzer.analyze_async(
        project_path=TEST_REPO_PATH,
        config=AnalysisConfig()
    )

    assert intelligence.file_tree.total_files > 0
    assert intelligence.tech_stack.primary_language == "Python"
    assert intelligence.token_estimate.total > 0

@pytest.mark.asyncio
async def test_analyzer_with_gitignore():
    """Test that .gitignore is respected."""
    analyzer = IntelligentRepoAnalyzer()

    intelligence = await analyzer.analyze_async(
        project_path=TEST_REPO_WITH_GITIGNORE,
        config=AnalysisConfig()
    )

    # Should not include files in .gitignore
    file_paths = {f.path for f in intelligence.file_tree.files}
    assert not any("__pycache__" in str(p) for p in file_paths)
    assert not any(".pyc" in str(p) for p in file_paths)
```

### Integration Tests

```python
# tests/onboarding/test_orchestrator.py
@pytest.mark.asyncio
async def test_full_onboarding():
    """Test complete onboarding flow."""
    orchestrator = create_test_orchestrator()

    result = await orchestrator.execute_onboarding(
        project_path=TEST_REPO_PATH,
        mode=OnboardingMode.FULL
    )

    assert result.status == OnboardingStatus.SUCCESS
    assert len(result.progress.completed_phases) == 5
    assert result.health_score > 0.5
```

### Performance Tests

```python
@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_analyzer_performance_large_repo():
    """Benchmark analysis of large repository (1000+ files)."""
    analyzer = IntelligentRepoAnalyzer()

    start = time.time()
    intelligence = await analyzer.analyze_async(LARGE_REPO_PATH)
    duration = time.time() - start

    assert duration < 5.0, f"Analysis took {duration}s, expected < 5s"
    assert intelligence.file_tree.total_files > 1000
```

---

## Migration Guide

### For Existing Users

**Step 1**: Update configuration

```yaml
# .cde/config.yml (NEW)
onboarding:
  analyzer:
    max_file_size: 1000000
    include_patterns:
      - "*.py"
      - "*.md"
    exclude_patterns:
      - "__pycache__"
      - "*.pyc"
  cache:
    enabled: true
    ttl: 86400  # 24 hours
```

**Step 2**: Run migration script

```bash
python -m cde_orchestrator.onboarding.migrate --project-path .
```

**Step 3**: Validate new structure

```bash
python -m cde_orchestrator.onboarding.validate --project-path .
```

---

## Performance Benchmarks

| Operation | Target | Current | Status |
|-----------|--------|---------|--------|
| Small repo (< 100 files) | < 1s | TBD | 🟡 |
| Medium repo (100-1000 files) | < 3s | TBD | 🟡 |
| Large repo (1000+ files) | < 5s | TBD | 🟡 |
| Token estimation | < 500ms | TBD | 🟡 |
| Cache hit | < 100ms | TBD | 🟡 |

---

## Next Steps

1. **Create Feature Branch**: `feature/onboarding-redesign`
2. **Setup Package Structure**: Create `src/cde_orchestrator/onboarding/`
3. **Implement Sprint 1**: Focus on analyzer + cache
4. **Test on Real Projects**: CDE, Spec-Kit, GitIngest
5. **Iterate & Refine**: Based on feedback

---

**Document Status**: ✅ IMPLEMENTATION READY
**Dependencies**: tiktoken, pathspec, jinja2, aiofiles
**Est. Completion**: 8 weeks (4 sprints)
