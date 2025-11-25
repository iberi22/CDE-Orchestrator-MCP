---
title: Professional Spec Generator - cde_generateSpec
description: Complete documentation for the professional specification generator tool
type: guide
status: active
created: '2025-11-24'
updated: '2025-11-24'
author: Nexus AI Team
tags:
  - tool
  - spec-generator
  - spec-kit
  - github
llm_summary: "Complete guide for cde_generateSpec tool. Generates professional feature specifications based on GitHub Spec-Kit standards with deep analysis and comprehensive documentation."
---

# cde_generateSpec - Professional Spec Generator

> **Tool for generating comprehensive feature specifications**
> **Based on**: GitHub Spec-Kit Standard
> **Last Updated**: 2025-11-24

---

## 🎯 Overview

`cde_generateSpec` is a professional specification generator that creates comprehensive feature documentation following GitHub's Spec-Kit standards. It generates three core documents:

1. **spec.md** - Product Requirements Document (PRD)
2. **plan.md** - Technical Design Document
3. **tasks.md** - Implementation Checklist

### Key Features

✅ **Deep Analysis**: Integrates with project analysis for context-aware specs
✅ **Spec-Kit Compliant**: Follows GitHub Spec-Kit structure and best practices
✅ **YAML Frontmatter**: All documents include proper metadata
✅ **Intelligent Recommendations**: Context-based suggestions for implementation
✅ **Multiple Spec Types**: Standard, quick-fix, research, refactor workflows
✅ **Progress Tracking**: Real-time progress reporting during generation

---

## 📋 Usage

### Basic Usage

```python
# Generate standard spec
result = await cde_generateSpec(
    feature_description="Add Redis caching to user authentication"
)

# Generate with research
result = await cde_generateSpec(
    feature_description="Implement OAuth2 authentication",
    include_research=True
)

# Generate for refactoring
result = await cde_generateSpec(
    feature_description="Refactor database layer to async/await",
    spec_type="refactor",
    include_architecture=True
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `feature_description` | `str` | **Required** | Natural language description of feature |
| `project_path` | `str` | `"."` | Path to project (default: current directory) |
| `spec_type` | `str` | `"standard"` | Type of spec: `standard`, `quick-fix`, `research`, `refactor` |
| `include_research` | `bool` | `True` | Include competitive analysis and research section |
| `include_architecture` | `bool` | `True` | Include architecture diagrams and patterns |

### Return Value

Returns JSON with:

```json
{
  "status": "success",
  "feature": "Add Redis caching to user authentication",
  "spec_directory": "E:\\project\\specs\\add-redis-caching-to-user-authentication",
  "files_created": [
    "E:\\project\\specs\\add-redis-caching-to-user-authentication\\spec.md",
    "E:\\project\\specs\\add-redis-caching-to-user-authentication\\plan.md",
    "E:\\project\\specs\\add-redis-caching-to-user-authentication\\tasks.md"
  ],
  "spec_type": "standard",
  "recommendations": [
    "✅ Use full 6-phase workflow (define → decompose → design → implement → test → review)",
    "📋 Consider breaking into multiple sprints if estimated > 2 weeks",
    "🔌 Follow MCP tool standards (use @tool_handler decorator)",
    "📚 Review existing architecture docs before starting"
  ],
  "next_steps": [
    "Review spec files in E:\\project\\specs\\add-redis-caching-to-user-authentication",
    "Use cde_startFeature to begin implementation",
    "Use cde_selectWorkflow to determine optimal workflow"
  ]
}
```

---

## 📂 Generated Files

### 1. spec.md (Product Requirements Document)

**Sections**:
- 🎯 Overview & Problem Statement
- 📋 Requirements & User Stories
- 🔍 Functional Requirements
- 🎨 User Experience & UI/UX
- ⚙️ Non-Functional Requirements (Performance, Security, Scalability)
- 🔗 Dependencies (Internal & External)
- 📊 Success Metrics & KPIs
- 🚧 Constraints & Assumptions
- 🗺️ Roadmap (MVP → Enhancement → Polish)
- 📚 References
- ✅ Approval & Sign-off

**Optional Sections** (if `include_research=True`):
- 🔬 Research & Analysis
- 💡 Alternatives Considered

**Example Excerpt**:
```markdown
## 🎯 Overview

### Problem Statement

**What problem does this solve?**
User authentication is slow due to frequent database lookups...

**Who is affected?**
All users logging in (avg: 10,000 logins/day)...
```

### 2. plan.md (Technical Design)

**Sections**:
- 🏗️ Architecture & Components
- 📐 Design Patterns
- 💾 Data Model & Schema
- 🔌 API Design
- 🧪 Testing Strategy
- 🚀 Deployment Plan
- 📊 Performance Optimization
- 🔐 Security Implementation
- 🔧 Configuration
- 📝 Documentation Requirements
- 🛠️ Development Guidelines
- 📅 Timeline & Milestones
- 🤝 Dependencies
- 🚨 Risks & Mitigation
- ✅ Definition of Done

**Optional Sections** (if `include_architecture=True`):
- 📊 Architecture Diagrams (Component, Sequence, Data Flow)

**Example Excerpt**:
```markdown
## 🏗️ Architecture

### System Overview

```
┌─────────────────┐       ┌─────────────────┐
│   Auth Service  │───────│   Redis Cache   │
│                 │       │   (TTL: 1h)     │
└─────────────────┘       └─────────────────┘
         │
         ▼
┌─────────────────┐
│   Database      │
│   (PostgreSQL)  │
└─────────────────┘
```
```

### 3. tasks.md (Implementation Checklist)

**Phases** (Standard 6-Phase CDE Workflow):
1. 🎯 Phase 1: Define
2. 🔨 Phase 2: Decompose
3. 📐 Phase 3: Design
4. 💻 Phase 4: Implement
5. 🧪 Phase 5: Test
6. 🔍 Phase 6: Review
7. 🚀 Phase 7: Deploy (Bonus)

**Task Format**:
```markdown
- [ ] **Task**: Description
  - **Assignee**: TBD
  - **Estimated**: X hours
  - **Dependencies**: Task IDs
  - **Files**: `path/to/file.py`
  - **Deliverable**: What's produced
```

**Example Excerpt**:
```markdown
### 4.1 Backend Implementation

- [ ] **Task**: Implement Redis cache layer
  - **Assignee**: TBD
  - **Estimated**: 4 hours
  - **Dependencies**: 3.1 (data model)
  - **Files**: `src/cache/redis_client.py`
  - **Deliverable**: Working cache integration
```

---

## 🎨 Spec Types

### Standard (Default)

**When to Use**: Most features, new functionality, enhancements
**Workflow**: Full 6-phase (define → decompose → design → implement → test → review)
**Generated Tasks**: ~30-50 tasks across all phases
**Timeline**: 1-4 weeks

**Example**:
```python
cde_generateSpec("Add user profile management system")
```

### Quick-Fix

**When to Use**: Bug fixes, typos, small corrections
**Workflow**: Skip design, jump to implement
**Generated Tasks**: ~10-15 tasks (implement + test only)
**Timeline**: < 1 day

**Example**:
```python
cde_generateSpec("Fix typo in error message", spec_type="quick-fix")
```

### Research

**When to Use**: POCs, investigations, technical spikes
**Workflow**: Heavy research phase, light implementation
**Generated Tasks**: ~20-30 tasks (research-heavy)
**Timeline**: 1-2 weeks

**Example**:
```python
cde_generateSpec(
    "Research best practices for microservices communication",
    spec_type="research",
    include_research=True
)
```

### Refactor

**When to Use**: Code improvements, technical debt, optimization
**Workflow**: Start with test coverage, then refactor
**Generated Tasks**: ~25-40 tasks (test + refactor focus)
**Timeline**: 1-3 weeks

**Example**:
```python
cde_generateSpec(
    "Refactor authentication module to use dependency injection",
    spec_type="refactor"
)
```

---

## 🔄 Integration with CDE Workflow

### Recommended Flow

```
1. cde_selectWorkflow("Feature description")
   ↓ Returns: workflow_type, complexity, recipe_id

2. cde_generateSpec("Feature description", spec_type=workflow_type)
   ↓ Creates: specs/[feature]/spec.md, plan.md, tasks.md

3. Review generated specs
   ↓ Edit and customize as needed

4. cde_startFeature("Feature description")
   ↓ Begins: Phase 1 (Define)

5. cde_submitWork(feature_id, phase_id, results)
   ↓ Progress: Through all phases
```

### Example

```python
# Step 1: Analyze and recommend
workflow = await cde_selectWorkflow("Add Redis caching to auth")
# Returns: { workflow_type: "standard", complexity: "moderate", ... }

# Step 2: Generate comprehensive spec
spec = await cde_generateSpec(
    "Add Redis caching to auth",
    spec_type=workflow["workflow_type"]
)
# Creates: specs/add-redis-caching-to-auth/{spec,plan,tasks}.md

# Step 3: Start implementation
feature = await cde_startFeature("Add Redis caching to auth")
# Returns: { feature_id: "uuid", phase: "define", ... }
```

---

## 🎯 Context-Aware Features

### Project Analysis Integration

The tool integrates with `cde_onboardingProject` to provide context-aware recommendations:

**Detected**: MCP Server Project
**Recommendation**: "🔌 Follow MCP tool standards (use @tool_handler decorator)"

**Detected**: FastAPI Tech Stack
**Recommendation**: "🚀 Use FastAPI dependency injection pattern"

**Detected**: React Tech Stack
**Recommendation**: "⚛️ Use React hooks and functional components"

### Intelligent Recommendations

Based on:
- **Spec Type**: Workflow suggestions
- **Project Type**: Architecture patterns
- **Tech Stack**: Framework-specific best practices
- **Complexity**: Sprint planning advice

**Example Output**:
```json
"recommendations": [
  "✅ Use full 6-phase workflow (define → decompose → design → implement → test → review)",
  "📋 Consider breaking into multiple sprints if estimated > 2 weeks",
  "🔌 Follow MCP tool standards (use @tool_handler decorator)",
  "🚀 Use FastAPI dependency injection pattern",
  "📚 Review existing architecture docs before starting"
]
```

---

## 📊 Examples

### Example 1: Standard Feature

```python
result = await cde_generateSpec(
    feature_description="Add user notification system with email and SMS support",
    project_path="E:\\my-project",
    spec_type="standard",
    include_research=True,
    include_architecture=True
)

# Generated files:
# specs/add-user-notification-system-with-email-and-sms-support/
#   ├── spec.md      (PRD with research section)
#   ├── plan.md      (Technical design with diagrams)
#   └── tasks.md     (Implementation checklist)
```

### Example 2: Quick Fix

```python
result = await cde_generateSpec(
    feature_description="Fix validation error in user registration form",
    spec_type="quick-fix",
    include_research=False,
    include_architecture=False
)

# Generated files (streamlined):
# specs/fix-validation-error-in-user-registration-form/
#   ├── spec.md      (Minimal PRD)
#   ├── plan.md      (Quick design notes)
#   └── tasks.md     (Implementation only, no design phase)
```

### Example 3: Research Task

```python
result = await cde_generateSpec(
    feature_description="Evaluate GraphQL vs REST for API redesign",
    spec_type="research",
    include_research=True
)

# Generated files (research-heavy):
# specs/evaluate-graphql-vs-rest-for-api-redesign/
#   ├── spec.md      (Research objectives, competitive analysis)
#   ├── plan.md      (Evaluation criteria, POC plan)
#   └── tasks.md     (Research tasks, POC implementation)
```

---

## 🚀 Best Practices

### 1. Always Start with Workflow Selection

```python
# ✅ GOOD: Analyze first, then generate
workflow = await cde_selectWorkflow("Feature description")
spec = await cde_generateSpec("Feature description", spec_type=workflow["workflow_type"])

# ❌ BAD: Generate without analysis
spec = await cde_generateSpec("Feature description")  # Might use wrong spec_type
```

### 2. Customize Generated Specs

The tool generates **templates** that should be reviewed and customized:

```markdown
<!-- BEFORE (Generated) -->
**What problem does this solve?**
<!-- Describe the problem or pain point this feature addresses -->

<!-- AFTER (Customized) -->
**What problem does this solve?**
User authentication is slow due to frequent database lookups.
Average login time is 2.5 seconds, causing 15% user drop-off.
```

### 3. Use Include Flags Appropriately

```python
# Research-heavy features
cde_generateSpec("New ML model", include_research=True)  # ✅

# Simple fixes
cde_generateSpec("Fix typo", include_research=False)  # ✅

# Architecture changes
cde_generateSpec("Migrate to microservices", include_architecture=True)  # ✅
```

### 4. Link Specs to Implementation

After generating specs, use `cde_startFeature` to begin:

```python
# Generate spec
spec = await cde_generateSpec("Add feature X")

# Review and customize spec files

# Start implementation
feature = await cde_startFeature("Add feature X")
```

---

## 🔍 Troubleshooting

### Issue 1: Spec directory already exists

**Error**: `FileExistsError: specs/feature-name/ already exists`

**Solution**: Remove existing directory or use a different feature description:
```powershell
Remove-Item -Recurse -Force "specs\feature-name"
```

### Issue 2: Project analysis fails

**Error**: `Could not analyze project`

**Solution**: Ensure project path is correct and contains valid project files:
```python
# Verify project path
import os
os.path.exists("E:\\my-project")  # Should be True
```

### Issue 3: Missing recommendations

**Symptom**: Generated spec has generic recommendations

**Solution**: Run `cde_onboardingProject` first for better context:
```python
# Enrich project context first
await cde_onboardingProject(project_path="E:\\my-project")

# Then generate spec with full context
await cde_generateSpec("Feature description")
```

---

## 📚 See Also

- [Configuration Guide](configuration-guide.md) - How to use CDE tools in other projects
- [Spec-Kit Templates](../specs/templates/) - Template files for spec.md, plan.md, tasks.md
- [Workflow Guide](../specs/design/architecture/README.md) - Understanding CDE workflows
- [cde_selectWorkflow](../specs/api/mcp-tools.md#cde_selectWorkflow) - Workflow recommendation
- [cde_startFeature](../specs/api/mcp-tools.md#cde_startFeature) - Begin implementation

---

**Tool Version**: 1.0.0
**Spec-Kit Standard**: GitHub Spec-Kit v1.0
**Last Updated**: 2025-11-24
**Maintainer**: Nexus AI Team
