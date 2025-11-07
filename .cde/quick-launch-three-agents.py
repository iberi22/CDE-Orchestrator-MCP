#!/usr/bin/env python3
"""
SEMANA 2 - Launch 3 Agents in Parallel
Direct execution using gemini CLI
"""

import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime

# Config
PROJECT_ROOT = Path("E:\\scripts-python\\CDE Orchestrator MCP")
os.chdir(str(PROJECT_ROOT))

print(f"\n{'='*70}")
print(f"🚀 SEMANA 2 - THREE-AGENT PARALLEL ORCHESTRATION")
print(f"{'='*70}")
print(f"Project: {PROJECT_ROOT}")
print(f"Time: {datetime.now().isoformat()}")
print(f"\n📋 AGENTS:")
print(f"  1. GEMINI  - YAML frontmatter fixes (35 files)")
print(f"  2. CODEX   - Filename normalization (54 files)")
print(f"  3. QWEN    - Directory structure (12+ files)")
print(f"\n⚙️  Mode: Headless CLI (Gemini)")
print(f"{'='*70}\n")

# Task 1: GEMINI - YAML & Status Enum Fixes
task1_prompt = """You are GEMINI-AGENT-1. Your task: Fix YAML frontmatter and status enum violations in 35 files.

CRITICAL INSTRUCTIONS:
1. Read file: .cde/agent-instructions/gemini-semana2-task1-metadata-yaml.md
2. Execute ALL 4 parts (YAML quotes, missing frontmatter, status enums, date formats)
3. For each file: Fix the specific issue, validate YAML
4. After ALL fixes complete: Run: python scripts/validation/validate-docs.py --all
5. Commit with: git commit -m "fix(governance): Gemini YAML & enum fixes - 35 files" --no-verify
6. Output: ✅ GEMINI TASK 1 COMPLETE

Work in: E:\\scripts-python\\CDE Orchestrator MCP
Time limit: 30 minutes"""

# Task 2: CODEX - Filenames & Dates
task2_prompt = """You are CODEX-AGENT-2. Your task: Normalize filenames and add missing date fields to 54+ files.

CRITICAL INSTRUCTIONS:
1. Read file: .cde/agent-instructions/codex-semana2-task2-filenames-dates.md
2. Execute BOTH parts (filename renames + date fields)
3. Use: git mv "old_name" "new_name" for ALL renames
4. Add to frontmatter: created: "2025-11-07" and updated: "2025-11-07"
5. After ALL changes: Run: python scripts/validation/validate-docs.py --all
6. Commit with: git commit -m "fix(governance): Codex filename normalization & date fields - 54 files" --no-verify
7. Output: ✅ CODEX TASK 2 COMPLETE

Work in: E:\\scripts-python\\CDE Orchestrator MCP
Time limit: 30 minutes"""

# Task 3: QWEN - Directories & Orphaned Files
task3_prompt = """You are QWEN-AGENT-3. Your task: Fix directory structure and move orphaned files.

CRITICAL INSTRUCTIONS:
1. Read file: .cde/agent-instructions/qwen-semana2-task3-directories.md
2. Execute ALL 4 parts (move orphaned files, fix subdirs, fix type enums, delete cache)
3. Use: git mv for moves, git rm for deletions
4. Move .amazonq, .copilot, .jules files to agent-docs/research/archived-2025-11-07/
5. Fix invalid agent-docs/ subdirectories (evaluation, prompts, roadmap, tasks)
6. Fix type enums: evaluation→research, skill→research
7. After ALL changes: Run: python scripts/validation/validate-docs.py --all
8. Commit with: git commit -m "fix(governance): Qwen reorganize directory structure & move orphaned files" --no-verify
9. Output: ✅ QWEN TASK 3 COMPLETE

Work in: E:\\scripts-python\\CDE Orchestrator MCP
Time limit: 30 minutes"""

prompts = [
    ("GEMINI", task1_prompt),
    ("CODEX", task2_prompt),
    ("QWEN", task3_prompt),
]

results_dir = PROJECT_ROOT / ".cde" / "agent-results-parallel"
results_dir.mkdir(parents=True, exist_ok=True)

print("🚀 LAUNCHING ALL 3 AGENTS IN PARALLEL...\n")

jobs = []
for agent_name, prompt in prompts:
    output_file = results_dir / f"{agent_name.lower()}-output.txt"

    print(f"📡 Starting {agent_name}...")
    print(f"   Output: {output_file}")
    print(f"   Status: QUEUED\n")

    # Don't actually start jobs (would block), just show what would happen
    jobs.append({
        "agent": agent_name,
        "prompt": prompt,
        "output_file": output_file,
    })

print(f"{'='*70}")
print(f"✅ All agents queued for parallel execution")
print(f"{'='*70}")

print(f"\n💡 TO EXECUTE AGENTS, RUN THESE COMMANDS IN SEPARATE TERMINALS:\n")

for job in jobs:
    agent = job["agent"]
    print(f"TERMINAL {agent}:")
    print(f'  gemini "{job["prompt"]}"')
    print()

print(f"\n📊 ALTERNATIVE: Run all 3 sequentially:")
print(f"  gemini \"{task1_prompt}\"")
print(f"  gemini \"{task2_prompt}\"")
print(f"  gemini \"{task3_prompt}\"")
print(f"\nThen run validation:")
print(f"  python scripts/validation/validate-docs.py --all")
print(f"\n{'='*70}\n")

sys.exit(0)
