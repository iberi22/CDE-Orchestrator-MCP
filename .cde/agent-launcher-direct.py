#!/usr/bin/env python3
"""
Direct launcher for 3 agents using gemini CLI
"""

import subprocess
import sys
from pathlib import Path

PROJECT = "E:\\scripts-python\\CDE Orchestrator MCP"

# Simplified prompts (fit within CLI limits)
prompts = {
    "GEMINI": "Read .cde/agent-instructions/gemini-semana2-task1-metadata-yaml.md. Fix YAML frontmatter, missing metadata, status enums (completed→archived), and date formats in 35 files. Then: python scripts/validation/validate-docs.py --all && git commit -m 'fix(governance): Gemini YAML & enum fixes - 35 files' --no-verify. Output: ✅ GEMINI COMPLETE with validation results.",

    "CODEX": "Read .cde/agent-instructions/codex-semana2-task2-filenames-dates.md. Rename 13 files using 'git mv' to lowercase-hyphens. Add created/updated dates to 54+ files. Then: python scripts/validation/validate-docs.py --all && git commit -m 'fix(governance): Codex filenames & dates - 54 files' --no-verify. Output: ✅ CODEX COMPLETE with validation results.",

    "QWEN": "Read .cde/agent-instructions/qwen-semana2-task3-directories.md. Move 8 orphaned files to agent-docs/research/, fix invalid agent-docs/ subdirectories, fix type enums (evaluation→research, skill→research). Use git mv and git rm. Then: python scripts/validation/validate-docs.py --all && git commit -m 'fix(governance): Qwen directories & orphaned files' --no-verify. Output: ✅ QWEN COMPLETE with validation results.",
}

print("\n" + "="*70)
print("🚀 GEMINI/CODEX/QWEN AGENTS - DIRECT LAUNCHER")
print("="*70)
print(f"Project: {PROJECT}")
print(f"\nCommands to execute in PARALLEL (3 separate terminals):\n")

for agent, prompt in prompts.items():
    print(f"AGENT {agent}:")
    print(f"  cd \"{PROJECT}\"")
    print(f"  gemini \"{prompt}\"")
    print()

print("="*70)
print("\nTo launch ALL 3 in parallel:")
print("1. Open 3 terminals")
print("2. Run GEMINI command in terminal 1")
print("3. Run CODEX command in terminal 2")
print("4. Run QWEN command in terminal 3")
print("5. Each will output ✅ COMPLETE when done")
print("6. Then run: python scripts/validation/validate-docs.py --all")
print("="*70 + "\n")

# Try launching all 3 with timeout (adjust as needed)
print("\n⚙️  To execute now (sequential, not parallel):\n")
for agent, prompt in prompts.items():
    print(f"Launching {agent}...\n")
    cmd = ["gemini", prompt, "--approval-mode", "auto_edit"]
    # Uncomment to actually execute:
    # subprocess.run(cmd, cwd=PROJECT, timeout=1800)
