---
title: "Model Usage Rules: CLI vs SDK Patterns"
description: "Memories and rules for choosing between CLI tools and SDK/MCP approaches for different AI models and services"
type: research
status: active
created: "2025-11-05"
updated: "2025-11-05"
author: "GitHub Copilot"
tags:
  - cli
  - sdk
  - mcp
  - models
  - patterns
llm_summary: |
  Decision framework for CLI vs SDK usage across AI models.
  Covers Claude Code, Jules, Gemini CLI, AWS Bedrock SDK, and MCP integration patterns.
  Includes practical rules and configuration examples from CDE Orchestrator execution.
---

# 📋 Model Usage Rules: CLI vs SDK Patterns

**Memories from CDE Orchestrator MCP Execution**
*Documenting learned patterns for CLI vs SDK selection across different AI services*

## 🎯 Core Decision Framework

### Rule 1: CLI First for Interactive Development

**When to Use CLI Tools:**
- ✅ **Real-time coding sessions** (Claude Code, Aider)
- ✅ **Background research tasks** (Gemini CLI, Jules)
- ✅ **Quick prototyping** (GitHub Copilot CLI)
- ✅ **Parallel execution** (Multiple Jules sessions)

**When to Use SDK/MCP:**
- ✅ **Integrated workflows** (MCP server tools)
- ✅ **Batch processing** (AWS Bedrock SDK)
- ✅ **Custom integrations** (API-based services)
- ✅ **Production deployments** (Managed services)

### Rule 2: Complexity Threshold

```
Low Complexity (< 30 min)     → CLI Tools
Medium Complexity (1-4 hours)  → CLI + MCP Orchestration
High Complexity (4+ hours)     → Jules Parallel + MCP
Enterprise Scale              → SDK Integration
```

## 🛠️ Tool-Specific Patterns

### Claude Code (Anthropic)

**CLI Usage:**

```bash
# Interactive coding
claude-code

# With specific model
claude-code --provider bedrock --model anthropic.claude-sonnet-4-5-20250929-v1:0
```

**SDK/MCP Usage:**

```python
# Through MCP tools
cde_delegateToJules(user_prompt="Complex task", require_plan_approval=True)
```

**Learned Rule:** Use CLI for interactive coding, MCP delegation for complex multi-step tasks.

### Jules (Google)

**CLI Usage:**

```bash
# Parallel development
jules remote create --session "Feature implementation"
jules remote list --session
jules remote pull --session <ID> --apply
```

**Background Pattern:**

```python
# Monitor script from this execution
def get_sessions_status():
    output = run_command('jules remote list --session')
    # Parse and track 10 parallel sessions
```

**Learned Rule:** Jules excels at parallel execution of roadmap tasks. Use for distributed development across multiple phases.

### Gemini CLI (Google)

**CLI Usage:**

```bash
# Background research
gemini --model=gemini-2.0-flash-exp --yolo "research query"
```

**PowerShell Background Pattern:**

```powershell
Start-Job -ScriptBlock {
    gemini --model=gemini-2.0-flash-exp --yolo "investigate topic"
} -Name "GeminiResearch"
```

**Learned Rule:** Perfect for background research while continuing other work. Use PowerShell jobs for non-blocking execution.

### AWS Bedrock SDK

**SDK Usage:**

```python
import boto3

bedrock = boto3.client('bedrock-runtime')
response = bedrock.invoke_model(
    modelId='anthropic.claude-3-sonnet-20240229-v1:0',
    body=json.dumps({"prompt": "...", "max_tokens": 1000})
)
```

**Learned Rule:** Use SDK for batch processing, custom integrations, and when you need fine-grained control over model parameters.

### GitHub Copilot CLI

**CLI Usage:**

```bash
# Code suggestions
gh copilot suggest "implement authentication"

# Code explanation
gh copilot explain "complex function"
```

**Learned Rule:** Best for quick code suggestions and explanations. Use within existing terminal workflows.

## 🔄 Integration Patterns Learned

### Pattern 1: MCP-First Orchestration
```python
# From this execution - Always start with MCP analysis
recommendation = cde_selectWorkflow("Add Redis caching")
# Returns optimal workflow + recipe + skills

# Then delegate based on complexity
if recommendation["complexity"] == "epic":
    cde_delegateToJules(user_prompt=task, require_plan_approval=True)
else:
    # Use CLI tools directly
```

### Pattern 2: Parallel Execution Framework
```python
# Learned from Jules execution plan
# 10 parallel sessions across phases:
# - 3 testing infrastructure
# - 3 performance optimization
# - 2 documentation
# - 2 advanced features

# Monitoring pattern
def monitor_progress():
    sessions = get_sessions_status()
    planning = sum(1 for s in sessions if s["status"] == "Planning")
    in_progress = sum(1 for s in sessions if s["status"] == "In Progress")
    completed = sum(1 for s in sessions if s["status"] == "Complete")
```

### Pattern 3: Background Research Pipeline
```powershell
# Gemini CLI background research
Start-Job -ScriptBlock {
    gemini --model=gemini-2.0-flash-exp --yolo "research microservices patterns"
} -Name "ResearchJob"

# Monitor and collect results
Get-Job -Name "ResearchJob"
Receive-Job -Name "ResearchJob" -Keep
```

## 📚 Skills Documented from This Execution

### Skill 1: Parallel Development Orchestration
**Source:** Jules execution with 10 concurrent sessions
**Pattern:** Distribute roadmap tasks across specialized agents
**Files:** `scripts/jules_monitor.py`, `.cde/jules_execution_plan.md`

### Skill 2: CLI Background Processing
**Source:** PowerShell jobs with Gemini CLI
**Pattern:** Non-blocking research while continuing development
**Files:** `.copilot/skills/parallel-ai-research.md`

### Skill 3: MCP Workflow Routing
**Source:** CDE Orchestrator intelligent analysis
**Pattern:** Automatic workflow selection based on complexity
**Files:** `src/mcp_tools/workflow.py`, `src/mcp_tools/onboarding.py`

### Skill 4: AWS Bedrock Integration
**Source:** Claude Code + Aider configuration
**Pattern:** Multiple authentication methods (CLI, env vars, profiles)
**Files:** `BEDROCK_SETUP.md`, `.env.bedrock`

## 🔗 Documentation Links

### Official Documentation

- **Claude Code:** [https://docs.anthropic.com/claude/docs/claude-code](https://docs.anthropic.com/claude/docs/claude-code)
- **Jules:** [https://jules.google/](https://jules.google/)
- **Gemini CLI:** [https://ai.google.dev/docs](https://ai.google.dev/docs)
- **AWS Bedrock:** [https://docs.aws.amazon.com/bedrock/](https://docs.aws.amazon.com/bedrock/)
- **GitHub Copilot CLI:** [https://docs.github.com/en/copilot/github-copilot-in-the-cli](https://docs.github.com/en/copilot/github-copilot-in-the-cli)

### Project-Specific

- **CDE Architecture:** `specs/design/ARCHITECTURE.md`
- **MCP Tools:** `AGENTS.md`, `GEMINI.md`
- **Setup Guides:** `BEDROCK_SETUP.md`, `CONTRIBUTING.md`

### Configuration Examples

- **Environment Setup:** `.env.example`
- **VS Code Tasks:** `.vscode/tasks.json`
- **Pre-commit Hooks:** `.pre-commit-config.yaml`

## ⚡ Quick Reference Rules

| Task Type | Primary Tool | Secondary | Reasoning |
|-----------|-------------|-----------|-----------|
| Interactive Coding | Claude Code CLI | Aider | Real-time collaboration |
| Parallel Development | Jules CLI | MCP orchestration | Distributed execution |
| Background Research | Gemini CLI | PowerShell jobs | Non-blocking |
| Batch Processing | AWS Bedrock SDK | Custom scripts | Scalability |
| Code Suggestions | GitHub Copilot CLI | IDE extensions | Quick assistance |
| Complex Workflows | MCP Tools | CLI delegation | Intelligent routing |

## 🎯 Success Patterns from This Execution

1. **MCP-First Approach:** Always analyze with `cde_selectWorkflow` before starting work
2. **Parallel Execution:** Use Jules for distributing large roadmaps across multiple agents
3. **Background Processing:** Leverage CLI tools with PowerShell jobs for non-blocking research
4. **Skill Persistence:** Document patterns in `.copilot/skills/` for reuse
5. **Monitoring:** Implement continuous tracking for distributed work

## 🔄 Evolution Notes

**Current State:** CLI-heavy for development speed, MCP for orchestration
**Future Direction:** More SDK integration for production deployments
**Learnings:** Parallel execution significantly accelerates development (10x with Jules)
**Recommendations:** Start with CLI for exploration, migrate to SDK for production
