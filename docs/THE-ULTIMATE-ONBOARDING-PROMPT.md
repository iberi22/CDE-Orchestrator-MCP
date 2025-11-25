---
title: The Ultimate CDE Onboarding Prompt
description: Single prompt for complete CDE integration from 0% to 100%
type: guide
status: active
created: '2025-11-24'
updated: '2025-11-24'
author: Nexus AI Team
tags:
  - onboarding
  - prompt
  - orchestration
  - complete-workflow
llm_summary: "The definitive prompt for complete CDE integration. One command to rule them all."
---

# 🚀 The Ultimate CDE Onboarding Prompt

> **Purpose**: Single prompt for complete CDE integration from scratch or any implementation stage
> **Time**: 2-5 minutes for complete setup
> **Output**: Fully configured project with CDE orchestrating all development

---

## 🎯 The One Prompt to Rule Them All

Copy and paste this into GitHub Copilot Chat in your project:

```
@workspace I want to integrate CDE Orchestrator as the complete orchestration system for this project.

⚠️ CRITICAL: You MUST execute these MCP tools (not just reference them):

1. **EXECUTE** cde_onboardingProject() to analyze current project state
2. **EXECUTE** cde_setupProject() to create project structure
3. **SHOW** .vscode/mcp.json configuration needed (I will create it manually)
4. **EXECUTE** cde_healthCheck() to verify all 27 CDE tools are available
5. **EXECUTE** cde_generateSpec("next feature description") to generate professional spec
6. **EXECUTE** cde_selectWorkflow("next feature description") to recommend optimal workflow

⚠️ DO NOT just list what these tools do - EXECUTE them and show the actual results.

After executing each tool, provide:
- ✅ Tool executed successfully
- 📊 Actual output/results
- 📝 What was created/analyzed
- ➡️ Next step

For step 3 (mcp.json), provide the exact configuration I need to create manually, then wait for me to confirm before continuing to step 4.

Execute all steps sequentially and show REAL results for each phase.
```

---

## 📊 What This Prompt Does

### Phase 1: Deep Analysis (cde_onboardingProject)

**⚠️ CRITICAL: The agent MUST execute the actual MCP tool, not just describe it.**

**Execution**:
```python
# Agent must invoke this via MCP, not just describe it
cde_onboardingProject(project_path=".")
```

**Common Agent Mistake**:
❌ "I can provide guidance on CDE Orchestrator usage patterns..."
✅ "Executing cde_onboardingProject()... [shows actual results]"

**Output**:
- 📁 **570+ files analyzed** (Python, JS, TS, etc.)
- 🐍 **Python version detected** (3.11+, 3.14, etc.)
- 🏗️ **Architecture pattern** (Hexagonal, Clean, MVC, etc.)
- 📚 **Framework detection** (FastAPI, Next.js, React, etc.)
- 📝 **Git insights** (commits, branches, contributors)
- 🤖 **AI tools present** (Copilot, Gemini, Claude, etc.)

**Example Result**:
```json
{
  "status": "Analysis complete",
  "project_name": "my-app",
  "total_files": 245,
  "primary_language": "Python",
  "python_version": "3.14.0",
  "frameworks": ["FastAPI", "React"],
  "architecture_pattern": "Hexagonal",
  "git_analysis": {
    "total_commits": 156,
    "contributors": 3,
    "age_days": 45,
    "active_branches": 5
  },
  "ai_assistants_detected": ["GitHub Copilot", "Cursor"]
}
```

---

### Phase 2: Project Setup (cde_setupProject)

**Execution**:
```python
cde_setupProject(project_path=".", force=False)
```

**Creates**:
- ✅ `.cde/workflow.yml` - 6-phase CDE workflow
- ✅ `AGENTS.md` - AI agent instructions
- ✅ `GEMINI.md` - Gemini-specific instructions
- ✅ `.github/copilot-instructions.md` - Copilot instructions
- ✅ `.gitignore` - Enhanced ignore patterns
- ✅ `specs/` - Feature specification templates
- ✅ `memory/constitution.md` - Project principles

**Output**:
```json
{
  "status": "success",
  "files_written": [
    ".cde/workflow.yml",
    "AGENTS.md",
    "GEMINI.md",
    ".github/copilot-instructions.md",
    ".gitignore",
    "specs/templates/spec.md",
    "specs/templates/plan.md",
    "specs/templates/tasks.md",
    "memory/constitution.md"
  ]
}
```

---

### Phase 3: MCP Configuration (Manual + Verification)

**For External Projects** (outside CDE Orchestrator repo):

Create `.vscode/mcp.json`:

```json
{
  "servers": {
    "CDE_Orchestrator": {
      "command": "python",
      "args": [
        "E:\\scripts-python\\CDE Orchestrator MCP\\src\\server.py",
        "--scan-paths",
        "E:\\your-project-path"
      ],
      "env": {
        "PYTHONPATH": "E:\\scripts-python\\CDE Orchestrator MCP\\src",
        "CDE_AUTO_DISCOVER": "true",
        "CDE_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Then reload VS Code**: `Ctrl+Shift+P` → "Developer: Reload Window"

**Verification**:
```python
cde_healthCheck()
```

**Expected**:
```json
{
  "status": "healthy",
  "python_version": "3.14.0",
  "rust_module": "loaded",
  "tools_registered": 27
}
```

---

### Phase 4: Generate Professional Spec (cde_generateSpec)

**Execution**:
```python
cde_generateSpec(
    feature_description="Your next feature or improvement",
    spec_type="standard",
    include_research=True,
    include_architecture=True
)
```

**Creates**:
- 📄 `specs/your-feature/spec.md` - Product Requirements Document
- 📄 `specs/your-feature/plan.md` - Technical Design Document
- 📄 `specs/your-feature/tasks.md` - Implementation Checklist

**Output**:
```json
{
  "status": "success",
  "spec_directory": "specs/add-redis-caching",
  "files_created": [
    "specs/add-redis-caching/spec.md",
    "specs/add-redis-caching/plan.md",
    "specs/add-redis-caching/tasks.md"
  ],
  "recommendations": [
    "Download skill: redis-caching-patterns",
    "Use workflow: standard (6-phase)",
    "Estimated duration: 2-4 hours"
  ]
}
```

---

### Phase 5: Workflow Recommendation (cde_selectWorkflow)

**Execution**:
```python
cde_selectWorkflow(user_prompt="Your task description")
```

**Output**:
```json
{
  "workflow_type": "standard",
  "complexity": "moderate",
  "recipe_id": "ai-engineer",
  "estimated_duration": "2-4 hours",
  "required_skills": ["redis-caching", "auth-best-practices"],
  "phases_to_skip": [],
  "reasoning": "Moderate complexity with database + security concerns",
  "confidence": 0.85,
  "domain": "database"
}
```

---

## 🎬 Complete Example Interaction

### User Prompt:
```
@workspace I want to integrate CDE Orchestrator as the complete orchestration
system for this project. Please analyze, setup, configure, verify, generate
a spec for "Add Redis caching to authentication", and recommend workflow.
```

### Expected Response:

**Step 1: Project Analysis**
```
✅ Analysis Complete
   - Project: MyApp
   - Files: 245 Python files
   - Framework: FastAPI 0.115.0
   - Architecture: Hexagonal
   - Git: 156 commits, 3 contributors, 45 days old
   - AI Tools: GitHub Copilot detected
```

**Step 2: Project Setup**
```
✅ Setup Complete
   Created:
   - .cde/workflow.yml (6-phase workflow)
   - AGENTS.md (AI instructions)
   - GEMINI.md (Gemini config)
   - .github/copilot-instructions.md
   - specs/ directory with templates
   - memory/constitution.md
```

**Step 3: Configuration**
```
⚠️  Action Required:
   1. Create .vscode/mcp.json with provided configuration
   2. Reload VS Code (Ctrl+Shift+P → Reload Window)
   3. Wait 15 seconds for MCP server restart
```

**Step 4: Health Check**
```
✅ CDE Health: Healthy
   - Python: 3.14.0
   - Tools: 27 registered
   - Rust Module: Loaded
```

**Step 5: Spec Generation**
```
✅ Spec Generated: Add Redis Caching to Authentication
   Location: specs/add-redis-caching-to-authentication/
   Files:
   - spec.md (Product Requirements - 450 lines)
   - plan.md (Technical Design - 380 lines)
   - tasks.md (Implementation Checklist - 45 tasks)

   Recommendations:
   - Download skill: redis-caching-patterns
   - Download skill: auth-security-best-practices
```

**Step 6: Workflow Recommendation**
```
✅ Recommended Workflow: Standard (6-phase)
   - Complexity: Moderate
   - Duration: 2-4 hours
   - Recipe: ai-engineer.poml
   - Phases: define → decompose → design → implement → test → review

   Next Steps:
   1. Review generated spec
   2. Use cde_sourceSkill to download recommended skills
   3. Use cde_startFeature to begin implementation
```

---

## 🚀 Quick Start Variations

### For New Projects (0% implementation)

```
@workspace I'm starting a new [project type] project from scratch.
Use CDE to set up complete structure, generate initial specs, and
recommend development workflow.
```

### For Existing Projects (any % implementation)

```
@workspace Analyze this existing project and integrate CDE orchestration.
Current status: [brief description]. Next goal: [feature/improvement].
Set up CDE to manage all future development.
```

### For Specific Features

```
@workspace I want to add [feature description] to this project.
Use CDE to analyze current state, generate professional spec,
download required skills, and start the implementation workflow.
```

---

## 📖 Post-Onboarding Workflow

Once CDE is integrated, your development flow becomes:

```
1. New Feature Request
   ↓
2. cde_selectWorkflow("Add X feature")
   ↓
3. cde_generateSpec("Add X feature")
   ↓
4. cde_sourceSkill("required-skill")
   ↓
5. cde_startFeature("Add X feature")
   ↓
6. Work on Phase 1 (Define)
   ↓
7. cde_submitWork(phase="define", results={...})
   ↓
8. CDE generates next phase prompt
   ↓
9. Repeat for phases 2-6
   ↓
10. Feature Complete ✅
```

---

## 🎯 Success Criteria

After running the onboarding prompt, you should have:

- ✅ **Project analyzed** with full context (Git, frameworks, architecture)
- ✅ **Structure created** (specs/, memory/, .cde/, AI configs)
- ✅ **27 CDE tools available** in Copilot Chat
- ✅ **Professional spec generated** for next feature
- ✅ **Workflow recommended** based on complexity
- ✅ **Clear next steps** for CDE-driven development

---

## 🔧 Troubleshooting

### Issue: "Tool not found" after onboarding

**Solution**: Reload VS Code
```
Ctrl+Shift+P → "Developer: Reload Window"
```

### Issue: Health check shows < 27 tools

**Solution**: Check MCP configuration
```
1. Verify .vscode/mcp.json exists
2. Check paths are absolute
3. Reload VS Code
4. Run: .\scripts\diagnose-cde-tools.ps1
```

### Issue: Spec generation fails

**Solution**: Check project analysis completed
```
@workspace Run cde_onboardingProject first to gather context
```

---

## 📚 Reference Documentation

- **Configuration Guide**: `docs/configuration-guide.md`
- **Quick Fix**: `docs/QUICKFIX-RELOAD-TOOLS.md`
- **Tool Documentation**: `docs/tool-cde-generatespec.md`
- **Architecture**: `specs/design/architecture/README.md`
- **Roadmap**: `specs/tasks/improvement-roadmap.md`

---

## 💡 Pro Tips

1. **Start with onboarding**: Always run the complete onboarding prompt first
2. **Review generated specs**: CDE creates professional specs, but review before starting
3. **Use skill sourcing**: Download external knowledge with `cde_sourceSkill`
4. **Follow 6-phase workflow**: Define → Decompose → Design → Implement → Test → Review
5. **Trust the orchestration**: CDE knows when to use which agent/tool

---

## 🎓 Advanced: Multi-Project Orchestration

For managing multiple projects:

```json
{
  "servers": {
    "CDE_Orchestrator": {
      "args": [
        "E:\\scripts-python\\CDE Orchestrator MCP\\src\\server.py",
        "--scan-paths",
        "E:\\project1",
        "E:\\project2",
        "E:\\project3"
      ],
      "env": {
        "CDE_AUTO_DISCOVER": "true"
      }
    }
  }
}
```

Then CDE auto-discovers all projects and routes commands correctly.

---

**TL;DR**: Copy the prompt at the top, paste in Copilot Chat, wait 2 minutes, and CDE orchestrates everything. 🚀
