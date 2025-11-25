# AI Agent Instructions - CDE Orchestrator MCP

> **Quick Reference for AI Coding Agents**
> **Last Updated**: 2025-11-24
> **Full Details**: `.github/copilot-instructions.md`

---

## 🚨 Critical Rules (ENFORCED by pre-commit)

1. **NO .md files in root** except: README, CHANGELOG, CONTRIBUTING, AGENTS, GEMINI
2. **All docs → correct location**: `specs/[feature]/`, `agent-docs/execution/`, etc.
3. **YAML frontmatter required** in all .md files (title, description, type, status, dates)
4. **No vague names**: Use `execution-topic-2025-11-24.md`, not `REPORT.md`

📖 **Full Governance**: `specs/governance/DOCUMENTATION_GOVERNANCE.md`

---

## 🏗️ Architecture

**Pattern**: Hexagonal (Ports & Adapters)

```
Domain (entities.py) → Application (use_cases/) → Adapters (filesystem, copilot_cli)
```

**Key Rule**: Dependencies point INWARD only. Domain never imports infrastructure.

📖 **Details**: `specs/design/architecture/README.md`

---

## 📂 Spec-Kit Workflow (NEW: 2025-11-24)

### ✅ Automated (Recommended)

```python
# 1. Analyze complexity & select workflow
cde_selectWorkflow("Add Redis caching to auth module")

# 2. Start feature (auto-creates specs/[feature]/)
cde_startFeature(
    user_prompt="Add Redis caching to auth",
    workflow_type="standard"
)
# Creates: specs/add-redis-caching-to-auth/
#   ├── spec.md   (PRD)
#   ├── plan.md   (technical design)
#   └── tasks.md  (executable checklist)

# 3. Submit phase work
cde_submitWork(
    feature_id="uuid",
    phase_id="define",
    results={"specification": "..."}
)
```

### 🔧 Manual Fallback

```bash
mkdir specs/my-feature/
cp specs/templates/spec.md specs/my-feature/
cp specs/templates/plan.md specs/my-feature/
cp specs/templates/tasks.md specs/my-feature/
# Edit frontmatter: [FEATURE NAME], [DATE], [AUTHOR]
```

### 🔄 Template Synchronization (NEW: 2025-11-25)

Keep local templates in sync with the official GitHub Spec-Kit standard. This workflow ensures that all generated specifications adhere to the latest best practices, while preserving CDE-specific customizations.

**Validated Workflow**:

1.  **Check for Updates (Dry Run)**:
    Run the sync tool without forcing an overwrite. If templates are up-to-date, it will report a `skipped` status.

    ```python
    # Returns 'skipped' if no updates are needed
    cde_syncTemplates(project_path=".", force=False)
    ```

2.  **Force Sync (If Needed)**:
    If updates are available or templates are corrupted, use `force=True` to back up the existing templates and download fresh copies.

    ```python
    # Backs up local templates and downloads the latest versions
    cde_syncTemplates(project_path=".", force=True)
    ```

3.  **Validate a Specification**:
    After generating a new specification, or to check an existing one, use the validation tool. It provides a conformity score and a detailed list of issues.

    ```python
    # Analyzes a spec directory and returns a conformity score
    cde_validateSpec(spec_directory="specs/ai-assistant-config", strict=False)
    ```

4.  **Enforce Quality with Strict Mode**:
    For CI/CD or pre-commit checks, use `strict=True`. The tool will return a `warning` status if the conformity score is below 95%, making it easy to integrate into automated quality gates.

    ```python
    # Fails if conformity score is less than 95%
    cde_validateSpec(spec_directory="specs/ai-assistant-config", strict=True)
    ```

**Key Features**:
- **Safe by Default**: `force=False` prevents accidental overwrites.
- **Detailed Validation**: Checks frontmatter, structure, naming, and content quality.
- **CI/CD Ready**: `strict=True` mode for automated quality checks.
- **CDE Customizations**: Automatically applies and preserves CDE-specific sections and fields.

📖 **Full Documentation**: `specs/spec-kit-synchronization/tasks.md`

---

## 📁 Directory Structure

### Feature Documentation (Spec-Kit)

```
specs/
├── [feature-name]/        # Feature-specific (NEW standard)
│   ├── spec.md           # PRD (user stories, requirements)
│   ├── plan.md           # Technical design
│   └── tasks.md          # Executable checklist
├── design/               # Cross-cutting architecture
├── governance/           # Process rules
└── templates/            # Reusable templates
```

### Legacy (DEPRECATED)

```
specs/features/           # OLD: single-file specs (use specs/[feature]/ instead)
agent-docs/execution/     # OLD: for features (use specs/[feature]/tasks.md instead)
```

**Migration Status**:
- ✅ HIGH: ai-assistant-config, onboarding-system (migrated)
- ⏸️ MEDIUM: python-314, server-refactoring, amazon-q (pending)
- 📦 LOW: 4 archived proposals

📖 **Migration Guide**: `specs/features/README.md`

---

## 🎓 Core Concepts

### 1. Context-Driven Engineering (CDE)

Development as **state transitions** via 6 phases:

```
define → decompose → design → implement → test → review
```

**Workflow Config**: `.cde/workflow.yml`

### 2. Multi-Project Management

**Philosophy**: Stateless & Simple. Agent knows context, CDE validates and executes.

```python
# All tools accept project_path or project_name
cde_startFeature(project_name="CDE", user_prompt="Add auth")
# OR
cde_startFeature(project_path="E:\\projects\\CDE", user_prompt="Add auth")
```

### 3. Intelligent Orchestration (MCP-First)

```
User Request → cde_selectWorkflow → cde_startFeature → cde_submitWork → Complete
```

**Key Tools**:
- `cde_selectWorkflow`: Analyzes complexity, recommends workflow+recipe+skills
- `cde_sourceSkill`: Downloads knowledge from awesome-claude-skills
- `cde_updateSkill`: Web research for latest library versions

📖 **Full Workflow**: `agent-docs/execution/intelligent-agent-system-implementation-2025-11.md`

---

## 🔧 Development Guidelines

### Adding Features

1. **Create Spec**: `specs/[feature]/spec.md` (user stories, requirements, acceptance criteria)
2. **Create Plan**: `specs/[feature]/plan.md` (architecture, testing, performance)
3. **Create Tasks**: `specs/[feature]/tasks.md` (numbered tasks across phases)
4. **Use CDE**: `cde_startFeature()` → auto-creates structure

📖 **Examples**: `specs/ai-assistant-config/`, `specs/onboarding-system/`

### Code Style

**Domain Layer** (entities.py):
```python
# ✅ Rich domain models with behavior
class Feature:
    def advance_phase(self, next_phase: str):
        if self.status == FeatureStatus.COMPLETED:
            raise ValueError("Cannot advance completed feature")
        self.current_phase = next_phase
```

**Application Layer** (use_cases/):
```python
# ✅ Explicit inputs/outputs
class StartFeatureUseCase:
    def execute(self, input_data: Dict) -> Dict:
        project = self.repo.get_by_id(input_data["project_id"])
        feature = project.start_feature(input_data["prompt"])
        return {"status": "success", "feature_id": feature.id}
```

**Adapters** (adapters/):
```python
# ✅ Implement port interface
class CopilotCLIAdapter(ICodeExecutor):
    async def execute_prompt(self, project_path, prompt, context):
        cmd = ["gh", "copilot", "suggest"]
        # ... implementation
```

📖 **Patterns**: `.github/copilot-instructions.md` (sections on Domain/Application/Adapters)

---

## 📊 Current Status

### ✅ Completed
- Phase 1-2: Spec-Kit governance + tooling
- Phase 3: HIGH priority feature migration
- Hexagonal architecture foundation
- Multi-project auto-discovery
- AI assistant configuration
- Project onboarding system

### 🔄 In Progress
- Use cases implementation
- Copilot CLI adapter
- Unit test coverage (target: 80%)

📖 **Roadmap**: `specs/tasks/improvement-roadmap.md` (63 tasks)

---

## 🎯 Quick Tips

1. **Check layer before coding**: Domain? No external deps. Application? Orchestrate. Adapters? Infrastructure OK.
2. **Follow ports**: Define interface in `domain/ports.py`, implement in `adapters/`, wire in `infrastructure/di_container.py`
3. **Write tests first** for complex logic
4. **Use roadmap**: Check what's done/in-progress to avoid conflicts
5. **Respect constitution**: `memory/constitution.md` for values and standards

---

## 📚 Essential References

| Topic | Location |
|-------|----------|
| **Governance** | `specs/governance/DOCUMENTATION_GOVERNANCE.md` |
| **Architecture** | `specs/design/architecture/README.md` |
| **Roadmap** | `specs/tasks/improvement-roadmap.md` |
| **Constitution** | `memory/constitution.md` |
| **Spec-Kit Migration** | `specs/features/README.md` |
| **Full Instructions** | `.github/copilot-instructions.md` |

---

**Remember**: This is a tool FOR AI AGENTS. Design prioritizes:
1. **Explicitness** over cleverness
2. **Contracts** over implementations
3. **Isolation** over shared state
4. **LLM-readability** over human terseness

📖 **For comprehensive guidance, see**: `.github/copilot-instructions.md` (1000+ lines, all patterns and examples)
