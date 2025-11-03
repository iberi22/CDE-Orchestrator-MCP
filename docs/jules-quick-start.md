---
title: Jules Integration Quick Start Guide
description: Step-by-step guide to integrate and use Jules AI agent for complex development tasks
type: guide
status: active
created: 2025-11-03
updated: 2025-11-03
author: CDE Team
tags:
  - jules
  - quickstart
  - setup
  - agents
  - tutorial
llm_summary: |
  Quick start guide for integrating Jules AI agent with CDE Orchestrator MCP.
  Covers installation, setup, configuration, and usage examples for delegating
  complex coding tasks to Jules with full repository context.
---

# Jules Integration Quick Start Guide

> **Goal**: Get Jules up and running in **< 5 minutes**
> **For**: Developers using CDE Orchestrator MCP
> **Level**: Beginner-friendly

---

## ⚡ Quick Setup (3 Steps)

### 1. Install Jules SDK

```bash
# Activate your virtual environment first
.\.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install Jules SDK
pip install jules-agent-sdk
```

### 2. Get API Key

1. Go to <https://jules.google/>
2. Sign in with your Google account
3. Navigate to **Settings** → **API Keys**
4. Click **"Create API Key"**
5. Copy your key (looks like `AQ.xxxxx...`)

### 3. Configure Environment

Add to your `.env` file:

```bash
# .env
JULES_API_KEY=AQ.Ab8RN6LliWPrEfS_VGB1nncm6BxVB-0JmEyAyC-5_NqVkbHW4g
```

**Done!** Jules is now available.

---

## 🎯 First Task: Simple Feature

Let's delegate a simple task to Jules:

```python
# Example: Add error handling to API
result = cde_delegateToJules(
    user_prompt="Add comprehensive error handling and logging to all API endpoints",
    branch="develop"
)
```

**What happens:**

1. Jules resolves your project (auto-connects via GitHub)
2. Creates a session with your prompt
3. Analyzes your codebase (full context)
4. Generates and executes code changes
5. Returns results with activity log

**Output:**

```json
{
  "success": true,
  "session_id": "sessions/abc123",
  "state": "COMPLETED",
  "modified_files": [
    "src/api/users.py",
    "src/api/auth.py",
    "tests/test_api.py"
  ],
  "activities_count": 8,
  "log": "Jules Session Activity Log:\n...",
  "metadata": {
    "session_url": "https://jules.google/sessions/abc123",
    "prompt": "Add comprehensive error handling...",
    "branch": "develop"
  }
}
```

---

## 🚀 Common Use Cases

### Use Case 1: Quick Feature

**Scenario:** Add a simple feature

```python
cde_delegateToJules(
    user_prompt="Add user profile endpoint with CRUD operations",
    branch="main"
)
```

**Duration:** ~10-15 minutes

---

### Use Case 2: Complex Refactor (with Plan Approval)

**Scenario:** Major refactoring that needs review

```python
cde_delegateToJules(
    user_prompt="Migrate from REST to GraphQL with comprehensive type safety",
    require_plan_approval=True,  # ⚠️ You'll approve the plan first
    timeout=3600  # 1 hour
)
```

**Workflow:**

1. Jules analyzes codebase
2. Generates execution plan
3. **You review and approve** the plan
4. Jules executes changes
5. Returns results

**Duration:** ~30-60 minutes

---

### Use Case 3: Long-Running Task (Detached)

**Scenario:** Very complex task you want to run in background

```python
cde_delegateToJules(
    user_prompt="Complete system-wide security audit and apply all recommended fixes",
    detached=True,  # Don't wait, return immediately
    timeout=7200  # 2 hours
)
```

**Workflow:**

1. Jules starts session
2. Returns session ID immediately
3. You can check progress at Jules web UI
4. Session continues in background

**Duration:** Variable (2+ hours)

---

## 🔍 Checking Available Agents

Before delegating, check which agents are available:

```python
result = cde_listAvailableAgents()
```

**Output:**

```json
{
  "summary": "2/4 agents available",
  "available_agents": [
    {
      "name": "Jules",
      "type": "async_api",
      "status": "available",
      "capabilities": ["full_context", "plan_approval", "long_running"],
      "best_for": ["refactoring", "complex_features"]
    },
    {
      "name": "Copilot CLI",
      "type": "sync_cli",
      "status": "available",
      "capabilities": ["quick_suggestions", "code_generation"],
      "best_for": ["quick_fixes", "code_completion"]
    }
  ],
  "recommendations": {
    "complex_tasks": "Jules (async, full context)",
    "quick_fixes": "Copilot CLI",
    "documentation": "Gemini CLI"
  }
}
```

---

## 🎓 Best Practices

### When to Use Jules

✅ **USE Jules for:**

- Complex features (4-8 hour estimated tasks)
- Large-scale refactoring
- Multi-file changes with dependencies
- Tasks needing full codebase context
- Long-running operations

❌ **DON'T use Jules for:**

- Quick typo fixes (use Copilot CLI)
- Single-file edits (use Copilot CLI)
- Documentation generation (use Gemini CLI)
- Simple code suggestions (use Copilot CLI)

### Prompt Writing Tips

**❌ BAD Prompts:**

- "Fix the bug" (too vague)
- "Improve code" (no specifics)
- "Make it better" (unclear)

**✅ GOOD Prompts:**

- "Add comprehensive error handling to all API endpoints with proper HTTP status codes and error messages"
- "Refactor authentication module to use OAuth2 with JWT tokens, including refresh token logic"
- "Implement caching layer using Redis for database queries with TTL of 5 minutes"

**Key Elements:**

1. **Specific action** (Add, Refactor, Implement)
2. **Target scope** (authentication module, API endpoints)
3. **Technical details** (OAuth2, Redis, TTL)
4. **Acceptance criteria** (implicit: working code with proper patterns)

---

## 🛠️ Configuration Options

### Environment Variables

```bash
# .env

# Required
JULES_API_KEY=your-api-key-here

# Optional
JULES_BASE_URL=https://jules.googleapis.com/v1alpha  # Custom endpoint
JULES_DEFAULT_TIMEOUT=1800  # 30 minutes
JULES_REQUIRE_PLAN_APPROVAL=false  # Global default
```

### Per-Task Configuration

```python
cde_delegateToJules(
    user_prompt="Your task",
    branch="develop",           # Git branch to use
    require_plan_approval=True, # Override global setting
    timeout=3600,               # Custom timeout (seconds)
    detached=False              # Wait for completion
)
```

---

## 🔧 Troubleshooting

### Error: "JULES_API_KEY not found"

**Solution:** Add key to `.env` file (see Setup step 2)

### Error: "No Jules source found for project"

**Solution:** Connect your repository at <https://jules.google/>

1. Go to Jules dashboard
2. Click "Connect Repository"
3. Authorize GitHub
4. Select your repo

### Error: "jules-agent-sdk not installed"

**Solution:**

```bash
pip install jules-agent-sdk
```

### Session Takes Too Long

**Solutions:**

1. **Increase timeout:**

   ```python
   cde_delegateToJules(
       user_prompt="...",
       timeout=7200  # 2 hours
   )
   ```

2. **Use detached mode:**

   ```python
   cde_delegateToJules(
       user_prompt="...",
       detached=True
   )
   # Check progress at Jules web UI
   ```

---

## 📚 Next Steps

### Learn More

- **Full Documentation:** `specs/design/multi-agent-orchestration-system.md`
- **Jules CLI:** <https://jules.google/docs/cli/reference>
- **Jules API:** <https://developers.google.com/jules/api>

### Advanced Features

- **Agent Selection Policy:** Let CDE choose best agent automatically
- **Parallel Execution:** Run multiple agents concurrently
- **Skill Integration:** Combine Jules with dynamic skill system

### Get Help

- **Issues:** Report bugs at GitHub Issues
- **Questions:** Ask in project discussions
- **Jules Support:** <https://jules.google/docs/feedback/>

---

## 🎉 Success Checklist

- [ ] Jules SDK installed (`pip install jules-agent-sdk`)
- [ ] API key configured in `.env`
- [ ] Repository connected at <https://jules.google/>
- [ ] First task completed successfully
- [ ] Understand when to use Jules vs CLI agents
- [ ] Know how to check agent availability

**Ready to delegate complex tasks to Jules!** 🚀

---

**Pro Tip:** Start with `require_plan_approval=True` for your first few tasks to understand how Jules works, then switch to auto-approval for routine tasks.
