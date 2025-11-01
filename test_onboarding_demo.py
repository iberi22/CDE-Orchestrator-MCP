#!/usr/bin/env python3
"""
Demo del sistema de onboarding con AI Assistant Configuration.
Este script demuestra cómo funciona el onboarding en nuestro propio proyecto.
"""
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cde_orchestrator.application.ai_config import AIConfigUseCase
from cde_orchestrator.application.onboarding import OnboardingUseCase, SpecKitStructureGenerator


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def main():
    """Run onboarding demo."""
    project_root = Path(__file__).parent

    print_section("🚀 CDE Orchestrator MCP - Onboarding Demo")
    print(f"Project Root: {project_root}\n")

    # Step 1: Analyze project structure
    print_section("📊 Step 1: Analyzing Project Structure")
    analyzer = OnboardingUseCase(project_root)
    analysis = analyzer.needs_onboarding()

    print(f"Needs Onboarding: {analysis['needs_onboarding']}")
    print(f"\nExisting Structure ({len(analysis['existing_structure'])} items):")
    for item in analysis['existing_structure'][:10]:  # Show first 10
        print(f"  ✓ {item}")
    if len(analysis['existing_structure']) > 10:
        print(f"  ... and {len(analysis['existing_structure']) - 10} more")

    print(f"\nMissing Structure ({len(analysis['missing_structure'])} items):")
    for item in analysis['missing_structure']:
        print(f"  ✗ {item}")

    # Step 2: Analyze Git History
    print_section("🔍 Step 2: Analyzing Git History")
    git_info = analysis['project_info']['git']

    print(f"Is Git Repo: {git_info['is_git_repo']}")
    if git_info['is_git_repo']:
        print(f"Total Commits: {git_info['commit_count']}")
        print(f"Project Age: {git_info['project_age_days']} days")
        print(f"Branches: {len(git_info['branches'])}")
        print(f"Active Features: {len(git_info['active_features'])}")

        if git_info['recent_commits']:
            print(f"\nRecent Commits (last 3):")
            for commit in git_info['recent_commits'][:3]:
                print(f"  • {commit['hash']} - {commit['message'][:60]}")
                print(f"    by {commit['author']} on {commit['date']}")

    # Step 3: Detect AI Assistants
    print_section("🤖 Step 3: Detecting AI Assistants")
    ai_configurator = AIAssistantConfigurator(project_root)

    print("Detecting installed AI tools...")
    detected_agents = ai_configurator.detect_installed_agents()

    print(f"\n✓ Detected {len(detected_agents)} AI assistant(s):")
    for agent_key in detected_agents:
        config = ai_configurator.AGENT_CONFIG[agent_key]
        print(f"  • {config.name} ({agent_key})")
        print(f"    - Config Folder: {config.folder}")
        print(f"    - Files to Generate: {', '.join(config.config_files)}")

    if not detected_agents:
        print("  ⚠ No AI assistants detected via CLI")
        print("    Will configure defaults: GitHub Copilot + AGENTS.md")

    # Step 4: Get Configuration Summary
    print_section("📋 Step 4: Configuration Summary")
    summary = ai_configurator.get_configuration_summary()

    print(f"Total AI Assistants Supported: {summary['total_agents']}")
    print(f"Detected on System: {len(summary['detected_agents'])}")
    print(f"Already Configured: {len(summary['configured_agents'])}")

    print(f"\nAvailable AI Assistants:")
    for agent_key in summary['available_agents']:
        config = ai_configurator.AGENT_CONFIG[agent_key]
        status = "✓ Configured" if agent_key in summary['configured_agents'] else "○ Available"
        detected = "🔍 Detected" if agent_key in summary['detected_agents'] else ""
        print(f"  {status} {config.name:20} {detected}")

    # Step 5: Check what files exist
    print_section("📂 Step 5: Checking Existing AI Config Files")

    config_files_to_check = [
        "AGENTS.md",
        "GEMINI.md",
        ".github/copilot-instructions.md",
        ".claude/",
        ".cursor/",
        ".windsurf/",
        ".gemini/"
    ]

    print("AI Assistant Configuration Files:")
    for file_path in config_files_to_check:
        full_path = project_root / file_path
        exists = full_path.exists()
        status = "✓ EXISTS" if exists else "✗ MISSING"
        file_type = "📁 Folder" if file_path.endswith("/") else "📄 File"
        print(f"  {status:12} {file_type} {file_path}")

        if exists and not file_path.endswith("/"):
            size = full_path.stat().st_size
            print(f"               Size: {size:,} bytes")

    # Step 6: Simulate onboarding (dry-run)
    print_section("🎯 Step 6: Simulating Onboarding (Dry Run)")

    if analysis['needs_onboarding']:
        print("✓ Onboarding needed - would create:")
        plan = analyzer.generate_onboarding_plan()

        for item in plan.get("structure_to_create", []):
            if item["type"] == "directory":
                print(f"  📁 {item['path']}/")

        print("\n✓ AI Assistant configuration would generate:")
        # Simulate what would be generated
        agents_to_config = detected_agents if detected_agents else ["copilot"]
        for agent_key in agents_to_config:
            if agent_key in ai_configurator.AGENT_CONFIG:
                config = ai_configurator.AGENT_CONFIG[agent_key]
                for config_file in config.config_files:
                    if config_file in ["AGENTS.md", "GEMINI.md"]:
                        print(f"  📄 {config_file}")
                    else:
                        print(f"  📄 {config.folder}{config_file}")
    else:
        print("✓ Project already has Spec-Kit structure")
        print("✓ AI Assistant configuration files:")

        existing_configs = []
        for agent_key in summary['configured_agents']:
            config = ai_configurator.AGENT_CONFIG[agent_key]
            for config_file in config.config_files:
                file_path = config_file if config_file in ["AGENTS.md", "GEMINI.md"] else f"{config.folder}{config_file}"
                if (project_root / file_path).exists():
                    existing_configs.append(file_path)

        for config_file in existing_configs:
            print(f"  ✓ {config_file}")

    # Step 7: Summary
    print_section("✨ Summary")

    print("Onboarding Status:")
    print(f"  • Project Structure: {'✓ Complete' if not analysis['needs_onboarding'] else '⚠ Needs Setup'}")
    print(f"  • Git Repository: {'✓ Initialized' if git_info['is_git_repo'] else '✗ Not initialized'}")
    print(f"  • AI Assistants Detected: {len(detected_agents)}")
    print(f"  • AI Assistants Configured: {len(summary['configured_agents'])}")

    print(f"\nAI Assistant Configuration:")
    for agent_key in summary['available_agents'][:6]:  # Show top 6
        config = ai_configurator.AGENT_CONFIG[agent_key]
        detected = "🔍" if agent_key in detected_agents else " "
        configured = "✓" if agent_key in summary['configured_agents'] else "○"
        print(f"  {detected} {configured} {config.name}")

    print("\n" + "=" * 80)
    print("  Demo Complete!")
    print("=" * 80)
    print("\nThis demonstrates:")
    print("  1. ✓ Project structure analysis")
    print("  2. ✓ Git history analysis")
    print("  3. ✓ AI assistant auto-detection")
    print("  4. ✓ Configuration file management")
    print("  5. ✓ Spec-Kit compatibility")
    print("\nTo actually run onboarding, use the MCP tool:")
    print("  >>> cde_onboardingProject()")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
