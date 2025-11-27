---
title: AWS Bedrock + Aider CLI Agent Setup
description: Comprehensive setup scripts for integrating Aider with AWS Bedrock (Claude
  Sonnet 4.5) for the CDE-Orchestrator-MCP project.
type: guide
status: draft
created: '2025-11-20'
updated: '2025-11-20'
author: Auto-Generated
tags:
- aider
- api
- architecture
- authentication
- documentation
- mcp
llm_summary: "User guide for AWS Bedrock + Aider CLI Agent Setup.\n  Comprehensive\
  \ setup scripts for integrating Aider with AWS Bedrock (Claude Sonnet 4.5) for the\
  \ CDE-Orchestrator-MCP project. - ✅ Aider CLI agent (latest version) - ✅ AWS CLI\
  \ v2 (if not present) - ✅ Python dependencies (anthropic, boto3)\n  Reference when\
  \ working with guide documentation."
---

# AWS Bedrock + Aider CLI Agent Setup

Comprehensive setup scripts for integrating Aider with AWS Bedrock (Claude Sonnet 4.5) for the CDE-Orchestrator-MCP project.

## Quick Start

```bash
# 1. Run the setup script
.\setup-aider-bedrock.ps1

# 2. Verify installation
aider --version
aws bedrock list-foundation-models --region us-east-1

# 3. Start your first session
aider --model bedrock/anthropic.claude-sonnet-4-5-20250929-v1:0 /path/to/project
```

## What Gets Installed

- ✅ Aider CLI agent (latest version)
- ✅ AWS CLI v2 (if not present)
- ✅ Python dependencies (anthropic, boto3)
- ✅ AWS Bedrock profile configuration
- ✅ Environment variables setup
- ✅ PowerShell function aliases for convenience

## Files in This Directory

- `setup-aider-bedrock.ps1` - Main setup script (Windows PowerShell)
- `setup-aider-bedrock.sh` - Setup script (Linux/Mac)
- `.env.example` - Environment variables template
- `README.md` - This file

## Configuration

### AWS Credentials

Required environment variables or `~/.aws/credentials`:

```ini
[bedrock]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

Or set via PowerShell:

```powershell
$env:AWS_ACCESS_KEY_ID = "your-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret"
$env:AWS_REGION = "us-east-1"
$env:AWS_PROFILE = "bedrock"
```

### Aider Configuration

Create `~/.config/aider/aider.conf.yml`:

```yaml
model: bedrock/anthropic.claude-sonnet-4-5-20250929-v1:0
auto-commit: true
auto-test: true
pretty: true
```

## Usage Examples

### Basic Code Editing Session

```bash
# Open directory with Aider
aider /path/to/project

# Inside Aider prompt:
# > Add authentication to user module
# > Fix the bug in payment processing
# > Write tests for API endpoints
```

### Non-Interactive Mode (for automation)

```bash
# Make changes without confirmation prompts
aider --yes --model bedrock/anthropic.claude-sonnet-4-5-20250929-v1:0 \
  /path/to/project

# With specific instructions
echo "Add error handling to main.py" | aider --yes \
  --model bedrock/anthropic.claude-sonnet-4-5-20250929-v1:0 \
  /path/to/project
```

### With CDE-Orchestrator-MCP

```python
import subprocess
import os

def start_coding_session(prompt, project_path):
    """Start Aider session via CDE agent"""
    env = os.environ.copy()
    env['AWS_PROFILE'] = 'bedrock'
    env['AWS_REGION'] = 'us-east-1'

    cmd = [
        'aider',
        '--model', 'bedrock/anthropic.claude-sonnet-4-5-20250929-v1:0',
        '--yes',  # Non-interactive
        project_path
    ]

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )

    # Send initial prompt
    stdout, stderr = process.communicate(input=prompt.encode())

    return {
        "status": "completed",
        "output": stdout.decode(),
        "errors": stderr.decode()
    }
```

## Troubleshooting

### "bedrock: command not found"

```bash
# Install Aider
pip install aider-chat

# Or update
pip install --upgrade aider-chat
```

### "ModelNotFound" error

```bash
# Verify Bedrock model access
aws bedrock list-foundation-models --region us-east-1

# Check if model needs request
# Visit: https://console.aws.amazon.com/bedrock/
```

### AWS Credentials errors

```bash
# Test credentials
aws sts get-caller-identity --profile bedrock

# Configure profile
aws configure --profile bedrock
```

### Git repository not initialized

```bash
# Aider requires a git repository
cd /path/to/project
git init
git add .
git commit -m "initial"

# Then start Aider
aider --model bedrock/anthropic.claude-sonnet-4-5-20250929-v1:0 .
```

## Advanced Configuration

### Custom Model Parameters

```bash
aider \
  --model bedrock/anthropic.claude-sonnet-4-5-20250929-v1:0 \
  --temperature 0.7 \
  --max-tokens 2048 \
  /path/to/project
```

### Integrated with CDE Workflow

See `specs/design/bedrock-agent-integration-strategy.md` for CDE-Orchestrator-MCP integration patterns.

## Security Considerations

- ⚠️ Never commit AWS credentials to git
- ⚠️ Use IAM roles in production (not user keys)
- ⚠️ Rotate credentials regularly
- ✅ Use `--yes` flag only with trusted prompts
- ✅ Review git diffs before auto-commit

## Performance Tips

1. **Reduce project size**: Aider works best with focused repositories
2. **Add `.aiderignore`**: Exclude non-essential files (like node_modules)
3. **Use smaller models first**: Test with Haiku before Sonnet on large tasks
4. **Enable caching**: Aider caches codebase maps for faster iterations

### Example .aiderignore

```
__pycache__
*.pyc
node_modules
.git
.venv
build
dist
*.egg-info
.pytest_cache
.coverage
htmlcov
```

## Integration Checklist

- [ ] AWS Bedrock profile configured
- [ ] Aider installed and tested
- [ ] Git repositories initialized
- [ ] `.aiderignore` files created
- [ ] Credentials stored securely
- [ ] CDE-Orchestrator-MCP updated with agent tools
- [ ] Team documentation written

## Links & Resources

- 📖 Aider Documentation: https://aider.chat/docs/
- 🔗 Bedrock Docs: https://docs.aws.amazon.com/bedrock/
- 🏗️ CDE Architecture: `specs/design/bedrock-agent-integration-strategy.md`
- 🐛 Report Issues: [GitHub Issues](https://github.com/paul-gauthier/aider/issues)

## Support

For issues:

1. Check Aider troubleshooting: https://aider.chat/docs/troubleshooting.html
2. Verify AWS credentials work: `aws sts get-caller-identity`
3. Check Bedrock model availability: `aws bedrock list-foundation-models`
4. Review CDE logs for context

---

**Last Updated**: 2025-11-02
**Maintained By**: CDE Architecture Team
