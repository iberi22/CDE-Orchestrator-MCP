#!/usr/bin/env python3
"""
🚀 LAUNCH THREE AGENTS - DIRECT EXECUTION
==========================================

Lanza 3 agentes AI directamente usando gemini CLI con archivos de prompt.
Cada agente recibe su propia tarea separada en paralelo.
"""

import subprocess
import json
import sys
import time
import threading
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
AGENT_INSTRUCTIONS_DIR = PROJECT_ROOT / ".cde" / "agent-instructions"
RESULTS_DIR = PROJECT_ROOT / ".cde" / "agent-results-parallel"
RESULTS_DIR.mkdir(exist_ok=True, parents=True)

# Agent task definitions
AGENTS = {
    "GEMINI-YAML": {
        "name": "GEMINI",
        "task_id": "SEMANA2-YAML-FIXES",
        "task_file": "gemini-semana2-task1-metadata-yaml.md",
        "description": "Fix YAML frontmatter & status enums (35 files)",
    },
    "CODEX-FILES": {
        "name": "CODEX",
        "task_id": "SEMANA2-FILENAMES",
        "task_file": "codex-semana2-task2-filenames-dates.md",
        "description": "Normalize filenames & add dates (54 files)",
    },
    "QWEN-DIRS": {
        "name": "QWEN",
        "task_id": "SEMANA2-DIRECTORIES",
        "task_file": "qwen-semana2-task3-directories.md",
        "description": "Fix directories & move orphaned files (12+ files)",
    }
}


def get_agent_system_prompt(agent_key):
    """Retorna el system prompt específico para cada agente."""

    prompts = {
        "GEMINI-YAML": """You are GEMINI-AGENT-1, specialized in YAML and metadata validation.

Your task: Fix 35 documentation files with YAML frontmatter issues.

Work approach:
1. Systematically go through each file mentioned
2. Identify specific issues (quoted scalars, missing frontmatter, wrong status, wrong dates)
3. Apply fixes precisely as specified
4. After all fixes, run validation and commit
5. Report completion status

You MUST use git commands to commit your changes.
Work directory: E:\\scripts-python\\CDE Orchestrator MCP

Success indicator: Output "✅ GEMINI TASK 1 COMPLETE" when done.""",

        "CODEX-FILES": """You are CODEX-AGENT-2, specialized in file operations and normalization.

Your task: Normalize 13 filenames and add 54 date fields.

Work approach:
1. Use git mv for all filename changes (preserves history)
2. Add created/updated dates to frontmatter fields
3. After all changes, run validation
4. Commit all changes together
5. Report completion status

You MUST use git commands for all file operations.
Work directory: E:\\scripts-python\\CDE Orchestrator MCP

Success indicator: Output "✅ CODEX TASK 2 COMPLETE" when done.""",

        "QWEN-DIRS": """You are QWEN-AGENT-3, specialized in directory structure and organization.

Your task: Reorganize directories and move 12+ orphaned files.

Work approach:
1. Move orphaned files from .amazonq, .copilot, .jules to agent-docs/research/
2. Fix invalid agent-docs/ subdirectories
3. Fix invalid type enums
4. Run validation and commit
5. Report completion status

You MUST use git mv and git rm commands.
Work directory: E:\\scripts-python\\CDE Orchestrator MCP

Success indicator: Output "✅ QWEN TASK 3 COMPLETE" when done."""
    }

    return prompts.get(agent_key, "")


def create_agent_prompt(agent_key):
    """Crea el prompt completo para cada agente."""

    task_file = AGENT_INSTRUCTIONS_DIR / AGENTS[agent_key]["task_file"]

    if not task_file.exists():
        return None

    with open(task_file, 'r', encoding='utf-8') as f:
        task_instructions = f.read()

    system_prompt = get_agent_system_prompt(agent_key)

    combined_prompt = f"""{system_prompt}

DETAILED TASK INSTRUCTIONS:
===========================

{task_instructions}

CRITICAL REMINDERS:
- Always use git for all file operations
- After completing fixes, run: python scripts/validation/validate-docs.py --all
- Commit with appropriate semantic message
- End with either "✅ TASK COMPLETE" or "❌ TASK FAILED" plus summary"""

    return combined_prompt


def launch_agent_gemini_cli(agent_key):
    """Lanza un agente usando gemini CLI."""

    agent_name = AGENTS[agent_key]["name"]
    print(f"\n{'='*70}")
    print(f"🚀 Launching {agent_name} Agent")
    print(f"{'='*70}")
    print(f"Task ID: {AGENTS[agent_key]['task_id']}")
    print(f"Description: {AGENTS[agent_key]['description']}")
    print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")

    # Create prompt
    prompt = create_agent_prompt(agent_key)
    if not prompt:
        print(f"❌ Failed to create prompt for {agent_name}")
        return {
            "agent": agent_name,
            "status": "FAILED",
            "error": "Could not create prompt",
            "timestamp": datetime.now().isoformat(),
        }

    # Save prompt to temporary file
    prompt_file = RESULTS_DIR / f"{agent_key.lower()}-prompt.md"
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(prompt)

    output_file = RESULTS_DIR / f"{agent_key.lower()}-output.txt"

    print(f"📝 Prompt saved: {prompt_file}")
    print(f"📄 Output will be saved to: {output_file}")

    try:
        # Execute gemini CLI with prompt from file
        cmd = [
            "gemini",
            "--read", str(prompt_file),
            "--output", str(output_file),
        ]

        print(f"⏳ Running: gemini --read {prompt_file.name} --output {output_file.name}")
        print(f"   (This may take 5-15 minutes per agent)...")

        result = subprocess.run(
            cmd,
            capture_output=False,
            text=True,
            timeout=1800,  # 30 minutes
            cwd=str(PROJECT_ROOT)
        )

        # Read output
        output_text = ""
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                output_text = f.read()

        # Determine if complete (look for success marker)
        completed = f"✅ {agent_name.upper()} TASK" in output_text.upper()

        print(f"\n{'='*70}")
        if completed:
            print(f"✅ {agent_name} Task Completed Successfully")
        else:
            print(f"⚠️  {agent_name} Task Status Unclear (Check output file)")
        print(f"Return Code: {result.returncode}")
        print(f"Output file: {output_file}")
        print(f"{'='*70}")

        return {
            "agent": agent_name,
            "status": "COMPLETED" if completed else "COMPLETED_UNCLEAR",
            "return_code": result.returncode,
            "output_file": str(output_file),
            "timestamp": datetime.now().isoformat(),
        }

    except subprocess.TimeoutExpired:
        print(f"❌ {agent_name}: Timeout after 30 minutes")
        return {
            "agent": agent_name,
            "status": "TIMEOUT",
            "error": "Execution timeout (30 minutes)",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        print(f"❌ {agent_name}: {str(e)}")
        return {
            "agent": agent_name,
            "status": "FAILED",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


def main():
    """Main orchestration function."""

    print("\n" + "="*70)
    print("🎯 SEMANA 2 - THREE-AGENT PARALLEL ORCHESTRATION")
    print("="*70)
    print(f"Project: {PROJECT_ROOT}")
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Results dir: {RESULTS_DIR}")
    print("\n📋 Agent Assignments:")
    print("  1️⃣  GEMINI  (Agent 1) - YAML frontmatter & status enums (35 files)")
    print("  2️⃣  CODEX   (Agent 2) - Filename normalization & dates (54 files)")
    print("  3️⃣  QWEN    (Agent 3) - Directory structure & orphaned files (12+ files)")
    print("\n⚙️  Execution Mode: PARALLEL HEADLESS (via Gemini CLI)")
    print("⏱️  Timeout: 30 minutes per agent")
    print("="*70)

    # Launch all 3 agents in parallel
    results = {}
    start_time = time.time()

    print("\n📡 Launching agents in parallel threads...\n")

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_agent = {
            executor.submit(launch_agent_gemini_cli, agent_key): agent_key
            for agent_key in ["GEMINI-YAML", "CODEX-FILES", "QWEN-DIRS"]
        }

        # Collect results as they complete
        for future in as_completed(future_to_agent):
            agent_key = future_to_agent[future]
            try:
                result = future.result()
                agent_name = result.get("agent", "UNKNOWN")
                results[agent_name] = result
            except Exception as e:
                agent_name = AGENTS[agent_key]["name"]
                results[agent_name] = {
                    "agent": agent_name,
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

    elapsed = time.time() - start_time

    # Print summary
    print("\n" + "="*70)
    print("📊 EXECUTION SUMMARY")
    print("="*70)

    completed_count = 0

    for agent_key in ["GEMINI-YAML", "CODEX-FILES", "QWEN-DIRS"]:
        agent_name = AGENTS[agent_key]["name"]
        result = results.get(agent_name, {})
        status = result.get("status", "UNKNOWN")

        if status in ["COMPLETED", "COMPLETED_UNCLEAR"]:
            icon = "✅"
            completed_count += 1
        else:
            icon = "❌"

        print(f"{icon} {agent_name:8} | {status:20} | {result.get('error', 'OK')}")

    print(f"\n📈 Results: {completed_count}/3 agents completed")
    print(f"⏱️  Total execution time: {elapsed/60:.1f} minutes ({elapsed:.0f} seconds)")

    # Save orchestration results
    orchestration_file = RESULTS_DIR / "orchestration-summary.json"
    with open(orchestration_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": elapsed,
            "agents_completed": completed_count,
            "agents_total": 3,
            "results": results,
        }, f, indent=2)

    print(f"\n📄 Summary saved: {orchestration_file}")

    # Post-execution validation
    print("\n" + "="*70)
    print("🔍 POST-EXECUTION VALIDATION")
    print("="*70)

    print("\nRunning governance validation...\n")

    try:
        result = subprocess.run(
            ["python", "scripts/validation/validate-docs.py", "--all"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )

        # Show last lines (summary)
        output_lines = result.stdout.split('\n')
        for line in output_lines[-10:]:
            if line.strip():
                print(line)

    except Exception as e:
        print(f"⚠️  Could not run validation: {e}")

    # Next steps
    print("\n" + "="*70)
    print("🎯 NEXT STEPS")
    print("="*70)
    print(f"1. Review output files in: {RESULTS_DIR}")
    print(f"2. Check git status: git status")
    print(f"3. Review commits: git log --oneline -5")
    print(f"4. Full validation: python scripts/validation/validate-docs.py --all")
    print(f"5. Expected target: < 50 errors (currently 88)")
    print("="*70 + "\n")

    return 0 if completed_count == 3 else 1


if __name__ == "__main__":
    sys.exit(main())
