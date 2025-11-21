---
title: CDE Orchestrator MCP - Project Structure
description: '``` src/ ├── cde_orchestrator/           # Main application package'
type: guide
status: draft
created: '2025-11-20'
updated: '2025-11-20'
author: Auto-Generated
tags:
- api
- architecture
- documentation
- mcp
- orchestration
- python
llm_summary: "User guide for CDE Orchestrator MCP - Project Structure.\n  The project\
  \ follows clean architecture principles with strict dependency rules: **Dependency\
  \ Flow**: External → Adapters → Application → Domain - **Domain Layer**: Pure business\
  \ logic, no external dependencies\n  Reference when working with guide documentation."
---

# CDE Orchestrator MCP - Project Structure

## Directory Organization

### Core Source Code (`src/`)
```
src/
├── cde_orchestrator/           # Main application package
│   ├── domain/                 # Business logic and entities (hexagonal core)
│   ├── application/            # Use cases and orchestration layer
│   ├── adapters/               # Infrastructure implementations
│   ├── infrastructure/         # Dependency injection and configuration
│   └── skills/                 # Dynamic skill management system
├── mcp_tools/                  # MCP server tool implementations
│   ├── agents.py               # AI agent configuration tools
│   ├── documentation.py        # Documentation management tools
│   ├── onboarding.py           # Repository onboarding tools
│   └── orchestration.py        # Workflow orchestration tools
└── server.py                   # Main MCP server entry point
```

### Specifications & Documentation (`specs/`)
```
specs/
├── features/                   # Feature specifications (Spec-Kit format)
├── design/                     # Technical architecture and decisions
├── tasks/                      # Project roadmaps and task tracking
├── governance/                 # Process rules and documentation standards
├── templates/                  # Document templates and patterns
└── api/                        # MCP tool API specifications
```

### Agent Documentation (`agent-docs/`)
```
agent-docs/
├── execution/                  # Workflow execution reports
├── sessions/                   # Development session summaries
├── feedback/                   # Analysis and recommendations
├── research/                   # Web research (90-day archive)
└── prompts/                    # Master prompts for AI agents
```

### Testing Infrastructure (`tests/`)
```
tests/
├── unit/                       # Isolated component tests
│   ├── domain/                 # Domain entity tests
│   ├── application/            # Use case tests
│   ├── adapters/               # Adapter implementation tests
│   └── mcp_tools/              # MCP tool tests
└── integration/                # End-to-end integration tests
```

### Configuration & Automation
```
.amazonq/rules/                 # Amazon Q AI assistant rules
.github/workflows/              # CI/CD automation
scripts/                        # Utility and setup scripts
memory/                         # Project constitution and principles
```

## Architectural Patterns

### Hexagonal Architecture (Ports & Adapters)
The project follows clean architecture principles with strict dependency rules:

**Dependency Flow**: External → Adapters → Application → Domain
- **Domain Layer**: Pure business logic, no external dependencies
- **Application Layer**: Use cases and orchestration, depends only on domain
- **Adapters Layer**: Infrastructure implementations of domain ports
- **External Layer**: MCP tools, web APIs, file systems

### Key Components & Relationships

#### Domain Entities
- **Project**: Core business entity representing a development project
- **Feature**: Represents a feature under development with lifecycle management
- **Workflow**: Defines the development process phases and transitions
- **Specification**: Documentation and requirements management

#### Application Use Cases
- **StartFeatureUseCase**: Initiates new feature development workflows
- **SubmitWorkUseCase**: Handles phase completion and transitions
- **OnboardingUseCase**: Manages repository analysis and setup
- **AIConfigUseCase**: Handles AI assistant configuration management

#### Adapter Implementations
- **FileSystemProjectRepository**: Persistent project state management
- **CopilotCLIAdapter**: Integration with GitHub Copilot CLI
- **YAMLWorkflowEngine**: Workflow definition processing
- **MCPServerAdapter**: Model Context Protocol server implementation

#### Infrastructure Services
- **DIContainer**: Dependency injection and service wiring
- **ConfigurationManager**: Environment and settings management
- **ServiceConnector**: External service integration coordination

## Data Flow Architecture

### MCP Request Processing
1. **External Agent** → MCP Tool (validation)
2. **MCP Tool** → Use Case (business logic)
3. **Use Case** → Domain Entity (core operations)
4. **Use Case** → Adapter (persistence/external calls)
5. **Response** ← formatted JSON back to agent

### Workflow State Management
1. **Project Discovery**: Auto-scan or explicit path validation
2. **State Loading**: Read `.cde/state.json` or create new project
3. **Phase Execution**: Load POML templates, execute with context
4. **State Persistence**: Save updated project state
5. **Artifact Generation**: Create specifications, code, documentation

### Multi-Project Coordination
- **Stateless Design**: No central registry, each project self-contained
- **Path Resolution**: Direct paths or name-based lookup via scan roots
- **Context Isolation**: Each project maintains independent state
- **Concurrent Support**: Multiple projects can be active simultaneously

## Configuration Management

### Environment Configuration
- **`.env`**: Environment variables and secrets
- **`pyproject.toml`**: Python project configuration and dependencies
- **`.cde/workflow.yml`**: Project-specific workflow definitions

### Runtime Configuration
- **State Files**: `.cde/state.json` per project for persistent state
- **Skill Cache**: `.copilot/skills/` for dynamic skill management
- **Template Cache**: `.cde/prompts/` for POML template storage

## Integration Points

### External Service Integration
- **GitHub API**: Repository and issue management
- **Git CLI**: Version control operations
- **MCP Ecosystem**: Coordination with other MCP servers
- **AI Services**: Integration with various LLM providers

### Development Tool Integration
- **VS Code**: Native MCP server integration
- **GitHub Copilot**: CLI integration for code generation
- **Testing Frameworks**: pytest for comprehensive testing
- **CI/CD**: GitHub Actions for automated workflows
