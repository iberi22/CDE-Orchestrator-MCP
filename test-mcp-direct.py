#!/usr/bin/env python3
"""
Direct MCP Tool Test - Bypass Gemini CLI
Tests the cde_onboardingProject tool directly via Python
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the MCP server module
try:
    from cde_orchestrator.application.onboarding import OnboardingUseCase
    from cde_orchestrator.adapters.repository.git_adapter import GitAdapter
    from pathlib import Path
    print("✓ Imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)


class MockContext:
    """Mock FastMCP Context for testing"""

    def __init__(self):
        self.messages = []
        self.progress_updates = []

    async def info(self, message: str):
        """Log info message"""
        self.messages.append(("INFO", message))
        print(f"[INFO] {message}")

    async def debug(self, message: str):
        """Log debug message"""
        self.messages.append(("DEBUG", message))
        print(f"[DEBUG] {message}")

    async def error(self, message: str):
        """Log error message"""
        self.messages.append(("ERROR", message))
        print(f"[ERROR] {message}")

    async def report_progress(self, current: float, total: float, message: str):
        """Report progress"""
        self.progress_updates.append((current, total, message))
        percentage = int((current / total) * 100)
        bar_length = 40
        filled = int((current / total) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"[PROGRESS] {bar} {percentage}% - {message}")


async def test_onboarding():
    """Test the onboarding tool directly"""
    print("\n" + "="*60)
    print("🚀 Direct MCP Tool Test - cde_onboardingProject")
    print("="*60 + "\n")

    # Create mock context
    ctx = MockContext()

    # Get project root
    project_root = Path.cwd()
    print(f"Project root: {project_root}\n")

    # Create adapters
    git_adapter = GitAdapter(project_root)
    analyzer = OnboardingUseCase(project_root, git_adapter)

    # Simulate the tool execution with progress tracking
    try:
        # Checkpoint 1: Initialize (0%)
        await ctx.info("🚀 CDE Onboarding Analysis Started")
        await ctx.report_progress(0.0, 1.0, "Initializing onboarding analysis")

        # Checkpoint 2: Scan (20%)
        await ctx.info("📁 Scanning project structure...")
        await ctx.report_progress(0.2, 1.0, "Scanning directory structure")

        # Check if onboarding is needed
        analysis = await analyzer.needs_onboarding()

        # Checkpoint 3: Analysis (40%)
        git_info = analysis.get("project_info", {}).get("git", {})
        commit_count = git_info.get("commit_count", 0)
        missing_count = len(analysis.get("missing_structure", []))

        await ctx.info(f"📊 Analysis: {commit_count} commits, {missing_count} missing items")
        await ctx.report_progress(0.4, 1.0, "Structure analysis complete")

        if not analysis["needs_onboarding"]:
            await ctx.info("✅ Project already configured!")
            await ctx.report_progress(1.0, 1.0, "Analysis complete - no onboarding needed")

            result = {
                "status": "already_configured",
                "message": "Project already has Spec-Kit compatible structure.",
                "existing_structure": analysis["existing_structure"],
            }
        else:
            # Checkpoint 4: Generate plan (60%)
            await ctx.info("📝 Generating onboarding plan...")
            await ctx.report_progress(0.6, 1.0, "Generating comprehensive plan")

            plan = await analyzer.generate_onboarding_plan()

            await ctx.debug(f"Plan generated: {len(plan.get('docs_to_generate', []))} docs, {len(plan.get('structure_to_create', []))} directories")

            # Checkpoint 5: AI Detection (75%)
            await ctx.info("🤖 Detecting AI assistants...")
            await ctx.report_progress(0.75, 1.0, "Detecting AI agents")

            # For simplicity, skip AI detection in direct test
            detected_agents = ["Cursor", "GitHub Copilot"]
            if detected_agents:
                await ctx.info(f"✨ Detected: {', '.join(detected_agents)}")

            # Checkpoint 6: Finalize (90%)
            await ctx.info("📄 Preparing onboarding prompt...")
            await ctx.report_progress(0.9, 1.0, "Finalizing analysis")

            # Checkpoint 7: Complete (100%)
            await ctx.info("✅ Onboarding draft ready!")
            await ctx.report_progress(1.0, 1.0, "Complete - awaiting document generation")

            result = {
                "status": "success",
                "analysis": analysis,
                "plan": plan,
                "detected_agents": detected_agents
            }

        # Print results
        print("\n" + "="*60)
        print("📊 RESULTS")
        print("="*60 + "\n")
        print(json.dumps(result, indent=2, default=str))

        print("\n" + "="*60)
        print("📈 SUMMARY")
        print("="*60 + "\n")
        print(f"Total Messages: {len(ctx.messages)}")
        for msg_type in ["INFO", "DEBUG", "ERROR"]:
            count = sum(1 for t, _ in ctx.messages if t == msg_type)
            print(f"  - {msg_type}: {count}")
        print(f"Total Progress Updates: {len(ctx.progress_updates)}")

        print("\n✅ Test completed successfully!")
        return True

    except Exception as e:
        await ctx.error(f"Test failed: {e}")
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Starting direct MCP tool test...")
    success = asyncio.run(test_onboarding())
    sys.exit(0 if success else 1)
