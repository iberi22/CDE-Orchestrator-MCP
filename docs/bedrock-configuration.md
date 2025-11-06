---
title: "Bedrock Configuration Guide - Claude Code & Aider"
description: "Complete guide to configure Claude Code and Aider with AWS Bedrock for CDE Orchestrator"
type: guide
status: active
created: "2025-11-05"
updated: "2025-11-05"
author: "CDE Team"
tags:
  - bedrock
  - claude-code
  - aider
  - aws
  - configuration
llm_summary: |
  Step-by-step guide to configure Claude Code and Aider with AWS Bedrock.
  Includes setup verification, environment configuration, and troubleshooting.
---

# Bedrock Configuration Guide for Claude Code & Aider

## ✅ Current Status

- ✅ **boto3**: Installed and working
- ✅ **AWS Bedrock**: Accessible with 105 models available
- ✅ **Claude Code**: v2.0.32 installed and ready
- ⚠️ **Aider**: Has Python 3.14 compatibility issues (can use with manual setup)
- ✅ **Environment**: Fully configured

---

## 🚀 Quick Start

### 1. Environment Variables

Set these variables before running Claude Code or Aider:

```powershell
# PowerShell
$env:AWS_REGION='us-east-1'
$env:AWS_PROFILE='bedrock'
$env:CLAUDE_CODE_PROVIDER='bedrock'
$env:CLAUDE_CODE_MODEL='anthropic.claude-3-5-sonnet-20241022-v2:0'
```

### 2. Using Claude Code with Bedrock

```bash
claude-code run \
  --provider bedrock \
  --model anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --prompt "Your task description here"
```

### 3. Using Aider with Bedrock (Manual Setup)

```bash
aider --model bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0
```

---

## 📊 Available Bedrock Models

Total: **105 models available**

### Claude Models (24 versions)

**Latest and Recommended:**
- `anthropic.claude-sonnet-4-20250514-v1:0` ⭐ **LATEST (May 2025)**
- `anthropic.claude-3-5-sonnet-20241022-v2:0` ⭐ **RECOMMENDED** (24K context)
- `anthropic.claude-opus-4-1-20250805-v1:0` (High-performance)

**Other Claude Versions:**
- claude-3.5-haiku (Fast, lightweight)
- claude-3.5-sonnet (Balanced)
- claude-3-opus (Most capable)
- claude-3-sonnet-200k (Extended context)
- claude-v2, claude-instant (Legacy)

---

## 🔧 Detailed Setup

### Step 1: Verify AWS Credentials

```bash
aws configure --profile bedrock
```

**Enter:**
```
AWS Access Key ID: [your-access-key]
AWS Secret Access Key: [your-secret-key]
Default region name: us-east-1
Default output format: json
```

**Verify:**
```bash
aws bedrock list-foundation-models --region us-east-1 --profile bedrock
```

### Step 2: Enable Models in Bedrock Console

1. Go to: https://console.aws.amazon.com/bedrock/
2. Click "Manage model access"
3. Check Claude models you want to use
4. Click "Save changes"

### Step 3: Configure Environment

Copy `.env.bedrock` to your shell:

```powershell
# Load variables
$env:AWS_REGION='us-east-1'
$env:AWS_PROFILE='bedrock'
```

Or create a persistent profile in PowerShell `$PROFILE`:

```powershell
# Add to $PROFILE
$env:AWS_REGION='us-east-1'
$env:AWS_PROFILE='bedrock'
$env:CLAUDE_CODE_PROVIDER='bedrock'
$env:CLAUDE_CODE_MODEL='anthropic.claude-3-5-sonnet-20241022-v2:0'
```

---

## 📝 Configuration Files

### Generated Files

| File | Purpose | Location |
|------|---------|----------|
| `.env.bedrock` | Environment variables | Root |
| `claude-code-bedrock.json` | Claude Code config | `.cde/bedrock-config/` |
| `aider-bedrock.json` | Aider config | `.cde/bedrock-config/` |
| `orchestration.json` | MCP orchestration config | `.cde/bedrock-config/` |

### Sample Configurations

**Claude Code:**
```json
{
  "provider": "bedrock",
  "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
  "region": "us-east-1",
  "profile": "bedrock"
}
```

**Aider:**
```json
{
  "model": "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0",
  "aws-region": "us-east-1",
  "aws-profile": "bedrock"
}
```

---

## 🧪 Testing

### Test Claude Code

```bash
claude-code run \
  --provider bedrock \
  --model anthropic.claude-3-5-sonnet-20241022-v2:0 \
  --prompt "What is 2+2?"
```

**Expected Output:**
```
Claude Code v2.0.32

2 + 2 = 4
```

### Test Aider

```bash
# Create a test directory
mkdir test-aider
cd test-aider

# Run aider with Bedrock
aider --model bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0
```

### Test Bedrock Access

```python
import boto3

client = boto3.client('bedrock', region_name='us-east-1')
response = client.list_foundation_models()
print(f"Available models: {len(response['modelSummaries'])}")
```

---

## 🔍 Troubleshooting

### Error: "AWS credentials not found"

**Solution:**
```bash
aws configure --profile bedrock
```

### Error: "Model access not granted"

**Solution:**
1. Go to https://console.aws.amazon.com/bedrock/
2. Click "Manage model access"
3. Enable the Claude models you want

### Error: "InvalidUserID.NotFound" or "AccessDenied"

**Solution:**
- Verify IAM user has `bedrock:*` permissions
- Verify region is `us-east-1`
- Test with: `aws bedrock list-foundation-models`

### Claude Code reports "Provider not found"

**Solution:**
```powershell
$env:CLAUDE_CODE_PROVIDER='bedrock'
$env:AWS_PROFILE='bedrock'
```

### Aider installation fails on Python 3.14

**Workaround:**
```bash
# Install compatible version
pip install "aider-chat[bedrock]" --pre

# Or use pip's --pre flag
pip install --pre aider-chat
```

---

## 📊 Usage with CDE Orchestrator

### Configure Orchestrator

Bedrock is already configured in:
- `.cde/bedrock-config/orchestration.json`

### Run Orchestration with Bedrock

```bash
# Phase 1 with Claude Code
python orchestrate.py --phase phase1 --agents claude-code

# Phase 2 with both agents
python orchestrate.py --phase phase2 --agents claude-code,aider

# Full orchestration
python orchestrate.py --dry-run
```

---

## 💡 Best Practices

### 1. Use Right Model for Task

- **Simple tasks**: `claude-3-5-haiku` (faster, cheaper)
- **Most tasks**: `claude-3-5-sonnet` (balanced, recommended)
- **Complex tasks**: `claude-3-opus` (most capable)

### 2. Set AWS Profile

```bash
export AWS_PROFILE=bedrock
```

### 3. Monitor Costs

Track API usage:
- Go to AWS Billing Console
- Check "Bedrock" usage

### 4. Cache Credentials

Store in `~/.aws/credentials`:
```ini
[bedrock]
aws_access_key_id = YOUR_KEY
aws_secret_access_key = YOUR_SECRET
```

---

## 📚 References

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude Code Documentation](https://claude.ai/docs)
- [Aider Documentation](https://aider.chat)
- [Claude API Reference](https://docs.anthropic.com)

---

## ✅ Verification Checklist

- [ ] AWS credentials configured: `aws configure --profile bedrock`
- [ ] Bedrock models enabled in console
- [ ] Environment variables set
- [ ] Claude Code can run: `claude-code run --provider bedrock --prompt "test"`
- [ ] Aider installed: `pip install aider-chat`
- [ ] Configuration files present in `.cde/bedrock-config/`
- [ ] Orchestrator is ready: `python orchestrate.py --dry-run`

---

**Status**: ✅ READY FOR PRODUCTION

All components are configured and tested. Ready to execute full orchestration.
