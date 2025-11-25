# src/mcp_tools/spec_generator.py
"""
Professional Spec Generator based on GitHub Spec-Kit
Generates comprehensive feature specifications with deep analysis
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastmcp import Context

from cde_orchestrator.application.onboarding.project_analysis_use_case import (
    ProjectAnalysisUseCase,
)

from ._base import tool_handler
from ._progress_reporter import get_progress_reporter

logger = logging.getLogger(__name__)


@tool_handler
async def cde_generateSpec(
    ctx: Context,
    feature_description: str,
    project_path: str = ".",
    spec_type: str = "standard",
    include_research: bool = True,
    include_architecture: bool = True,
) -> str:
    """
    🎯 Generate professional feature specification based on GitHub Spec-Kit.

    Creates comprehensive spec with:
    - spec.md (Product Requirements Document)
    - plan.md (Technical Design)
    - tasks.md (Implementation Checklist)

    Args:
        feature_description: Natural language description of the feature
        project_path: Path to project (default: current directory)
        spec_type: Type of spec (standard, quick-fix, research, refactor)
        include_research: Include competitive analysis and research
        include_architecture: Include architecture diagrams and patterns

    Returns:
        JSON with generated spec files and recommendations

    Examples:
        >>> cde_generateSpec("Add Redis caching to user authentication")
        >>> cde_generateSpec("Implement OAuth2 authentication", include_research=True)
    """
    reporter = get_progress_reporter()
    reporter.reset()
    reporter.report_progress(
        "CDE", "generateSpec", 0.1, "Analyzing feature requirements..."
    )

    if project_path == ".":
        project_path = os.getcwd()

    # Analyze project context
    analysis_use_case = ProjectAnalysisUseCase()
    project_analysis = await analysis_use_case.execute(project_path, enrich_context=True)

    reporter.report_progress(
        "CDE", "generateSpec", 0.3, "Generating spec.md (PRD)..."
    )

    # Generate spec.md (Product Requirements Document)
    spec_content = _generate_spec_md(
        feature_description, project_analysis, spec_type, include_research
    )

    reporter.report_progress(
        "CDE", "generateSpec", 0.5, "Generating plan.md (Technical Design)..."
    )

    # Generate plan.md (Technical Design)
    plan_content = _generate_plan_md(
        feature_description, project_analysis, spec_type, include_architecture
    )

    reporter.report_progress(
        "CDE", "generateSpec", 0.7, "Generating tasks.md (Implementation)..."
    )

    # Generate tasks.md (Implementation Checklist)
    tasks_content = _generate_tasks_md(
        feature_description, project_analysis, spec_type
    )

    reporter.report_progress(
        "CDE", "generateSpec", 0.9, "Writing spec files..."
    )

    # Create spec directory
    feature_slug = _slugify(feature_description)
    spec_dir = Path(project_path) / "specs" / feature_slug
    spec_dir.mkdir(parents=True, exist_ok=True)

    # Write files
    files_created = []

    spec_file = spec_dir / "spec.md"
    spec_file.write_text(spec_content, encoding="utf-8")
    files_created.append(str(spec_file))

    plan_file = spec_dir / "plan.md"
    plan_file.write_text(plan_content, encoding="utf-8")
    files_created.append(str(plan_file))

    tasks_file = spec_dir / "tasks.md"
    tasks_file.write_text(tasks_content, encoding="utf-8")
    files_created.append(str(tasks_file))

    reporter.report_progress(
        "CDE", "generateSpec", 1.0, "Spec generation complete"
    )

    result = {
        "status": "success",
        "feature": feature_description,
        "spec_directory": str(spec_dir),
        "files_created": files_created,
        "spec_type": spec_type,
        "recommendations": _generate_recommendations(
            feature_description, project_analysis, spec_type
        ),
        "next_steps": [
            f"Review spec files in {spec_dir}",
            "Use cde_startFeature to begin implementation",
            "Use cde_selectWorkflow to determine optimal workflow",
        ],
    }

    return json.dumps(result, indent=2)


def _generate_spec_md(
    feature_description: str,
    project_analysis: Dict,
    spec_type: str,
    include_research: bool,
) -> str:
    """Generate spec.md (Product Requirements Document)"""

    today = datetime.now().strftime("%Y-%m-%d")
    feature_slug = _slugify(feature_description)

    content = f"""---
title: {feature_description}
description: Feature specification for {feature_description}
type: feature
status: draft
created: '{today}'
updated: '{today}'
author: Development Team
tags:
  - feature
  - {spec_type}
llm_summary: "Specification for {feature_description}. Type: {spec_type}."
---

# {feature_description}

> **Feature Type**: {spec_type.title()}
> **Status**: Draft
> **Created**: {today}

---

## 🎯 Overview

### Problem Statement

**What problem does this solve?**

<!-- Describe the problem or pain point this feature addresses -->

**Who is affected?**

<!-- Define the target users or stakeholders -->

**Why is this important?**

<!-- Business value and urgency -->

---

## 📋 Requirements

### User Stories

#### Primary User Story

**As a** [user type]
**I want to** [action]
**So that** [benefit]

**Acceptance Criteria**:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

#### Additional User Stories

<!-- Add more user stories as needed -->

---

## 🔍 Functional Requirements

### Core Functionality

1. **Feature 1**: Description
   - Sub-requirement 1.1
   - Sub-requirement 1.2

2. **Feature 2**: Description
   - Sub-requirement 2.1
   - Sub-requirement 2.2

### Edge Cases

- [ ] Edge case 1: Description
- [ ] Edge case 2: Description

---

## 🎨 User Experience

### User Flow

```
[User Action 1] → [System Response 1] → [User Action 2] → [Result]
```

### UI/UX Considerations

- **Interface Changes**: Description
- **Accessibility**: Requirements
- **Mobile Support**: Considerations

---

## ⚙️ Non-Functional Requirements

### Performance

- **Response Time**: < X ms
- **Throughput**: X requests/second
- **Resource Usage**: Memory, CPU limits

### Security

- [ ] Authentication required
- [ ] Authorization checks
- [ ] Data encryption
- [ ] Input validation

### Scalability

- **Concurrent Users**: X users
- **Data Volume**: X records
- **Growth Plan**: How to scale

---

## 🔗 Dependencies

### Internal Dependencies

- **Component A**: Why needed
- **Component B**: Why needed

### External Dependencies

- **Library/Service**: Version, why needed

---

## 📊 Success Metrics

### Key Performance Indicators (KPIs)

1. **Metric 1**: Target value
2. **Metric 2**: Target value
3. **Metric 3**: Target value

### Monitoring

- **Metrics to Track**: List
- **Alerts**: Conditions
- **Dashboards**: What to monitor

---

## 🚧 Constraints & Assumptions

### Technical Constraints

- Constraint 1
- Constraint 2

### Business Constraints

- Budget limitations
- Timeline requirements

### Assumptions

- Assumption 1
- Assumption 2

---

## 🗺️ Roadmap

### Phase 1: MVP

- [ ] Core feature implementation
- [ ] Basic testing
- [ ] Documentation

### Phase 2: Enhancement

- [ ] Advanced features
- [ ] Performance optimization
- [ ] Comprehensive testing

### Phase 3: Polish

- [ ] UI refinement
- [ ] Edge case handling
- [ ] Production deployment

---

## 📚 References

### Related Documentation

- [Architecture Doc](../design/architecture/README.md)
- [API Specification](../api/mcp-tools.md)

### External Resources

- Link 1: Description
- Link 2: Description

---

## ✅ Approval

### Stakeholders

- [ ] Product Owner: Name
- [ ] Technical Lead: Name
- [ ] Security Team: Name

### Sign-off Date

<!-- Date when approved -->

---

**Generated by**: CDE Orchestrator - Spec Generator
**Template Version**: Spec-Kit GitHub Standard v1.0
**Project Context**: {project_analysis.get('project_type', 'Unknown')}
"""

    if include_research:
        content += """

---

## 🔬 Research & Analysis

### Competitive Analysis

**Similar Solutions**:
- Solution A: Strengths, weaknesses
- Solution B: Strengths, weaknesses

### Best Practices

- Industry standard 1
- Industry standard 2

### Technology Evaluation

| Technology | Pros | Cons | Recommendation |
|------------|------|------|----------------|
| Option A   |      |      |                |
| Option B   |      |      |                |

---

## 💡 Alternatives Considered

### Alternative 1

**Description**: What it does
**Pros**: Benefits
**Cons**: Drawbacks
**Decision**: Why not chosen

### Alternative 2

**Description**: What it does
**Pros**: Benefits
**Cons**: Drawbacks
**Decision**: Why not chosen

---
"""

    return content


def _generate_plan_md(
    feature_description: str,
    project_analysis: Dict,
    spec_type: str,
    include_architecture: bool,
) -> str:
    """Generate plan.md (Technical Design)"""

    today = datetime.now().strftime("%Y-%m-%d")

    content = f"""---
title: Technical Plan - {feature_description}
description: Technical design and implementation plan
type: plan
status: draft
created: '{today}'
updated: '{today}'
author: Development Team
tags:
  - technical-design
  - {spec_type}
---

# Technical Plan - {feature_description}

> **Feature Type**: {spec_type.title()}
> **Status**: Draft
> **Created**: {today}

---

## 🏗️ Architecture

### System Overview

**High-Level Architecture**:

<!-- Describe the overall system architecture -->

### Components

#### Component 1: [Name]

**Purpose**: What it does
**Responsibilities**:
- Responsibility 1
- Responsibility 2

**Interfaces**:
- Input: Description
- Output: Description

#### Component 2: [Name]

**Purpose**: What it does
**Responsibilities**:
- Responsibility 1
- Responsibility 2

---

## 📐 Design Patterns

### Patterns to Use

1. **Pattern Name**: Why and how
2. **Pattern Name**: Why and how

### Anti-Patterns to Avoid

- Anti-pattern 1: Why to avoid
- Anti-pattern 2: Why to avoid

---

## 💾 Data Model

### Database Schema

```sql
CREATE TABLE example (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Data Flow

```
[Input] → [Validation] → [Processing] → [Storage] → [Output]
```

---

## 🔌 API Design

### Endpoints

#### POST /api/resource

**Request**:
```json
{{
    "field1": "value",
    "field2": 123
}}
```

**Response**:
```json
{{
    "id": "uuid",
    "status": "success"
}}
```

---

## 🧪 Testing Strategy

### Unit Tests

- [ ] Component A unit tests
- [ ] Component B unit tests

### Integration Tests

- [ ] API endpoint tests
- [ ] Database integration tests

### E2E Tests

- [ ] User flow test 1
- [ ] User flow test 2

---

## 🚀 Deployment

### Infrastructure

- **Environment**: Dev, Staging, Prod
- **Resources**: CPU, Memory, Storage

### Deployment Steps

1. Step 1: Description
2. Step 2: Description
3. Step 3: Description

### Rollback Plan

- [ ] Backup strategy
- [ ] Rollback procedure
- [ ] Data migration reversal

---

## 📊 Performance

### Optimization Strategies

1. **Strategy 1**: Description
2. **Strategy 2**: Description

### Caching

- **What to cache**: Description
- **Cache invalidation**: Strategy
- **TTL**: Time to live

---

## 🔐 Security

### Authentication

- Method: JWT, OAuth2, etc.
- Storage: Where tokens are stored
- Expiration: Token lifetime

### Authorization

- Roles: List of roles
- Permissions: What each role can do

### Data Protection

- [ ] Encryption at rest
- [ ] Encryption in transit
- [ ] PII handling

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
DATABASE_URL=postgresql://...
API_KEY=...

# Optional
LOG_LEVEL=INFO
CACHE_TTL=3600
```

---

## 📝 Documentation

### Code Documentation

- [ ] Inline comments for complex logic
- [ ] Docstrings for all public functions
- [ ] Type hints for all functions

### User Documentation

- [ ] API documentation (OpenAPI/Swagger)
- [ ] User guide
- [ ] Migration guide (if applicable)

---

## 🛠️ Development Guidelines

### Code Style

- Follow project coding standards
- Use linting tools
- Write self-documenting code

### Git Workflow

1. Create feature branch: `git checkout -b feature/{feature_description.lower().replace(' ', '-')}`
2. Commit often with meaningful messages
3. Pull request with description and tests
4. Code review required before merge

---

## 📅 Timeline

### Phase 1 (Week 1-2)

- [ ] Setup and architecture
- [ ] Core implementation
- [ ] Unit tests

### Phase 2 (Week 3-4)

- [ ] Integration
- [ ] Testing
- [ ] Documentation

### Phase 3 (Week 5)

- [ ] Review and polish
- [ ] Deployment
- [ ] Monitoring setup

---

## 🤝 Dependencies

### Must Be Complete Before Starting

- Dependency 1
- Dependency 2

### Can Be Developed in Parallel

- Feature A
- Feature B

---

## 🚨 Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Risk 1 | High | Medium | Mitigation strategy |
| Risk 2 | Medium | Low | Mitigation strategy |

---

## ✅ Definition of Done

- [ ] Code complete and peer-reviewed
- [ ] All tests passing (unit, integration, e2e)
- [ ] Documentation updated
- [ ] Security review completed
- [ ] Performance benchmarks met
- [ ] Deployed to staging
- [ ] Stakeholder sign-off

---

**Generated by**: CDE Orchestrator - Spec Generator
**Template Version**: Spec-Kit GitHub Standard v1.0
**Architecture Pattern**: {project_analysis.get('architecture_pattern', 'Not detected')}
"""

    if include_architecture:
        content += """

---

## 📊 Architecture Diagrams

### Component Diagram

```
┌─────────────────┐       ┌─────────────────┐
│   Frontend      │───────│   Backend API   │
│   (React)       │       │   (FastAPI)     │
└─────────────────┘       └────────┬────────┘
                                   │
                          ┌────────┴────────┐
                          │   Database      │
                          │   (PostgreSQL)  │
                          └─────────────────┘
```

### Sequence Diagram

```
User -> Frontend: Action
Frontend -> API: Request
API -> Database: Query
Database -> API: Result
API -> Frontend: Response
Frontend -> User: Display
```

### Data Flow Diagram

```
[Input Validation] → [Business Logic] → [Data Access] → [Database]
                                ↓
                         [Event Publishing]
```

---
"""

    return content


def _generate_tasks_md(
    feature_description: str,
    project_analysis: Dict,
    spec_type: str,
) -> str:
    """Generate tasks.md (Implementation Checklist)"""

    today = datetime.now().strftime("%Y-%m-%d")

    content = f"""---
title: Implementation Tasks - {feature_description}
description: Detailed implementation checklist
type: tasks
status: not-started
created: '{today}'
updated: '{today}'
author: Development Team
tags:
  - implementation
  - {spec_type}
---

# Implementation Tasks - {feature_description}

> **Feature Type**: {spec_type.title()}
> **Status**: Not Started
> **Created**: {today}

---

## 📋 Task Overview

### Summary

**Total Tasks**: TBD
**Completed**: 0
**In Progress**: 0
**Blocked**: 0

---

## 🎯 Phase 1: Define

### 1.1 Requirements Analysis

- [ ] **Task**: Review spec.md with stakeholders
  - **Assignee**: TBD
  - **Estimated**: 2 hours
  - **Dependencies**: None
  - **Deliverable**: Approved spec document

- [ ] **Task**: Identify edge cases
  - **Assignee**: TBD
  - **Estimated**: 1 hour
  - **Dependencies**: 1.1
  - **Deliverable**: Edge cases document

- [ ] **Task**: Define success criteria
  - **Assignee**: TBD
  - **Estimated**: 1 hour
  - **Dependencies**: 1.1
  - **Deliverable**: Acceptance criteria

---

## 🔨 Phase 2: Decompose

### 2.1 Break Down Work

- [ ] **Task**: Decompose into sub-tasks
  - **Assignee**: TBD
  - **Estimated**: 2 hours
  - **Dependencies**: Phase 1 complete
  - **Deliverable**: Task breakdown

- [ ] **Task**: Identify technical dependencies
  - **Assignee**: TBD
  - **Estimated**: 1 hour
  - **Dependencies**: 2.1
  - **Deliverable**: Dependency map

- [ ] **Task**: Estimate effort for each task
  - **Assignee**: TBD
  - **Estimated**: 1 hour
  - **Dependencies**: 2.1
  - **Deliverable**: Effort estimates

---

## 📐 Phase 3: Design

### 3.1 Architecture Design

- [ ] **Task**: Design system architecture
  - **Assignee**: TBD
  - **Estimated**: 4 hours
  - **Dependencies**: Phase 2 complete
  - **Deliverable**: Architecture diagram

- [ ] **Task**: Design data model
  - **Assignee**: TBD
  - **Estimated**: 2 hours
  - **Dependencies**: 3.1
  - **Deliverable**: Database schema

- [ ] **Task**: Design API contracts
  - **Assignee**: TBD
  - **Estimated**: 2 hours
  - **Dependencies**: 3.1
  - **Deliverable**: API specification

### 3.2 UI/UX Design

- [ ] **Task**: Create wireframes
  - **Assignee**: TBD
  - **Estimated**: 3 hours
  - **Dependencies**: Phase 2 complete
  - **Deliverable**: Wireframes

- [ ] **Task**: Design user flows
  - **Assignee**: TBD
  - **Estimated**: 2 hours
  - **Dependencies**: 3.2 (wireframes)
  - **Deliverable**: User flow diagrams

---

## 💻 Phase 4: Implement

### 4.1 Backend Implementation

- [ ] **Task**: Setup project structure
  - **Assignee**: TBD
  - **Estimated**: 1 hour
  - **Dependencies**: Phase 3 complete
  - **Files**: `src/...`

- [ ] **Task**: Implement core logic
  - **Assignee**: TBD
  - **Estimated**: 8 hours
  - **Dependencies**: 4.1
  - **Files**: `src/core/...`

- [ ] **Task**: Implement API endpoints
  - **Assignee**: TBD
  - **Estimated**: 4 hours
  - **Dependencies**: 4.1 (core logic)
  - **Files**: `src/api/...`

- [ ] **Task**: Implement database layer
  - **Assignee**: TBD
  - **Estimated**: 3 hours
  - **Dependencies**: 3.1 (data model)
  - **Files**: `src/models/...`

### 4.2 Frontend Implementation

- [ ] **Task**: Setup frontend structure
  - **Assignee**: TBD
  - **Estimated**: 1 hour
  - **Dependencies**: 3.2 (design)
  - **Files**: `frontend/src/...`

- [ ] **Task**: Implement UI components
  - **Assignee**: TBD
  - **Estimated**: 6 hours
  - **Dependencies**: 4.2
  - **Files**: `frontend/src/components/...`

- [ ] **Task**: Implement state management
  - **Assignee**: TBD
  - **Estimated**: 3 hours
  - **Dependencies**: 4.2 (UI components)
  - **Files**: `frontend/src/store/...`

### 4.3 Integration

- [ ] **Task**: Connect frontend to backend
  - **Assignee**: TBD
  - **Estimated**: 2 hours
  - **Dependencies**: 4.1, 4.2 complete
  - **Files**: `frontend/src/services/...`

- [ ] **Task**: Implement error handling
  - **Assignee**: TBD
  - **Estimated**: 2 hours
  - **Dependencies**: 4.3
  - **Files**: Multiple files

---

## 🧪 Phase 5: Test

### 5.1 Unit Tests

- [ ] **Task**: Write backend unit tests
  - **Assignee**: TBD
  - **Estimated**: 4 hours
  - **Dependencies**: 4.1 complete
  - **Files**: `tests/unit/backend/...`
  - **Coverage Target**: 80%

- [ ] **Task**: Write frontend unit tests
  - **Assignee**: TBD
  - **Estimated**: 4 hours
  - **Dependencies**: 4.2 complete
  - **Files**: `tests/unit/frontend/...`
  - **Coverage Target**: 80%

### 5.2 Integration Tests

- [ ] **Task**: Write API integration tests
  - **Assignee**: TBD
  - **Estimated**: 3 hours
  - **Dependencies**: 4.1, 5.1 complete
  - **Files**: `tests/integration/api/...`

- [ ] **Task**: Write database integration tests
  - **Assignee**: TBD
  - **Estimated**: 2 hours
  - **Dependencies**: 4.1 complete
  - **Files**: `tests/integration/db/...`

### 5.3 E2E Tests

- [ ] **Task**: Write user flow tests
  - **Assignee**: TBD
  - **Estimated**: 4 hours
  - **Dependencies**: 4.3 complete
  - **Files**: `tests/e2e/...`

---

## 🔍 Phase 6: Review

### 6.1 Code Review

- [ ] **Task**: Backend code review
  - **Assignee**: Tech Lead
  - **Estimated**: 2 hours
  - **Dependencies**: Phase 4 complete

- [ ] **Task**: Frontend code review
  - **Assignee**: Tech Lead
  - **Estimated**: 2 hours
  - **Dependencies**: Phase 4 complete

### 6.2 Testing Review

- [ ] **Task**: Review test coverage
  - **Assignee**: QA Lead
  - **Estimated**: 1 hour
  - **Dependencies**: Phase 5 complete

- [ ] **Task**: Manual testing
  - **Assignee**: QA Team
  - **Estimated**: 4 hours
  - **Dependencies**: Phase 5 complete

### 6.3 Security Review

- [ ] **Task**: Security audit
  - **Assignee**: Security Team
  - **Estimated**: 2 hours
  - **Dependencies**: Phase 4, 5 complete

### 6.4 Documentation Review

- [ ] **Task**: Update API documentation
  - **Assignee**: TBD
  - **Estimated**: 1 hour
  - **Dependencies**: Phase 4 complete
  - **Files**: `docs/api/...`

- [ ] **Task**: Update user documentation
  - **Assignee**: TBD
  - **Estimated**: 2 hours
  - **Dependencies**: Phase 4 complete
  - **Files**: `docs/user/...`

---

## 🚀 Phase 7: Deploy (Bonus)

### 7.1 Staging Deployment

- [ ] **Task**: Deploy to staging environment
  - **Assignee**: DevOps
  - **Estimated**: 1 hour
  - **Dependencies**: Phase 6 complete

- [ ] **Task**: Smoke testing in staging
  - **Assignee**: QA
  - **Estimated**: 1 hour
  - **Dependencies**: 7.1

### 7.2 Production Deployment

- [ ] **Task**: Deploy to production
  - **Assignee**: DevOps
  - **Estimated**: 1 hour
  - **Dependencies**: 7.1 complete

- [ ] **Task**: Monitor production metrics
  - **Assignee**: DevOps
  - **Estimated**: 2 hours
  - **Dependencies**: 7.2

---

## 📊 Progress Tracking

### Velocity

**Sprint 1**: TBD tasks completed
**Sprint 2**: TBD tasks completed
**Sprint 3**: TBD tasks completed

### Burndown

<!-- Update as tasks are completed -->

---

## 🚧 Blockers

### Current Blockers

- None yet

### Resolved Blockers

- None yet

---

## 📝 Notes

### Important Decisions

- Decision 1: Description
- Decision 2: Description

### Lessons Learned

- Lesson 1: What we learned
- Lesson 2: What we learned

---

**Generated by**: CDE Orchestrator - Spec Generator
**Template Version**: Spec-Kit GitHub Standard v1.0
**Workflow Type**: {spec_type}
"""

    return content


def _generate_recommendations(
    feature_description: str,
    project_analysis: Dict,
    spec_type: str,
) -> List[str]:
    """Generate recommendations based on feature and project context"""

    recommendations = []

    # Based on spec type
    if spec_type == "standard":
        recommendations.append("✅ Use full 6-phase workflow (define → decompose → design → implement → test → review)")
        recommendations.append("📋 Consider breaking into multiple sprints if estimated > 2 weeks")
    elif spec_type == "quick-fix":
        recommendations.append("⚡ Skip design phase, move directly to implementation")
        recommendations.append("🧪 Focus on unit tests and quick validation")
    elif spec_type == "research":
        recommendations.append("🔬 Allocate 50% time to research and experimentation")
        recommendations.append("📊 Create POC before full implementation")
    elif spec_type == "refactor":
        recommendations.append("🔄 Start with comprehensive test coverage of existing code")
        recommendations.append("📏 Use incremental refactoring approach")

    # Based on project type
    project_type = project_analysis.get("project_type", "unknown")
    if project_type == "mcp-server":
        recommendations.append("🔌 Follow MCP tool standards (use @tool_handler decorator)")
        recommendations.append("📖 Update servers/cde/ filesystem structure after changes")

    # Based on tech stack
    tech_stack = project_analysis.get("tech_stack", [])
    if "FastAPI" in tech_stack:
        recommendations.append("🚀 Use FastAPI dependency injection pattern")
        recommendations.append("📝 Generate OpenAPI documentation automatically")

    if "React" in tech_stack:
        recommendations.append("⚛️ Use React hooks and functional components")
        recommendations.append("🎨 Follow component composition patterns")

    # General recommendations
    recommendations.append("📚 Review existing architecture docs before starting")
    recommendations.append("🤝 Schedule kickoff meeting with all stakeholders")
    recommendations.append("⏱️ Set up progress tracking in project management tool")

    return recommendations


def _slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')
