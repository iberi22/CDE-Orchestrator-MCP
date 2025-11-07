---
title: CDE Orchestrator - External Service Integration
description: The CDE Orchestrator now supports external service integration through
  a flexible, detection-based approach. The orchestrator automatically detects an
type: guide
status: draft
created: '2025-11-02'
updated: '2025-11-02'
author: Auto-Generated
tags:
- api
- authentication
- integration
- mcp
- python
- workflow
llm_summary: "User guide for CDE Orchestrator - External Service Integration.\n  The\
  \ CDE Orchestrator now supports external service integration through a flexible,\
  \ detection-based approach. The orchestrator automatically detects and uses external\
  \ MCP servers (like GitHub MCP) when they are configured by the user, falling back\
  \ to local implementations when needed.\n  Reference when working with guide documentation."
---

# CDE Orchestrator - External Service Integration

## Overview

The CDE Orchestrator now supports external service integration through a flexible, detection-based approach. The orchestrator automatically detects and uses external MCP servers (like GitHub MCP) when they are configured by the user, falling back to local implementations when needed.

## How It Works

### 1. MCP Detection

The orchestrator automatically scans for MCP server configurations in common locations:
- `~/.cursor/mcp.json`
- `~/.vscode/mcp.json`
- `.kiro/settings/mcp.json`
- `.vscode/mcp.json`

### 2. Service Priority

When executing operations, the orchestrator uses the following priority:

**For GitHub Operations:**
1. **External GitHub MCP Server** (if configured by user)
2. **GitHub API** (if `GITHUB_TOKEN` is set)
3. **Local File Storage** (fallback)

**For Git Operations:**
1. **Local Git Commands** (always available)

### 3. Automatic Branch Creation

When a new feature is started (in the `define` phase), the orchestrator automatically:
- Creates a Git branch named `feature-{feature_id}`
- Tracks the branch in the feature state

## New MCP Tools

### `cde_createGitBranch`

Creates a new Git branch for a feature.

```python
cde_createGitBranch(
    feature_id: str,
    branch_name: str,
    base_branch: str = "main"
)
```

**Example:**
```
Create a branch 'user-auth' for feature abc12345
→ Creates branch: abc12345-user-auth
```

### `cde_createGitHubIssue`

Creates a GitHub issue for a feature.

```python
cde_createGitHubIssue(
    feature_id: str,
    title: str,
    description: str,
    labels: Optional[List[str]] = None
)
```

**Behavior:**
- If GitHub MCP is configured: Creates issue via MCP
- If `GITHUB_TOKEN` is set: Creates issue via API
- Otherwise: Saves issue locally in `.cde/issues/`

**Example:**
```
Create GitHub issue with title "Implement user authentication"
→ Automatically detects best method and creates issue
```

### `cde_commitWork`

Commits work for a feature.

```python
cde_commitWork(
    feature_id: str,
    message: str,
    files: Optional[List[str]] = None
)
```

**Example:**
```
Commit with message "Add user authentication feature"
→ Commits changes to Git repository
```

### `cde_getServiceStatus`

Gets the status of all configured service integrations.

```python
cde_getServiceStatus()
```

**Returns:**
```json
{
  "github": {
    "mcp_available": true,
    "mcp_config": true,
    "api_available": false,
    "fallback": false
  },
  "git": {
    "available": true,
    "message": "Local git repository"
  }
}
```

## User Configuration

### Setting up GitHub MCP

1. Install the GitHub MCP server:
   ```bash
   npm install -g @modelcontextprotocol/server-github
   ```

2. Configure in your MCP config file (e.g., `~/.cursor/mcp.json`):
   ```json
   {
     "mcpServers": {
       "github": {
         "command": "npx",
         "args": ["-y", "@modelcontextprotocol/server-github"],
         "env": {
           "GITHUB_TOKEN": "your-token-here"
         },
         "disabled": false
       }
     }
   }
   ```

3. The CDE Orchestrator will automatically detect and use this configuration.

### Setting up GitHub API (Alternative)

If you don't use GitHub MCP, you can use the GitHub API directly:

1. Create a GitHub Personal Access Token
2. Set environment variable:
   ```bash
   export GITHUB_TOKEN=your-token-here
   ```

### Repository Configuration

Set repository information (optional):

```bash
export GITHUB_REPO_OWNER=your-username
export GITHUB_REPO_NAME=your-repo
```

## Workflow Integration

### Automatic Branch Creation

When you start a new feature using `cde_startFeature`:

```python
cde_startFeature("Add user authentication")
```

The orchestrator will:
1. Generate a unique feature ID
2. Create a Git branch: `feature-{feature_id}`
3. Track the branch in the feature state

### Manual Operations

You can manually trigger Git/GitHub operations at any time:

```python
# Create GitHub issue
cde_createGitHubIssue(
    feature_id="abc12345",
    title="Implement login screen",
    description="Create the UI for user login",
    labels=["ui", "auth"]
)

# Commit work
cde_commitWork(
    feature_id="abc12345",
    message="Add login screen UI components"
)
```

## Local Fallback

When no external services are configured, the orchestrator gracefully falls back to local operations:

- **GitHub Issues** → Saved to `.cde/issues/{issue_id}.md`
- **Git Operations** → Still work with local repository
- **All workflows** → Continue to function normally

This ensures that the CDE Orchestrator always works, even without external service configuration.

## Best Practices

1. **Always check service status** before starting workflows:
   ```
   cde_getServiceStatus()
   ```

2. **Use descriptive branch names**:
   ```
   cde_createGitBranch(feature_id, "implement-user-auth")
   ```

3. **Commit frequently** during implementation:
   ```
   cde_commitWork(feature_id, "Add authentication service layer")
   ```

4. **Link issues to features** by including feature ID in labels

## Troubleshooting

### GitHub MCP not detected

Check that your MCP config file exists and GitHub server is enabled:
```bash
cat ~/.cursor/mcp.json | jq '.mcpServers.github.disabled'
# Should return: false
```

### Git branch creation fails

Verify you're in a Git repository:
```bash
git status
```

### API rate limits

If using GitHub API, be aware of rate limits. Consider using GitHub MCP for better rate limit handling.

## Future Enhancements

- Support for more MCP servers (GitLab, Bitbucket, etc.)
- Automatic issue creation from task breakdowns
- PR creation workflows
- GitHub Actions integration
- Multi-repository support
