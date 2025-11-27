---
title: Quick Reference Onboarding
description: Legacy documentation file
type: guide
status: archived
created: '2025-11-27'
updated: '2025-11-27'
author: Legacy
---

# 🚀 CDE Onboarding - Quick Reference Card

> **Print this. Keep it visible. Use it always.**

---

## THE PROMPT (Copy & Paste)

```
@workspace I want to integrate CDE Orchestrator as the complete orchestration
system for this project. Please:

1. ANALYZE current project state using cde_onboardingProject
2. SETUP project structure with cde_setupProject
3. CONFIGURE .vscode/mcp.json for external project integration
4. VERIFY all 27 CDE tools are available with cde_healthCheck
5. GENERATE a professional spec for [FEATURE] using cde_generateSpec
6. RECOMMEND optimal workflow with cde_selectWorkflow

Execute all steps sequentially and show results for each phase.
```

**Replace `[FEATURE]` with your next feature/improvement**

---

## After Onboarding: Development Flow

```
1. cde_selectWorkflow("Feature description")
2. cde_generateSpec("Feature description")
3. cde_sourceSkill("required-skill") [if needed]
4. cde_startFeature("Feature description")
5. Work on Phase 1
6. cde_submitWork(phase="phase1", results={...})
7. Repeat steps 5-6 for phases 2-6
```

---

## Common Commands

| Command | Purpose |
|---------|---------|
| `cde_healthCheck` | Verify 27 tools available |
| `cde_onboardingProject` | Analyze project |
| `cde_setupProject` | Create CDE structure |
| `cde_generateSpec` | Generate professional spec |
| `cde_selectWorkflow` | Recommend workflow |
| `cde_sourceSkill` | Download external skill |
| `cde_startFeature` | Start new feature |
| `cde_submitWork` | Submit phase work |

---

## Quick Fixes

### Tool Not Found
```
Ctrl+Shift+P → "Developer: Reload Window"
Wait 15 seconds
```

### Health Check < 27 Tools
```powershell
cd "E:\scripts-python\CDE Orchestrator MCP"
.\scripts\diagnose-cde-tools.ps1
```

### Need Configuration
```
See: docs/configuration-guide.md
Create: .vscode/mcp.json with absolute paths
```

---

## File Locations

- **Full Guide**: `docs/THE-ULTIMATE-ONBOARDING-PROMPT.md`
- **Spanish**: `docs/PROMPT-DEFINITIVO-ONBOARDING-ES.md`
- **Quick Fix**: `docs/QUICKFIX-RELOAD-TOOLS.md`
- **Config**: `docs/configuration-guide.md`

---

## Success Checklist

After onboarding:
- [ ] 27 tools available (`cde_healthCheck`)
- [ ] Structure created (specs/, memory/, .cde/)
- [ ] Spec generated for next feature
- [ ] Workflow recommended
- [ ] Next steps clear

---

**Print this card. Use it daily. 🚀**
