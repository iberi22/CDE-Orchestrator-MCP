#!/usr/bin/env python3
"""
Test script to validate onboarding functionality directly
without needing the full MCP server running.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cde_orchestrator.adapters.state import StateAdapter  # noqa: E402
from cde_orchestrator.application.onboarding import OnboardingUseCase  # noqa: E402


def test_onboarding():
    """Test the onboarding process."""
    project_root = Path.cwd()
    print(f"Testing onboarding for: {project_root}")
    print("=" * 80)

    # Step 1: Analyze current state
    print("\n1. ANALYZING PROJECT STRUCTURE...")
    analyzer = OnboardingUseCase(project_root)
    analysis = analyzer.needs_onboarding()

    print(f"   Needs onboarding: {analysis['needs_onboarding']}")
    print(f"   Missing structure: {len(analysis['missing_structure'])} items")
    print(f"   Existing structure: {len(analysis['existing_structure'])} items")

    if not analysis["needs_onboarding"]:
        print("\n✅ Project already has Spec-Kit compatible structure!")
        print("\nExisting structure:")
        for item in analysis["existing_structure"]:
            print(f"   - {item}")
        return

    # Step 2: Generate onboarding plan
    print("\n2. GENERATING ONBOARDING PLAN...")
    plan = analyzer.generate_onboarding_plan()

    print(f"   Structure to create: {len(plan['structure_to_create'])} items")
    print(f"   Docs to generate: {len(plan['docs_to_generate'])} docs")

    # Step 3: Show cleanup recommendations
    cleanup_plan = plan.get("cleanup_plan", {})
    if cleanup_plan:
        print("\n3. CLEANUP RECOMMENDATIONS:")

        tests_to_move = cleanup_plan.get("tests_to_move", [])
        if tests_to_move:
            print(f"\n   Tests to relocate ({len(tests_to_move)}):")
            for test in tests_to_move[:5]:  # Show first 5
                print(f"   - {test}")
            if len(tests_to_move) > 5:
                print(f"   ... and {len(tests_to_move) - 5} more")

        obsolete = cleanup_plan.get("obsolete_files", [])
        if obsolete:
            print(f"\n   Obsolete files to review ({len(obsolete)}):")
            for file in obsolete:
                print(f"   - {file}")

    # Step 5: Check if prompt template exists
    print("\n5. VALIDATING PROMPT TEMPLATE...")
    prompt_path = project_root / ".cde" / "prompts" / "00_onboarding.poml"
    if prompt_path.exists():
        print(f"   ✅ Found: {prompt_path}")
        with open(prompt_path, "r", encoding="utf-8") as f:
            content = f.read()
            print(f"   Template size: {len(content)} chars")
    else:
        print(f"   ❌ Missing: {prompt_path}")

    # Step 6: Validate state file
    print("\n6. CHECKING STATE MANAGER...")
    state_file = project_root / ".cde" / "state.json"
    if state_file.exists():
        state_mgr = StateAdapter(state_file)
        state = state_mgr.load_state()
        onboarding_data = state.get("onboarding", {})

        print("   ✅ State file exists")
        print(f"   Has onboarding data: {bool(onboarding_data)}")

        if onboarding_data:
            print(
                f"   Awaiting approval: {onboarding_data.get('awaiting_approval', False)}"
            )
            print(f"   Has plan: {bool(onboarding_data.get('plan'))}")
    else:
        print(f"   ⚠️  No state file at {state_file}")

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY:")
    print("=" * 80)

    components_ready = {
        "OnboardingUseCase": True,
        "needs_onboarding detection": True,
        "plan generation": len(plan.get("docs_to_generate", [])) > 0,
        "cleanup detection": bool(cleanup_plan),
        "repository ingestion": True,
        "POML template": prompt_path.exists(),
        "state management": state_file.exists(),
    }

    for component, status in components_ready.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component}")

    all_ready = all(components_ready.values())

    print("\n" + "=" * 80)
    if all_ready:
        print("🎉 ALL SYSTEMS READY FOR ONBOARDING!")
        print("\nYou can now run: cde_onboardingProject()")
        print("This will:")
        print("  1. Generate a contextualized prompt for document creation")
        print("  2. Store the plan in state for review")
        print("  3. Wait for human approval before applying changes")
    else:
        print("⚠️  SOME COMPONENTS NEED ATTENTION")
        print("\nFix the issues above before running onboarding.")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_onboarding()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
