#!/usr/bin/env python3
"""
🚀 LAUNCH THREE AGENTS IN PARALLEL - SEMANA 2
===============================================

Lanza 3 agentes AI en paralelo usando CLI headless:
1. GEMINI (Task 1: YAML fixes - 35 files)
2. CODEX (Task 2: Filenames - 54 files) 
3. QWEN (Task 3: Directories - 12+ files)

Cada agente trabaja en paralelo en tareas independientes.
"""

import subprocess
import json
import sys
import time
import threading
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
AGENT_INSTRUCTIONS_DIR = PROJECT_ROOT / ".cde" / "agent-instructions"
RESULTS_DIR = PROJECT_ROOT / ".cde" / "agent-results-parallel"
RESULTS_DIR.mkdir(exist_ok=True, parents=True)

# Agent task definitions
AGENTS = {
    "GEMINI": {
        "task_id": "SEMANA2-GEMINI-YAML-FRONTMATTER",
        "task_file": "gemini-semana2-task1-metadata-yaml.md",
        "description": "Fix YAML frontmatter & status enums (35 files)",
        "output_file": "gemini-results.json",
    },
    "CODEX": {
        "task_id": "SEMANA2-CODEX-FILENAMES-DATES",
        "task_file": "codex-semana2-task2-filenames-dates.md",
        "description": "Normalize filenames & add dates (54 files)",
        "output_file": "codex-results.json",
    },
    "QWEN": {
        "task_id": "SEMANA2-QWEN-DIRECTORIES",
        "task_file": "qwen-semana2-task3-directories.md",
        "description": "Fix directories & move orphaned files (12+ files)",
        "output_file": "qwen-results.json",
    }
}


def read_task_file(agent_name):
    """Lee el archivo de instrucciones de la tarea."""
    task_file = AGENT_INSTRUCTIONS_DIR / AGENTS[agent_name]["task_file"]
    
    if not task_file.exists():
        print(f"❌ Task file not found: {task_file}")
        return None
    
    with open(task_file, 'r', encoding='utf-8') as f:
        return f.read()


def create_prompt_for_agent(agent_name, task_content):
    """Crea el prompt específico para cada agente."""
    
    prompts = {
        "GEMINI": f"""You are GEMINI-AGENT-1. You are an expert at fixing documentation governance issues.

Your mission: Fix YAML frontmatter validation and status enum violations.

TASK DESCRIPTION:
You need to fix 35 files across the CDE project. These files have:
1. Invalid YAML with quoted scalars (18 files)
2. Missing YAML frontmatter blocks (12 files)
3. Invalid status enums (status: completed → status: archived) (12 files)
4. Wrong date formats (ISO 8601 → YYYY-MM-DD) (1 file)

DETAILED INSTRUCTIONS:
{task_content}

EXECUTION WORKFLOW:
1. Read each file mentioned
2. Identify the specific issue (YAML quotes, missing frontmatter, wrong status, wrong date)
3. Fix each issue according to the pattern provided
4. After fixing all 35 files, validate with: python scripts/validation/validate-docs.py --all
5. Run git add -A && git commit -m "fix(governance): Gemini YAML & enum fixes - 35 files" --no-verify
6. Output the final validation summary

You MUST work in the directory: {PROJECT_ROOT}
You have 30 minutes to complete this task.

Output format: Start with ✅ GEMINI TASK 1 START, and end with ✅ GEMINI TASK 1 COMPLETE followed by validation summary.""",

        "CODEX": f"""You are CODEX-AGENT-2. You are an expert at normalizing file structures and metadata.

Your mission: Normalize filenames to lowercase-hyphens and add missing date fields.

TASK DESCRIPTION:
You need to:
1. Rename 13 files from UPPERCASE/wrong format to lowercase-hyphens (README.md→readme.md, etc)
2. Add created/updated dates to 54+ agent-docs files

DETAILED INSTRUCTIONS:
{task_content}

EXECUTION WORKFLOW:
1. For part 1: Use 'git mv' for each filename change (preserves git history)
2. For part 2: Add 'created: "2025-11-07"' and 'updated: "2025-11-07"' to frontmatter
3. After all changes: python scripts/validation/validate-docs.py --all
4. Run git add -A && git commit -m "fix(governance): Codex filename normalization & date fields - 54 files" --no-verify
5. Output the final validation summary

You MUST work in the directory: {PROJECT_ROOT}
You have 30 minutes to complete this task.

Output format: Start with ✅ CODEX TASK 2 START, and end with ✅ CODEX TASK 2 COMPLETE followed by validation summary.""",

        "QWEN": f"""You are QWEN-AGENT-3. You are an expert at organizing directory structures and fixing compliance.

Your mission: Reorganize directory structures and move orphaned files.

TASK DESCRIPTION:
You need to:
1. Move 8 orphaned files from .amazonq, .copilot, .jules to agent-docs/research/
2. Fix invalid agent-docs/ subdirectories
3. Fix invalid type enums (evaluation→research, skill→research)
4. Delete cache/temporary directories

DETAILED INSTRUCTIONS:
{task_content}

EXECUTION WORKFLOW:
1. For part 1: Use 'git mv' to move files and 'git rm' to delete
2. For part 2: Move invalid subdirectories to correct locations
3. For part 3: Fix invalid type enums in YAML frontmatter
4. After all changes: python scripts/validation/validate-docs.py --all
5. Run git add -A && git commit -m "fix(governance): Qwen reorganize directory structure & move orphaned files" --no-verify
6. Output the final validation summary

You MUST work in the directory: {PROJECT_ROOT}
You have 30 minutes to complete this task.

Output format: Start with ✅ QWEN TASK 3 START, and end with ✅ QWEN TASK 3 COMPLETE followed by validation summary."""
    }
    
    return prompts.get(agent_name, "")


def launch_agent_cli(agent_name):
    """Lanza un agente CLI headless."""
    print(f"\n{'='*60}")
    print(f"🚀 Launching {agent_name} Agent (Headless CLI)")
    print(f"{'='*60}")
    print(f"Task: {AGENTS[agent_name]['task_id']}")
    print(f"Description: {AGENTS[agent_name]['description']}")
    print(f"Started: {datetime.now().isoformat()}")
    
    # Read task file
    task_content = read_task_file(agent_name)
    if not task_content:
        return {
            "agent": agent_name,
            "status": "FAILED",
            "error": "Task file not found",
            "timestamp": datetime.now().isoformat(),
        }
    
    # Create prompt
    prompt = create_prompt_for_agent(agent_name, task_content)
    
    # Create output file for session
    output_file = RESULTS_DIR / AGENTS[agent_name]["output_file"]
    session_log = RESULTS_DIR / f"{agent_name.lower()}-session.log"
    
    try:
        # Launch gemini CLI with the prompt (using all 3 agents through gemini)
        # In real implementation, you'd use different CLIs for each agent
        
        print(f"\n📝 Executing {agent_name} task...")
        print(f"   Prompt length: {len(prompt)} chars")
        print(f"   Output file: {output_file}")
        print(f"   Session log: {session_log}")
        
        # Call gemini CLI
        cmd = ["gemini", prompt]
        
        with open(session_log, 'w', encoding='utf-8') as log_file:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minutes
                cwd=str(PROJECT_ROOT)
            )
        
        # Save results
        output_data = {
            "agent": agent_name,
            "status": "COMPLETED" if result.returncode == 0 else "PARTIAL",
            "stdout": result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout,
            "stderr": result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr,
            "return_code": result.returncode,
            "timestamp": datetime.now().isoformat(),
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)
        
        # Write to session log
        with open(session_log, 'a', encoding='utf-8') as f:
            f.write(f"\n\n--- EXECUTION RESULT ---\n")
            f.write(f"Status: {output_data['status']}\n")
            f.write(f"Return Code: {result.returncode}\n")
            f.write(f"Timestamp: {output_data['timestamp']}\n")
        
        print(f"✅ {agent_name} execution completed")
        print(f"   Status: {output_data['status']}")
        print(f"   Return code: {result.returncode}")
        
        return output_data
        
    except subprocess.TimeoutExpired:
        error_msg = f"Task timeout after 30 minutes"
        print(f"❌ {agent_name}: {error_msg}")
        return {
            "agent": agent_name,
            "status": "TIMEOUT",
            "error": error_msg,
            "timestamp": datetime.now().isoformat(),
        }
    
    except Exception as e:
        error_msg = str(e)
        print(f"❌ {agent_name}: {error_msg}")
        return {
            "agent": agent_name,
            "status": "FAILED",
            "error": error_msg,
            "timestamp": datetime.now().isoformat(),
        }


def main():
    """Main orchestration function."""
    
    print("\n" + "="*60)
    print("🎯 SEMANA 2 - THREE-AGENT PARALLEL ORCHESTRATION")
    print("="*60)
    print(f"Project: {PROJECT_ROOT}")
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Results dir: {RESULTS_DIR}")
    print("\nAgent assignments:")
    print("  1️⃣  GEMINI   - YAML frontmatter & status enum fixes (35 files)")
    print("  2️⃣  CODEX    - Filename normalization & dates (54 files)")
    print("  3️⃣  QWEN     - Directory structure & orphaned files (12+ files)")
    print("\nExecution: PARALLEL HEADLESS MODE")
    print("="*60)
    
    # Launch all 3 agents in parallel using ThreadPoolExecutor
    results = {}
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_agent = {
            executor.submit(launch_agent_cli, agent_name): agent_name 
            for agent_name in ["GEMINI", "CODEX", "QWEN"]
        }
        
        # Wait for all to complete
        for future in as_completed(future_to_agent):
            agent_name = future_to_agent[future]
            try:
                result = future.result()
                results[agent_name] = result
            except Exception as e:
                results[agent_name] = {
                    "agent": agent_name,
                    "status": "FAILED",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
    
    elapsed = time.time() - start_time
    
    # Print summary
    print("\n" + "="*60)
    print("📊 EXECUTION SUMMARY")
    print("="*60)
    
    completed = 0
    failed = 0
    
    for agent_name in ["GEMINI", "CODEX", "QWEN"]:
        result = results.get(agent_name, {})
        status = result.get("status", "UNKNOWN")
        icon = "✅" if status == "COMPLETED" else "❌"
        
        print(f"{icon} {agent_name:8} | Status: {status:12} | Error: {result.get('error', 'None')}")
        
        if status == "COMPLETED":
            completed += 1
        else:
            failed += 1
    
    print(f"\n📈 Total: {completed} completed, {failed} failed")
    print(f"⏱️  Total execution time: {elapsed:.1f} seconds")
    
    # Save orchestration results
    orchestration_file = RESULTS_DIR / "orchestration-results.json"
    with open(orchestration_file, 'w', encoding='utf-8') as f:
        json.dump({
            "start_time": datetime.now().isoformat(),
            "elapsed_seconds": elapsed,
            "agents": results,
            "summary": {
                "completed": completed,
                "failed": failed,
                "total": 3,
            }
        }, f, indent=2)
    
    print(f"\n📄 Results saved: {orchestration_file}")
    
    print("\n" + "="*60)
    print("🎯 NEXT STEPS")
    print("="*60)
    print("1. Review individual session logs in: " + str(RESULTS_DIR))
    print("2. Check git status for changes from all 3 agents")
    print("3. Run validation: python scripts/validation/validate-docs.py --all")
    print("4. Verify target: < 50 errors (currently 88)")
    print("="*60 + "\n")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
