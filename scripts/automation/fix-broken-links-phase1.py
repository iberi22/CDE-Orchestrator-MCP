#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix broken links in critical documentation files.

This script implements Phase 1 quick wins:
1. Fix architecture cross-references
2. Fix documentation example references
3. Create index files for orphaned documents
"""

import re
from pathlib import Path


def fix_architecture_references() -> int:
    """Fix broken architecture cross-references."""
    arch_dir = Path("specs/design/architecture")

    # Files that need fixing
    files_to_fix = [
        "architecture-domain-layer.md",
        "architecture-application-layer.md",
        "architecture-ports.md",
    ]

    replacements = [
        (r"../architecture\.md", "./architecture-overview.md"),
        (r"architecture-application-layer\.md", "./architecture-application-layer.md"),
        (r"architecture-ports-adapters\.md", "./architecture-ports.md"),
        (r"architecture-domain-layer\.md", "./architecture-domain-layer.md"),
        (r"architecture-use-cases\.md", "./architecture-use-cases.md"),
        (r"architecture-adapters\.md", "./architecture-adapters.md"),
    ]

    fixed_count = 0
    for file_name in files_to_fix:
        file_path = arch_dir / file_name
        if not file_path.exists():
            print(f"Skip: {file_name} (not found)")
            continue

        content = file_path.read_text(encoding="utf-8")
        original_content = content

        for old_pattern, new_path in replacements:
            content = re.sub(old_pattern, new_path, content)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            fixed_count += 1
            print(f"Fixed: {file_name}")
        else:
            print(f"No changes: {file_name}")

    return fixed_count


def fix_documentation_examples() -> int:
    """Fix documentation example references."""
    files_to_fix = [
        (
            "CONTRIBUTING.md",
            [
                (
                    "specs/features/my-feature.md",
                    "<!-- Example: specs/features/my-feature.md -->",
                ),
            ],
        ),
        (
            "GEMINI.md",
            [
                (
                    "specs/features/my-feature.md",
                    "<!-- Example: specs/features/my-feature.md -->",
                ),
            ],
        ),
        (
            ".github/copilot-instructions.md",
            [
                (
                    "specs/features/my-feature.md",
                    "<!-- Example: specs/features/my-feature.md -->",
                ),
                (
                    r"EXECUTIONS-julius-\*-YYYY-MM-DD-HHmm\.md",
                    "<!-- Example: EXECUTIONS-julius-{topic}-YYYY-MM-DD-HHmm.md -->",
                ),
            ],
        ),
    ]

    fixed_count = 0
    for file_name, replacements_list in files_to_fix:
        file_path = Path(file_name)
        if not file_path.exists():
            print(f"Skip: {file_name} (not found)")
            continue

        content = file_path.read_text(encoding="utf-8")
        original_content = content

        for old_ref, comment in replacements_list:
            # Add HTML comment to mark as example
            if f"[{old_ref}]" in content:
                content = content.replace(
                    f"[{old_ref}]", f"<!-- Example: {old_ref} -->"
                )
                fixed_count += 1
                print(f"  Marked as example in {file_name}: {old_ref}")

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")

    return fixed_count


def create_index_files() -> int:
    """Create README index files for orphaned documents."""

    # Agent-docs/execution index
    execution_index = """---
title: "Execution Reports Index"
description: "Index of workflow execution reports from CDE Orchestrator"
type: "guide"
status: "active"
created: "2025-11-20"
updated: "2025-11-20"
author: "CDE Team"
---

# Execution Reports

This directory contains reports of completed workflow executions.

## Recent Reports

- [Quality Improvements (2025-11-20)](./execution-quality-improvements-2025-11-20.md)
- [Phase 2 Complete (2025-11-20)](./execution-phase2-complete-2025-11-20.md)
- [Phase 2 Gitignore Integration (2025-11-20)](./execution-phase2-gitignore-integration-2025-11-20.md)
- [Phase 3 Testing (2025-11-20)](./execution-phase3-testing-2025-11-20.md)
- [Phase 2 Gitignore Integration (2025-11-20)](./execution-phase2-gitignore-integration-2025-11-20.md)

## Archived

- See `./archive/` for older execution reports

---

For more information, see [Specs Tasks](../../specs/tasks/).
"""

    # Agent-docs/research index
    research_index = """---
title: "Research Documents Index"
description: "Index of research and analysis documents"
type: "guide"
status: "active"
created: "2025-11-20"
updated: "2025-11-20"
author: "CDE Team"
---

# Research Documents

This directory contains research, analysis, and investigation reports.

## Current Research

- [CDE Orchestrator Comparative Analysis (2025-11-04)](./cde-orchestrator-comparative-analysis-2025-11-04.md)
- [Research - Anthropic MCP Code Execution (2025-11-09)](./research-anthropic-mcp-code-execution-2025-11-09.md)
- [Model Usage Rules - CLI vs SDK (2025-11-05)](./model-usage-rules-cli-vs-sdk-2025-11-05.md)

## Archived Research

- See `./archived-2025-11-07/` for older research documents

---

See [Specs Features](../../specs/features/) for feature specifications.
"""

    # Specs/design index (partial)
    design_index = """---
title: "Design Documents Index"
description: "Architecture, design decisions, and technical specifications"
type: "guide"
status: "active"
created: "2025-11-20"
updated: "2025-11-20"
author: "CDE Team"
---

# Design Documents

This directory contains architecture decisions, technical designs, and system specifications.

## Core Architecture

- See [`./architecture/`](./architecture/) for complete hexagonal architecture documentation

## Key Designs

- [Dynamic Skill System](./dynamic-skill-system-core.md) - Core models and architecture
- [Multi-Agent Orchestration System](./multi-agent-orchestration-system.md)
- [MCP Tool Design Decision](./mcp-tool-design-decision.md)
- [Jules Dual-Mode Architecture](./jules-dual-mode-architecture.md)

## See Also

- [Features](../features/) - User-facing specifications
- [Tasks](../tasks/) - Roadmaps and planning documents
"""

    # Create files
    files_created = 0

    exec_dir = Path("agent-docs/execution")
    exec_readme = exec_dir / "README.md"
    if not exec_readme.exists():
        exec_readme.write_text(execution_index, encoding="utf-8")
        print(f"Created: {exec_readme}")
        files_created += 1

    research_dir = Path("agent-docs/research")
    research_readme = research_dir / "README.md"
    if not research_readme.exists():
        research_readme.write_text(research_index, encoding="utf-8")
        print(f"Created: {research_readme}")
        files_created += 1

    design_dir = Path("specs/design")
    design_readme = design_dir / "README.md"
    if not design_readme.exists():
        design_readme.write_text(design_index, encoding="utf-8")
        print(f"Created: {design_readme}")
        files_created += 1
    else:
        print(f"Skip: {design_readme} (already exists)")

    return files_created


def main() -> None:
    """Main entry point."""
    print("=" * 60)
    print("Phase 1: Fixing Critical Broken Links")
    print("=" * 60)

    print("\n1. Fixing architecture cross-references...")
    arch_fixed = fix_architecture_references()
    print(f"   Fixed {arch_fixed} files\n")

    print("2. Fixing documentation example references...")
    example_fixed = fix_documentation_examples()
    print(f"   Fixed {example_fixed} references\n")

    print("3. Creating index files for orphaned documents...")
    index_created = create_index_files()
    print(f"   Created {index_created} index files\n")

    print("=" * 60)
    print(
        f"Summary: {arch_fixed} architecture files fixed, {example_fixed} examples updated, {index_created} indexes created"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
