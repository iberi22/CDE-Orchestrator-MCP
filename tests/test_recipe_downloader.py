"""
Test script for recipe downloader.

Tests downloading recipes from GitHub to .cde/ directory.
"""

import json
import sys
import pytest
import asyncio
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from cde_orchestrator.adapters.recipe import GitHubRecipeDownloader
from cde_orchestrator.application.orchestration import RecipeDownloaderUseCase


@pytest.mark.asyncio
async def test_download_recipes():
    """Test downloading recipes to a test directory."""
    print("🧪 Testing Recipe Downloader...")
    print("=" * 60)

    # Create test directory
    test_dir = Path(__file__).parent / "test_project"
    test_dir.mkdir(exist_ok=True)

    print(f"\n📁 Test directory: {test_dir}")

    # Create downloader
    downloader = GitHubRecipeDownloader(timeout=60)
    use_case = RecipeDownloaderUseCase(downloader=downloader)

    # Test 1: Check if .cde/ exists
    print("\n1️⃣ Checking if .cde/ exists...")
    exists = use_case.check_cde_exists(str(test_dir))
    print(f"   Result: .cde/ {'exists' if exists else 'does NOT exist'}")

    # Test 2: Download recipes
    print("\n2️⃣ Downloading recipes from GitHub...")
    result = await use_case.execute(
        project_path=str(test_dir),
        repo_url="https://github.com/iberi22/agents-flows-recipes",
        branch="main",
        force=True  # Force to allow re-download for testing
    )

    print(f"   Status: {result['status']}")
    print(f"   Message: {result['message']}")
    print(f"   Destination: {result['destination']}")
    print(f"   Files downloaded: {len(result['files_downloaded'])}")

    if result.get('errors'):
        print(f"\n⚠️  Errors encountered:")
        for error in result['errors']:
            print(f"   - {error}")

    # Test 3: Verify files
    print("\n3️⃣ Verifying downloaded files...")
    cde_dir = test_dir / ".cde"

    expected_files = [
        "recipes/engineering/ai-engineer.poml",
        "recipes/engineering/backend-architect.poml",
        "recipes/engineering/test-writer-fixer.poml",
        "recipes/design/brand-guardian.poml",
        "recipes/product/sprint-prioritizer.poml",
        "recipes/testing/workflow-optimizer.poml",
        "recipes/bonus/studio-coach.poml",
        "docs/qwen-rules.md",
        "docs/advanced-techniques.md",
    ]

    for expected_file in expected_files:
        file_path = cde_dir / expected_file
        if file_path.exists():
            print(f"   ✅ {expected_file}")
        else:
            print(f"   ❌ {expected_file} (MISSING)")

    # Test 4: Ensure workflow.yml
    print("\n4️⃣ Ensuring workflow.yml exists...")
    workflow_result = use_case.ensure_workflow_yml(str(test_dir))
    print(f"   Status: {workflow_result['status']}")
    print(f"   Message: {workflow_result['message']}")
    print(f"   Path: {workflow_result['path']}")

    # Test 5: Verify workflow.yml content
    workflow_file = cde_dir / "workflow.yml"
    if workflow_file.exists():
        print("\n5️⃣ Workflow.yml content preview:")
        content = workflow_file.read_text(encoding="utf-8")
        lines = content.split("\n")[:20]
        for line in lines:
            print(f"   {line}")
        print(f"   ... ({len(content.split(chr(10)))} lines total)")

    # Test 6: Check again
    print("\n6️⃣ Checking if .cde/ exists now...")
    exists_after = use_case.check_cde_exists(str(test_dir))
    print(f"   Result: .cde/ {'exists' if exists_after else 'does NOT exist'}")

    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print(f"\n📁 You can inspect the downloaded files at: {cde_dir}")

    return result


if __name__ == "__main__":
    try:
        result = test_download_recipes()
        print("\n📊 Final Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
