# CDE Orchestrator MCP - Development Guidelines

## Code Quality Standards

### Docstring Conventions
- **Triple quotes**: Use `"""` for all docstrings (100% consistency across codebase)
- **Comprehensive documentation**: Every function includes purpose, args, returns, and examples
- **MCP tool documentation**: Extensive docstrings with emoji headers, usage examples, and workflow descriptions
- **Business context**: Domain methods include business rule explanations

**Example Pattern**:
```python
def cde_delegateToJules(
    user_prompt: str,
    project_path: str = ".",
    branch: str = "main",
    require_plan_approval: bool = False,
    timeout: int = 1800,
    detached: bool = False,
) -> str:
    """
    🤖 **Jules AI Agent Integration** - Delegate complex coding tasks to Jules.

    Use this tool to execute long-running, complex development tasks using Jules,
    Google's async AI coding agent with full repository context.

    **When to Use:**
    - Complex feature development (4-8 hours estimated)
    - Large-scale refactoring across multiple files
    
    **Args:**
        user_prompt: Natural language task description
        project_path: Path to project (default: current directory)
        
    **Returns:**
        JSON with execution results and session information
    """
```

### Type Annotations
- **Comprehensive typing**: All function parameters and return types annotated
- **Complex types**: Use `Dict[str, Any]`, `List[str]`, `Optional[Type]` patterns
- **Domain entities**: Strong typing with custom classes and enums
- **Async support**: Proper `async`/`await` annotations for coroutines

**Example Pattern**:
```python
async def needs_onboarding(self) -> Dict[str, Any]:
    """Check if the project needs onboarding."""
    
def _calculate_task_complexity(task_description: str) -> str:
    """Calculate task complexity from description."""
    
class OnboardingUseCase:
    def __init__(self, project_root: Path, git_adapter: IGitAdapter):
```

### Error Handling
- **Structured error responses**: JSON format for MCP tools with error type, message, and context
- **Exception chaining**: Preserve original exceptions with logging
- **Graceful degradation**: Continue operation when non-critical components fail
- **Validation errors**: Pydantic-based input validation with detailed error messages

**Example Pattern**:
```python
try:
    # Operation logic
    result = await adapter.execute_prompt(...)
    return result_json
except Exception as e:
    return json.dumps({
        "error": "jules_execution_failed",
        "message": str(e),
        "type": type(e).__name__,
    }, indent=2)
```

### Logging Standards
- **Module-level loggers**: `logger = logging.getLogger(__name__)` pattern
- **Appropriate levels**: INFO for user actions, DEBUG for internal state, WARNING for recoverable issues
- **Structured messages**: Include context and actionable information
- **Exception logging**: Use `exc_info=True` for stack traces

**Example Pattern**:
```python
logger = logging.getLogger(__name__)

logger.info(f"Configuring AI assistants: {', '.join(agents_to_config)}")
logger.debug(f"Skipping existing file: {file_path}")
logger.warning("Error analyzing git history with adapter: %s", exc, exc_info=True)
```

## Architectural Patterns

### Hexagonal Architecture Implementation
- **Dependency inversion**: Domain layer has no external dependencies
- **Port interfaces**: Abstract base classes define contracts (`IGitAdapter`, `IProjectRepository`)
- **Adapter pattern**: Infrastructure implementations in `adapters/` directory
- **Use case orchestration**: Application layer coordinates domain entities and adapters

**Example Pattern**:
```python
# Domain port (interface)
class IGitAdapter:
    async def traverse_commits(self) -> AsyncGenerator[Commit, None]:
        """Traverse Git commits in chronological order."""
        
# Application use case
class OnboardingUseCase:
    def __init__(self, project_root: Path, git_adapter: IGitAdapter):
        self.git_adapter = git_adapter  # Dependency injection
        
    async def _analyze_git_history_with_adapter(self) -> Dict[str, Any]:
        # Use adapter through interface
        async for commit in self.git_adapter.traverse_commits():
            commits.append(commit)
```

### Factory Pattern Usage
- **Entity creation**: Static factory methods for domain entities
- **Validation integration**: Factory methods include business rule validation
- **Immutable construction**: Entities created in valid state from factory

**Example Pattern**:
```python
class Specification:
    @classmethod
    def create(
        cls,
        title: str,
        type: DocumentType,
        author: str,
        content: str = "",
        tags: List[str] = None,
        llm_summary: Optional[str] = None,
    ) -> "Specification":
        """Factory method with validation."""
        if len(title.strip()) < 3:
            raise SpecificationValidationError("Title must be at least 3 characters")
        # ... validation logic
        return cls(...)
```

### State Management Patterns
- **Enum-based states**: Use Python enums for status management
- **Transition validation**: Business rules enforce valid state transitions
- **Immutable state changes**: State changes through methods, not direct assignment

**Example Pattern**:
```python
class DocumentStatus(Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    
    def can_transition_to(self, target: "DocumentStatus") -> bool:
        """Define valid state transitions."""
        
def activate(self):
    """Transition from DRAFT to ACTIVE with validation."""
    if self.status != DocumentStatus.DRAFT:
        raise InvalidStatusTransitionError(...)
```

## Testing Patterns

### Test Organization
- **Layer separation**: Unit tests for domain (no I/O), integration tests for adapters
- **Descriptive names**: `test_<method>_<scenario>_<expected>` pattern
- **Comprehensive coverage**: Test business rules, edge cases, and error conditions
- **Fixture usage**: pytest fixtures for common test data setup

**Example Pattern**:
```python
def test_create_specification_with_minimal_fields():
    """Test creating specification with only required fields."""
    
def test_activate_requires_llm_summary():
    """Test that activation requires LLM summary."""
    
def test_cannot_deprecate_draft():
    """Test that draft specs cannot be deprecated."""
```

### Domain Testing Strategy
- **Pure domain tests**: No external dependencies, fast execution
- **Business rule validation**: Test all domain constraints and invariants
- **State transition testing**: Verify all valid and invalid state changes
- **Exception testing**: Use `pytest.raises()` for expected failures

**Example Pattern**:
```python
def test_cannot_link_archived_specification():
    """Test that archived specs cannot create links."""
    spec = Specification.create(...)
    spec.activate()
    spec.archive()
    
    with pytest.raises(InvalidLinkError) as exc_info:
        spec.establish_link(target_id, LinkRelationship.IMPLEMENTS)
    
    assert "Cannot link archived specifications" in str(exc_info.value)
```

## Data Validation Patterns

### Pydantic Integration
- **Input validation**: Decorator-based validation for MCP tools
- **Model configuration**: Use `ConfigDict` for validation rules
- **Error formatting**: Structured JSON responses for validation failures
- **Type coercion**: Automatic type conversion where appropriate

**Example Pattern**:
```python
class StartFeatureInput(BaseModel):
    """Validation model for cde_startFeature."""
    user_prompt: str
    
    model_config = ConfigDict(
        str_min_length=10,
        str_max_length=5000
    )

@validate_input(StartFeatureInput)
def cde_startFeature(user_prompt: str) -> str:
    """Tool with automatic input validation."""
```

### String Sanitization
- **Length limits**: Enforce maximum string lengths to prevent abuse
- **Character filtering**: Remove control characters except whitespace
- **Path validation**: Prevent directory traversal attacks
- **Extension checking**: Validate file extensions for security

**Example Pattern**:
```python
def sanitize_string(value: str, max_length: int = 10000) -> str:
    """Sanitize string input by removing dangerous characters."""
    sanitized = value[:max_length]
    sanitized = "".join(
        char for char in sanitized if ord(char) >= 32 or char in "\n\r\t"
    )
    return sanitized
```

## Configuration Management

### Environment Variables
- **Secure defaults**: Use environment variables for sensitive configuration
- **Optional dependencies**: Graceful handling when optional services unavailable
- **Configuration validation**: Check required environment variables at startup
- **Development vs production**: Different configurations for different environments

**Example Pattern**:
```python
api_key = os.getenv("JULES_API_KEY")
if not api_key:
    return json.dumps({
        "error": "JULES_API_KEY not found in environment",
        "setup_instructions": [
            "1. Go to https://jules.google/",
            "2. Sign in with Google",
            "3. Add to .env: JULES_API_KEY=your-key-here",
        ],
    }, indent=2)
```

### Agent Detection Patterns
- **CLI availability**: Use `shutil.which()` to detect command-line tools
- **SDK installation**: Check Python package availability with `importlib.util`
- **Graceful fallbacks**: Provide alternatives when preferred tools unavailable
- **Status reporting**: Clear feedback about what's available and what's missing

**Example Pattern**:
```python
# Check CLI availability
copilot_available = shutil.which("gh") is not None

# Check Python package
try:
    import importlib.util
    jules_sdk_installed = importlib.util.find_spec("jules_agent_sdk") is not None
except ImportError:
    jules_sdk_installed = False
```

## File and Path Management

### Path Handling
- **Pathlib usage**: Use `Path` objects instead of string manipulation
- **Cross-platform compatibility**: Handle Windows and Unix path differences
- **Relative path resolution**: Resolve paths relative to project root
- **Safety validation**: Prevent directory traversal and invalid paths

**Example Pattern**:
```python
def __init__(self, project_root: Path):
    self.project_root = project_root
    self.specs_root = project_root / "specs"
    self.memory_root = project_root / "memory"
    
# Path validation
if ".." in path or path.startswith("/"):
    raise ValueError(f"Invalid path: {path}. Path traversal not allowed.")
```

### File Operations
- **UTF-8 encoding**: Explicit encoding specification for text files
- **Atomic operations**: Use temporary files for safe writes
- **Existence checking**: Check file/directory existence before operations
- **Permission handling**: Graceful handling of permission errors

**Example Pattern**:
```python
file_path.write_text(content, encoding="utf-8")

if file_path.exists() and not force:
    results["skipped"].append(str(file_path))
    return
```

## Async Programming Patterns

### Async/Await Usage
- **Proper async propagation**: Async methods call other async methods with `await`
- **Resource management**: Use `async with` for resource cleanup
- **Error handling**: Proper exception handling in async contexts
- **Generator patterns**: Use `AsyncGenerator` for streaming data

**Example Pattern**:
```python
async def needs_onboarding(self) -> Dict[str, Any]:
    """Async method that awaits other async operations."""
    git_info = await self._analyze_git_history_with_adapter()
    
async def traverse_commits(self) -> AsyncGenerator[Commit, None]:
    """Async generator for streaming commits."""
    for commit in commits:
        yield commit
```

## JSON Response Patterns

### Structured Responses
- **Consistent format**: All MCP tools return JSON strings
- **Error standardization**: Common error format with type, message, and context
- **Pretty printing**: Use `indent=2` for readable JSON output
- **Status indicators**: Include success/failure indicators in responses

**Example Pattern**:
```python
return json.dumps({
    "selected_agent": actual_agent.value,
    "task_description": task_description,
    "complexity": complexity,
    "reasoning": f"Selected {actual_agent.value} for task execution",
    "capabilities": {
        "async": capabilities.supports_async,
        "plan_approval": capabilities.supports_plan_approval,
    },
    "available_agents": [a.value for a in available_agent_types],
}, indent=2)
```

## Common Anti-Patterns to Avoid

### Code Smells
- **Long parameter lists**: Use configuration objects or builders for complex parameters
- **Deep nesting**: Extract methods to reduce complexity
- **Magic strings**: Use enums and constants instead of hardcoded strings
- **Silent failures**: Always log errors and provide feedback

### Architecture Violations
- **Domain dependencies**: Domain layer must not import infrastructure
- **Circular imports**: Use dependency injection to break cycles
- **Tight coupling**: Use interfaces and dependency injection
- **Mixed concerns**: Separate business logic from infrastructure

### Testing Issues
- **Brittle tests**: Don't test implementation details, test behavior
- **Slow tests**: Keep unit tests fast by avoiding I/O
- **Unclear assertions**: Use descriptive assertion messages
- **Test pollution**: Ensure tests are independent and isolated