---
llm_summary: Technical implementation plan with architecture, design decisions, and
  testing strategy. Defines HOW the feature will be built.
---# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [single/web/mobile - determines source structure]
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## 🏗️ Hexagonal Architecture Patterns

**Note**: This is a CDE extension for projects using Hexagonal Architecture (Ports & Adapters).

### Pattern Overview

```
External Systems → Adapters → Application (Use Cases) → Domain (Entities)
```

**Key Principles**:
- Dependencies point INWARD only (Domain never imports infrastructure)
- Domain contains business logic, NO framework dependencies
- Ports define interfaces (contracts)
- Adapters implement ports (infrastructure details)

### Implementation Guidelines

**Domain Layer** (`domain/entities.py`):
```python
# ✅ Rich domain models with behavior
class Feature:
    def advance_phase(self, next_phase: str):
        if self.status == FeatureStatus.COMPLETED:
            raise ValueError("Cannot advance completed feature")
        self.current_phase = next_phase
```

**Ports Layer** (`domain/ports.py`):
```python
# ✅ Define interfaces
class IFeatureRepository(ABC):
    @abstractmethod
    def get_by_id(self, feature_id: str) -> Optional[Feature]:
        pass

    @abstractmethod
    def save(self, feature: Feature) -> None:
        pass
```

**Application Layer** (`application/use_cases/`):
```python
# ✅ Orchestration logic
class StartFeatureUseCase:
    def __init__(self, repo: IFeatureRepository):
        self.repo = repo

    def execute(self, input_data: Dict) -> Dict:
        project = self.repo.get_by_id(input_data["project_id"])
        feature = project.start_feature(input_data["prompt"])
        return {"status": "success", "feature_id": feature.id}
```

**Adapters Layer** (`adapters/`):
```python
# ✅ Infrastructure implementations
class FilesystemFeatureRepository(IFeatureRepository):
    def get_by_id(self, feature_id: str) -> Optional[Feature]:
        path = self.base_path / f"{feature_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        return Feature.from_dict(data)
```

### Testing Strategy

- **Domain**: Pure unit tests (no I/O, fast)
- **Use Cases**: Integration tests with mock adapters
- **Adapters**: Integration tests with real infrastructure
- **E2E**: Full flows (rare, expensive)

**Reference**: `specs/design/architecture/README.md`
