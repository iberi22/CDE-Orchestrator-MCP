import asyncio
import shutil
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from cde_orchestrator.application.use_cases.start_feature import StartFeatureUseCase
from cde_orchestrator.domain.entities import Feature, Project, ProjectStatus, ProjectId

async def run_test():
    # Setup temp dir
    temp_dir = Path("temp_test_project")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()

    # Create templates
    templates_dir = temp_dir / "specs" / "templates"
    templates_dir.mkdir(parents=True)
    (templates_dir / "spec.md").write_text("# Spec: [FEATURE NAME]", encoding="utf-8")
    (templates_dir / "plan.md").write_text("# Plan: [FEATURE]", encoding="utf-8")
    (templates_dir / "tasks.md").write_text("# Tasks: [FEATURE NAME]", encoding="utf-8")

    # Mock dependencies
    project_repo = MagicMock()
    # Need correct ProjectId type
    pid = ProjectId("test-123")
    project = Project.create(name="TestProject", path=str(temp_dir), project_id=pid)
    project.status = ProjectStatus.ACTIVE

    async def get_or_create(path):
        return project
    project_repo.get_or_create.side_effect = get_or_create

    async def save(p):
        pass
    project_repo.save.side_effect = save

    workflow_repo_factory = MagicMock()
    workflow_repo = MagicMock()
    async def load_workflow():
        return MagicMock(get_initial_phase=lambda: MagicMock(id="define", prompt_recipe="define.poml"))
    workflow_repo.load_workflow.side_effect = load_workflow
    workflow_repo_factory.return_value = workflow_repo

    prompt_renderer = MagicMock()
    async def load_and_prepare(path, context):
        return "Prompt"
    prompt_renderer.load_and_prepare.side_effect = load_and_prepare

    # Init Use Case
    use_case = StartFeatureUseCase(project_repo, workflow_repo_factory, prompt_renderer)

    # Create .cde/workflow.yml to bypass validation check
    (temp_dir / ".cde").mkdir()
    (temp_dir / ".cde" / "workflow.yml").touch()

    # Execute
    print("Executing StartFeatureUseCase...")
    await use_case.execute(
        project_path=str(temp_dir),
        user_prompt="Add login feature",
        workflow_type="standard"
    )

    # Verify
    feature_dir = temp_dir / "specs" / "add-login-feature"

    created_dirs = [d for d in (temp_dir / "specs").iterdir() if d.is_dir() and d.name != "templates"]
    if not created_dirs:
        print("FAIL: No feature directory created")
        return

    feature_path = created_dirs[0]
    print(f"Created feature dir: {feature_path}")

    files = ["spec.md", "plan.md", "tasks.md"]
    all_exist = True
    for f in files:
        if not (feature_path / f).exists():
            print(f"FAIL: Missing {f}")
            all_exist = False
        else:
            content = (feature_path / f).read_text(encoding="utf-8")
            if "[FEATURE NAME]" in content or "[FEATURE]" in content:
                 print(f"FAIL: Placeholder not replaced in {f}: {content}")
                 all_exist = False
            else:
                 print(f"PASS: {f} looks good: {content}")

    if all_exist:
        print("SUCCESS: All files created and parameterized.")

    # Cleanup
    shutil.rmtree(temp_dir)

if __name__ == "__main__":
    asyncio.run(run_test())
