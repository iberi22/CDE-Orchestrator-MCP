---
title: "Feature: Amazon Q Developer Integration"
description: "Integrate Amazon Q as an AI coding agent in CDE Orchestrator MCP"
type: "feature"
status: "active"
created: "2025-11-04"
updated: "2025-11-04"
author: "CDE Team"
tags:
  - amazon-q
  - ai-agents
  - aws
  - integration
---

## Amazon Q Developer Integration

> **Priority:** 🟢 MEDIUM | **Effort:** 2-3 days | **Status:** 🟡 Planning

### Overview

### Problem

CDE Orchestrator MCP supports multiple AI agents (Copilot, Gemini, Claude, etc.) but **Amazon Q** is missing. Amazon Q is:

- AWS-native AI coding assistant
- Available across multiple IDEs (VS Code, JetBrains, Eclipse, CLI)
- Integrated with AWS Bedrock for customizable LLM selection
- Free tier friendly (50 interactions/month)
- Enterprise-grade security with IAM integration

### Solution

Add **Amazon Q Developer** as a first-class AI agent in CDE Orchestrator by:

- Adding Amazon Q to `AIAssistantConfigurator` detection
- Implementing CLI detection and IDE plugin detection
- Generating `AMAZON-Q.md` with Bedrock configuration
- Creating CLI adapter for code generation
- Supporting AWS IAM authentication

---

## Success Criteria

- ✅ Detect Amazon Q in 3+ environments (CLI, VS Code, JetBrains)
- ✅ Generate `AMAZON-Q.md` with Bedrock models
- ✅ Support AWS credential validation
- ✅ Integration tests >85% coverage
- ✅ Complete documentation

---

## Architecture

### Detection Strategy

```text
Priority 1: CLI Check
└─ which amazon-q && amazon-q --version

Priority 2: IDE Extensions
├─ VS Code: ~/.vscode/extensions/AmazonWebServices.amazon-q-vscode-*
├─ JetBrains: ~/.local/share/JetBrains/*/plugins/amazon-q-*
└─ Eclipse: ~/.eclipse/.../plugins/

Priority 3: AWS Credentials
└─ ~/.aws/credentials or IAM role
```

### Integration Points

1. **AIAssistantConfigurator** - Detection & config generation
2. **SelectWorkflowUseCase** - Pattern matching for "amazon q", "aws"
3. **MultiAgentOrchestrator** - Route to Amazon Q for AWS tasks

---

## Components to Implement

### 1. Amazon Q Detector

**File**: `src/cde_orchestrator/application/ai_config/amazon_q_detector.py`

- `detect_cli()` - Check amazon-q CLI
- `detect_vscode_extension()` - VS Code plugin
- `detect_jetbrains_plugin()` - JetBrains plugin
- `validate_aws_credentials()` - IAM validation
- `list_bedrock_models()` - Available models

### 2. Configuration Generator

**File**: `src/cde_orchestrator/adapters/agents/amazon_q_configurator.py`

- `generate_amazon_q_config()` - Create AMAZON-Q.md
- `generate_iam_policy()` - IAM policy JSON
- `generate_setup_guide()` - Step-by-step guide

### 3. AIAssistantConfigurator Updates

**File**: `src/cde_orchestrator/application/ai_config/ai_config_use_case.py`

```python
AGENT_CONFIG["amazon-q"] = AgentConfig(
    name="Amazon Q Developer",
    key="amazon-q",
    install_url="https://aws.amazon.com/q/developer/",
    requires_cli=False,
    cli_check_command="amazon-q",
    config_files=["AGENTS.md", "AMAZON-Q.md"],
)
```

### 4. CLI Adapter

**File**: `src/cde_orchestrator/adapters/agents/amazon_q_cli_adapter.py`

```python
class AmazonQCLIAdapter(CodeCLIAdapter, ICodeExecutor):
    def _build_command(self, prompt: str, context: Dict) -> List[str]:
        return [
            "amazon-q", "chat",
            "--message", prompt,
            "--model", context.get("model", "claude-3-sonnet"),
            "--region", context.get("region", "us-east-1"),
            "--temperature", "0.2",
            "--max-tokens", "1000",
        ]
```

### 5. Test Suite

**File**: `tests/unit/test_amazon_q_integration.py`

- Detection tests (CLI, VS Code, JetBrains)
- AWS credential validation
- Configuration generation
- IAM policy validation
- CLI adapter tests

---

## Bedrock Models Supported

| Model | Provider | Best For |
|-------|----------|----------|
| claude-3-sonnet | Anthropic | General, balanced |
| claude-3-haiku | Anthropic | Speed, cost |
| claude-3-opus | Anthropic | Complex reasoning |
| llama2-70b | Meta | Speed |
| mistral-large | Mistral | Code generation |

---

## IAM Permissions Required

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:GetModel",
        "bedrock:ListFoundationModels"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/*"
    }
  ]
}
```

---

## Implementation Phases

### Phase 1: Core Integration (2 days)

- Add Amazon Q to AGENT_CONFIG
- CLI detection
- AMAZON-Q.md template
- IAM policy validation
- Unit tests >80%

### Phase 2: Advanced (1 day)

- IDE extension detection
- Bedrock model enumeration
- Custom prompt templates
- Integration tests

### Phase 3: Documentation (1 day)

- Setup guide
- IAM policy guide
- Code examples
- Troubleshooting

---

## Related Documentation

- PR #2: Hexagonal Architecture Migration
- `specs/features/ai-assistant-config.md`
- [Amazon Q Developer Docs][aws-q]
- [AWS Bedrock Guide][bedrock]

[aws-q]: https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/
[bedrock]: https://docs.aws.amazon.com/bedrock/latest/userguide/
