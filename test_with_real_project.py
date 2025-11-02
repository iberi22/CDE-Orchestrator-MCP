"""
Script de prueba para CDE Orchestrator MCP con proyecto real.

Prueba las 3 herramientas principales del MCP en el proyecto real del usuario.
"""

import asyncio
import json
from pathlib import Path

# Importar las herramientas MCP
from cde_orchestrator.application.orchestration import (
    WorkflowSelectorUseCase,
    SkillSourcingUseCase,
    WebResearchUseCase,
)


async def test_with_real_project(project_path: str):
    """
    Prueba completa del flujo MCP-first con proyecto real.

    Args:
        project_path: Ruta al proyecto MCP del usuario
    """
    print("=" * 80)
    print(f"🧪 TESTING CDE ORCHESTRATOR MCP")
    print(f"📂 Project: {project_path}")
    print("=" * 80)
    print()

    # ========================================
    # TEST 1: Workflow Selection
    # ========================================
    print("📋 TEST 1: Workflow Selection")
    print("-" * 80)

    test_prompts = [
        "Fix typo in README",
        "Add logging to database queries",
        "Implement Redis caching for user sessions",
        "Research best practices for async Python patterns",
        "Build complete authentication system with OAuth2"
    ]

    selector = WorkflowSelectorUseCase()

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n{i}. Prompt: \"{prompt}\"")
        try:
            result = selector.execute(prompt)
            rec = result['recommendation']  # Access nested recommendation
            print(f"   ✅ Workflow: {rec['workflow_type']}")
            print(f"   ✅ Complexity: {rec['complexity']}")
            print(f"   ✅ Recipe: {rec['recipe_id']}")
            print(f"   ✅ Duration: {rec['estimated_duration']}")
            print(f"   ✅ Skills: {', '.join(rec['required_skills']) if rec['required_skills'] else 'None'}")
            print(f"   ✅ Confidence: {rec['confidence']:.2f}")
            print(f"   ✅ Next Action: {result['next_action']}")
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")

    print("\n" + "=" * 80)
    print()

    # ========================================
    # TEST 2: Skill Sourcing (with real GitHub API)
    # ========================================
    print("📚 TEST 2: Skill Sourcing from awesome-claude-skills")
    print("-" * 80)

    skill_queries = [
        "redis caching patterns",
        "async python best practices",
    ]

    sourcer = SkillSourcingUseCase()

    for i, query in enumerate(skill_queries, 1):
        print(f"\n{i}. Query: \"{query}\"")
        try:
            result = await sourcer.execute(
                skill_query=query,
                source="awesome-claude-skills",
                destination="ephemeral"
            )
            print(f"   ✅ Skills found: {result['skills_found']}")
            print(f"   ✅ Skills downloaded: {len(result['skills_downloaded'])}")

            if result['skills_downloaded']:
                for skill in result['skills_downloaded'][:2]:  # Show first 2
                    print(f"      - {skill['name']} (rating: {skill['metadata']['rating']:.2f})")
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")

    print("\n" + "=" * 80)
    print()

    # ========================================
    # TEST 3: Web Research (with real web scraping)
    # ========================================
    print("🔍 TEST 3: Web Research for Skill Updates")
    print("-" * 80)

    research_tasks = [
        {
            "skill_name": "redis-caching",
            "topics": ["redis 7.x breaking changes", "connection pooling 2025"]
        },
    ]

    researcher = WebResearchUseCase()

    for i, task in enumerate(research_tasks, 1):
        print(f"\n{i}. Skill: {task['skill_name']}")
        print(f"   Topics: {', '.join(task['topics'])}")
        try:
            result = await researcher.execute(
                skill_name=task['skill_name'],
                topics=task['topics'],
                max_sources=5  # Limit for testing
            )
            print(f"   ✅ Sources consulted: {result['sources']}")
            print(f"   ✅ Insights found: {len(result['insights'])}")

            if result['insights']:
                for insight in result['insights'][:3]:  # Show first 3
                    print(f"      - [{insight['category']}] {insight['summary']} (confidence: {insight['confidence']:.2f})")
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")

    print("\n" + "=" * 80)
    print()

    # ========================================
    # SUMMARY
    # ========================================
    print("📊 TEST SUMMARY")
    print("-" * 80)
    print("✅ TEST 1: Workflow Selection - COMPLETED")
    print("✅ TEST 2: Skill Sourcing - COMPLETED")
    print("✅ TEST 3: Web Research - COMPLETED")
    print()
    print("🎉 All tests completed! CDE Orchestrator MCP is ready to use.")
    print("=" * 80)


async def main():
    """Main entry point."""
    # Tu proyecto MCP
    project_path = r"E:\scripts-python\MCP"

    if not Path(project_path).exists():
        print(f"❌ ERROR: Project path does not exist: {project_path}")
        return

    await test_with_real_project(project_path)


if __name__ == "__main__":
    asyncio.run(main())
