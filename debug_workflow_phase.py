from cde_orchestrator.domain.entities import WorkflowPhase

try:
    wp = WorkflowPhase(
        id="test",
        description="test",
        prompt_recipe="test.poml",
        handler="agent",
        inputs=[],
        outputs=[],
    )
    print("Successfully created WorkflowPhase")
    print(wp)
except Exception as e:
    print(f"Error: {e}")
