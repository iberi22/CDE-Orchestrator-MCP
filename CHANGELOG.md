# Changelog

## [Unreleased] - 2025-10-31

### Added

#### External Service Integration
- **MCP Detection System**: Automatically detects configured external MCP servers (GitHub, etc.)
- **Service Connector Architecture**: New modular system for integrating external services without embedding internal servers
- **Smart Fallback Mechanism**: Graceful degradation when external services are unavailable
  - GitHub operations fallback: MCP → API → Local file storage
  - Git operations always available locally

#### New MCP Tools
- `cde_createGitBranch`: Creates Git branches for features
- `cde_createGitHubIssue`: Creates GitHub issues with automatic MCP detection
- `cde_commitWork`: Commits work to Git repositories
- `cde_getServiceStatus`: Gets status of all configured integrations

#### Git/GitHub Workflow Integration
- Automatic branch creation when starting new features
- Issue tracking in feature state
- Commit history tracking
- Configurable Git/GitHub operations

#### Documentation
- **INTEGRATION.md**: Comprehensive guide for external service integration
- Updated **README.md** with new tool documentation
- Configuration examples for GitHub MCP
- Troubleshooting guide

### Changed

#### Architecture
- Service connectors now prioritize external MCP servers over direct API calls
- `_process_phase_results` now triggers Git operations automatically
- State management enhanced to track Git/GitHub operations

#### Development
- Added `os` import to support environment variable access
- `ServiceConnectorFactory` for unified service management
- `MCPDetector` for automatic MCP server discovery

### Technical Details

#### File Structure
```
src/cde_orchestrator/
├── service_connector.py  (NEW) - MCP detection and service connectors
├── workflow_manager.py   (EXISTING)
├── prompt_manager.py     (EXISTING)
├── state_manager.py      (EXISTING)
├── recipe_manager.py     (EXISTING)
└── models.py             (EXISTING)

src/
└── server.py             (ENHANCED) - Added Git/GitHub tools
```

#### Configuration Files
- `.cursor/mcp.json` - MCP server configuration (auto-detected)
- `.cde/issues/` - Local issue storage (fallback)
- `INTEGRATION.md` - Integration documentation

### How It Works

1. **Detection Phase**: On startup, the orchestrator scans for MCP configurations
2. **Service Priority**:
   - GitHub: MCP Server → API → Local
   - Git: Always local
3. **Operation Execution**: Connectors execute operations using available methods
4. **State Tracking**: All operations are tracked in feature state

### Migration Guide

No migration needed! The new integration is backward compatible and works with existing workflows.

To enable external services:
1. Configure GitHub MCP in your MCP config file
2. Or set `GITHUB_TOKEN` environment variable
3. Run `cde_getServiceStatus()` to verify

### Future Enhancements

Planned features:
- Support for GitLab MCP
- Bitbucket integration
- Automatic PR creation workflows
- GitHub Actions integration
- Multi-repository support

### Testing

All changes have been tested with:
- Local Git repository operations
- GitHub issue creation with fallback
- Service status detection
- Automatic MCP configuration detection
- Backward compatibility with existing workflows

### Breaking Changes

None. All changes are additive and backward compatible.

