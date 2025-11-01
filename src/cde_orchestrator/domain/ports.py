# src/cde_orchestrator/domain/ports.py
"""
Domain Ports - Interface Contracts for Adapters.

Ports define WHAT the domain needs, never HOW it's implemented.
All adapters (infrastructure) must implement these interfaces.

Naming Convention:
    - All ports prefixed with 'I' (IProjectRepository, etc.)
    - Async methods use 'async def' where I/O is expected
    - Return types are explicit (no 'Any' unless truly dynamic)

Design for LLMs:
    - Every method has complete docstring
    - Input/output contracts specified
    - Exceptions documented
    - Examples provided
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, AsyncIterator
from .entities import Project, ProjectId, Feature, Workflow, WorkflowPhase, CodeArtifact


# ============================================================================
# PERSISTENCE PORTS
# ============================================================================

class IProjectRepository(ABC):
    """
    Port: Project persistence and retrieval.

    Implementations:
        - FileSystemProjectRepository (JSON files)
        - DatabaseProjectRepository (SQL/NoSQL)
        - InMemoryProjectRepository (testing)

    Responsibilities:
        - Store/retrieve projects
        - Maintain project-path index
        - Support bulk operations for scale (1000+ projects)
    """

    @abstractmethod
    def get_by_id(self, project_id: ProjectId) -> Optional[Project]:
        """
        Retrieve project by ID.

        Args:
            project_id: Project identifier

        Returns:
            Project if found, None otherwise

        Examples:
            >>> repo.get_by_id(ProjectId("abc-123"))
            Project(id=ProjectId('abc-123'), name='My Project', ...)
        """
        pass

    @abstractmethod
    def get_by_path(self, path: str) -> Optional[Project]:
        """
        Find project by filesystem path.

        Args:
            path: Absolute filesystem path

        Returns:
            Project if registered at that path, None otherwise

        Examples:
            >>> repo.get_by_path("E:\\\\scripts-python\\\\my-project")
            Project(...)
        """
        pass

    @abstractmethod
    def list_all(self, limit: Optional[int] = None) -> List[Project]:
        """
        Get all registered projects.

        Args:
            limit: Optional max number of projects to return

        Returns:
            List of all projects (or first N if limit specified)

        Performance:
            Should support 1000+ projects efficiently via pagination/streaming
        """
        pass

    @abstractmethod
    async def list_all_async(
        self,
        limit: Optional[int] = None
    ) -> AsyncIterator[Project]:
        """
        Stream all projects asynchronously.

        Preferred for large datasets to avoid loading everything into memory.

        Yields:
            Project instances one at a time

        Examples:
            >>> async for project in repo.list_all_async():
            ...     print(project.name)
        """
        pass

    @abstractmethod
    def save(self, project: Project) -> None:
        """
        Persist project state.

        Args:
            project: Project to save (creates or updates)

        Raises:
            RepositoryError: If save fails

        Side Effects:
            - Writes to storage
            - Updates index if path changed
        """
        pass

    @abstractmethod
    def delete(self, project_id: ProjectId) -> None:
        """
        Remove project from registry.

        Args:
            project_id: Project to delete

        Raises:
            ProjectNotFoundError: If project doesn't exist
            RepositoryError: If deletion fails

        Note:
            Does NOT delete filesystem content, only registry entry
        """
        pass

    @abstractmethod
    def exists(self, project_id: ProjectId) -> bool:
        """Check if project exists without loading it."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Get total number of registered projects."""
        pass


class IStateStore(ABC):
    """
    Port: Generic key-value state persistence.

    Used for non-project state like:
        - Onboarding progress
        - Global configuration
        - Temporary caches

    Implementations:
        - JSONStateStore (single file)
        - RedisStateStore (distributed)
        - InMemoryStateStore (testing)
    """

    @abstractmethod
    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Load state by key.

        Args:
            key: State identifier

        Returns:
            State dict if found, None otherwise
        """
        pass

    @abstractmethod
    def save(self, key: str, data: Dict[str, Any]) -> None:
        """
        Persist state.

        Args:
            key: State identifier
            data: State to save
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove state by key."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """
        List all keys, optionally filtered by prefix.

        Examples:
            >>> store.list_keys(prefix="project:")
            ["project:abc-123", "project:xyz-789"]
        """
        pass


# ============================================================================
# WORKFLOW ENGINE PORT
# ============================================================================

class IWorkflowEngine(ABC):
    """
    Port: Workflow definition and execution logic.

    Implementations:
        - YAMLWorkflowEngine (reads .cde/workflow.yml)
        - PythonWorkflowEngine (programmatic workflows)
        - RemoteWorkflowEngine (centralized workflow service)

    Responsibilities:
        - Load workflow definitions
        - Validate workflow structure
        - Determine phase transitions
        - Validate phase results
    """

    @abstractmethod
    def load_for_project(self, project: Project) -> Workflow:
        """
        Load workflow definition for given project.

        Args:
            project: Project to load workflow for

        Returns:
            Workflow instance

        Raises:
            WorkflowValidationError: If workflow file invalid

        Notes:
            May return different workflows based on project metadata
            (e.g., "web_application" vs "data_processing" workflows)
        """
        pass

    @abstractmethod
    def get_phase(self, workflow: Workflow, phase_id: str) -> WorkflowPhase:
        """
        Get phase by ID from workflow.

        Args:
            workflow: Workflow to search
            phase_id: Phase identifier

        Returns:
            WorkflowPhase instance

        Raises:
            PhaseNotFoundError: If phase doesn't exist
        """
        pass

    @abstractmethod
    def get_next_phase(
        self,
        workflow: Workflow,
        current_phase_id: str
    ) -> Optional[WorkflowPhase]:
        """
        Determine next phase in workflow sequence.

        Args:
            workflow: Current workflow
            current_phase_id: Current phase

        Returns:
            Next WorkflowPhase or None if current is last

        Raises:
            PhaseNotFoundError: If current_phase_id not in workflow
        """
        pass

    @abstractmethod
    def validate_results(
        self,
        phase: WorkflowPhase,
        results: Dict[str, Any]
    ) -> bool:
        """
        Check if results satisfy phase requirements.

        Args:
            phase: Phase that produced results
            results: Actual results to validate

        Returns:
            True if valid, False otherwise

        Raises:
            ArtifactValidationError: If validation fails (with details)
        """
        pass

    @abstractmethod
    def detect_workflow_type(self, user_prompt: str) -> str:
        """
        Analyze user prompt to suggest workflow type.

        Args:
            user_prompt: User's feature request

        Returns:
            Workflow type identifier (e.g., "web_application", "bug_fix")

        Examples:
            >>> engine.detect_workflow_type("Add user login page")
            "web_application"
        """
        pass


# ============================================================================
# CODE EXECUTION PORT
# ============================================================================

class ICodeExecutor(ABC):
    """
    Port: Execute code generation agents.

    Implementations:
        - CopilotCLIAdapter (GitHub Copilot headless)
        - OpenAIChatAdapter (direct GPT-4 calls)
        - LocalLLMAdapter (Ollama, llama.cpp, etc.)

    Responsibilities:
        - Execute prompts in project context
        - Capture generated code
        - Apply changes (if YOLO mode)
        - Return structured results
    """

    @abstractmethod
    async def execute_prompt(
        self,
        project_path: str,
        prompt: str,
        context: Dict[str, Any]
    ) -> 'ExecutionResult':
        """
        Execute code generation with given prompt.

        Args:
            project_path: Absolute path to project directory
            prompt: Natural language instruction
            context: Additional context (files, specs, yolo flag, etc.)

        Returns:
            ExecutionResult with generated code and metadata

        Context Keys:
            - yolo: bool - Auto-apply without confirmation
            - files: List[str] - Files to include in context
            - max_tokens: int - Token limit for generation

        Examples:
            >>> result = await executor.execute_prompt(
            ...     "/path/to/project",
            ...     "Create user model with email and password fields",
            ...     {"yolo": True}
            ... )
            >>> result.success
            True
            >>> result.modified_files
            ["src/models/user.py"]
        """
        pass

    @abstractmethod
    def supports_yolo_mode(self) -> bool:
        """
        Check if executor supports auto-apply without confirmation.

        Returns:
            True if YOLO mode supported, False otherwise
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return executor capabilities metadata.

        Returns:
            Dict with keys:
                - name: str
                - version: str
                - supports_yolo: bool
                - max_context_tokens: int
                - supported_languages: List[str]
        """
        pass


# ============================================================================
# AGENT ORCHESTRATION PORT
# ============================================================================

class IAgentOrchestrator(ABC):
    """
    Port: Orchestrate external agents and services.

    Implementations:
        - MCPClientAdapter (calls other MCP servers)
        - DirectAPIAdapter (direct HTTP calls)
        - MockOrchestrator (testing)

    Responsibilities:
        - Manage connections to external services
        - Route requests to appropriate service
        - Handle authentication
        - Provide service discovery
    """

    @abstractmethod
    async def call_github(
        self,
        operation: str,
        params: Dict[str, Any]
    ) -> Any:
        """
        Execute GitHub operation via MCP or API.

        Args:
            operation: Operation name (e.g., "create_issue", "create_pr")
            params: Operation-specific parameters

        Returns:
            Operation result (structure depends on operation)

        Raises:
            ServiceUnavailableError: If GitHub service not accessible

        Examples:
            >>> result = await orch.call_github("create_issue", {
            ...     "repo": "owner/repo",
            ...     "title": "Bug in feature X",
            ...     "body": "Description here"
            ... })
        """
        pass

    @abstractmethod
    async def call_copilot(
        self,
        command: str,
        args: Dict[str, Any]
    ) -> Any:
        """
        Execute Copilot CLI command.

        Args:
            command: Copilot command (e.g., "suggest", "explain")
            args: Command arguments

        Returns:
            Command result
        """
        pass

    @abstractmethod
    def is_service_available(self, service_name: str) -> bool:
        """
        Check if external service is accessible.

        Args:
            service_name: Service identifier ("github", "copilot", etc.)

        Returns:
            True if service can be called, False otherwise
        """
        pass

    @abstractmethod
    def list_available_services(self) -> List[str]:
        """
        Get list of all available external services.

        Returns:
            List of service names
        """
        pass


# ============================================================================
# PROMPT RENDERING PORT
# ============================================================================

class IPromptRenderer(ABC):
    """
    Port: Render POML templates with context.

    Implementations:
        - POMLRenderer (native POML parsing)
        - JinjaRenderer (Jinja2 templates)
        - MarkdownRenderer (simple Markdown templates)

    Responsibilities:
        - Load template files
        - Inject context variables
        - Validate template syntax
        - Return rendered prompt
    """

    @abstractmethod
    def render(self, template_path: str, context: Dict[str, Any]) -> str:
        """
        Render prompt template with given context.

        Args:
            template_path: Path to template file (relative or absolute)
            context: Variables to inject into template

        Returns:
            Rendered prompt string

        Raises:
            TemplateNotFoundError: If template file doesn't exist
            TemplateRenderError: If rendering fails

        Examples:
            >>> renderer.render(
            ...     ".cde/prompts/01_define.poml",
            ...     {"USER_PROMPT": "Add login feature"}
            ... )
            "You are a senior engineer. Task: Add login feature..."
        """
        pass

    @abstractmethod
    def validate_template(self, template_path: str) -> bool:
        """
        Check if template is well-formed.

        Args:
            template_path: Path to template file

        Returns:
            True if valid, False otherwise

        Raises:
            TemplateNotFoundError: If template file doesn't exist
        """
        pass

    @abstractmethod
    def list_templates(self, directory: str) -> List[str]:
        """
        List all templates in directory.

        Args:
            directory: Directory to scan

        Returns:
            List of template file paths
        """
        pass


# ============================================================================
# RESULT VALUE OBJECTS
# ============================================================================

class ExecutionResult:
    """
    Value object: Result of code execution.

    This is a domain object (not just a dict) to ensure type safety
    and provide clear contract for LLMs.
    """

    def __init__(
        self,
        success: bool,
        modified_files: List[str],
        diff: str,
        log: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.modified_files = modified_files
        self.diff = diff
        self.log = log
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for JSON serialization."""
        return {
            "success": self.success,
            "modified_files": self.modified_files,
            "diff": self.diff,
            "log": self.log,
            "metadata": self.metadata
        }

    @classmethod
    def failure(cls, error_message: str, log: str = "") -> 'ExecutionResult':
        """Factory: Create failed result."""
        return cls(
            success=False,
            modified_files=[],
            diff="",
            log=log,
            metadata={"error": error_message}
        )
