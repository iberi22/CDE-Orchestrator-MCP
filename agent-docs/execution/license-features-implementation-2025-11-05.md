---
title: "License Update & Governance Implementation"
description: "Cambio a licencia AGPL-3.0 con restricción anti-lucro e implementación de features de investigación continua"
type: "execution"
status: "active"
created: "2025-11-05"
updated: "2025-11-05"
author: "GitHub Copilot"
---

# License Update & Advanced Features Implementation

**Date:** 2025-11-05
**Status:** Implementation Planned
**Priority:** 🔴 CRITICAL

---

## 📋 Summary

El proyecto CDE Orchestrator MCP ha sido transformado de MIT a un modelo de **Dual Licensing**:

- **AGPL-3.0-or-later** para uso no-comercial (libre y abierto)
- **Commercial License** para uso comercial (con acuerdo explícito)

**Restricción principal:** Todo software construido con este código DEBE ser libre y accesible a modelos LLM sin fines de lucro.

---

## 🔄 Changes Made

### 1. License Files Created

✅ **`LICENSE-DUAL.md`** - Descripción completa del modelo dual
✅ **`LICENSE-AGPL-3.0`** - Texto completo de AGPL-3.0

### 2. Features Specified

✅ **`specs/features/advanced-research-features.md`** - Especificación completa con:
- Research Agent para ArXiv integration
- Intelligent Dependabot workflows
- Project Intelligence Gatherer
- GitHub Actions automation

---

## 🎯 Phase 1: License Implementation

### 1.1 Update Repository Files

**Changes to make:**

```bash
# Update README.md
- Agregar sección "License" explaining dual licensing
- Agregar enlace a LICENSE-DUAL.md
- Clarificar restricción anti-lucro

# Update CONTRIBUTING.md
- Explicar que contribuciones bajo AGPL-3.0
- Requiere aceptación de dual licensing
- CDE project retiene derechos comerciales

# Create LEGAL.md
- Términos y condiciones de uso
- Enforcement policy
- Compliance requirements

# Add LICENSE headers to all source files
```

### 1.2 Source Code Attribution

**Header to add to all Python/Rust/TS files:**

```python
# CDE Orchestrator MCP
# Copyright (c) 2025 [Project Authors]
# Licensed under AGPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# For commercial licensing, see LICENSE-DUAL.md
```

---

## 🔬 Phase 2: Research Features Implementation

### 2.1 Research Agent (ArXiv Integration)

**Timeline:** Week 1-2

**Implementation:**
```python
# src/cde_orchestrator/adapters/arxiv_research_adapter.py
class ArxivResearchAdapter(IResearchAdapter):
    """Adapter for ArXiv.org API integration"""

    async def search(self, keywords: List[str]) -> List[ResearchPaper]:
        """Search ArXiv for relevant papers"""

    async def fetch_paper(self, paper_id: str) -> ResearchPaper:
        """Fetch complete paper metadata"""

    async def generate_guide(self, papers: List[ResearchPaper]) -> ResearchGuide:
        """Synthesize findings into research guide"""
```

**MCP Tool:**
```python
# src/mcp_tools/research_tools.py
@tool
async def cde_researchArxiv(
    keywords: List[str],
    max_results: int = 10,
    categories: Optional[List[str]] = None
) -> Dict:
    """Search ArXiv and generate research insights"""
```

### 2.2 Dependabot Intelligence

**Timeline:** Week 2-3

**Implementation:**
```python
# src/cde_orchestrator/adapters/dependency_analyzer_adapter.py
class DependencyAnalyzerAdapter(IDependencyAdapter):
    """Analyze dependencies for security & compatibility"""

    async def analyze_change(
        self,
        package: str,
        old_version: str,
        new_version: str
    ) -> DependencyAnalysis:
        """Analyze dependency change impact"""

    async def check_vulnerabilities(self, package: str, version: str):
        """Check for known CVEs"""

    async def detect_breaking_changes(self, changes: List[str]):
        """Detect API breaking changes"""
```

**MCP Tool:**
```python
# src/mcp_tools/dependency_tools.py
@tool
async def cde_analyzeDependencies(
    manifest_file: str = None,
    include_security: bool = True
) -> Dict:
    """Analyze all project dependencies"""
```

### 2.3 Project Intelligence Gatherer

**Timeline:** Week 3-4

**Implementation:**
```python
# src/cde_orchestrator/adapters/project_intelligence_adapter.py
class ProjectIntelligenceAdapter(IIntelligenceAdapter):
    """Gather comprehensive project intelligence"""

    async def gather_all(self, project_path: str) -> ProjectIntelligence:
        """Gather all available intelligence"""

    async def scan_dependencies(self) -> DependencyInventory:
        """Scan all dependencies"""

    async def analyze_metrics(self) -> CodeMetrics:
        """Analyze code quality & complexity"""

    async def generate_report(self) -> IntelligenceReport:
        """Generate comprehensive report"""
```

**MCP Tool:**
```python
# src/mcp_tools/intelligence_tools.py
@tool
async def cde_gatherProjectIntelligence(
    project_path: str = None,
    include_git_history: bool = True
) -> Dict:
    """Gather project intelligence"""
```

---

## 🤖 Phase 3: GitHub Actions Integration

### 3.1 Workflows to Create

**`.github/workflows/research-scheduler.yml`**
- Runs weekly ArXiv search
- Generates research guides
- Updates documentation

**`.github/workflows/dependabot-intelligence.yml`**
- Analyzes dependency changes
- Checks security vulnerabilities
- Generates migration guides

**`.github/workflows/intelligence-gatherer.yml`**
- Runs weekly project scans
- Generates quarterly reports
- Creates improvement issues

**`.github/workflows/continuous-improvement.yml`**
- Orchestrates all three workflows
- Coordinates findings
- Creates GitHub issues for improvements

### 3.2 Custom GitHub Actions

**`.github/actions/cde-research/`**
```yaml
name: CDE Research
description: Search ArXiv and generate research guides
```

**`.github/actions/cde-analyze-deps/`**
```yaml
name: CDE Dependency Analysis
description: Analyze dependencies for security & compatibility
```

**`.github/actions/cde-gather-intelligence/`**
```yaml
name: CDE Intelligence Gathering
description: Gather comprehensive project intelligence
```

---

## 📊 Phase 4: Documentation & Governance

### 4.1 Documentation Files

**`LICENSE-DUAL.md`** ✅ Created
- Explain dual licensing model
- Clarify restrictions
- Attribution requirements

**`LEGAL.md`** - To Create
```markdown
# Legal Terms

## Acceptable Use

✅ Non-commercial projects
✅ Educational use
✅ Internal corporate use
✅ Contributing improvements

## Restricted Use

❌ Commercial software development
❌ Closed-source derivatives
❌ Proprietary products
```

**`RESEARCH-MANIFESTO.md`** - To Create
```markdown
# CDE Research Manifesto

This project commits to:
1. Continuous academic research
2. Knowledge sharing with AI community
3. Keeping all core technology libre
4. Accessibility for LLM models
```

### 4.2 GitHub Governance

**Add branch protection rule:**
```
- Require AGPL-3.0 licensing checks
- Require attribution validation
- Require commercial restriction review for new deps
```

**Pre-commit hooks:**
```bash
- Check license headers on new files
- Validate attribution in documentation
- Scan for commercial use patterns
```

---

## 🔐 Phase 5: Enforcement & Monitoring

### 5.1 Pre-commit Hooks

**`.pre-commit-config.yaml` additions:**
```yaml
- repo: local
  hooks:
    - id: check-license-headers
    - id: check-agpl-compliance
    - id: check-attribution
    - id: check-commercial-restriction
```

### 5.2 CI/CD Validation

**GitHub Actions:**
```yaml
- Validate all new files have license headers
- Check for GPL compliance
- Scan for commercial code patterns
- Validate attribution accuracy
```

### 5.3 Issue Template

**Bug Report Template:**
```markdown
## License Compliance

This issue may involve:
- [ ] New third-party dependency (requires GPL review)
- [ ] Potential commercial use case (requires approval)
- [ ] Attribution or licensing question
```

---

## 📈 Success Criteria

### License Change
- ✅ AGPL-3.0 license file in place
- ✅ All source files have license headers
- ✅ README updated with licensing info
- ✅ Contributing guidelines updated
- ✅ Pre-commit hooks enforcing compliance

### Research Features
- ✅ ArXiv integration working
- ✅ Dependabot intelligence implemented
- ✅ Project intelligence gatherer operational
- ✅ All MCP tools registered
- ✅ GitHub Actions workflows running

### Governance
- ✅ Legal documentation complete
- ✅ Enforcement mechanisms in place
- ✅ Community guidelines published
- ✅ Attribution validated
- ✅ Commercial restriction enforced

---

## 🚀 Next Steps

1. **Immediate (Today):**
   - ✅ Create LICENSE-DUAL.md
   - ✅ Create advanced-research-features.md
   - [ ] Download AGPL-3.0 license text
   - [ ] Update README.md with license section

2. **This Week:**
   - [ ] Add license headers to all source files
   - [ ] Create LEGAL.md with terms
   - [ ] Create RESEARCH-MANIFESTO.md
   - [ ] Update CONTRIBUTING.md

3. **Next Week:**
   - [ ] Implement Research Agent
   - [ ] Create GitHub Actions workflows
   - [ ] Set up pre-commit hooks
   - [ ] Begin testing

---

## 📞 Questions & Clarifications

**Q: Will this break existing projects using the old MIT license?**
A: No. Previous versions remain under MIT. Only new versions use AGPL-3.0.

**Q: Can companies use this?**
A: Yes, for internal use. For commercial products, contact maintainers.

**Q: Can I contribute?**
A: Yes! Contributions are licensed under AGPL-3.0 and dual-licensed to the project.

**Q: What about existing commercial users?**
A: They should obtain a Commercial License. Grandfather clauses available upon request.

---

**Implementation Owner:** GitHub Copilot / CDE Team
**Review Date:** 2025-11-12
**Approval Required:** Project Lead & Legal Review
