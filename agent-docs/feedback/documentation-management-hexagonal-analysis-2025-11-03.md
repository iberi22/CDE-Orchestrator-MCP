---
title: "Documentation Management Hexagonal Architecture Analysis"
description: "Analysis and recommendations for improving documentation management using hexagonal architecture patterns and Gateway design"
type: "feedback"
status: "draft"
created: "2025-11-03"
updated: "2025-11-03"
author: "GitHub Copilot"
tags:
  - "architecture"
  - "documentation"
  - "hexagonal"
  - "gateway"
  - "agent-docs"
  - "spec-kit"
llm_summary: |
  Comprehensive analysis of current documentation management tools (cde_scanDocumentation,
  cde_analyzeDocumentation, cde_onboardingProject, cde_publishOnboarding) with recommendations
  for hexagonal architecture improvements using Gateway pattern for external system interaction.
---

# Documentation Management Hexagonal Architecture Analysis

> **Generated**: 2025-11-03
> **Context**: User request to improve documentation management using hexagonal architecture
> **Research Sources**: Martin Fowler's Gateway Pattern, current MCP tool implementation

---

## 🎯 Executive Summary

### Current State
- **4 MCP Tools** for documentation management:
  - `cde_onboardingProject` - Analyze & initialize projects
  - `cde_publishOnboarding` - Apply LLM-generated docs
  - `cde_scanDocumentation` - Audit doc structure
  - `cde_analyzeDocumentation` - Deep quality analysis

### Key Findings
1. ✅ **Good Separation**: Tools are properly granular, not monolithic
2. ⚠️ **No Agent-Docs Management Tool**: Missing automated cleanup/organization
3. ⚠️ **Mixed Concerns**: Onboarding handles both analysis AND file writing
4. ⚠️ **No Gateway Pattern**: Direct filesystem interaction, hard to test
5. ⚠️ **No Spec Creation Tool**: Agents can't create professional specs via MCP

### Recommendations
1. **Create `cde_organizeAgentDocs` tool** - Automated cleanup following governance
2. **Implement Gateway Pattern** - Isolate filesystem/Git interactions
3. **Split onboarding concerns** - Separate analysis from file writing
4. **Add `cde_createSpec` tool** - Professional spec generation following Spec-Kit

---

## 📊 Current Architecture Analysis

### MCP Tool Layer (src/server.py)

```python
# CURRENT: Direct coupling to use cases
@app.tool()
def cde_scanDocumentation(project_path: str = ".") -> str:
    use_case = ScanDocumentationUseCase()  # ✅ Good: Uses application layer
    result = use_case.execute(project_path)
    return json.dumps(result, indent=2)

@app.tool()
def cde_publishOnboarding(documents: Dict[str, str], approve: bool = True) -> str:
    # ❌ BAD: Direct filesystem interaction in MCP layer
    for path, content in documents.items():
        dest = project_root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    # ...
```

**Issues**:
1. `cde_publishOnboarding` bypasses application layer, writes files directly
2. No gateway for external systems (filesystem, Git)
3. Hard to test without actual file I/O

---

## 🏗️ Hexagonal Architecture with Gateway Pattern

### Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Tool Layer (server.py)                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ cde_scanDocumentation()                              │   │
│  │ cde_analyzeDocumentation()                           │   │
│  │ cde_organizeAgentDocs() 🆕                           │   │
│  │ cde_createSpec() 🆕                                  │   │
│  │ cde_publishDocuments() (renamed)                     │   │
│  └────────────────────┬────────────────────────────────┘   │
└───────────────────────┼────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Application Layer (use cases)                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ScanDocumentationUseCase                             │   │
│  │ AnalyzeDocumentationUseCase                          │   │
│  │ OrganizeAgentDocsUseCase 🆕                          │   │
│  │ CreateSpecificationUseCase 🆕                        │   │
│  │ PublishDocumentsUseCase                              │   │
│  └────────────────────┬────────────────────────────────┘   │
└───────────────────────┼────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│            Domain Layer (entities & ports)                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Entities:                                            │   │
│  │   - DocumentationProject                             │   │
│  │   - Specification                                    │   │
│  │   - AgentReport                                      │   │
│  │                                                       │   │
│  │ Ports (Interfaces):                                  │   │
│  │   - IDocumentationRepository                         │   │
│  │   - IFileSystemGateway 🆕                            │   │
│  │   - IGitGateway 🆕                                   │   │
│  │   - IMetadataValidator                               │   │
│  └────────────────────┬────────────────────────────────┘   │
└───────────────────────┼────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│           Adapters Layer (implementations)                   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ FileSystemGateway 🆕                                 │   │
│  │   - read_file()                                      │   │
│  │   - write_file()                                     │   │
│  │   - move_file()                                      │   │
│  │   - list_directory()                                 │   │
│  │                                                       │   │
│  │ GitGateway 🆕                                        │   │
│  │   - git_mv() (preserves history)                     │   │
│  │   - commit()                                         │   │
│  │   - get_history()                                    │   │
│  │                                                       │   │
│  │ DocumentationRepository                              │   │
│  │   (Uses FileSystemGateway + GitGateway)              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Detailed Analysis by Tool

### 1. `cde_scanDocumentation` ✅ Good

**Current Implementation**:
```python
@app.tool()
def cde_scanDocumentation(project_path: str = ".") -> str:
    use_case = ScanDocumentationUseCase()
    result = use_case.execute(project_path)
    return json.dumps(result, indent=2)
```

**Analysis**:
- ✅ Follows hexagonal pattern correctly
- ✅ Delegates to application layer
- ✅ No direct filesystem access in tool
- ⚠️ Use case likely has direct filesystem access (acceptable in use case)

**Recommendation**: Keep as-is, but ensure use case uses gateway internally.

---

### 2. `cde_analyzeDocumentation` ✅ Good

**Current Implementation**:
```python
@app.tool()
def cde_analyzeDocumentation(project_path: str = ".") -> str:
    use_case = AnalyzeDocumentationUseCase()
    result = use_case.execute(project_path)
    return json.dumps(result, indent=2)
```

**Analysis**: Same as `cde_scanDocumentation` - follows pattern correctly.

---

### 3. `cde_publishOnboarding` ❌ Needs Refactoring

**Current Implementation**:
```python
@app.tool()
def cde_publishOnboarding(documents: Dict[str, str], approve: bool = True) -> str:
    # ❌ Direct filesystem access in MCP layer!
    for path, content in documents.items():
        dest = project_root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
```

**Problems**:
1. ❌ Bypasses application layer completely
2. ❌ Direct filesystem manipulation in MCP tool
3. ❌ Hard to test (requires actual file I/O)
4. ❌ No gateway isolation
5. ❌ Mixed concerns (approval logic + file writing)

**Recommended Refactoring**:

```python
# MCP Tool (server.py)
@app.tool()
def cde_publishDocuments(
    documents: Dict[str, str],
    approve: bool = True,
    category: str = "onboarding"  # or "spec", "agent-report"
) -> str:
    """
    Generic document publishing tool.
    Replaces cde_publishOnboarding with broader scope.
    """
    use_case = PublishDocumentsUseCase(
        filesystem_gateway=container.get_filesystem_gateway(),
        git_gateway=container.get_git_gateway()
    )

    result = use_case.execute({
        "documents": documents,
        "approve": approve,
        "category": category,
        "project_root": os.getcwd()
    })

    return json.dumps(result, indent=2)


# Application Layer (use_cases/publish_documents_use_case.py)
class PublishDocumentsUseCase:
    def __init__(self, filesystem_gateway: IFileSystemGateway, git_gateway: IGitGateway):
        self.fs_gateway = filesystem_gateway
        self.git_gateway = git_gateway

    def execute(self, input_data: Dict) -> Dict:
        documents = input_data["documents"]
        approve = input_data["approve"]
        category = input_data["category"]
        project_root = Path(input_data["project_root"])

        # Business logic: Validate approval
        if not approve:
            return {"status": "declined", "message": "User declined"}

        # Business logic: Determine target directory based on category
        target_dirs = {
            "onboarding": project_root,
            "spec": project_root / "specs",
            "agent-report": project_root / "agent-docs"
        }
        target_dir = target_dirs.get(category, project_root)

        # Use gateway to write files
        created = []
        failed = []

        for path, content in documents.items():
            try:
                # Gateway handles all filesystem concerns
                full_path = self.fs_gateway.write_file(
                    target_dir / path,
                    content,
                    create_parents=True
                )
                created.append(str(full_path))
            except Exception as e:
                failed.append({"path": path, "error": str(e)})

        return {
            "status": "applied",
            "created": created,
            "failed": failed
        }


# Adapter (adapters/filesystem_gateway.py) 🆕
class FileSystemGateway(IFileSystemGateway):
    """
    Gateway for filesystem operations.
    Isolates external filesystem concerns from domain logic.
    """

    def write_file(
        self,
        path: Path,
        content: str,
        create_parents: bool = False
    ) -> Path:
        """Write file to filesystem."""
        if create_parents:
            path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(content, encoding="utf-8")
        return path

    def read_file(self, path: Path) -> str:
        """Read file from filesystem."""
        return path.read_text(encoding="utf-8")

    def move_file(self, src: Path, dest: Path, preserve_history: bool = False) -> Path:
        """Move file, optionally preserving Git history."""
        if preserve_history and self._is_git_tracked(src):
            # Delegate to Git gateway
            return self._git_move(src, dest)
        else:
            # Simple filesystem move
            dest.parent.mkdir(parents=True, exist_ok=True)
            src.rename(dest)
            return dest

    def list_directory(
        self,
        path: Path,
        pattern: str = "*.md",
        recursive: bool = True
    ) -> List[Path]:
        """List files matching pattern."""
        if recursive:
            return list(path.rglob(pattern))
        return list(path.glob(pattern))
```

---

## 🆕 Missing Tool: `cde_organizeAgentDocs`

### Problem Statement

**Current Situation**:
- Agent-generated docs land in `agent-docs/` subdirectories
- Governance rules defined in `specs/governance/DOCUMENTATION_GOVERNANCE.md`
- **NO automated cleanup/organization tool exists**
- Manual cleanup required after each agent session

**User's Question**:
> "en que tool se hace la limpieza y movimiento de los archivos con la especificacion de agent-docs"

**Answer**: **No existe todavía**. Es necesario crear esta herramienta.

### Recommended Tool: `cde_organizeAgentDocs`

```python
@app.tool()
@tool_handler
def cde_organizeAgentDocs(
    dry_run: bool = True,
    auto_archive_research: bool = True,
    preserve_git_history: bool = True
) -> str:
    """
    🧹 Organize agent-generated documentation following governance rules.

    **USE THIS TOOL TO:**
    - Move orphaned reports to correct agent-docs/ subdirectories
    - Auto-archive research notes older than 90 days
    - Validate metadata in all agent-docs
    - Cleanup root-level agent reports
    - Enforce agent-docs/ structure

    Args:
        dry_run: If True, only report what would be done (default: True)
        auto_archive_research: Archive research/ docs > 90 days (default: True)
        preserve_git_history: Use git mv instead of filesystem mv (default: True)

    Returns:
        JSON with:
            - actions_planned: List of operations to perform
            - actions_completed: What was actually done (if dry_run=False)
            - violations_found: Files violating governance
            - recommendations: Suggested manual actions

    Examples:
        >>> cde_organizeAgentDocs(dry_run=True)
        {
          "actions_planned": [
            "MOVE: ROOT/session-report.md → agent-docs/sessions/",
            "ARCHIVE: agent-docs/research/old-research-2024-08.md → .archive/",
            "ADD_METADATA: agent-docs/execution/report.md"
          ],
          "violations_found": 3,
          "recommendations": [
            "Run with dry_run=False to apply changes",
            "Review archived research before deletion"
          ]
        }

        >>> cde_organizeAgentDocs(dry_run=False, preserve_git_history=True)
        # Executes cleanup with git mv (preserves history)

    **Common Use Cases:**
    1. After agent session: `cde_organizeAgentDocs(dry_run=True)` (preview)
    2. Apply cleanup: `cde_organizeAgentDocs(dry_run=False)`
    3. Weekly maintenance: Auto-archive old research

    **Governance Rules Applied:**
    - Sessions → agent-docs/sessions/
    - Execution reports → agent-docs/execution/
    - Feedback → agent-docs/feedback/
    - Research > 90 days → agent-docs/research/.archive/
    - Orphaned root reports → agent-docs/sessions/ (default)
    """
    use_case = OrganizeAgentDocsUseCase(
        filesystem_gateway=container.get_filesystem_gateway(),
        git_gateway=container.get_git_gateway(),
        metadata_validator=container.get_metadata_validator()
    )

    result = use_case.execute({
        "project_root": os.getcwd(),
        "dry_run": dry_run,
        "auto_archive_research": auto_archive_research,
        "preserve_git_history": preserve_git_history
    })

    return json.dumps(result, indent=2)
```

### Implementation Plan

**Phase 1: Create Gateway Adapters** (2 hours)

**Files to Create**:
- `src/cde_orchestrator/domain/ports.py` - Add `IFileSystemGateway`, `IGitGateway`
- `src/cde_orchestrator/adapters/filesystem_gateway.py` 🆕
- `src/cde_orchestrator/adapters/git_gateway.py` 🆕

**Phase 2: Create Use Case** (3 hours)

**Files to Create**:
- `src/cde_orchestrator/application/documentation/organize_agent_docs_use_case.py` 🆕

**Logic**:
1. Scan project root for orphaned .md files
2. Detect document type from metadata (session/execution/feedback/research)
3. Check research/ for files > 90 days old
4. Plan moves (root → agent-docs/, research → .archive/)
5. Validate metadata exists
6. Execute moves using gateway (preserves Git history if requested)

**Phase 3: Add MCP Tool** (1 hour)

**Files to Modify**:
- `src/server.py` - Add `cde_organizeAgentDocs` tool

**Phase 4: Testing** (2 hours)

**Files to Create**:
- `tests/unit/application/test_organize_agent_docs_use_case.py`
- `tests/integration/test_cde_organize_agent_docs_tool.py`

**Total Effort**: ~8 hours

---

## 🆕 Missing Tool: `cde_createSpec`

### Problem Statement

**Current Situation**:
- Agents can analyze projects (`cde_onboardingProject`)
- Agents can publish generic documents (`cde_publishOnboarding`)
- **NO tool for creating professional Spec-Kit specifications**
- Agents must manually craft specs without structured guidance

**User's Need**:
> "quiero que vayamos mejorando tool por tool, para usar con un proyecto real muy robusto"

**Answer**: Need `cde_createSpec` for professional specification creation.

### Recommended Tool: `cde_createSpec`

```python
@app.tool()
@tool_handler
def cde_createSpec(
    title: str,
    spec_type: str,  # "feature" | "design" | "task" | "api"
    content: str,
    author: Optional[str] = None,
    tags: Optional[List[str]] = None,
    related_specs: Optional[List[str]] = None
) -> str:
    """
    📝 Create professional Spec-Kit specification with proper structure.

    **USE THIS TOOL TO:**
    - Create feature specifications in specs/features/
    - Create design documents in specs/design/
    - Create task plans in specs/tasks/
    - Create API docs in specs/api/
    - Auto-generate YAML frontmatter
    - Enforce Spec-Kit conventions

    Args:
        title: Specification title (e.g., "User Authentication System")
        spec_type: Type of spec ("feature" | "design" | "task" | "api")
        content: Markdown content (without frontmatter)
        author: Author name (default: detected from git config)
        tags: List of tags (default: auto-generated from content)
        related_specs: List of related spec IDs for linking

    Returns:
        JSON with:
            - spec_id: Generated unique ID
            - file_path: Where spec was created
            - metadata: Applied YAML frontmatter
            - validation: Governance checks passed
            - next_steps: Suggested related actions

    Examples:
        >>> cde_createSpec(
        ...     title="Redis Caching Layer",
        ...     spec_type="design",
        ...     content=\"\"\"
        ... ## Problem
        ... Current system makes repeated database calls...
        ...
        ... ## Solution
        ... Implement Redis caching with connection pooling...
        ... \"\"\",
        ...     tags=["redis", "performance", "database"]
        ... )
        {
          "spec_id": "redis-caching-layer",
          "file_path": "specs/design/redis-caching-layer.md",
          "metadata": {
            "title": "Redis Caching Layer",
            "type": "design",
            "status": "draft",
            "created": "2025-11-03",
            "tags": ["redis", "performance", "database"]
          },
          "validation": {
            "governance": "passed",
            "metadata": "valid",
            "links": "none_broken"
          },
          "next_steps": [
            "Link from specs/design/README.md",
            "Create implementation task in specs/tasks/",
            "Add related feature spec"
          ]
        }

    **Common Use Cases:**
    1. Feature planning: `cde_createSpec(title="...", spec_type="feature")`
    2. Architecture design: `cde_createSpec(title="...", spec_type="design")`
    3. Task breakdown: `cde_createSpec(title="...", spec_type="task")`

    **Spec-Kit Conventions Applied:**
    - Auto-generate slug ID from title
    - Add complete YAML frontmatter
    - Place in correct specs/ subdirectory
    - Validate metadata requirements
    - Check for broken links
    - Suggest index updates
    """
    use_case = CreateSpecificationUseCase(
        filesystem_gateway=container.get_filesystem_gateway(),
        metadata_validator=container.get_metadata_validator()
    )

    result = use_case.execute({
        "title": title,
        "spec_type": spec_type,
        "content": content,
        "author": author,
        "tags": tags or [],
        "related_specs": related_specs or [],
        "project_root": os.getcwd()
    })

    return json.dumps(result, indent=2)
```

### Implementation Plan

**Phase 1: Create Domain Entities** (2 hours)

**Files to Create**:
- `src/cde_orchestrator/domain/entities.py` - Add `Specification` entity

```python
class Specification:
    """Domain entity for Spec-Kit specifications."""

    id: str  # Slug generated from title
    title: str
    spec_type: SpecType  # Enum: FEATURE, DESIGN, TASK, API
    content: str
    metadata: SpecificationMetadata
    status: SpecStatus  # Enum: DRAFT, ACTIVE, DEPRECATED, ARCHIVED

    @classmethod
    def create(cls, title: str, spec_type: str, content: str) -> "Specification":
        """Factory method with business rules."""
        # Generate slug ID
        spec_id = cls._generate_slug(title)

        # Create metadata
        metadata = SpecificationMetadata.create(title, spec_type)

        return cls(
            id=spec_id,
            title=title,
            spec_type=SpecType(spec_type),
            content=content,
            metadata=metadata,
            status=SpecStatus.DRAFT
        )

    def validate(self) -> List[str]:
        """Validate spec follows Spec-Kit conventions."""
        errors = []

        # Business rules
        if len(self.title) < 5:
            errors.append("Title too short (min 5 chars)")

        if not self.metadata.description:
            errors.append("Missing description in metadata")

        # Content structure validation
        if "## Problem" not in self.content and self.spec_type == SpecType.FEATURE:
            errors.append("Feature specs must have '## Problem' section")

        return errors
```

**Phase 2: Create Use Case** (3 hours)

**Files to Create**:
- `src/cde_orchestrator/application/documentation/create_specification_use_case.py` 🆕

**Phase 3: Add MCP Tool** (1 hour)

**Files to Modify**:
- `src/server.py` - Add `cde_createSpec` tool

**Total Effort**: ~6 hours

---

## 🔧 Gateway Pattern Implementation

### New Port Interfaces

```python
# src/cde_orchestrator/domain/ports.py

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional


class IFileSystemGateway(ABC):
    """
    Gateway for filesystem operations.
    Isolates file I/O concerns from domain logic.
    Based on Martin Fowler's Gateway Pattern.
    """

    @abstractmethod
    def write_file(self, path: Path, content: str, create_parents: bool = False) -> Path:
        """Write content to file."""
        pass

    @abstractmethod
    def read_file(self, path: Path) -> str:
        """Read file content."""
        pass

    @abstractmethod
    def move_file(self, src: Path, dest: Path, preserve_history: bool = False) -> Path:
        """Move file, optionally preserving Git history."""
        pass

    @abstractmethod
    def delete_file(self, path: Path) -> None:
        """Delete file."""
        pass

    @abstractmethod
    def list_directory(
        self,
        path: Path,
        pattern: str = "*",
        recursive: bool = False
    ) -> List[Path]:
        """List files matching pattern."""
        pass

    @abstractmethod
    def file_exists(self, path: Path) -> bool:
        """Check if file exists."""
        pass


class IGitGateway(ABC):
    """
    Gateway for Git operations.
    Isolates version control concerns from domain logic.
    """

    @abstractmethod
    def git_mv(self, src: Path, dest: Path) -> bool:
        """Move file using git mv (preserves history)."""
        pass

    @abstractmethod
    def is_tracked(self, path: Path) -> bool:
        """Check if file is tracked by Git."""
        pass

    @abstractmethod
    def commit(self, message: str, paths: Optional[List[Path]] = None) -> bool:
        """Commit changes."""
        pass

    @abstractmethod
    def get_file_history(self, path: Path, limit: int = 10) -> List[Dict]:
        """Get commit history for file."""
        pass


class IMetadataValidator(ABC):
    """
    Gateway for metadata validation.
    Validates YAML frontmatter in documentation.
    """

    @abstractmethod
    def validate(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate metadata in file.

        Returns:
            {
                "valid": bool,
                "errors": List[str],
                "metadata": Dict (if valid)
            }
        """
        pass

    @abstractmethod
    def extract_metadata(self, content: str) -> Optional[Dict]:
        """Extract YAML frontmatter from content."""
        pass

    @abstractmethod
    def add_metadata(
        self,
        content: str,
        title: str,
        doc_type: str,
        **kwargs
    ) -> str:
        """Add YAML frontmatter to content."""
        pass
```

### Adapter Implementations

```python
# src/cde_orchestrator/adapters/filesystem_gateway.py

from pathlib import Path
from typing import List
from ..domain.ports import IFileSystemGateway


class FileSystemGateway(IFileSystemGateway):
    """
    Production implementation of file system gateway.
    Uses standard library pathlib for filesystem operations.
    """

    def write_file(self, path: Path, content: str, create_parents: bool = False) -> Path:
        if create_parents:
            path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(content, encoding="utf-8")
        return path

    def read_file(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def move_file(self, src: Path, dest: Path, preserve_history: bool = False) -> Path:
        dest.parent.mkdir(parents=True, exist_ok=True)

        if preserve_history and self.file_exists(src / ".git"):
            # Use Git gateway if available
            # For now, fall back to simple rename
            pass

        src.rename(dest)
        return dest

    def delete_file(self, path: Path) -> None:
        if path.exists():
            path.unlink()

    def list_directory(
        self,
        path: Path,
        pattern: str = "*",
        recursive: bool = False
    ) -> List[Path]:
        if recursive:
            return list(path.rglob(pattern))
        return list(path.glob(pattern))

    def file_exists(self, path: Path) -> bool:
        return path.exists() and path.is_file()


# src/cde_orchestrator/adapters/git_gateway.py

import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from ..domain.ports import IGitGateway


class GitGateway(IGitGateway):
    """
    Production implementation of Git gateway.
    Uses subprocess to call git commands.
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root

    def git_mv(self, src: Path, dest: Path) -> bool:
        """Use git mv to preserve file history."""
        try:
            subprocess.run(
                ["git", "mv", str(src), str(dest)],
                cwd=self.repo_root,
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def is_tracked(self, path: Path) -> bool:
        """Check if file is tracked by Git."""
        try:
            result = subprocess.run(
                ["git", "ls-files", "--error-unmatch", str(path)],
                cwd=self.repo_root,
                capture_output=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def commit(self, message: str, paths: Optional[List[Path]] = None) -> bool:
        try:
            cmd = ["git", "commit", "-m", message]
            if paths:
                cmd.extend([str(p) for p in paths])

            subprocess.run(cmd, cwd=self.repo_root, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def get_file_history(self, path: Path, limit: int = 10) -> List[Dict]:
        """Get commit history for file."""
        try:
            result = subprocess.run(
                [
                    "git", "log",
                    f"-{limit}",
                    "--format=%H|%an|%at|%s",
                    "--", str(path)
                ],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )

            history = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    hash, author, timestamp, message = line.split("|", 3)
                    history.append({
                        "hash": hash,
                        "author": author,
                        "timestamp": int(timestamp),
                        "message": message
                    })

            return history
        except Exception:
            return []
```

---

## 📋 Implementation Roadmap

### Phase 1: Gateway Infrastructure (Week 1)

**Priority**: 🔴 CRITICAL (Foundation for all improvements)

**Tasks**:
1. Create `IFileSystemGateway`, `IGitGateway`, `IMetadataValidator` ports
2. Implement `FileSystemGateway` adapter
3. Implement `GitGateway` adapter
4. Implement `MetadataValidator` adapter
5. Add to DI container
6. Write unit tests with mocks

**Files**:
- `src/cde_orchestrator/domain/ports.py` (+80 lines)
- `src/cde_orchestrator/adapters/filesystem_gateway.py` 🆕 (+120 lines)
- `src/cde_orchestrator/adapters/git_gateway.py` 🆕 (+90 lines)
- `src/cde_orchestrator/adapters/metadata_validator.py` 🆕 (+60 lines)
- `tests/unit/adapters/test_filesystem_gateway.py` 🆕 (+150 lines)

**Acceptance Criteria**:
```python
def test_filesystem_gateway():
    gateway = FileSystemGateway()
    path = gateway.write_file(Path("test.md"), "content")
    content = gateway.read_file(path)
    assert content == "content"

def test_git_gateway():
    git = GitGateway(Path.cwd())
    assert git.is_tracked(Path("src/server.py")) == True
```

---

### Phase 2: Refactor Existing Tools (Week 2)

**Priority**: 🟡 HIGH

**Tasks**:
1. Refactor `cde_publishOnboarding` → `cde_publishDocuments`
2. Update `PublishDocumentsUseCase` to use gateways
3. Update `ScanDocumentationUseCase` to use `IFileSystemGateway`
4. Update `AnalyzeDocumentationUseCase` to use `IFileSystemGateway`
5. Add gateway injection to DI container

**Files Modified**:
- `src/server.py` (refactor `cde_publishOnboarding`)
- `src/cde_orchestrator/application/documentation/` (update use cases)

**Acceptance Criteria**:
```python
def test_publish_documents_use_case():
    mock_fs = MockFileSystemGateway()
    use_case = PublishDocumentsUseCase(filesystem_gateway=mock_fs)

    result = use_case.execute({
        "documents": {"test.md": "content"},
        "approve": True
    })

    assert result["status"] == "applied"
    assert mock_fs.write_file_called
```

---

### Phase 3: Add `cde_organizeAgentDocs` (Week 3)

**Priority**: 🟡 HIGH (User's primary request)

**Tasks**:
1. Create `Specification` domain entity
2. Create `OrganizeAgentDocsUseCase`
3. Add `cde_organizeAgentDocs` MCP tool
4. Implement dry-run mode
5. Implement auto-archive logic (90 days)
6. Add Git history preservation
7. Write comprehensive tests

**Files**:
- `src/cde_orchestrator/domain/entities.py` (+50 lines - Specification entity)
- `src/cde_orchestrator/application/documentation/organize_agent_docs_use_case.py` 🆕 (+200 lines)
- `src/server.py` (+40 lines - new tool)
- `tests/unit/application/test_organize_agent_docs.py` 🆕 (+180 lines)
- `tests/integration/test_cde_organize_agent_docs_tool.py` 🆕 (+120 lines)

**Acceptance Criteria**:
```python
def test_organize_agent_docs_dry_run():
    result = cde_organizeAgentDocs(dry_run=True)
    data = json.loads(result)

    assert "actions_planned" in data
    assert len(data["actions_planned"]) > 0
    assert data["violations_found"] >= 0

def test_organize_agent_docs_execute():
    result = cde_organizeAgentDocs(dry_run=False, preserve_git_history=True)
    data = json.loads(result)

    assert data["status"] == "completed"
    assert len(data["actions_completed"]) > 0
```

---

### Phase 4: Add `cde_createSpec` (Week 4)

**Priority**: 🟢 MEDIUM

**Tasks**:
1. Create `Specification` domain entity (if not in Phase 3)
2. Create `CreateSpecificationUseCase`
3. Add `cde_createSpec` MCP tool
4. Implement slug generation
5. Implement metadata auto-generation
6. Add spec template system
7. Write tests

**Files**:
- `src/cde_orchestrator/application/documentation/create_specification_use_case.py` 🆕 (+180 lines)
- `src/server.py` (+35 lines - new tool)
- `tests/unit/application/test_create_specification.py` 🆕 (+160 lines)

**Acceptance Criteria**:
```python
def test_create_spec():
    result = cde_createSpec(
        title="Redis Caching",
        spec_type="design",
        content="## Problem\n..."
    )
    data = json.loads(result)

    assert data["spec_id"] == "redis-caching"
    assert Path(data["file_path"]).exists()
    assert data["validation"]["governance"] == "passed"
```

---

### Phase 5: Documentation & Training (Week 5)

**Priority**: 🟢 MEDIUM

**Tasks**:
1. Update `specs/api/mcp-tools.md` with new tools
2. Update `AGENTS.md` with usage examples
3. Update `.github/copilot-instructions.md`
4. Create `docs/documentation-management-guide.md`
5. Add examples to `specs/templates/`

**Files**:
- `specs/api/mcp-tools.md` (+150 lines)
- `AGENTS.md` (+80 lines)
- `.github/copilot-instructions.md` (+60 lines)
- `docs/documentation-management-guide.md` 🆕 (+250 lines)

---

## 🎯 Expected Benefits

### For AI Agents

1. ✅ **Automated Cleanup**: `cde_organizeAgentDocs` handles post-session cleanup
2. ✅ **Professional Specs**: `cde_createSpec` guides Spec-Kit creation
3. ✅ **Clear Contracts**: Gateway interfaces document filesystem/Git operations
4. ✅ **Better Testing**: Mock gateways for rapid testing

### For Developers

1. ✅ **Testability**: Gateway pattern enables fast unit tests
2. ✅ **Isolation**: Domain logic separated from infrastructure
3. ✅ **Flexibility**: Easy to swap filesystem implementations (cloud storage, etc.)
4. ✅ **Clarity**: Explicit contracts for external systems

### For Project

1. ✅ **Governance Enforcement**: Automated compliance checking
2. ✅ **Consistency**: Professional specs follow Spec-Kit conventions
3. ✅ **History Preservation**: Git history maintained during cleanup
4. ✅ **Maintainability**: Hexagonal architecture improves long-term health

---

## 🚀 Next Steps

### Immediate Actions (This Week)

1. **Review this analysis** with team
2. **Prioritize phases** (I recommend Phase 1 → Phase 3 → Phase 2 → Phase 4 → Phase 5)
3. **Create GitHub issues** for each phase
4. **Start Phase 1** (Gateway infrastructure)

### Questions for Human Decision

1. **Priority**: Should we implement `cde_organizeAgentDocs` before `cde_createSpec`?
2. **Scope**: Should `cde_publishDocuments` replace `cde_publishOnboarding` or coexist?
3. **Testing**: Should we write integration tests against real projects or synthetic examples?
4. **Migration**: How to migrate existing onboarding flow to use gateways?

---

## 📚 References

### External Sources

1. **Martin Fowler - Gateway Pattern**
   https://www.martinfowler.com/articles/gateway-pattern.html
   - Explains Gateway pattern for isolating external systems
   - Provides TypeScript examples with test doubles
   - Discusses when to use Gateway vs Adapter/Facade

### Internal Documentation

1. **Hexagonal Architecture**
   `specs/design/ARCHITECTURE.md` (Lines 1-1400)
   - Current architecture overview
   - Dependency rules (inward only)

2. **Documentation Governance**
   `specs/governance/DOCUMENTATION_GOVERNANCE.md`
   - Agent-docs structure rules
   - Metadata requirements
   - Auto-archive policy (90 days)

3. **MCP Tools API**
   `specs/api/mcp-tools.md`
   - Current tool documentation
   - Usage patterns

4. **Agent Instructions**
   `AGENTS.md`, `.github/copilot-instructions.md`
   - How agents should use MCP tools
   - Workflow patterns

---

## ✍️ Author Notes

**Generated by**: GitHub Copilot
**Date**: 2025-11-03
**Context**: User request for hexagonal architecture improvements to documentation management
**Research Duration**: 45 minutes (web research + code analysis)
**Confidence**: High (based on established patterns + current codebase analysis)

**Key Insight**: The missing piece is not tool consolidation, but rather:
1. **Gateway pattern** for external system isolation
2. **`cde_organizeAgentDocs`** for automated governance enforcement
3. **`cde_createSpec`** for professional specification creation

These additions align with hexagonal architecture principles and fill real gaps in the current MCP tool surface.
