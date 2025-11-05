# CDE Orchestrator MCP - Technology Stack

## Programming Languages & Versions

### Primary Language
- **Python 3.11+** (minimum supported)
- **Python 3.14+** (recommended for optimal performance)
  - 10-20% faster asyncio operations
  - Improved garbage collection for long-running servers
  - Enhanced type system features

### Configuration Languages
- **YAML**: Workflow definitions and configuration files
- **JSON**: State persistence and API responses
- **TOML**: Python project configuration (pyproject.toml)
- **Markdown**: Documentation and specifications

## Core Dependencies

### MCP Framework
- **fastmcp==2.12.3**: Model Context Protocol server implementation
- **pydantic**: Type-safe data validation and serialization
- **pydantic-settings**: Environment-based configuration management

### Data Processing
- **PyYAML**: YAML parsing for workflow definitions
- **lxml**: XML/HTML parsing for web scraping and document processing
- **pathspec**: Git-style path pattern matching

### Environment Management
- **python-dotenv**: Environment variable loading from .env files

## Development Dependencies

### Testing Framework
- **pytest>=7.0**: Primary testing framework
- **pytest-cov**: Code coverage reporting
- **coverage**: Coverage analysis and reporting

### Code Quality Tools
- **black>=23.0**: Code formatting (line-length: 88, target: py313)
- **isort>=5.0**: Import sorting (black profile)
- **flake8>=6.0**: Linting and style checking
- **mypy>=1.0**: Static type checking (Python 3.14 target)
- **types-PyYAML**: Type stubs for PyYAML

### Pre-commit Hooks
- **pre-commit**: Git hook management
- **markdownlint**: Markdown file linting
- **document governance validation**: Custom validation scripts

## Build System & Package Management

### Build Configuration
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
```

### Package Structure
- **Namespace**: `cde-orchestrator-mcp`
- **Version**: 0.2.0
- **Entry Point**: `src/server.py`
- **Package Discovery**: `src/` directory with setuptools

## Development Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]
```

### Code Quality
```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
```

### Server Operations
```bash
# Start MCP server
python src/server.py

# Run with specific environment
PYTHONPATH=src python src/server.py

# Debug mode with verbose logging
DEBUG=1 python src/server.py
```

## Architecture & Design Patterns

### Hexagonal Architecture
- **Domain-Driven Design**: Pure business logic in domain layer
- **Ports & Adapters**: Interface-based dependency inversion
- **Clean Architecture**: Strict dependency rules (inward-only)

### Design Patterns
- **Repository Pattern**: Data access abstraction
- **Use Case Pattern**: Application service layer
- **Adapter Pattern**: External service integration
- **Factory Pattern**: Dependency injection container

### Type System
- **Strict Typing**: `disallow_untyped_defs = true`
- **Pydantic Models**: Runtime type validation
- **Generic Types**: Type-safe collections and protocols
- **Protocol Classes**: Interface definitions

## Integration Technologies

### Version Control
- **Git**: Primary version control system
- **GitHub**: Repository hosting and CI/CD
- **GitHub CLI**: Command-line GitHub integration

### AI & LLM Integration
- **Model Context Protocol (MCP)**: Primary AI integration standard
- **GitHub Copilot CLI**: Code generation integration
- **OpenAI API**: LLM service integration (optional)
- **Anthropic Claude**: Alternative LLM provider (optional)

### External Services
- **GitHub API**: Repository and issue management
- **Web Scraping**: Research and documentation updates
- **File System**: Local project management
- **Process Execution**: CLI tool integration

## Configuration Management

### Environment Variables
```bash
# Required for GitHub integration
GITHUB_TOKEN=your_github_personal_access_token

# Optional debugging
DEBUG=1
PYTHONPATH=src
```

### Configuration Files
- **`.env`**: Environment variables and secrets
- **`pyproject.toml`**: Python project and tool configuration
- **`.cde/workflow.yml`**: Project workflow definitions
- **`.cde/state.json`**: Project state persistence

### Tool Configuration
- **Black**: Line length 88, Python 3.13 target
- **isort**: Black profile compatibility
- **MyPy**: Python 3.14 target, strict type checking
- **Pytest**: `src/` in Python path, test discovery patterns

## Performance Considerations

### Python 3.14 Optimizations
- **Asyncio Performance**: 10-20% improvement in async operations
- **Memory Management**: Enhanced garbage collection for long-running processes
- **Type System**: Improved runtime type checking performance

### Caching Strategies
- **Skill Caching**: Dynamic skill management with persistence
- **Template Caching**: POML template compilation and reuse
- **State Caching**: In-memory project state management

### Scalability Features
- **Stateless Design**: No central state, project-level isolation
- **Concurrent Projects**: Multiple active projects without interference
- **Resource Management**: Efficient file system and memory usage