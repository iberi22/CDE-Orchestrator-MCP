---
title: "Documentation Architecture Migration Plan"
description: "Actionable roadmap to implement documentation as a domain layer with LLM-first principles"
type: "task"
status: "active"
created: "2025-11-01"
updated: "2025-11-01"
author: "GitHub Copilot"
llm_summary: |
  12-week plan to migrate CDE documentation to hexagonal architecture with
  LLM-first enhancements. Includes domain layer, use cases, MCP tools, semantic
  search, and migration automation.
---

# Documentation Architecture Migration Plan

**Related Research:** `agent-docs/research/documentation-architecture-llm-first-research.md`

---

## Vision Statement

Transform CDE documentation from static Markdown files into a **semantic, LLM-first domain layer** where:

- 🎯 **AI agents discover** architectural constraints via semantic queries
- 🎯 **Documentation validates itself** against governance rules
- 🎯 **Projects migrate automatically** to Spec-Kit with one MCP tool call
- 🎯 **Feedback loops improve** docs based on LLM usage patterns

---

## Success Metrics

### Technical

- ✅ 80% test coverage (domain + application)
- ✅ 0 cyclomatic complexity > 10
- ✅ 100% specs have valid YAML frontmatter
- ✅ 90% specs have `llm_summary`

### Business

- 🎯 50% reduction in "documentation not found" queries
- 🎯 80% of LLM queries return useful results
- 🎯 30% faster onboarding for new projects
- 🎯 Migration tool onboards projects in <5 minutes

---

## 12-Week Roadmap

### Phase 1: Foundation (Week 1-2)

**Goal:** Domain layer for documentation

#### Tasks

**TASK-DOC-001: Create Domain Module Structure**
- **Priority:** 🔴 CRITICAL | **Effort:** 1 day | **Status:** ⏸️

**Implementation:**
- [ ] SUB-01: Create directory structure
  ```bash
  mkdir -p src/cde_orchestrator/domain/documentation
  mkdir -p tests/unit/domain/documentation
  mkdir -p tests/integration/adapters/documentation
  ```

- [ ] SUB-02: Create `entities.py` with Specification entity
- [ ] SUB-03: Create `ports.py` with repository interfaces
- [ ] SUB-04: Create `exceptions.py` with domain exceptions

**Files Modified:**
- `src/cde_orchestrator/domain/documentation/__init__.py` (new)
- `src/cde_orchestrator/domain/documentation/entities.py` (new)
- `src/cde_orchestrator/domain/documentation/ports.py` (new)
- `src/cde_orchestrator/domain/documentation/exceptions.py` (new)

**Tests:**
- `tests/unit/domain/documentation/test_specification.py`

**Acceptance Criteria:**

```python
def test_specification_creation():
    spec = Specification.create(
        title="Test Feature",
        type=DocumentType.FEATURE,
        author="Alice"
    )
    assert spec.status == DocumentStatus.DRAFT
    assert spec.id is not None

def test_specification_activation():
    spec = Specification.create("Test", DocumentType.FEATURE, "Alice")
    spec.activate()
    assert spec.status == DocumentStatus.ACTIVE

def test_cannot_link_archived_spec():
    spec = Specification.create("Test", DocumentType.FEATURE, "Alice")
    spec.archive()

    target = Specification.create("Target", DocumentType.FEATURE, "Bob")

    with pytest.raises(ValueError, match="Cannot link archived"):
        spec.establish_link(target, "references")
```

---

**TASK-DOC-002: Implement Specification Entity**
- **Priority:** 🔴 CRITICAL | **Effort:** 2 days | **Status:** ⏸️

**Description:**
Core domain entity with business rules for specifications.

**Implementation:**
- [ ] SUB-01: Define DocumentType and DocumentStatus enums
- [ ] SUB-02: Implement Specification dataclass with business methods
- [ ] SUB-03: Add semantic link validation
- [ ] SUB-04: Implement status transitions (draft → active → deprecated)
- [ ] SUB-05: Write comprehensive unit tests

**Files Modified:**
- `src/cde_orchestrator/domain/documentation/entities.py` (+150 lines)

**Key Methods:**
```python
class Specification:
    @classmethod
    def create(...) -> 'Specification'  # Factory

    def activate() -> None  # DRAFT → ACTIVE
    def deprecate(reason, successor) -> None  # → DEPRECATED
    def archive() -> None  # → ARCHIVED

    def establish_link(target, relationship) -> None
    def add_tag(tag) -> None
    def update_content(content) -> None
```

**Tests:**
- `tests/unit/domain/documentation/test_specification.py` (+200 lines)

---

**TASK-DOC-003: Define Port Interfaces**
- **Priority:** 🔴 CRITICAL | **Effort:** 1 day | **Status:** ⏸️

**Description:**
Define contracts for adapters (repositories, renderers, context providers).

**Implementation:**
- [ ] SUB-01: Define `ISpecificationRepository` interface
- [ ] SUB-02: Define `ISemanticContext` interface
- [ ] SUB-03: Define `IDocumentationRenderer` interface
- [ ] SUB-04: Document port contracts in docstrings

**Files Modified:**
- `src/cde_orchestrator/domain/documentation/ports.py` (+80 lines)

**Port Interfaces:**
```python
class ISpecificationRepository(ABC):
    @abstractmethod
    def save(spec: Specification) -> None: ...

    @abstractmethod
    def get_by_id(spec_id: str) -> Specification: ...

    @abstractmethod
    def find_by_title(title: str) -> Optional[Specification]: ...

    @abstractmethod
    def get_related(spec_id: str) -> List[Specification]: ...

    @abstractmethod
    def search_semantic(query: str) -> List[Specification]: ...

class ISemanticContext(ABC):
    @abstractmethod
    def get_context_for_task(task: Task) -> Dict[str, Any]: ...

class IDocumentationRenderer(ABC):
    @abstractmethod
    def render(spec: Specification) -> str: ...
```

---

### Phase 2: Application Layer (Week 3-4)

**Goal:** Use cases for documentation operations

**TASK-DOC-004: Implement Use Cases**
- **Priority:** 🔴 CRITICAL | **Effort:** 3 days | **Status:** ⏸️

**Description:**
Create use cases for specification lifecycle operations.

**Implementation:**
- [ ] SUB-01: `CreateSpecificationUseCase`
- [ ] SUB-02: `LinkSpecificationsUseCase`
- [ ] SUB-03: `DeprecateSpecificationUseCase`
- [ ] SUB-04: `GetLLMContextUseCase`
- [ ] SUB-05: Write integration tests

**Files Modified:**
- `src/cde_orchestrator/application/documentation/__init__.py` (new)
- `src/cde_orchestrator/application/documentation/create_specification_use_case.py` (new)
- `src/cde_orchestrator/application/documentation/link_specifications_use_case.py` (new)
- `src/cde_orchestrator/application/documentation/get_llm_context_use_case.py` (new)

**Tests:**
- `tests/integration/application/documentation/` (new)

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

    # Verify persistence
    spec = container.get_specification_repository().get_by_id(
        result["spec_id"]
    )
    assert spec.title == "New Feature"
```

---

**TASK-DOC-005: Markdown Repository Adapter**
- **Priority:** 🔴 CRITICAL | **Effort:** 2 days | **Status:** ⏸️

**Description:**
Adapter to persist specifications as Markdown files (existing format).

**Implementation:**
- [ ] SUB-01: Implement `MarkdownSpecificationRepository`
- [ ] SUB-02: Parse existing Markdown files with YAML frontmatter
- [ ] SUB-03: Write Markdown with preserved metadata
- [ ] SUB-04: Handle semantic links (store as metadata)
- [ ] SUB-05: Write integration tests

**Files Modified:**
- `src/cde_orchestrator/adapters/documentation/markdown_repository.py` (new, +150 lines)

**Key Methods:**
```python
class MarkdownSpecificationRepository(ISpecificationRepository):
    def save(self, spec: Specification) -> None:
        # Convert to Markdown with YAML frontmatter
        pass

    def get_by_id(self, spec_id: str) -> Specification:
        # Parse Markdown, extract entity
        pass

    def _to_markdown(self, spec: Specification) -> str:
        # YAML + content
        pass

    def _from_markdown(self, filepath: Path) -> Specification:
        # Parse YAML, create entity
        pass
```

---

**TASK-DOC-006: Update DI Container**
- **Priority:** 🟡 HIGH | **Effort:** 1 day | **Status:** ⏸️

**Description:**
Wire documentation dependencies in DI container.

**Implementation:**
- [ ] SUB-01: Add `get_specification_repository()` method
- [ ] SUB-02: Add `get_create_specification_use_case()` method
- [ ] SUB-03: Add `get_link_specifications_use_case()` method
- [ ] SUB-04: Update tests

**Files Modified:**
- `src/cde_orchestrator/infrastructure/di_container.py` (+30 lines)

---

### Phase 3: MCP Tools (Week 5-6)

**Goal:** Expose documentation operations via MCP

**TASK-DOC-007: Add MCP Tools for Documentation**
- **Priority:** 🟡 HIGH | **Effort:** 2 days | **Status:** ⏸️

**Description:**
Create MCP tools for AI agents to manage specifications.

**Implementation:**
- [ ] SUB-01: `cde_createSpec` tool
- [ ] SUB-02: `cde_linkSpecs` tool
- [ ] SUB-03: `cde_getSpec` tool
- [ ] SUB-04: Document tools in `specs/api/mcp-tools-documentation.md`
- [ ] SUB-05: Test with Claude Desktop

**Files Modified:**
- `src/server.py` (+60 lines)
- `specs/api/mcp-tools-documentation.md` (+50 lines)

**Tool Signatures:**

```python
@server.tool()
def cde_createSpec(
    title: str,
    type: str,  # "feature", "design", "task", etc.
    content: str,
    author: Optional[str] = None,
    tags: Optional[List[str]] = None
) -> str:
    """
    Create new specification in CDE system.

    Args:
        title: Specification title (unique within type)
        type: Document type (feature|design|task|guide|governance)
        content: Markdown content
        author: Author name (defaults to current user)
        tags: Optional tags for categorization

    Returns:
        JSON: {"status": "success", "spec_id": str, "message": str}
    """
    pass

@server.tool()
def cde_linkSpecs(
    source_id: str,
    target_id: str,
    relationship: str  # "references", "implements", "supersedes", etc.
) -> str:
    """
    Establish semantic link between specifications.

    Args:
        source_id: Source specification ID
        target_id: Target specification ID
        relationship: Relationship type

    Returns:
        JSON: {"status": "success", "message": str}
    """
    pass

@server.tool()
def cde_getSpec(spec_id: str) -> str:
    """
    Retrieve specification details.

    Args:
        spec_id: Specification ID

    Returns:
        JSON: Full specification including metadata, links, tags
    """
    pass
```

**Acceptance Criteria:**
- AI agent can create spec via tool
- AI agent can link specs
- Error handling with clear messages
- Tools return structured JSON

---

### Phase 4: Semantic Search (Week 7-8)

**Goal:** Enable LLM to query documentation semantically

**TASK-DOC-008: Vector DB Adapter**
- **Priority:** 🟡 HIGH | **Effort:** 3 days | **Status:** ⏸️

**Description:**
Implement vector database adapter for semantic search.

**Implementation:**
- [ ] SUB-01: Choose vector DB (ChromaDB recommended)
- [ ] SUB-02: Implement `VectorDBSpecificationRepository`
- [ ] SUB-03: Generate embeddings for specifications
- [ ] SUB-04: Implement semantic search
- [ ] SUB-05: Write integration tests

**Files Modified:**
- `src/cde_orchestrator/adapters/documentation/vector_db_repository.py` (new, +120 lines)
- `requirements.txt` (+1 line: `chromadb`)

**Key Methods:**
```python
class VectorDBSpecificationRepository(ISpecificationRepository):
    def __init__(self, vector_db: ChromaDB):
        self.vector_db = vector_db

    def save(self, spec: Specification) -> None:
        embedding = self._generate_embedding(spec)
        self.vector_db.upsert(
            id=spec.id,
            embedding=embedding,
            metadata={"title": spec.title, "type": spec.type.value}
        )

    def search_semantic(self, query: str) -> List[Specification]:
        query_embedding = self._generate_embedding_from_text(query)
        results = self.vector_db.search(query_embedding, top_k=10)
        return [self._from_metadata(r) for r in results]
```

---

**TASK-DOC-009: LLM Context Use Case**
- **Priority:** 🟡 HIGH | **Effort:** 2 days | **Status:** ⏸️

**Description:**
Use case to generate LLM-optimized context for tasks.

**Implementation:**
- [ ] SUB-01: Implement `GetLLMContextUseCase`
- [ ] SUB-02: Extract relevant specs for task
- [ ] SUB-03: Include code examples from specs
- [ ] SUB-04: Extract architectural constraints
- [ ] SUB-05: Write unit tests

**Files Modified:**
- `src/cde_orchestrator/application/documentation/get_llm_context_use_case.py` (new, +100 lines)

**Output Structure:**
```python
{
  "summary": "2-3 sentence task-specific summary",
  "relevant_specs": [
    {
      "id": "spec-uuid",
      "title": "Hexagonal Architecture",
      "relevance": 0.95,
      "key_points": ["Dependencies point inward", "Use ports & adapters"]
    }
  ],
  "code_examples": [
    {
      "path": "src/.../use_case.py",
      "lines": "10-30",
      "description": "Example use case implementation"
    }
  ],
  "constraints": [
    "Domain layer MUST NOT import adapters",
    "Use dependency injection for ports"
  ]
}
```

---

**TASK-DOC-010: Query Documentation MCP Tool**
- **Priority:** 🟡 HIGH | **Effort:** 1 day | **Status:** ⏸️

**Description:**
MCP tool for semantic documentation queries.

**Implementation:**
- [ ] SUB-01: Add `cde_queryDocumentation` tool
- [ ] SUB-02: Wire with `GetLLMContextUseCase`
- [ ] SUB-03: Test with real queries
- [ ] SUB-04: Document in API spec

**Files Modified:**
- `src/server.py` (+25 lines)

**Tool Signature:**
```python
@server.tool()
def cde_queryDocumentation(
    query: str,
    context: Optional[str] = None,
    include_examples: bool = True
) -> str:
    """
    Semantic search across all CDE documentation.

    Args:
        query: Natural language question
        context: Optional task context
        include_examples: Include code examples

    Returns:
        JSON: {
            "summary": str,
            "relevant_specs": List[Dict],
            "code_examples": List[Dict],
            "constraints": List[str]
        }

    Example:
        query="How do I add a new use case?"
        context="implementing authentication"

        Returns architecture specs, code examples, constraints
    """
    pass
```

**Acceptance Criteria:**
```python
# Agent asks natural language question
result = cde_queryDocumentation(
    query="How do I add a new use case?",
    context="implementing authentication"
)

# Returns structured JSON with specs, examples, constraints
assert "relevant_specs" in result
assert len(result["relevant_specs"]) > 0
assert "code_examples" in result
```

---

### Phase 5: Migration Automation (Week 9-10)

**Goal:** Tool to migrate existing projects to Spec-Kit

**TASK-DOC-011: Project Migration Use Case**
- **Priority:** 🟡 HIGH | **Effort:** 4 days | **Status:** ⏸️

**Description:**
Use case to scan and migrate existing projects to Spec-Kit structure.

**Implementation:**
- [ ] SUB-01: Implement `MigrateProjectToSpecsUseCase`
- [ ] SUB-02: Scan project for .md files
- [ ] SUB-03: Extract/generate YAML frontmatter
- [ ] SUB-04: Establish semantic links (references in content)
- [ ] SUB-05: Validate against governance rules
- [ ] SUB-06: Generate migration report
- [ ] SUB-07: Write integration tests

**Files Modified:**
- `src/cde_orchestrator/application/documentation/migrate_project_use_case.py` (new, +200 lines)

**Migration Process:**
1. Scan project for .md files
2. For each file:
   - Parse existing frontmatter (if any)
   - Infer document type from path
   - Generate missing metadata
   - Extract internal links
3. Create Specification entities
4. Establish semantic links
5. Validate all specs
6. Generate report

**Output:**
```json
{
  "status": "success",
  "specs_migrated": 45,
  "links_established": 23,
  "errors": [],
  "warnings": [
    {
      "file": "docs/old-doc.md",
      "issue": "Missing llm_summary, generated automatically"
    }
  ]
}
```

---

**TASK-DOC-012: Migrate Project MCP Tool**
- **Priority:** 🟡 HIGH | **Effort:** 1 day | **Status:** ⏸️

**Description:**
MCP tool to trigger project migration.

**Implementation:**
- [ ] SUB-01: Add `cde_migrateProject` tool
- [ ] SUB-02: Test on CDE project itself
- [ ] SUB-03: Document migration process
- [ ] SUB-04: Create migration checklist

**Files Modified:**
- `src/server.py` (+30 lines)
- `docs/MIGRATION_GUIDE.md` (new, +100 lines)

**Tool Signature:**
```python
@server.tool()
def cde_migrateProject(
    project_path: str,
    scan_subdirs: bool = True,
    auto_fix: bool = False,
    dry_run: bool = False
) -> str:
    """
    Migrate existing project to Spec-Kit documentation structure.

    Process:
    1. Scans for .md files
    2. Extracts/generates metadata
    3. Creates semantic links
    4. Validates against governance
    5. Generates migration report

    Args:
        project_path: Path to project root
        scan_subdirs: Scan subdirectories
        auto_fix: Auto-fix validation errors
        dry_run: Simulate migration without changes

    Returns:
        JSON: {
            "status": "success" | "error",
            "specs_migrated": int,
            "links_established": int,
            "errors": List[str],
            "warnings": List[str]
        }
    """
    pass
```

**Acceptance Criteria:**
- Migrates CDE project successfully
- All specs have valid YAML frontmatter
- Semantic links established
- Validation passes
- Migration report generated

---

### Phase 6: LLM Feedback Loop (Week 11-12)

**Goal:** Self-improving documentation based on LLM usage

**TASK-DOC-013: Document Feedback System**
- **Priority:** 🟢 MEDIUM | **Effort:** 3 days | **Status:** ⏸️

**Description:**
Track which docs help LLMs and flag docs for improvement.

**Implementation:**
- [ ] SUB-01: Implement `DocumentFeedbackUseCase`
- [ ] SUB-02: Track query → spec usage
- [ ] SUB-03: Flag specs with low usefulness scores
- [ ] SUB-04: Generate improvement suggestions
- [ ] SUB-05: Add analytics dashboard (optional)

**Files Modified:**
- `src/cde_orchestrator/application/documentation/document_feedback_use_case.py` (new, +80 lines)

**Tracking:**
```python
class DocumentFeedbackUseCase:
    def record_query(
        self,
        query: str,
        results: List[Specification],
        useful: bool
    ) -> None:
        """Track which specs useful for which queries."""
        self.analytics.track_query(
            query=query,
            results=[r.id for r in results],
            useful=useful
        )

        if not useful:
            for spec in results:
                spec.metadata['needs_improvement'] = True
                spec.metadata['improvement_context'] = query
                self.repo.save(spec)
```

---

**TASK-DOC-014: Auto-Generate LLM Summaries**
- **Priority:** 🟢 MEDIUM | **Effort:** 2 days | **Status:** ⏸️

**Description:**
Use LLM to generate llm_summary for specs without one.

**Implementation:**
- [ ] SUB-01: Implement `AutoGenerateLLMSummaryUseCase`
- [ ] SUB-02: Detect specs missing llm_summary
- [ ] SUB-03: Generate summary using GPT-4
- [ ] SUB-04: Validate summary length (2-3 sentences)
- [ ] SUB-05: Add MCP tool for manual trigger

**Files Modified:**
- `src/cde_orchestrator/application/documentation/auto_generate_llm_summary_use_case.py` (new, +60 lines)
- `src/server.py` (+20 lines)

**Tool Signature:**
```python
@server.tool()
def cde_generateLLMSummary(spec_id: str) -> str:
    """
    Generate LLM-optimized summary for specification.

    Args:
        spec_id: Specification ID

    Returns:
        JSON: {"status": "success", "summary": str}
    """
    pass
```

---

## Dependencies & Prerequisites

### Python Packages

```txt
# Add to requirements.txt
chromadb>=0.4.0  # Vector database
openai>=1.0.0    # LLM API (for summary generation)
pydantic>=2.0.0  # Already included
```

### External Services (Optional)

- **Vector DB:** ChromaDB (local) or Pinecone (hosted)
- **LLM API:** OpenAI GPT-4 or similar (for auto-summaries)

---

## Risk Mitigation

### Risk 1: Breaking Existing Documentation

**Mitigation:**
- Implement migration tool with `dry_run` mode
- Validate all changes before commit
- Keep backup of original files
- Test migration on copy of CDE project first

### Risk 2: Performance of Vector Search

**Mitigation:**
- Use ChromaDB (fast, local)
- Cache embeddings
- Limit search to top 10 results
- Implement pagination if needed

### Risk 3: LLM Summary Quality

**Mitigation:**
- Use GPT-4 (better than GPT-3.5)
- Provide clear prompt template
- Validate summary length
- Allow manual override
- Include human review step

---

## Testing Strategy

### Unit Tests

- All domain entities (Specification, SemanticLink)
- All use cases (CreateSpec, LinkSpecs, GetLLMContext)
- Business rule validation

**Target:** 80% coverage

### Integration Tests

- Markdown repository (read/write files)
- Vector DB repository (search)
- MCP tools (end-to-end)

**Target:** Key workflows covered

### Manual Testing

- Test with Claude Desktop
- Test migration on real projects
- Validate semantic search results
- Test feedback loop

---

## Documentation Updates

### New Documents

- `docs/MIGRATION_GUIDE.md` - How to migrate projects
- `specs/api/mcp-tools-documentation.md` - MCP tool reference (update)
- `specs/design/documentation-architecture.md` - Architecture spec

### Updated Documents

- `AGENTS.md` - Add documentation MCP tools
- `.github/copilot-instructions.md` - Add documentation patterns
- `README.md` - Add migration instructions

---

## Rollout Strategy

### Week 1-4: Internal Development

- Build domain layer
- Build application layer
- Test with CDE project

### Week 5-8: Alpha Testing

- Add MCP tools
- Test with Claude Desktop
- Gather feedback

### Week 9-10: Beta Testing

- Add migration tool
- Test on 2-3 external projects
- Refine based on feedback

### Week 11-12: Production Release

- Add feedback loop
- Write documentation
- Announce on GitHub

---

## Open Questions

1. **Vector DB Choice:** ChromaDB (local) vs Pinecone (hosted)?
   - Recommendation: ChromaDB for MVP, evaluate Pinecone later

2. **LLM Provider:** OpenAI vs Anthropic vs local model?
   - Recommendation: OpenAI GPT-4 for MVP (best quality)

3. **Embedding Model:** OpenAI embeddings vs sentence-transformers?
   - Recommendation: OpenAI embeddings (consistent with LLM)

4. **Migration Strategy:** Automatic vs manual review?
   - Recommendation: Automatic with dry-run, manual review for production

---

## Next Steps (This Week)

1. **Create GitHub Issue** for "Documentation as Domain Layer" epic
2. **Start TASK-DOC-001** (Create domain module structure)
3. **Schedule architecture review** with team
4. **Set up ChromaDB** locally for testing

---

## Appendix: Quick Reference

### Key Classes

```python
# Domain
Specification  # Core entity
DocumentType   # Enum: feature, design, task, etc.
DocumentStatus # Enum: draft, active, deprecated, archived
SemanticLink   # Value object for doc relationships

# Ports
ISpecificationRepository  # Persistence
ISemanticContext         # LLM context provider
IDocumentationRenderer   # Output formatting

# Use Cases
CreateSpecificationUseCase
LinkSpecificationsUseCase
GetLLMContextUseCase
MigrateProjectToSpecsUseCase

# Adapters
MarkdownSpecificationRepository  # Persist as .md files
VectorDBSpecificationRepository  # Semantic search
```

### Key MCP Tools

```python
cde_createSpec(title, type, content, ...)
cde_linkSpecs(source_id, target_id, relationship)
cde_queryDocumentation(query, context, ...)
cde_migrateProject(project_path, ...)
cde_generateLLMSummary(spec_id)
```

---

**End of Migration Plan**

For detailed research, see: `agent-docs/research/documentation-architecture-llm-first-research.md`

For questions or feedback, open a GitHub issue with label `documentation-architecture`.
