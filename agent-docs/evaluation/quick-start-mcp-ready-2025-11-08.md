---
title: "MCP Quick Start - Ready to Use"
description: "Quick guide to start using MCP tools with your real projects today"
type: "guide"
status: "active"
created: "2025-11-08"
updated: "2025-11-08"
author: "CDE Evaluation Agent"
---

## 🚀 MCP Tools - Quick Start Guide

### TL;DR: Yes, Use It Now ✅

The CDE Orchestrator MCP is **production-ready** for:
- Documentation organization
- Development workflow routing
- Project setup and governance
- Knowledge management

---

## 5-Minute Setup

### 1. Verify Server is Running

The MCP server runs via FastMCP (stdio transport). It's ready when called from your IDE/agent.

### 2. Test Basic Tools

#### Test Documentation Audit
```bash
cde_scanDocumentation("path/to/your/project")
```

Returns: Number of docs, issues found, recommendations

#### Test Workflow Selection
```bash
cde_selectWorkflow("Add authentication with OAuth2")
```

Returns: Workflow type, complexity, estimated time, required skills

#### Test Project Setup
```bash
cde_setupProject("path/to/your/project", force=False)
```

Returns: Files created (AGENTS.md, workflow.yml, etc.)

---

## 3 Most Important Tools

| Tool | When to Use | Result |
|------|-----------|--------|
| `cde_selectWorkflow()` | **FIRST** - Before any feature | Workflow route + time estimate |
| `cde_scanDocumentation()` | Project audit | Documentation health score |
| `cde_setupProject()` | Initialize project | Governance structure |

---

## Your First Real Project Workflow

### Example: Add feature to your project

```python
# 1. ANALYZE: What kind of work is this?
workflow = cde_selectWorkflow("Add user authentication with JWT tokens")

# Expected output:
{
  "workflow_type": "standard",
  "complexity": "moderate",
  "estimated_duration": "2-3 hours",
  "required_skills": ["jwt-auth", "security-best-practices"],
  "confidence": 0.87
}

# 2. SOURCE: Get knowledge about JWT
skills = cde_sourceSkill("JWT authentication patterns", destination="ephemeral")

# Expected output:
{
  "status": "success",
  "skills_downloaded": [
    {
      "name": "jwt-auth-guide.md",
      "source": "awesome-claude-skills"
    }
  ]
}

# 3. SELECT: Which agent should do this?
agent = cde_selectAgent("Implement JWT authentication middleware")

# Expected output:
{
  "recommended_agent": "claude-code",
  "confidence": 0.92,
  "reasoning": "Claude Code excels at security-critical middleware"
}

# 4. EXECUTE: Run the workflow (manual or agent-based)
# - If using agent: cde_executeWithBestAgent(...)
# - If manual: Use the workflow recommendation above
```

---

## Tool Categories & Readiness

### ✅ READY NOW (Use immediately)

- `cde_scanDocumentation` - Documentation audit
- `cde_analyzeDocumentation` - Quality metrics
- `cde_setupProject` - Project initialization
- `cde_onboardingProject` - Project analysis
- `cde_selectWorkflow` - Workflow routing
- `cde_sourceSkill` - Knowledge sourcing
- `cde_updateSkill` - Skill maintenance
- `cde_listAvailableAgents` - Agent discovery
- `cde_selectAgent` - Agent selection

### ⚠️ REQUIRES SETUP (Works, but optional)

- `cde_executeWithBestAgent` - Needs AWS Bedrock
- `cde_delegateToJules` - Needs Jules remote

### 🔬 EXPERIMENTAL (Reference only)

- `cde_executeFullImplementation` - Use for guidance

---

## Success Checklist for Your Real Project

- [ ] Run `cde_scanDocumentation()` to audit current state
- [ ] Run `cde_analyzeDocumentation()` to get quality score
- [ ] Run `cde_setupProject()` to initialize governance
- [ ] Use `cde_selectWorkflow()` for all new features
- [ ] Use `cde_sourceSkill()` to build knowledge base
- [ ] Use `cde_selectAgent()` to pick development approach

---

## Common Scenarios

### Scenario 1: Documentation Cleanup

```
1. cde_scanDocumentation(".")
   → Find 5 docs missing metadata, 2 orphaned files

2. cde_analyzeDocumentation(".")
   → Quality score 72/100, needs deployment guide

3. cde_setupProject(".", force=False)
   → Create AGENTS.md, workflow.yml

4. cde_publishOnboarding(files, ".")
   → Apply governance structure

Result: Clean, organized documentation
```

### Scenario 2: Feature Development

```
1. cde_selectWorkflow("Add Redis caching")
   → workflow_type="standard", duration="1-2 hours"

2. cde_sourceSkill("redis caching", "ephemeral")
   → Download patterns and examples

3. cde_selectAgent("Implement caching layer")
   → Recommend Claude Code

4. (Manual or automated) Implement

Result: Feature delivered with right tools
```

### Scenario 3: Team Knowledge Management

```
1. cde_sourceSkill("microservices patterns", "base")
   → Add to team knowledge base (persistent)

2. (Share) Reference the skill in project docs

3. cde_updateSkill("microservices", ["k8s", "grpc"])
   → Keep team knowledge current

Result: Shared expertise across projects
```

---

## Troubleshooting

### Issue: `cde_selectAgent()` shows no agents

**Solution**: Run `cde_listAvailableAgents()` first
- If empty: Install Claude Code or Aider
- If available but not showing: Check environment variables

### Issue: Skill sourcing returns empty

**Solution**: Check configured skill sources
- Verify internet connection
- Try manual skill creation in `.copilot/skills/`

### Issue: High complexity features getting low confidence

**Solution**: More specific user prompts help
- Instead of: "Add feature"
- Use: "Add two-factor authentication using TOTP tokens"

---

## Next Steps

### This Week

1. ✅ Set up a test project (use provided test-project-real)
2. ✅ Run `cde_scanDocumentation()` on your real project
3. ✅ Test `cde_selectWorkflow()` with 2-3 example features
4. ✅ Review recommended workflows with team

### Next Week

1. ✅ Use `cde_selectWorkflow()` for next real feature
2. ✅ Build first item in `.copilot/skills/base/` knowledge base
3. ✅ Document workflow as team standard

### Later

1. ✅ Configure AWS Bedrock (if you want agent automation)
2. ✅ Integrate agent delegation into CI/CD
3. ✅ Build comprehensive skills library

---

## Resources

- **Full Evaluation**: `agent-docs/evaluation/evaluation-mcp-tools-2025-11-08.md`
- **Architecture Guide**: `specs/design/ARCHITECTURE.md`
- **Governance Rules**: `specs/governance/DOCUMENTATION_GOVERNANCE.md`
- **Agent Integration**: `AGENTS.md`

---

**Status**: ✅ Ready to use now
**Recommendation**: Start with `cde_selectWorkflow()` and `cde_scanDocumentation()`
**Timeline**: Test this week, adopt next week, automate later

🚀 **Begin with test project**: `E:\scripts-python\test-project-real`
