---
title: "Documentation Architecture Research: LLM-First Approach"
description: "Comprehensive research on applying hexagonal architecture patterns to documentation with an LLM-first evolution strategy"
type: "research"
status: "active"
created: "2025-11-01"
updated: "2025-11-01"
author: "GitHub Copilot"
llm_summary: |
  Research investigating how to apply hexagonal architecture principles to documentation
  management, evolving the pattern for LLM-first development. Includes analysis of modern
  approaches, industry patterns, and actionable migration strategy for CDE Orchestrator MCP.
---

# Documentation Architecture Research: LLM-First Approach for CDE Orchestrator MCP

## Executive Summary

This research explores how to apply **hexagonal architecture principles to documentation** while evolving toward an **LLM-first paradigm**. The goal is to create a unified, agent-friendly approach where:

1. **Documentation becomes a first-class domain concern** (not an afterthought)
2. **AI agents can discover, navigate, and contribute** to documentation seamlessly
3. **The architecture pattern itself adapts for LLM consumption** (metadata-rich, semantic)
4. **Migration tools enable existing projects** to adopt this approach systematically

---

## Table of Contents

1. [Research Context](#research-context)
2. [Key Findings](#key-findings)
3. [Hexagonal Architecture for Documentation](#hexagonal-architecture-for-documentation)
4. [LLM-First Architecture Evolution](#llm-first-architecture-evolution)
5. [Modern Patterns Analysis](#modern-patterns-analysis)
6. [Proposed Architecture](#proposed-architecture)
7. [Migration Strategy](#migration-strategy)
8. [Implementation Plan](#implementation-plan)
9. [References](#references)

---

## Research Context

### Problem Statement

CDE Orchestrator MCP needs to:
- **Align existing projects** to a robust architecture pattern for AI agent management
- **Apply hexagonal architecture** not just to code, but to **documentation as a domain**
- **Evolve continuously** using LLM-first principles (self-documenting, agent-readable)
- **Enable migration tools** (MCP tools) to onboard legacy projects

### Current State

**Documentation Governance (2025-11-01):**
- ✅ Directory structure defined (`specs/`, `docs/`, `agent-docs/`)
- ✅ Metadata requirements (YAML frontmatter)
- ✅ Pre-commit validation hooks
- ❌ **NOT** treated as a domain layer in hexagonal architecture
- ❌ **NO** semantic discovery layer for LLMs
- ❌ **NO** versioning or dependency tracking between docs

**Code Architecture:**
- ✅ Hexagonal architecture foundation (Domain, Application, Adapters)
- ✅ Port interfaces defined (`IProjectRepository`, `ICodeExecutor`)
- 🔄 In Progress: Use cases, adapters implementation

---

## Key Findings

### 1. Hexagonal Architecture is Universally Applicable

**Source:** [Herberto Graça's "Explicit Architecture"](https://herbertograca.com/2017/11/16/explicit-architecture-01-ddd-hexagonal-onion-clean-cqrs-how-i-put-it-all-together/)

> **Core Principle:** "Dependencies point INWARD. Domain logic is independent of infrastructure."

**Applied to Documentation:**
```
┌──────────────────────────────────────┐
│   Documentation Domain (Core)       │
│  - Specification entities            │
│  - Knowledge models                  │
│  - Semantic relationships            │
└──────────┬───────────────────────────┘
           │
┌──────────▼───────────────────────────┐
│   Documentation Application Layer    │
│  - Generate spec use case            │
│  - Link docs use case                │
│  - Validate metadata use case        │
└──────────┬───────────────────────────┘
           │
┌──────────▼───────────────────────────┐
│   Documentation Adapters             │
│  - Markdown adapter                  │
│  - PDF generator adapter             │
│  - LLM context adapter (NEW)         │
│  - Vector DB adapter (NEW)           │
└──────────────────────────────────────┘
```

**Key Insight:** Documentation should NOT depend on Markdown. Markdown is just one **adapter** for rendering knowledge.

---

### 2. Domain-Oriented Observability Applies to Docs

**Source:** [Martin Fowler - Domain-Oriented Observability](https://martinfowler.com/articles/domain-oriented-observability.html)

> **Pattern:** "Domain Probes enable observability at the domain level, not just technical instrumentation."

**Applied to Documentation:**
- **Domain Probe for Docs:** `DocumentationInstrumentation`
  - Tracks: `documentCreated`, `linkEstablished`, `metadataValidated`
  - Consumers: Markdown files, vector DB, LLM context providers

```python
# Domain Layer
class Specification:
    def establish_link(self, target: 'Specification') -> None:
        if not self.can_link_to(target):
            raise ValueError("Invalid semantic link")
        self.links.append(target)
        self.instrumentation.linkEstablished(self, target)

# Application Layer
class LinkDocumentsUseCase:
    def execute(self, source_id: str, target_id: str) -> Dict:
        source = self.repo.get_by_id(source_id)
        target = self.repo.get_by_id(target_id)
        source.establish_link(target)
        self.repo.save(source)
```

**Key Insight:** Documentation changes are **domain events**, not file I/O operations.

---

### 3. LLM-First Architecture Requires Semantic Ports

**Source:** [GitHub Blog - AI Code Generation](https://github.blog/2024-01-22-how-ai-code-generation-works/)

> **Reality:** "LLMs benefit from explicit comments, clear variable names, and structured context."

**Applied to Architecture:**
- **New Port:** `ISemanticContext` (provides LLM-optimized context)
- **Adapters:**
  - `OpenAIContextAdapter` (formats for GPT-4)
  - `ClaudeContextAdapter` (formats for Claude)
  - `CopilotContextAdapter` (formats for GitHub Copilot Skills)

```python
# Domain Port
class ISemanticContext(ABC):
    @abstractmethod
    def get_context_for_task(self, task: Task) -> Dict[str, Any]:
        """Returns LLM-optimized context for a given task."""
        pass

# Adapter
class OpenAIContextAdapter(ISemanticContext):
    def get_context_for_task(self, task: Task) -> Dict[str, Any]:
        return {
            "system": self._build_system_prompt(task),
            "context": self._get_relevant_specs(task),
            "examples": self._get_code_examples(task),
            "constraints": self._get_architectural_rules(task)
        }
```

**Key Insight:** LLMs need **semantic ports**, not just data ports.

---

### 4. Documentation as Code ≠ Documentation as Domain

**Source:** [Alistair Cockburn - Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)

> **Misconception:** "Documentation in Markdown files in `/docs`" = treating docs as infrastructure.

**Reality Check:**
- ❌ **Docs as Code:** Documentation files stored alongside code (Markdown adapter)
- ✅ **Docs as Domain:** Knowledge entities with relationships, versioning, semantic links

**Example:**
```python
# ❌ WRONG: Documentation as infrastructure
def create_feature_spec(feature_name: str) -> None:
    markdown_file = f"specs/features/{feature_name}.md"
    write_file(markdown_file, template)  # Tight coupling to Markdown

# ✅ CORRECT: Documentation as domain
class CreateFeatureSpecUseCase:
    def execute(self, feature_name: str) -> Specification:
        spec = Specification.create(
            title=feature_name,
            type=SpecType.FEATURE,
            author=self.context.current_user
        )
        self.repo.save(spec)  # Repo handles persistence
        self.instrumentation.specCreated(spec)
        return spec
```

**Key Insight:** Markdown is an **adapter**, not the domain model.

---

## Hexagonal Architecture for Documentation

### Documentation Domain Layer

**Entities:**
```python
from enum import Enum
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field

class DocumentType(Enum):
    FEATURE = "feature"
    DESIGN = "design"
    TASK = "task"
    GUIDE = "guide"
    GOVERNANCE = "governance"
    SESSION = "session"
    EXECUTION = "execution"
    FEEDBACK = "feedback"
    RESEARCH = "research"

class DocumentStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

@dataclass
class Specification:
    """Domain entity for specifications."""
    id: str
    title: str
    description: str
    type: DocumentType
    status: DocumentStatus
    created: datetime
    updated: datetime
    author: str
    content: str  # Domain content (NOT Markdown)
    metadata: Dict[str, any] = field(default_factory=dict)
    links: List['Specification'] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def establish_link(self, target: 'Specification', relationship: str) -> None:
        """Business rule: Validate semantic link."""
        if self.status == DocumentStatus.ARCHIVED:
            raise ValueError("Cannot link archived specifications")
        self.links.append((target, relationship))

    def deprecate(self, reason: str, successor: Optional['Specification'] = None) -> None:
        """Business rule: Deprecation requires reason and optional successor."""
        self.status = DocumentStatus.DEPRECATED
        self.metadata['deprecation_reason'] = reason
        if successor:
            self.establish_link(successor, "superseded_by")
```

**Value Objects:**
```python
@dataclass(frozen=True)
class SemanticLink:
    """Value object for semantic relationships between docs."""
    source_id: str
    target_id: str
    relationship: str  # "references", "supersedes", "implements", "documents"
    created: datetime

@dataclass(frozen=True)
class LLMContext:
    """Value object for LLM-optimized context."""
    summary: str  # 2-3 sentence summary
    key_concepts: List[str]
    code_examples: List[str]
    related_specs: List[str]
    constraints: List[str]
```

### Documentation Application Layer

**Use Cases:**
```python
class CreateSpecificationUseCase:
    """Create a new specification in the system."""

    def __init__(
        self,
        repo: ISpecificationRepository,
        instrumentation: DocumentationInstrumentation
    ):
        self.repo = repo
        self.instrumentation = instrumentation

    def execute(self, input_data: Dict) -> Specification:
        spec = Specification.create(
            title=input_data["title"],
            type=DocumentType[input_data["type"].upper()],
            author=input_data["author"],
            content=input_data["content"]
        )

        self.repo.save(spec)
        self.instrumentation.specificationCreated(spec)

        return spec

class LinkSpecificationsUseCase:
    """Establish semantic link between two specifications."""

    def execute(self, source_id: str, target_id: str, relationship: str) -> None:
        source = self.repo.get_by_id(source_id)
        target = self.repo.get_by_id(target_id)

        source.establish_link(target, relationship)
        self.repo.save(source)

        self.instrumentation.linkEstablished(source, target, relationship)

class GetLLMContextUseCase:
    """Generate LLM-optimized context for a specification."""

    def execute(self, spec_id: str, task_type: str) -> LLMContext:
        spec = self.repo.get_by_id(spec_id)
        related = self.repo.get_related(spec_id)

        return LLMContext(
            summary=spec.metadata.get("llm_summary", spec.description),
            key_concepts=self._extract_concepts(spec),
            code_examples=self._get_examples(spec),
            related_specs=[r.id for r in related],
            constraints=self._get_constraints(spec, task_type)
        )
```

### Documentation Adapters

**Port Interface:**
```python
class ISpecificationRepository(ABC):
    """Port for specification persistence."""

    @abstractmethod
    def save(self, spec: Specification) -> None:
        pass

    @abstractmethod
    def get_by_id(self, spec_id: str) -> Specification:
        pass

    @abstractmethod
    def get_related(self, spec_id: str) -> List[Specification]:
        pass

    @abstractmethod
    def search_semantic(self, query: str) -> List[Specification]:
        pass

class IDocumentationRenderer(ABC):
    """Port for rendering documentation."""

    @abstractmethod
    def render(self, spec: Specification) -> str:
        pass
```

**Adapters:**
```python
class MarkdownSpecificationRepository(ISpecificationRepository):
    """Adapter: Persist specs as Markdown files."""

    def save(self, spec: Specification) -> None:
        path = self._get_path_for_type(spec.type)
        filepath = path / f"{spec.id}.md"

        markdown_content = self._to_markdown(spec)
        filepath.write_text(markdown_content)

    def _to_markdown(self, spec: Specification) -> str:
        return f"""---
title: "{spec.title}"
description: "{spec.description}"
type: "{spec.type.value}"
status: "{spec.status.value}"
created: "{spec.created.isoformat()}"
updated: "{spec.updated.isoformat()}"
author: "{spec.author}"
---

# {spec.title}

{spec.content}
"""

class VectorDBSpecificationRepository(ISpecificationRepository):
    """Adapter: Store specs in vector database for semantic search."""

    def __init__(self, vector_db: VectorDB):
        self.vector_db = vector_db

    def save(self, spec: Specification) -> None:
        embedding = self._generate_embedding(spec)
        self.vector_db.upsert(
            id=spec.id,
            embedding=embedding,
            metadata={
                "title": spec.title,
                "type": spec.type.value,
                "content": spec.content
            }
        )

    def search_semantic(self, query: str) -> List[Specification]:
        query_embedding = self._generate_embedding_from_text(query)
        results = self.vector_db.search(query_embedding, top_k=10)
        return [self._from_metadata(r) for r in results]

class OpenAIContextAdapter(ISemanticContext):
    """Adapter: Format context for OpenAI API."""

    def get_context_for_task(self, task: Task) -> Dict[str, Any]:
        specs = self.repo.get_related_to_task(task.id)

        return {
            "system_prompt": self._build_system_prompt(task),
            "context_documents": [
                {
                    "title": spec.title,
                    "summary": spec.metadata.get("llm_summary"),
                    "key_points": self._extract_key_points(spec)
                }
                for spec in specs
            ],
            "code_examples": self._get_code_examples(specs),
            "architectural_constraints": self._get_constraints(specs)
        }
```

---

## LLM-First Architecture Evolution

### Key Principles

1. **Explicit over Implicit:** All architectural decisions documented as domain entities
2. **Semantic Discovery:** LLMs can query "What are the coding standards?" via MCP tools
3. **Context-Aware:** Documentation adapts based on task type (feature dev, refactor, debug)
4. **Self-Improving:** Feedback loops from LLM interactions improve documentation

### LLM-First Enhancements

#### 1. Semantic Metadata (Enhanced YAML Frontmatter)

```yaml
---
title: "Feature: Multi-Project Support"
description: "Specification for managing 1000+ projects"
type: "feature"
status: "active"
created: "2025-11-01"
updated: "2025-11-01"
author: "Alice Developer"

# LLM-First Enhancements
llm_summary: |
  Enables CDE to work with unlimited projects. Agent knows context, CDE validates/executes.
  Stateless approach: no registries, just path validation.

key_concepts:
  - "Stateless multi-project management"
  - "Path-based project resolution"
  - "Per-project state isolation"

code_examples:
  - path: "src/cde_orchestrator/application/start_feature_use_case.py"
    lines: "15-30"
    description: "Project resolution via locator"

architectural_constraints:
  - "Domain layer MUST NOT import project_locator directly"
  - "Use IProjectLocator port interface"
  - "All MCP tools accept project_path or project_name"

related_documents:
  - id: "architecture-hexagonal"
    relationship: "implements"
  - id: "task-multi-project-discovery"
    relationship: "decomposes_into"

tags:
  - "multi-project"
  - "architecture"
  - "core-feature"
---
```

#### 2. Semantic Query Language for LLMs

**MCP Tool: `cde_queryDocumentation`**
```python
def cde_queryDocumentation(
    query: str,
    context: Optional[str] = None,
    include_examples: bool = True
) -> str:
    """
    Semantic search across all documentation.

    Args:
        query: Natural language question (e.g., "How do I add a new use case?")
        context: Optional context (e.g., "implementing authentication")
        include_examples: Include code examples in response

    Returns:
        JSON with relevant specs, examples, and constraints
    """
    use_case = GetLLMContextUseCase(vector_repo, semantic_search)
    results = use_case.execute(query, context)

    return json.dumps({
        "summary": results.summary,
        "relevant_specs": [
            {
                "id": spec.id,
                "title": spec.title,
                "relevance": spec.score,
                "key_points": spec.key_points
            }
            for spec in results.specs
        ],
        "code_examples": results.examples if include_examples else [],
        "constraints": results.constraints
    })
```

#### 3. Feedback Loop: LLM Interactions Improve Docs

```python
class DocumentFeedbackUseCase:
    """Capture LLM interactions to improve documentation."""

    def record_query(self, query: str, results: List[Specification], useful: bool):
        """Track which docs were useful for which queries."""
        self.analytics.track_query(
            query=query,
            results=[r.id for r in results],
            useful=useful
        )

        # If not useful, flag for improvement
        if not useful:
            for spec in results:
                spec.metadata['needs_improvement'] = True
                spec.metadata['improvement_context'] = query
                self.repo.save(spec)

class AutoGenerateLLMSummaryUseCase:
    """Use LLM to generate llm_summary for existing docs."""

    def execute(self, spec_id: str) -> str:
        spec = self.repo.get_by_id(spec_id)

        if "llm_summary" in spec.metadata:
            return spec.metadata["llm_summary"]

        # Use LLM to generate summary
        summary = self.llm.generate_summary(
            content=spec.content,
            context=f"This is a {spec.type.value} specification."
        )

        spec.metadata["llm_summary"] = summary
        self.repo.save(spec)

        return summary
```

---

## Modern Patterns Analysis

### Patterns from Industry Leaders

#### 1. GitHub Copilot's Approach

**Key Insight:** "Copilot benefits from explicit comments and clear names."

**Applied:**
- All domain methods have docstrings with:
  - Purpose (what it does)
  - Business rules (why it exists)
  - Examples (how to use)

```python
class Project:
    def start_feature(self, prompt: str) -> Feature:
        """
        Start a new feature in this project.

        Business Rule: Project must be in ACTIVE status.

        Args:
            prompt: User's feature description (10-5000 chars)

        Returns:
            Feature entity in DEFINING phase

        Raises:
            InvalidStateTransitionError: If project not active

        Example:
            >>> project = Project.create("MyApp", "/path/to/app")
            >>> project.activate()
            >>> feature = project.start_feature("Add login")
        """
        if self.status != ProjectStatus.ACTIVE:
            raise InvalidStateTransitionError("Project must be active")
        return Feature.create(self.id, prompt)
```

#### 2. Fowler's Domain-Oriented Observability

**Key Insight:** "Domain Probes keep instrumentation at domain level."

**Applied to Documentation:**
```python
class DocumentationInstrumentation:
    """Domain Probe for documentation events."""

    def specificationCreated(self, spec: Specification):
        self.logger.info(f"Specification created: {spec.title}")
        self.metrics.increment("specs.created", tags={"type": spec.type.value})
        self.analytics.track("Specification Created", {
            "spec_id": spec.id,
            "type": spec.type.value,
            "author": spec.author
        })

    def linkEstablished(self, source: Specification, target: Specification, rel: str):
        self.logger.info(f"Link: {source.title} -> {target.title} ({rel})")
        self.metrics.increment("specs.linked", tags={"relationship": rel})

        # Track semantic graph for analytics
        self.graph_db.add_edge(
            source=source.id,
            target=target.id,
            relationship=rel
        )
```

#### 3. Cockburn's Hexagonal Architecture

**Key Insight:** "Ports on all sides, adapters plug in."

**Applied:**
```
         ┌─────────────────────┐
         │   Documentation     │
      ┌─▶│      Domain        │◀─┐
      │  └─────────────────────┘  │
      │                            │
┌─────┴──────┐            ┌───────┴─────┐
│ Primary    │            │ Secondary   │
│ Ports      │            │ Ports       │
│            │            │             │
│ - Create   │            │ - Persist   │
│ - Link     │            │ - Search    │
│ - Query    │            │ - Render    │
└─────┬──────┘            └───────┬─────┘
      │                            │
┌─────▼──────┐            ┌───────▼─────┐
│ Primary    │            │ Secondary   │
│ Adapters   │            │ Adapters    │
│            │            │             │
│ - MCP Tools│            │ - Markdown  │
│ - CLI Cmds │            │ - Vector DB │
│ - Web UI   │            │ - PDF Gen   │
└────────────┘            └─────────────┘
```

---

## Proposed Architecture

### Complete Documentation System

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Tools Layer                      │
│  - cde_createSpec(title, type, content)                 │
│  - cde_linkSpecs(source_id, target_id, relationship)    │
│  - cde_queryDocumentation(query, context)               │
│  - cde_generateLLMContext(spec_id, task_type)           │
└──────────────┬──────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────┐
│            Application Layer (Use Cases)                │
│  - CreateSpecificationUseCase                           │
│  - LinkSpecificationsUseCase                            │
│  - GetLLMContextUseCase                                 │
│  - MigrateProjectToSpecsUseCase  ← NEW                 │
└──────────────┬──────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────┐
│                  Domain Layer                           │
│  Entities:                                              │
│    - Specification (title, content, metadata, links)    │
│    - SemanticLink (source, target, relationship)        │
│  Value Objects:                                         │
│    - LLMContext (summary, concepts, examples)           │
│  Ports:                                                 │
│    - ISpecificationRepository                           │
│    - ISemanticContext                                   │
│    - IDocumentationRenderer                             │
└──────────────┬──────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────┐
│              Adapters Layer                             │
│  Persistence:                                           │
│    - MarkdownSpecificationRepository                    │
│    - VectorDBSpecificationRepository                    │
│  Rendering:                                             │
│    - MarkdownRenderer                                   │
│    - PDFRenderer                                        │
│    - HTMLRenderer                                       │
│  LLM Context:                                           │
│    - OpenAIContextAdapter                               │
│    - ClaudeContextAdapter                               │
│    - CopilotSkillsAdapter  ← NEW                       │
└─────────────────────────────────────────────────────────┘
```

---

## Migration Strategy

### Phase 1: Foundation (Week 1-2)

**Goal:** Establish domain layer for documentation

**Tasks:**
1. Create `src/cde_orchestrator/domain/documentation/` module
   - `entities.py` (Specification, DocumentType, DocumentStatus)
   - `ports.py` (ISpecificationRepository, ISemanticContext)
   - `exceptions.py` (DocumentationError, InvalidLinkError)

2. Implement basic repository adapter
   - `MarkdownSpecificationRepository` (read/write existing specs)

3. Write unit tests
   - Test Specification entity business rules
   - Test repository adapter

**Acceptance Criteria:**
```python
def test_specification_entity():
    spec = Specification.create(
        title="Test Feature",
        type=DocumentType.FEATURE,
        author="Alice"
    )
    assert spec.status == DocumentStatus.DRAFT

    spec.activate()
    assert spec.status == DocumentStatus.ACTIVE
```

---

### Phase 2: Application Layer (Week 3-4)

**Goal:** Use cases for documentation operations

**Tasks:**
1. Create `src/cde_orchestrator/application/documentation/` module
   - `create_specification_use_case.py`
   - `link_specifications_use_case.py`
   - `get_llm_context_use_case.py`

2. Update `DIContainer` to wire documentation dependencies

3. Write integration tests

**Acceptance Criteria:**
```python
def test_create_specification_use_case():
    container = DIContainer.create_default()
    use_case = container.get_create_specification_use_case()

    result = use_case.execute({
        "title": "New Feature",
        "type": "feature",
        "author": "Alice",
        "content": "Feature description..."
    })

    assert result["status"] == "success"
    assert result["spec_id"] is not None
```

---

### Phase 3: MCP Tools (Week 5-6)

**Goal:** Expose documentation operations via MCP

**Tasks:**
1. Add MCP tools to `src/server.py`:
   ```python
   @server.tool()
   def cde_createSpec(
       title: str,
       type: str,
       content: str,
       author: Optional[str] = None
   ) -> str:
       """Create new specification in CDE system."""
       use_case = container.get_create_specification_use_case()
       result = use_case.execute({
           "title": title,
           "type": type,
           "content": content,
           "author": author or "unknown"
       })
       return json.dumps(result)
   ```

2. Document MCP tools in `specs/api/mcp-tools-documentation.md`

3. Test with Claude/Copilot

**Acceptance Criteria:**
- AI agent can create/link specs via MCP tools
- Tools return structured JSON
- Error handling with clear messages

---

### Phase 4: Semantic Search (Week 7-8)

**Goal:** Enable LLM to query documentation semantically

**Tasks:**
1. Implement `VectorDBSpecificationRepository` adapter
   - Use ChromaDB or similar
   - Generate embeddings for specs

2. Create `GetLLMContextUseCase`
   - Given task, return relevant specs
   - Include code examples, constraints

3. Add `cde_queryDocumentation` MCP tool

**Acceptance Criteria:**
```python
# Agent can ask natural language questions
result = cde_queryDocumentation(
    query="How do I add a new use case?",
    context="implementing authentication",
    include_examples=True
)

# Returns:
{
  "summary": "Use cases belong in application layer...",
  "relevant_specs": [
    {"id": "architecture", "title": "Hexagonal Architecture", ...},
    {"id": "coding-standards", "title": "Use Case Patterns", ...}
  ],
  "code_examples": [
    {"path": "src/.../start_feature_use_case.py", "lines": "10-30", ...}
  ],
  "constraints": [
    "Use cases MUST NOT import adapters directly",
    "Use dependency injection for ports"
  ]
}
```

---

### Phase 5: Migration Automation (Week 9-10)

**Goal:** Tool to migrate existing projects to Spec-Kit

**Tasks:**
1. Create `MigrateProjectToSpecsUseCase`
   - Scan project for docs
   - Extract metadata from existing files
   - Create Specification entities
   - Link related specs

2. Add `cde_migrateProject` MCP tool:
   ```python
   @server.tool()
   def cde_migrateProject(
       project_path: str,
       scan_subdirs: bool = True
   ) -> str:
       """
       Migrate existing project to Spec-Kit documentation structure.

       - Scans for .md files
       - Extracts/generates metadata
       - Creates semantic links
       - Validates against governance rules
       """
       use_case = container.get_migrate_project_use_case()
       result = use_case.execute({
           "project_path": project_path,
           "scan_subdirs": scan_subdirs
       })
       return json.dumps(result)
   ```

3. Test on real projects

**Acceptance Criteria:**
- Can migrate existing CDE project
- Generates valid YAML frontmatter
- Establishes semantic links
- Reports validation errors

---

### Phase 6: LLM Feedback Loop (Week 11-12)

**Goal:** Self-improving documentation based on LLM usage

**Tasks:**
1. Implement `DocumentFeedbackUseCase`
   - Track which specs used for which queries
   - Flag specs that didn't help

2. Create `AutoGenerateLLMSummaryUseCase`
   - Use LLM to generate `llm_summary` for specs without one

3. Add analytics dashboard (optional)

**Acceptance Criteria:**
- LLM queries tracked in analytics
- Specs flagged for improvement
- Auto-generated summaries validated

---

## Implementation Plan

### Immediate Actions (This Week)

1. **Create Domain Layer Skeleton**
   ```bash
   mkdir -p src/cde_orchestrator/domain/documentation
   touch src/cde_orchestrator/domain/documentation/__init__.py
   touch src/cde_orchestrator/domain/documentation/entities.py
   touch src/cde_orchestrator/domain/documentation/ports.py
   touch src/cde_orchestrator/domain/documentation/exceptions.py
   ```

2. **Define Specification Entity**
   - Implement in `entities.py`
   - Write unit tests in `tests/unit/domain/test_specification.py`

3. **Define Port Interfaces**
   - `ISpecificationRepository`
   - `ISemanticContext`
   - `IDocumentationRenderer`

### Next Sprint (Week 2-4)

1. **Implement Markdown Adapter**
   - `MarkdownSpecificationRepository`
   - Read/write existing specs
   - Preserve YAML frontmatter

2. **Create Use Cases**
   - `CreateSpecificationUseCase`
   - `LinkSpecificationsUseCase`

3. **Wire with DI Container**

### Next Month (Week 5-8)

1. **Add MCP Tools**
   - `cde_createSpec`
   - `cde_linkSpecs`
   - `cde_queryDocumentation`

2. **Implement Vector Search**
   - `VectorDBSpecificationRepository`
   - Semantic search use case

### Next Quarter (Week 9-12)

1. **Migration Automation**
   - `cde_migrateProject` tool
   - Test on CDE project

2. **Feedback Loop**
   - Track LLM queries
   - Auto-generate summaries

---

## Metrics for Success

### Technical Metrics

1. **Code Quality:**
   - ✅ 80% test coverage (domain + application layers)
   - ✅ 0 cyclomatic complexity > 10
   - ✅ All domain methods have docstrings

2. **Architecture Compliance:**
   - ✅ No domain imports from adapters
   - ✅ All use cases use DI
   - ✅ Ports defined for all external dependencies

3. **Documentation Quality:**
   - ✅ 100% specs have valid YAML frontmatter
   - ✅ 90% specs have `llm_summary`
   - ✅ Semantic links validated

### Business Metrics

1. **LLM Efficiency:**
   - 🎯 50% reduction in "documentation not found" queries
   - 🎯 80% of LLM queries return useful results
   - 🎯 30% faster onboarding for new projects

2. **Developer Experience:**
   - 🎯 Developers can ask "How do I...?" and get code examples
   - 🎯 AI agents can discover architectural constraints
   - 🎯 Migration tool onboards projects in <5 minutes

---

## References

### Academic & Industry Papers

1. **Cockburn, A. (2005)** - "Hexagonal Architecture (Ports & Adapters)"
   - Original pattern: https://alistair.cockburn.us/hexagonal-architecture/

2. **Graça, H. (2017)** - "DDD, Hexagonal, Onion, Clean, CQRS... How I put it all together"
   - Explicit Architecture: https://herbertograca.com/

3. **Fowler, M. (2019)** - "Domain-Oriented Observability"
   - Domain Probes pattern: https://martinfowler.com/articles/domain-oriented-observability.html

### Modern AI Development

4. **GitHub Blog (2024)** - "How AI Code Generation Works"
   - LLM-first principles: https://github.blog/2024-01-22-how-ai-code-generation-works/

5. **OpenAI (2024)** - "Best Practices for Prompt Engineering"
   - Context optimization: https://platform.openai.com/docs/guides/prompt-engineering

### Existing CDE Documentation

6. **CDE Constitution** - `memory/constitution.md`
   - Project values, decision-making

7. **Documentation Governance** - `specs/governance/DOCUMENTATION_GOVERNANCE.md`
   - Current rules, pre-commit hooks

8. **Architecture Spec** - `specs/design/ARCHITECTURE.md`
   - Hexagonal architecture implementation

---

## Conclusion

### Summary of Proposal

1. **Apply Hexagonal Architecture to Documentation:**
   - Treat documentation as a **domain layer** (not infrastructure)
   - Use **ports & adapters** (Markdown is one adapter, not the only one)
   - Enable **semantic search** for LLMs via vector DB adapter

2. **Evolve to LLM-First:**
   - Add `llm_summary` to all specs (2-3 sentence optimized for AI)
   - Expose **semantic query tools** via MCP (`cde_queryDocumentation`)
   - Implement **feedback loops** (track what docs help LLMs)

3. **Enable Migration:**
   - Create `cde_migrateProject` tool to onboard existing projects
   - Validate against governance rules
   - Generate missing metadata

### Next Steps

1. **Review this research document** with team
2. **Create GitHub issue** for "Documentation as Domain Layer" epic
3. **Start Phase 1 implementation** (Domain layer skeleton)
4. **Schedule architecture review** (validate ports & adapters)

### Long-Term Vision

**In 6 months:**
- CDE Orchestrator MCP has a **semantic documentation layer**
- AI agents can **discover**, **query**, and **contribute** to docs
- Existing projects can **migrate** to this pattern in <5 minutes
- Documentation **self-improves** based on LLM feedback

**In 1 year:**
- **Industry-leading LLM-first architecture** pattern
- **Open-source the pattern** as a reusable library
- **Publish case study** on GitHub blog or InfoQ

---

## Appendix A: Code Examples

### Complete Specification Entity

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Optional
import uuid

class DocumentType(Enum):
    FEATURE = "feature"
    DESIGN = "design"
    TASK = "task"
    GUIDE = "guide"
    GOVERNANCE = "governance"

class DocumentStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

@dataclass
class Specification:
    """
    Domain entity representing a specification document.

    Business Rules:
    - ID is immutable (generated on creation)
    - Cannot link to archived specs
    - Deprecation requires reason
    - Status transitions have constraints
    """
    id: str
    title: str
    description: str
    type: DocumentType
    status: DocumentStatus
    created: datetime
    updated: datetime
    author: str
    content: str
    metadata: Dict[str, any] = field(default_factory=dict)
    links: List[tuple['Specification', str]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        title: str,
        type: DocumentType,
        author: str,
        content: str = "",
        description: str = ""
    ) -> 'Specification':
        """Factory method to create new specification."""
        now = datetime.now(timezone.utc)
        return cls(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            type=type,
            status=DocumentStatus.DRAFT,
            created=now,
            updated=now,
            author=author,
            content=content
        )

    def activate(self) -> None:
        """Transition from DRAFT to ACTIVE."""
        if self.status != DocumentStatus.DRAFT:
            raise ValueError(f"Cannot activate spec in {self.status} status")
        self.status = DocumentStatus.ACTIVE
        self.updated = datetime.now(timezone.utc)

    def deprecate(
        self,
        reason: str,
        successor: Optional['Specification'] = None
    ) -> None:
        """
        Mark specification as deprecated.

        Business Rule: Must provide reason and optionally a successor.
        """
        if self.status == DocumentStatus.ARCHIVED:
            raise ValueError("Cannot deprecate archived spec")

        self.status = DocumentStatus.DEPRECATED
        self.metadata['deprecation_reason'] = reason
        self.updated = datetime.now(timezone.utc)

        if successor:
            self.establish_link(successor, "superseded_by")

    def establish_link(
        self,
        target: 'Specification',
        relationship: str
    ) -> None:
        """
        Create semantic link to another specification.

        Business Rules:
        - Cannot link archived specs
        - Cannot link to self
        - Relationship must be valid type
        """
        if self.status == DocumentStatus.ARCHIVED:
            raise ValueError("Cannot link archived spec")

        if target.id == self.id:
            raise ValueError("Cannot link spec to itself")

        valid_relationships = {
            "references", "implements", "supersedes", "superseded_by",
            "documents", "decomposes_into", "depends_on"
        }

        if relationship not in valid_relationships:
            raise ValueError(f"Invalid relationship: {relationship}")

        self.links.append((target, relationship))
        self.updated = datetime.now(timezone.utc)

    def add_tag(self, tag: str) -> None:
        """Add a tag for categorization."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated = datetime.now(timezone.utc)

    def update_content(self, content: str) -> None:
        """Update specification content."""
        self.content = content
        self.updated = datetime.now(timezone.utc)
```

---

## Appendix B: Complete Use Case Example

```python
from typing import Dict, Any
from datetime import datetime
from ..domain.documentation.entities import Specification, DocumentType
from ..domain.documentation.ports import ISpecificationRepository
from ..domain.documentation.instrumentation import DocumentationInstrumentation

class CreateSpecificationUseCase:
    """
    Use case: Create a new specification in the system.

    Input: {
        "title": str,
        "type": str,  # "feature", "design", etc.
        "author": str,
        "content": str,
        "description": str (optional),
        "tags": List[str] (optional)
    }

    Output: {
        "status": "success" | "error",
        "spec_id": str,
        "message": str
    }

    Business Rules:
    - Title must be unique within type
    - Author must be valid
    - Content can be empty initially (DRAFT)
    """

    def __init__(
        self,
        repository: ISpecificationRepository,
        instrumentation: DocumentationInstrumentation
    ):
        self.repository = repository
        self.instrumentation = instrumentation

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the use case."""
        try:
            # Validate input
            self._validate_input(input_data)

            # Create domain entity
            spec = Specification.create(
                title=input_data["title"],
                type=DocumentType[input_data["type"].upper()],
                author=input_data["author"],
                content=input_data.get("content", ""),
                description=input_data.get("description", "")
            )

            # Add tags if provided
            for tag in input_data.get("tags", []):
                spec.add_tag(tag)

            # Persist
            self.repository.save(spec)

            # Instrument
            self.instrumentation.specificationCreated(spec)

            return {
                "status": "success",
                "spec_id": spec.id,
                "message": f"Specification '{spec.title}' created successfully"
            }

        except ValueError as e:
            return {
                "status": "error",
                "spec_id": None,
                "message": str(e)
            }

    def _validate_input(self, data: Dict[str, Any]) -> None:
        """Validate input data."""
        required_fields = ["title", "type", "author"]
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: {field}")

        # Validate type
        try:
            DocumentType[data["type"].upper()]
        except KeyError:
            raise ValueError(f"Invalid type: {data['type']}")

        # Check title uniqueness
        existing = self.repository.find_by_title(data["title"])
        if existing and existing.type.value == data["type"]:
            raise ValueError(f"Specification with title '{data['title']}' already exists")
```

---

**End of Research Document**

For questions or feedback, please contact the CDE Orchestrator team or open a GitHub issue.
