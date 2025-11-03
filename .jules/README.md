# CDE Orchestrator MCP - Jules Configuration

This directory contains Jules-specific configuration files.

## Files

- `setup.sh` - Jules VM environment setup script
- `source_id` - Cached Jules source ID (auto-generated)

## Setup Script

The `setup.sh` script is executed by Jules when preparing the VM environment.

### What it does

1. Upgrades pip
2. Installs Python dependencies from requirements.txt
3. Verifies key packages (fastmcp, pydantic, jules-agent-sdk)
4. Optionally installs pre-commit hooks
5. Optionally runs tests and linting

### Environment Variables

- `RUN_TESTS` - Run tests during setup (default: true)
- `RUN_LINTING` - Run linting during setup (default: false)
- `RUN_MYPY` - Run type checking during setup (default: false)

### Testing the Setup

To test the setup script locally:

```bash
# Make executable
chmod +x .jules/setup.sh

# Run with default settings
./.jules/setup.sh

# Run without tests (faster)
RUN_TESTS=false ./.jules/setup.sh

# Run with full validation
RUN_TESTS=true RUN_LINTING=true RUN_MYPY=true ./.jules/setup.sh
```

## Source ID Cache

The `source_id` file is automatically created by the JulesAsyncAdapter when it resolves the project to a Jules source. This avoids repeated lookups.

To clear the cache:

```bash
rm .jules/source_id
```

## Jules Configuration

Configure Jules in your `.env` file:

```bash
JULES_API_KEY=your-api-key-here
JULES_BASE_URL=https://jules.googleapis.com/v1alpha  # Optional
JULES_DEFAULT_TIMEOUT=1800  # 30 minutes
JULES_REQUIRE_PLAN_APPROVAL=false
```

## Connecting Repository to Jules

1. Go to https://jules.google/
2. Click "Connect Repository"
3. Authorize GitHub access
4. Select your repository

Once connected, the adapter will automatically find and cache the source ID.
