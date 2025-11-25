"""
Customize Spec-Kit templates with CDE-specific extensions.

This script applies CDE customizations to pure Spec-Kit templates while
maintaining 100% structural conformity with Spec-Kit standards.

CDE Extensions Applied:
1. YAML Frontmatter: Add llm_summary field for AI agent optimization
2. spec.md: Add "MCP Tools Available" section with relevant tools
3. plan.md: Add "Hexagonal Architecture Patterns" section
4. tasks.md: Add "Phase Tracking" section for CDE workflow integration

Usage:
    python customize_templates.py --input templates/spec.md --output specs/templates/spec.md
    python customize_templates.py --batch --input-dir /tmp/spec-kit/ --output-dir specs/templates/
"""

import argparse
from pathlib import Path
from typing import Any

import yaml

# CDE Extension Templates
MCP_TOOLS_SECTION = """

## 🛠️ MCP Tools Available

**Note**: This is a CDE extension to help AI agents discover relevant tools.

For this feature, consider using:

- **`cde_selectWorkflow`** - Analyze task complexity and recommend optimal workflow
- **`cde_sourceSkill`** - Download relevant skills from awesome-claude-skills
- **`cde_startFeature`** - Initialize feature directory with spec/plan/tasks
- **`cde_submitWork`** - Submit phase results and advance workflow
- **`cde_validateSpec`** - Validate generated specs against Spec-Kit standard

**Full Tool List**: Use `cde_searchTools("")` to list all 27+ available tools.

**Examples**:
```python
# Analyze complexity before starting
result = cde_selectWorkflow("Add user authentication module")
# → Returns: workflow_type, complexity, recipe_id, required_skills

# Start feature with recommended workflow
result = cde_startFeature(
    user_prompt="Add user authentication",
    workflow_type="standard",
    recipe_id="ai-engineer"
)
# → Creates: specs/add-user-authentication/{spec.md, plan.md, tasks.md}

# Submit phase work
result = cde_submitWork(
    feature_id="uuid",
    phase_id="define",
    results={"specification": "..."}
)
# → Advances to next phase, returns prompt for next work
```
"""

HEXAGONAL_ARCHITECTURE_SECTION = """

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
"""

PHASE_TRACKING_SECTION = """

## 🔄 Phase Tracking

**Note**: This is a CDE extension for tracking feature development phases.

### CDE Workflow Phases

```
define → decompose → design → implement → test → review
```

### Task-to-Phase Mapping

Map tasks in this file to CDE workflow phases for automated progress tracking:

| Phase | Tasks | Focus |
|-------|-------|-------|
| **Define** | T001-T010 | Specification, requirements analysis |
| **Decompose** | T011-T020 | Task breakdown, dependencies |
| **Design** | T021-T030 | Architecture, patterns, interfaces |
| **Implement** | T031-T050 | Code implementation, adapters |
| **Test** | T051-T060 | Unit tests, integration tests, validation |
| **Review** | T061-T067 | Code review, documentation, cleanup |

### Using `cde_submitWork`

When completing a phase, use:

```python
result = cde_submitWork(
    feature_id="uuid",
    phase_id="define",
    results={
        "specification": "Complete spec with user stories and requirements",
        "files_created": ["specs/my-feature/spec.md"],
        "next_phase_ready": True
    }
)
# → Returns prompt for next phase (decompose)
```

### Workflow Configuration

Phase definitions are in `.cde/workflow.yml`. Example:

```yaml
phases:
  - id: define
    name: "Define Feature"
    inputs: ["user_prompt", "project_context"]
    outputs: ["specification", "user_stories"]

  - id: decompose
    name: "Decompose Tasks"
    inputs: ["specification"]
    outputs: ["task_breakdown", "dependencies"]
```
"""


def extract_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}, content

    try:
        parts = content.split("---", 2)
        if len(parts) < 3:
            return {}, content

        frontmatter = yaml.safe_load(parts[1])
        body = parts[2]
        return frontmatter or {}, body
    except yaml.YAMLError:
        return {}, content


def add_llm_summary_to_frontmatter(frontmatter: dict[str, Any], template_type: str) -> dict[str, Any]:
    """Add llm_summary field to YAML frontmatter."""
    if "llm_summary" in frontmatter:
        return frontmatter  # Already has it

    # Generate appropriate summary based on template type
    summaries = {
        "spec": "Feature specification with user stories, requirements, and acceptance criteria. "
        "Defines WHAT the feature does and WHY it's needed.",
        "plan": "Technical implementation plan with architecture, design decisions, and testing strategy. "
        "Defines HOW the feature will be built.",
        "tasks": "Executable task checklist organized by phases (define → decompose → design → implement → test → review). "
        "Tracks implementation progress and dependencies.",
    }

    frontmatter["llm_summary"] = summaries.get(template_type, "Feature documentation")
    return frontmatter


def customize_spec_template(content: str) -> str:
    """Apply CDE customizations to spec.md template."""
    # Extract frontmatter
    frontmatter, body = extract_frontmatter(content)

    # Add llm_summary
    frontmatter = add_llm_summary_to_frontmatter(frontmatter, "spec")

    # Rebuild frontmatter
    frontmatter_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
    customized = f"---\n{frontmatter_str}---{body}"

    # Add MCP Tools section (before "Out of Scope" if present, otherwise at end)
    if "## Out of Scope" in customized:
        customized = customized.replace("## Out of Scope", MCP_TOOLS_SECTION + "\n\n## Out of Scope")
    else:
        customized += MCP_TOOLS_SECTION

    return customized


def customize_plan_template(content: str) -> str:
    """Apply CDE customizations to plan.md template."""
    # Extract frontmatter
    frontmatter, body = extract_frontmatter(content)

    # Add llm_summary
    frontmatter = add_llm_summary_to_frontmatter(frontmatter, "plan")

    # Rebuild frontmatter
    frontmatter_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
    customized = f"---\n{frontmatter_str}---{body}"

    # Add Hexagonal Architecture section (before "Security Considerations" if present, otherwise at end)
    if "## Security Considerations" in customized:
        customized = customized.replace(
            "## Security Considerations", HEXAGONAL_ARCHITECTURE_SECTION + "\n\n## Security Considerations"
        )
    else:
        customized += HEXAGONAL_ARCHITECTURE_SECTION

    return customized


def customize_tasks_template(content: str) -> str:
    """Apply CDE customizations to tasks.md template."""
    # Extract frontmatter
    frontmatter, body = extract_frontmatter(content)

    # Add llm_summary
    frontmatter = add_llm_summary_to_frontmatter(frontmatter, "tasks")

    # Rebuild frontmatter
    frontmatter_str = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
    customized = f"---\n{frontmatter_str}---{body}"

    # Add Phase Tracking section at end
    customized += PHASE_TRACKING_SECTION

    return customized


def customize_template(template_path: Path, output_path: Path) -> None:
    """Customize a single template file."""
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Apply appropriate customization based on filename
    if template_path.name == "spec.md" or "spec-template" in template_path.name:
        customized = customize_spec_template(content)
    elif template_path.name == "plan.md" or "plan-template" in template_path.name:
        customized = customize_plan_template(content)
    elif template_path.name == "tasks.md" or "tasks-template" in template_path.name:
        customized = customize_tasks_template(content)
    else:
        # Unknown template type, copy as-is
        customized = content

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(customized)

    print(f"✅ Customized: {template_path.name} → {output_path}")


def customize_batch(input_dir: Path, output_dir: Path) -> None:
    """Customize all templates in a directory."""
    templates = ["spec.md", "plan.md", "tasks.md", "spec-template.md", "plan-template.md", "tasks-template.md"]

    customized_count = 0
    for template_name in templates:
        template_path = input_dir / template_name
        if template_path.exists():
            output_path = output_dir / template_name.replace("-template", "")
            customize_template(template_path, output_path)
            customized_count += 1

    print(f"\n✅ Customized {customized_count} templates")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Customize Spec-Kit templates with CDE extensions"
    )
    parser.add_argument("--input", type=Path, help="Input template file")
    parser.add_argument("--output", type=Path, help="Output customized file")
    parser.add_argument("--batch", action="store_true", help="Process all templates in directory")
    parser.add_argument("--input-dir", type=Path, help="Input directory (batch mode)")
    parser.add_argument("--output-dir", type=Path, help="Output directory (batch mode)")

    args = parser.parse_args()

    if args.batch:
        if not args.input_dir or not args.output_dir:
            parser.error("--batch requires --input-dir and --output-dir")

        if not args.input_dir.exists():
            print(f"❌ Input directory not found: {args.input_dir}")
            exit(1)

        customize_batch(args.input_dir, args.output_dir)
    else:
        if not args.input or not args.output:
            parser.error("Non-batch mode requires --input and --output")

        if not args.input.exists():
            print(f"❌ Input file not found: {args.input}")
            exit(1)

        customize_template(args.input, args.output)


if __name__ == "__main__":
    main()
