# src/cde_orchestrator/models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class WorkflowInput(BaseModel):
    """Defines an input artifact for a workflow phase."""
    type: str
    path: str

class WorkflowOutput(BaseModel):
    """Defines an output artifact for a workflow phase."""
    type: str
    path: Optional[str] = None
    labels: Optional[List[str]] = None

class Phase(BaseModel):
    """Represents a single phase in the CDE workflow."""
    id: str
    description: str
    handler: str
    prompt_recipe: str
    inputs: Optional[List[WorkflowInput]] = None
    outputs: List[WorkflowOutput]

class Workflow(BaseModel):
    """Represents the entire CDE workflow defined in workflow.yml."""
    name: str
    version: str
    phases: List[Phase]

class Task(BaseModel):
    """Represents a single, actionable task for the AI agent."""
    id: str
    feature_id: str
    phase_id: str
    context: Dict
    prompt: str
    status: str = "pending"
