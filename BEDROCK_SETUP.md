---
title: "AWS Bedrock Configuration for Claude Code and Aider"
description: "Complete setup guide for configuring Claude Code and Aider with AWS Bedrock"
type: guide
status: active
created: "2025-11-05"
updated: "2025-11-05"
author: "GitHub Copilot"
---

# AWS Bedrock Setup for Claude Code + Aider

## Prerequisites

- AWS Account with Bedrock access
- AWS Access Key ID and Secret Access Key
- Claude Code v2.0.32+ installed
- Aider v0.86.0+ installed
- Python 3.14+ with pip

## Step 1: Configure AWS Credentials

### Option A: Using AWS CLI

```bash
aws configure --profile bedrock
```

You'll be prompted for:
- AWS Access Key ID: `[Your AWS Access Key]`
- AWS Secret Access Key: `[Your AWS Secret Key]`
- Default region: `us-east-1` (or your preferred region)
- Default output format: `json`

### Option B: Using Environment Variables (PowerShell)

```powershell
$env:AWS_ACCESS_KEY_ID = 'your_access_key'
$env:AWS_SECRET_ACCESS_KEY = 'your_secret_key'
$env:AWS_REGION = 'us-east-1'
$env:AWS_PROFILE = 'bedrock'
```

### Option C: Create .env file

```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
AWS_PROFILE=bedrock
```

## Step 2: Enable Bedrock Models in AWS Console

1. Go to AWS Console → Bedrock → Model Access
2. Enable the following models:
   - **Claude 3.5 Sonnet**: `anthropic.claude-3-5-sonnet-20240620-v1:0`
   - **Claude 3.7 Sonnet** (new): `us.anthropic.claude-3-7-sonnet-20250219-v1:0`

Note: Claude 3.7 Sonnet uses Inference Profiles, so use the full `us.anthropic.*` ID.

## Step 3: Install Dependencies

### For Aider with Bedrock:

```bash
# Install Aider CLI
python -m pip install aider-install
aider-install

# Install boto3 for AWS SDK
pip install boto3

# Verify installation
aider --list-models bedrock/
```

### For Claude Code with Bedrock:

Claude Code automatically uses Bedrock when AWS credentials are configured. Just set the environment variable:

```bash
# PowerShell
$env:CLAUDE_CODE_USE_BEDROCK = '1'
$env:AWS_REGION = 'us-east-1'
```

## Step 4: Test Connections

### Test Aider with Bedrock:

```bash
cd /path/to/your/project

# List available Bedrock models
aider --list-models bedrock/

# Start with Claude 3.5 Sonnet
aider --model bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0

# Or with new Claude 3.7 Sonnet (Inference Profile)
aider --model bedrock/us.anthropic.claude-3-7-sonnet-20250219-v1:0
```

### Test Claude Code with Bedrock:

```bash
# Check connection status
claude /status

# Test a simple command
claude "What files are in this project?"
```

## Step 5: Configure CDE Orchestrator to Use Both Agents

Add this to your `.env` file:

```
# Bedrock Configuration
AWS_PROFILE=bedrock
AWS_REGION=us-east-1
CLAUDE_CODE_USE_BEDROCK=1

# Aider Configuration
AIDER_MODEL=bedrock/us.anthropic.claude-3-7-sonnet-20250219-v1:0
AIDER_WATCH_PATTERNS=src/,specs/

# Claude Code Configuration
CLAUDE_CODE_MODEL=sonnet-4  # Uses Bedrock when CLAUDE_CODE_USE_BEDROCK=1
```

## Step 6: Configure MCP Server for Multi-Agent Orchestration

The CDE Orchestrator MCP will auto-detect and use both agents:

```json
{
  "servers": {
    "CDE_Orchestrator": {
      "command": "python",
      "args": ["src/server.py", "--scan-paths", "E:\\scripts-python"],
      "env": {
        "PYTHONPATH": "src",
        "CDE_AUTO_DISCOVER": "true",
        "AWS_PROFILE": "bedrock",
        "AWS_REGION": "us-east-1",
        "CLAUDE_CODE_USE_BEDROCK": "1"
      }
    }
  }
}
```

## Troubleshooting

### Issue: "Model ID not supported"

**Error**: `BedrockException - Invocation of model ID anthropic.claude-3-7-sonnet-20250219-v1:0 with on-demand throughput isn't supported`

**Solution**: Use the Inference Profile ID instead:
```bash
aider --model bedrock/us.anthropic.claude-3-7-sonnet-20250219-v1:0
```

### Issue: "Access Denied" when connecting to Bedrock

**Cause**: AWS credentials not configured or invalid.

**Solution**:
1. Verify credentials: `aws sts get-caller-identity --profile bedrock`
2. Check model access in AWS Console → Bedrock → Model Access
3. Verify IAM permissions include `bedrock:InvokeModel`

### Issue: Aider fails to find boto3

**Solution**:
```bash
# Install boto3 in the same environment as aider
pip install boto3 --user
# or
pipx inject aider-chat boto3
```

### Issue: Claude Code doesn't detect Bedrock

**Solution**:
```bash
# Verify environment variable is set
echo $env:CLAUDE_CODE_USE_BEDROCK

# Try explicit Bedrock command
export CLAUDE_CODE_USE_BEDROCK=1
claude /status  # Should show Bedrock configuration
```

## Pricing

- **Claude 3.5 Sonnet**: $3 per 1M input tokens, $15 per 1M output tokens
- **Claude 3.7 Sonnet**: $3 per 1M input tokens, $15 per 1M output tokens (through Inference Profiles)

Track costs via AWS Cost Explorer → Bedrock.

## Next Steps

1. ✅ Configure AWS credentials
2. ✅ Enable Bedrock models in console
3. ✅ Install aider and boto3
4. ✅ Test both agents independently
5. ✅ Configure MCP server
6. ✅ Run full orchestration:

```bash
python orchestrate.py --phase phase1
```

## References

- [Aider + Bedrock](https://aider.chat/docs/llms/bedrock.html)
- [Claude Code + Bedrock](https://docs.claude.com/en/docs/claude-code/amazon-bedrock)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
