---
title: "CDE Orchestrator MCP Tools API Reference"
description: "Complete API reference for all MCP tools in CDE Orchestrator"
type: "design"
status: "active"
created: "2025-11-01"
updated: "2025-11-01"
author: "CDE Team"
llm_summary: |
  Complete API reference for CDE Orchestrator MCP tools. Includes core workflow tools,
  onboarding tools, service integration, and recipe management. Each tool documented
  with parameters, returns, examples, and error handling.
---

# CDE Orchestrator MCP Tools API Reference

> **Version**: 1.0.0
> **Protocol**: Model Context Protocol (MCP)
> **Framework**: FastMCP
> **Last Updated**: 2025-11-01

## Table of Contents

1. [Core Workflow Tools](#core-workflow-tools)
2. [Onboarding Tools](#onboarding-tools)
3. [Service Integration Tools](#service-integration-tools)
4. [Recipe Management Tools](#recipe-management-tools)
5. [Error Handling](#error-handling)
6. [Common Patterns](#common-patterns)

---

## Core Workflow Tools

### `cde_startFeature`

Start a new feature development workflow.

**Purpose**: Initialize a new feature, create state, generate define phase prompt.

**Parameters**:

```python
{
  "user_prompt": str  # Required: High-level feature description
}
```

**Returns**:

```json
{
  "status": "success",
  "feature_id": "uuid-string",
  "phase": "define",
  "prompt": "You are a senior engineer...",
  "context": {
    "PROJECT_NAME": "...",
    "FEATURE_ID": "...",
    "USER_PROMPT": "...",
    "WORKFLOW_CONTEXT": "...",
    "EXISTING_SPECS": "..."
  }
}
```

**Errors**:

- `workflow_error`: Workflow file not found or invalid
- `state_error`: Cannot create or save state
- `timeout`: Operation exceeded time limit

**Example Usage**:

```python
# Start new authentication feature
cde_startFeature(user_prompt="Add user authentication with OAuth2")

# Returns define phase prompt with context
```

**State Changes**:

- Creates new `FeatureState` in `.cde/state.json`
- Status: `DEFINING`
- Phase: `define`
- Created timestamp recorded

---

### `cde_submitWork`

Submit phase results and advance to next phase.

**Purpose**: Complete current phase, validate results, transition to next phase or completion.

**Parameters**:

```python
{
  "feature_id": str,        # Required: Feature UUID
  "phase_id": str,          # Required: Current phase (e.g., "define")
  "results": Dict[str, Any] # Required: Phase outputs
}
```

**Returns** (Next Phase):

```json
{
  "status": "ok",
  "phase": "decompose",
  "prompt": "Break down the feature...",
  "context": {
    "PREVIOUS_PHASE": "define",
    "PHASE_RESULTS": "...",
    "ACCUMULATED_CONTEXT": "..."
  }
}
```

**Returns** (Completion):

```json
{
  "status": "completed",
  "feature_id": "uuid-string",
  "message": "Feature workflow completed successfully"
}
```

**Errors**:

- `feature_not_found`: Feature ID doesn't exist
- `invalid_phase`: Phase ID doesn't match current phase
- `validation_error`: Results don't meet phase requirements
- `transition_error`: Cannot transition to next phase

**Example Usage**:

```python
# Submit define phase with specification
cde_submitWork(
    feature_id="abc-123",
    phase_id="define",
    results={
        "specification": "# Feature: User Auth\n...",
        "acceptance_criteria": ["User can login", "..."]
    }
)

# Returns decompose phase prompt
```

**State Changes**:

- Updates `FeatureState.current_phase`
- Updates `FeatureState.status`
- Stores results in phase history
- Updates `updated_at` timestamp

---

### `cde_getFeatureStatus`

Get current status and progress of a feature.

**Purpose**: Query feature state for monitoring and debugging.

**Parameters**:

```python
{
  "feature_id": str  # Required: Feature UUID
}
```

**Returns**:

```json
{
  "feature_id": "uuid-string",
  "status": "IMPLEMENTING",
  "current_phase": "implement",
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-11-01T12:30:00Z",
  "phase_history": [
    {
      "phase": "define",
      "completed_at": "2025-11-01T10:30:00Z",
      "results": {...}
    }
  ],
  "metadata": {...}
}
```

**Errors**:

- `feature_not_found`: Feature ID doesn't exist
- `state_error`: Cannot read state file

**Example Usage**:

```python
# Check feature progress
status = cde_getFeatureStatus(feature_id="abc-123")
print(status["current_phase"])  # "implement"
```

---

### `cde_listFeatures`

List all features and their current status.

**Purpose**: Overview of all features in project.

**Parameters**: None

**Returns**:

```json
{
  "features": [
    {
      "id": "uuid-1",
      "status": "IMPLEMENTING",
      "phase": "implement",
      "created_at": "2025-11-01T10:00:00Z"
    },
    {
      "id": "uuid-2",
      "status": "COMPLETED",
      "phase": "review",
      "created_at": "2025-10-30T14:00:00Z"
    }
  ],
  "count": 2
}
```

**Errors**:

- `state_error`: Cannot read state file

**Example Usage**:

```python
# List all features
features = cde_listFeatures()
for feature in features["features"]:
    print(f"{feature['id']}: {feature['status']}")
```

---

## Onboarding Tools

### `cde_onboardingProject`

Analyze project structure and perform onboarding setup.

**Purpose**: Initialize project with Spec-Kit structure, detect Git history, configure AI assistants.

**Parameters**: None (uses current directory)

**Returns**:

```json
{
  "status": "success",
  "analysis": {
    "has_git": true,
    "has_specs": false,
    "total_commits": 150,
    "project_age_days": 45,
    "recent_commits": [...]
  },
  "ai_assistants": {
    "detected": ["copilot", "gemini", "cursor"],
    "summary": {
      "total_supported": 6,
      "detected": 3,
      "configured": 3
    }
  },
  "actions_taken": [
    "Created specs/ directory",
    "Created memory/constitution.md",
    "Generated AGENTS.md",
    "Generated GEMINI.md"
  ],
  "prompt": "Based on your project analysis..."
}
```

**Errors**:

- `not_git_repo`: Current directory is not a Git repository
- `onboarding_error`: Failed to create required structure
- `io_error`: Cannot read/write files

**Example Usage**:

```python
# Run onboarding on current project
result = cde_onboardingProject()
print(result["ai_assistants"]["detected"])  # ["copilot", "gemini"]
```

**Generated Files**:

- `specs/` directory structure
- `specs/README.md`
- `memory/constitution.md`
- `AGENTS.md` (if AI assistants detected)
- `GEMINI.md` (if Gemini detected)
- `.github/copilot-instructions.md` (if Copilot detected)

**State Changes**:

- Creates `.cde/state.json` if doesn't exist
- Records onboarding status
- Stores AI assistant configuration

---

### `cde_publishOnboarding`

Apply onboarding documents generated by LLM into the repo.

**Purpose**: Write LLM-generated onboarding documents to filesystem.

**Parameters**:

```python
{
  "documents": Dict[str, str],  # Required: {file_path: content}
  "approve": bool = True         # Optional: Confirm write operation
}
```

**Returns**:

```json
{
  "status": "success",
  "files_written": [
    "specs/features/feature-1.md",
    "specs/design/architecture/README.md"
  ],
  "count": 2
}
```

**Errors**:

- `approval_required`: User must approve before writing
- `io_error`: Cannot write files
- `validation_error`: Invalid file paths or content

**Example Usage**:

```python
# Publish LLM-generated docs
documents = {
    "specs/features/auth.md": "# Feature: Authentication\n...",
    "specs/design/auth-flow.md": "# Auth Flow Design\n..."
}

result = cde_publishOnboarding(documents=documents, approve=True)
print(f"Wrote {result['count']} files")
```

---

## Service Integration Tools

### `cde_getServiceStatus`

Get status of all configured service integrations.

**Purpose**: Check connectivity to external services (GitHub, Git, MCP servers).

**Parameters**: None

**Returns**:

```json
{
  "services": {
    "github": {
      "available": true,
      "cli_version": "2.35.1",
      "authenticated": true
    },
    "git": {
      "available": true,
      "version": "2.40.0"
    },
    "mcp": {
      "servers_detected": 2,
      "servers": ["github-mcp", "filesystem-mcp"]
    }
  },
  "overall_status": "operational"
}
```

**Errors**:

- `service_check_failed`: Unable to check service status

**Example Usage**:

```python
# Check service availability
status = cde_getServiceStatus()
if status["services"]["github"]["available"]:
    print("GitHub CLI is ready")
```

---

### `cde_createGitHubIssue`

Create GitHub issue for a feature.

**Purpose**: Automatically create issues with proper labels and context.

**Parameters**:

```python
{
  "feature_id": str,          # Required: Feature UUID
  "title": str,               # Required: Issue title
  "description": str,         # Required: Issue body
  "labels": List[str] = None  # Optional: Issue labels
}
```

**Returns**:

```json
{
  "status": "success",
  "issue_url": "https://github.com/owner/repo/issues/42",
  "issue_number": 42
}
```

**Errors**:

- `github_not_available`: GitHub CLI not installed or not authenticated
- `api_error`: GitHub API request failed
- `feature_not_found`: Feature ID doesn't exist

**Example Usage**:

```python
# Create issue for feature
result = cde_createGitHubIssue(
    feature_id="abc-123",
    title="Implement user authentication",
    description="See specs/features/auth.md",
    labels=["feature", "auth"]
)
```

---

### `cde_createGitBranch`

Create Git branch for a feature.

**Purpose**: Create feature branch with standardized naming.

**Parameters**:

```python
{
  "feature_id": str,              # Required: Feature UUID
  "branch_name": str,             # Required: Branch name
  "base_branch": str = "main"     # Optional: Base branch
}
```

**Returns**:

```json
{
  "status": "success",
  "branch_name": "feature/abc-123-user-auth",
  "base_branch": "main"
}
```

**Errors**:

- `git_not_available`: Git not installed
- `branch_exists`: Branch already exists
- `git_error`: Git operation failed

**Example Usage**:

```python
# Create feature branch
result = cde_createGitBranch(
    feature_id="abc-123",
    branch_name="user-auth",
    base_branch="develop"
)
```

---

### `cde_commitWork`

Commit work for a feature to Git.

**Purpose**: Create conventional commit with feature context.

**Parameters**:

```python
{
  "feature_id": str,              # Required: Feature UUID
  "message": str,                 # Required: Commit message
  "files": List[str] = None       # Optional: Files to commit (None = all)
}
```

**Returns**:

```json
{
  "status": "success",
  "commit_hash": "abc123def456",
  "files_committed": 5
}
```

**Errors**:

- `git_not_available`: Git not installed
- `no_changes`: No changes to commit
- `git_error`: Commit failed

**Example Usage**:

```python
# Commit feature work
result = cde_commitWork(
    feature_id="abc-123",
    message="feat: Add OAuth2 authentication",
    files=["src/auth.py", "tests/test_auth.py"]
)
```

---

## Recipe Management Tools

### `cde_listRecipes`

List all available POML recipes.

**Purpose**: Discover specialized agent recipes for different tasks.

**Parameters**: None

**Returns**:

```json
{
  "recipes": {
    "development": [
      {
        "id": "ai-engineer",
        "name": "AI Engineer",
        "description": "Expert AI/ML engineer for model development"
      },
      {
        "id": "backend-engineer",
        "name": "Backend Engineer",
        "description": "Senior backend developer"
      }
    ],
    "planning": [
      {
        "id": "sprint-prioritizer",
        "name": "Sprint Prioritizer",
        "description": "Prioritize backlog items"
      }
    ]
  },
  "count": 15
}
```

**Errors**:

- `recipes_not_found`: No recipes directory

**Example Usage**:

```python
# List available recipes
recipes = cde_listRecipes()
for category, items in recipes["recipes"].items():
    print(f"{category}: {len(items)} recipes")
```

---

### `cde_useRecipe`

Use a specific POML recipe to generate specialized prompt.

**Purpose**: Invoke recipe with context to generate task-specific prompt.

**Parameters**:

```python
{
  "recipe_id": str,                    # Required: Recipe ID
  "user_prompt": str,                  # Required: Task description
  "context": Dict[str, str] = None     # Optional: Additional context
}
```

**Returns**:

```json
{
  "status": "success",
  "recipe_id": "ai-engineer",
  "prompt": "You are an expert AI engineer...",
  "metadata": {
    "recipe_name": "AI Engineer",
    "context_vars_used": ["PROJECT_NAME", "TECH_STACK"]
  }
}
```

**Errors**:

- `recipe_not_found`: Recipe ID doesn't exist
- `template_error`: Failed to render template
- `validation_error`: Invalid context variables

**Example Usage**:

```python
# Use AI engineer recipe
result = cde_useRecipe(
    recipe_id="ai-engineer",
    user_prompt="Optimize model inference speed",
    context={"TECH_STACK": "PyTorch, TensorRT"}
)
```

---

### `cde_suggestRecipe`

Suggest best recipe for a given task.

**Purpose**: Auto-select appropriate recipe based on task description.

**Parameters**:

```python
{
  "user_prompt": str,           # Required: Task description
  "phase_id": str = "define"    # Optional: Current workflow phase
}
```

**Returns**:

```json
{
  "status": "success",
  "suggested_recipe": "ai-engineer",
  "confidence": 0.92,
  "reason": "Task involves ML optimization",
  "alternatives": [
    {"id": "backend-engineer", "confidence": 0.45}
  ]
}
```

**Errors**:

- `no_match`: No suitable recipe found

**Example Usage**:

```python
# Get recipe suggestion
result = cde_suggestRecipe(
    user_prompt="Optimize database queries for high traffic",
    phase_id="implement"
)
print(result["suggested_recipe"])  # "backend-engineer"
```

---

### `cde_startFeatureWithRecipe`

Start feature using specific recipe or auto-suggested recipe.

**Purpose**: Combine feature start with recipe selection for specialized workflows.

**Parameters**:

```python
{
  "user_prompt": str,           # Required: Feature description
  "recipe_id": str = None       # Optional: Specific recipe (None = auto-suggest)
}
```

**Returns**:

```json
{
  "status": "success",
  "feature_id": "uuid-string",
  "recipe_used": "ai-engineer",
  "phase": "define",
  "prompt": "You are an expert AI engineer defining..."
}
```

**Errors**:

- `recipe_not_found`: Specified recipe doesn't exist
- `workflow_error`: Cannot start feature

**Example Usage**:

```python
# Start feature with AI engineer recipe
result = cde_startFeatureWithRecipe(
    user_prompt="Add GPU-accelerated inference",
    recipe_id="ai-engineer"
)

# Or auto-suggest
result = cde_startFeatureWithRecipe(
    user_prompt="Add caching layer"
)  # Will auto-select backend-engineer
```

---

## Error Handling

### Error Response Format

All tools return errors in this format:

```json
{
  "error": "error_type",
  "message": "Human-readable error message",
  "tool": "cde_toolName",
  "timestamp": "2025-11-01T12:00:00Z",
  "details": {
    "additional": "context"
  }
}
```

### Common Error Types

| Error Type | Description | Recovery |
|------------|-------------|----------|
| `feature_not_found` | Feature ID doesn't exist | Check feature ID with `cde_listFeatures` |
| `workflow_error` | Workflow file issue | Verify `.cde/workflow.yml` exists |
| `state_error` | State file read/write failed | Check `.cde/state.json` permissions |
| `timeout` | Operation exceeded time limit | Retry with smaller scope |
| `validation_error` | Invalid parameters | Check parameter format |
| `service_unavailable` | External service down | Check service status with `cde_getServiceStatus` |
| `git_error` | Git operation failed | Check Git configuration |
| `io_error` | File system operation failed | Check file permissions |

### Retry Strategy

For transient errors (timeout, service_unavailable):

1. Wait 1 second
2. Retry up to 3 times
3. Exponential backoff (1s, 2s, 4s)

For permanent errors (feature_not_found, validation_error):

- Do not retry
- Fix input and retry manually

---

## Common Patterns

### Pattern 1: Full Feature Workflow

```python
# 1. Start feature
result = cde_startFeature(user_prompt="Add search functionality")
feature_id = result["feature_id"]

# Agent writes specification...

# 2. Submit define phase
cde_submitWork(
    feature_id=feature_id,
    phase_id="define",
    results={"specification": "..."}
)

# 3. Continue through phases (decompose, design, implement, test, review)
# ...

# 4. Check status
status = cde_getFeatureStatus(feature_id=feature_id)
if status["status"] == "COMPLETED":
    print("Feature complete!")
```

### Pattern 2: Onboarding New Project

```python
# 1. Run onboarding
result = cde_onboardingProject()

# 2. Review AI assistants detected
ai_detected = result["ai_assistants"]["detected"]
print(f"Detected: {', '.join(ai_detected)}")

# 3. Start first feature
cde_startFeature(user_prompt="Set up project structure")
```

### Pattern 3: Recipe-Driven Development

```python
# 1. Get recipe suggestion
suggestion = cde_suggestRecipe(
    user_prompt="Optimize ML model",
    phase_id="implement"
)

# 2. Start with suggested recipe
result = cde_startFeatureWithRecipe(
    user_prompt="Optimize ML model",
    recipe_id=suggestion["suggested_recipe"]
)

# 3. Continue workflow...
```

### Pattern 4: Service Integration

```python
# 1. Check services
status = cde_getServiceStatus()

# 2. Create GitHub issue if available
if status["services"]["github"]["available"]:
    cde_createGitHubIssue(
        feature_id=feature_id,
        title="Feature: Search",
        description="..."
    )

# 3. Create branch
cde_createGitBranch(
    feature_id=feature_id,
    branch_name="search-feature"
)

# 4. Commit work
cde_commitWork(
    feature_id=feature_id,
    message="feat: Add search API"
)
```

---

## Rate Limits & Performance

### Tool Execution Times (Typical)

| Tool | Typical | Max |
|------|---------|-----|
| `cde_startFeature` | 0.5s | 2s |
| `cde_submitWork` | 0.3s | 1s |
| `cde_getFeatureStatus` | 0.1s | 0.5s |
| `cde_onboardingProject` | 2s | 10s |
| `cde_createGitHubIssue` | 1s | 5s |
| `cde_useRecipe` | 0.2s | 1s |

### Rate Limits

- No explicit rate limits (local execution)
- External services (GitHub) have their own limits
- File I/O limited by system performance

---

## Versioning

**Current Version**: 1.0.0

**Breaking Changes**: Will be documented in CHANGELOG.md

**Compatibility**: Tools maintain backward compatibility within major version.

---

## See Also

- [Workflow Configuration](../design/ARCHITECTURE.md)
- [Recipe Development](../../.cde/recipes/README.md)
- [Onboarding System](../features/onboarding-system.md)
- [AI Assistant Configuration](../features/ai-assistant-config.md)
