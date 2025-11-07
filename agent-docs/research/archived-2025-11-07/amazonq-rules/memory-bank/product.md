# CDE Orchestrator MCP - Product Overview

## Project Purpose
The CDE Orchestrator is a smart MCP (Model Context Protocol) server that implements Context-Driven Engineering (CDE) methodology. It guides AI coding assistants through structured, phase-based software development workflows, transforming development into a series of well-defined state transitions.

## Value Proposition
- **Structured Development**: Converts ad-hoc coding into systematic, repeatable workflows
- **AI-First Design**: Built specifically for AI agents to orchestrate complex development tasks
- **Context Preservation**: Maintains project state and context across development phases
- **Workflow as Code**: Version-controlled development processes in `.cde/workflow.yml`
- **Multi-Project Management**: Handles unlimited projects with stateless, simple architecture

## Key Features & Capabilities

### Core Workflow Management
- **Feature Development Lifecycle**: Guides through define → decompose → design → implement → test → review → integrate phases
- **State Management**: Persistent project state tracking with `.cde/state.json`
- **Phase Transitions**: Automated workflow progression with validation
- **POML Templates**: Prompt Object Markup Language for standardized AI instructions

### Repository Intelligence
- **Onboarding System**: Automated repository analysis and Spec-Kit compliance checking
- **Project Discovery**: Auto-detection of Git repositories across multiple root paths
- **Cleanup Recommendations**: Intelligent suggestions for test relocations and obsolete file removal
- **Technology Stack Analysis**: Automatic detection of programming languages, frameworks, and dependencies

### AI Agent Integration
- **MCP Protocol**: Native Model Context Protocol server for seamless AI assistant integration
- **Recipe System**: Specialized POML templates for different development scenarios (ai-engineer, documentation-writer, deep-research)
- **Intelligent Orchestration**: Dynamic workflow and recipe selection based on task complexity
- **External Service Integration**: Automatic detection and integration with GitHub MCP and other services

### Development Tools
- **Git Integration**: Branch creation, commit management, and repository operations
- **GitHub Integration**: Issue creation and project management (via external MCP when available)
- **Code Execution**: Headless Copilot CLI integration for code generation
- **Testing Framework**: Comprehensive unit and integration testing with pytest

## Target Users

### Primary Users
- **AI Coding Assistants**: GitHub Copilot, Claude, GPT-4, and other LLM-based development tools
- **Development Teams**: Teams seeking structured, repeatable development processes
- **Solo Developers**: Individual developers managing multiple projects with AI assistance

### Use Cases
- **Feature Development**: Structured implementation of new features with AI guidance
- **Project Onboarding**: Rapid analysis and setup of existing repositories
- **Code Quality Assurance**: Systematic review and testing workflows
- **Multi-Project Management**: Coordinated development across numerous codebases
- **Documentation Generation**: Automated creation of specifications and technical documentation

## Technical Specifications
- **Python 3.11+** (optimized for Python 3.14+ for enhanced performance)
- **FastMCP Framework**: Built on fastmcp==2.12.3 for robust MCP server implementation
- **Hexagonal Architecture**: Clean architecture with domain-driven design principles
- **Pydantic Validation**: Type-safe data models and validation
- **YAML Configuration**: Human-readable workflow and configuration files

## Integration Ecosystem
- **VS Code**: Native MCP integration with AI assistant extensions
- **GitHub**: Seamless repository and issue management
- **Git**: Full version control integration
- **External MCPs**: Automatic detection and coordination with other MCP servers
- **CI/CD**: GitHub Actions integration for automated testing and deployment