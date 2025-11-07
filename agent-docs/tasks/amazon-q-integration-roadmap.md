---
title: "Amazon Q Integration - Task Roadmap for Jules"
description: "Detailed implementation tasks for Amazon Q Developer integration in CDE Orchestrator MCP"
type: "task"
status: "active"
created: "2025-11-04"
updated: "2025-11-04"
author: "CDE Team"
tags:
  - amazon-q
  - tasks
  - jules
  - ai-agents
  - roadmap
---

## Amazon Q Integration - Task Roadmap for Jules

> **Duration**: 3 days total
> **Status**: Ready for Jules execution
> **Related**: PR #2 (Hexagonal Architecture), spec at `specs/features/amazon-q-integration.md`

---

## 📋 Executive Summary

This document organizes the Amazon Q integration work into structured tasks for Jules AI agent. All tasks align with:

- Hexagonal architecture from PR #2
- AIAssistantConfigurator pattern (existing ai-assistant-config)
- Multi-agent orchestration system
- Testing best practices (>80% coverage target)

---

## 🎯 Phase 1: Core Integration (2 days)

### TASK AQ-01: Add Amazon Q to AIAssistantConfigurator

**Effort**: 4 hours | **Priority**: 🔴 CRITICAL

**Objective**: Integrate Amazon Q detection and configuration into existing `AIAssistantConfigurator` system

**Files to Modify**:

1. `src/cde_orchestrator/application/ai_config/ai_config_use_case.py`
   - Add to `AGENT_CONFIG` dictionary
   - Update `detect_installed_agents()` method
   - Update `generate_config_files()` method

2. `src/cde_orchestrator/application/ai_config/amazon_q_detector.py` (NEW)
   - Implement `AmazonQDetector` class
   - Methods: `detect_cli()`, `validate_aws_credentials()`

**Subtasks**:

```
[ ] AQ-01.1: Define AgentConfig for Amazon Q in AGENT_CONFIG
    - name: "Amazon Q Developer"
    - key: "amazon-q"
    - install_url: "https://aws.amazon.com/q/developer/"
    - cli_check_command: "amazon-q"
    - config_files: ["AGENTS.md", "AMAZON-Q.md"]
    - requires_cli: false

[ ] AQ-01.2: Create amazon_q_detector.py with:
    - detect_cli(): Check `amazon-q --version`
    - detect_vscode_extension(): Check ~/.vscode/extensions/
    - detect_jetbrains_plugin(): Check ~/.local/share/JetBrains/

[ ] AQ-01.3: Update detect_installed_agents():
    - Add check for amazon-q detection
    - Return list with "amazon-q" if detected

[ ] AQ-01.4: Update generate_config_files():
    - Call AmazonQConfigurator if "amazon-q" in agents
    - Handle file generation

[ ] AQ-01.5: Add unit tests to test_ai_assistant_configurator.py:
    - test_detect_amazon_q_cli()
    - test_detect_amazon_q_vscode()
    - test_amazon_q_in_detected_agents()
```

**Acceptance Criteria**:

- ✅ Amazon Q appears in `detect_installed_agents()` output
- ✅ AGENT_CONFIG properly configured
- ✅ Tests passing with >85% coverage
- ✅ No breaking changes to existing agents

**Dependencies**: None - independent task

---

### TASK AQ-02: Implement Amazon Q Configuration Generator

**Effort**: 4 hours | **Priority**: 🔴 CRITICAL

**Objective**: Generate `AMAZON-Q.md` with Bedrock models, IAM setup, and region info

**Files to Create**:

1. `src/cde_orchestrator/adapters/agents/amazon_q_configurator.py` (NEW)

**Structure**:

```python
class AmazonQConfigurator:
    def __init__(self, project_root: Path):
        pass

    def generate_amazon_q_config(self) -> Dict[str, Any]:
        """Generate AMAZON-Q.md file with AWS Bedrock config"""
        pass

    def generate_iam_policy(self) -> str:
        """Generate minimal IAM policy JSON"""
        pass

    def detect_aws_region(self) -> str:
        """Detect AWS region from credentials/env"""
        pass

    def list_bedrock_models(self) -> List[str]:
        """List available Bedrock foundation models"""
        pass
```

**Subtasks**:

```
[ ] AQ-02.1: Implement basic structure & methods
    - Handle missing AWS credentials gracefully
    - Return default config if AWS not setup

[ ] AQ-02.2: Generate AMAZON-Q.md template with:
    - Bedrock models list (Claude 3, Llama 2, Mistral)
    - AWS region information
    - IAM setup guide
    - Custom prompt templates

[ ] AQ-02.3: Implement generate_iam_policy()
    - Return JSON with required permissions:
      * bedrock:InvokeModel
      * bedrock:ListFoundationModels
      * amazonq:CreateConversation

[ ] AQ-02.4: Implement AWS region detection
    - Check ~/.aws/config
    - Check AWS_REGION env var
    - Use default: us-east-1

[ ] AQ-02.5: Add 5+ unit tests:
    - test_generate_amazon_q_config_default()
    - test_generate_iam_policy_has_required_actions()
    - test_detect_aws_region_from_env()
    - test_generate_config_missing_credentials()
    - test_template_markdown_format()
```

**Acceptance Criteria**:

- ✅ AMAZON-Q.md generated successfully
- ✅ IAM policy valid JSON format
- ✅ Region detection working
- ✅ Tests >80% coverage
- ✅ Graceful handling of missing AWS setup

**Dependencies**: Task AQ-01 (needs AGENT_CONFIG setup)

---

### TASK AQ-03: Create Amazon Q CLI Adapter

**Effort**: 4 hours | **Priority**: 🟡 HIGH

**Objective**: Implement CLI execution adapter for Amazon Q code generation

**Files to Create**:

1. `src/cde_orchestrator/adapters/agents/amazon_q_cli_adapter.py` (NEW)

**Structure**:

```python
class AmazonQCLIAdapter(CodeCLIAdapter, ICodeExecutor):
    @property
    def cli_command(self) -> str:
        return "amazon-q"

    @property
    def provider_name(self) -> str:
        return "Amazon Q Developer"

    def _build_command(self, prompt: str, context: Dict[str, Any]) -> List[str]:
        """Build amazon-q CLI command"""
        pass

    def get_install_instructions(self) -> str:
        """Return installation instructions"""
        pass
```

**Subtasks**:

```
[ ] AQ-03.1: Implement CLI command builder
    - Support --model parameter (claude-3-sonnet default)
    - Support --region parameter (us-east-1 default)
    - Support --temperature (0.2 for code generation)
    - Support --max-tokens (1000 default)

[ ] AQ-03.2: Implement error handling
    - Check if amazon-q CLI is available
    - Handle timeout scenarios
    - Parse response properly

[ ] AQ-03.3: Add context support
    - Allow custom Bedrock model selection
    - Allow AWS region override
    - Allow temperature/token customization

[ ] AQ-03.4: Add 8+ unit tests:
    - test_build_command_defaults()
    - test_build_command_custom_model()
    - test_build_command_custom_region()
    - test_execute_prompt_success()
    - test_execute_prompt_cli_not_found()
    - test_execute_prompt_timeout()
    - test_install_instructions_format()
    - test_provider_name_correct()
```

**Acceptance Criteria**:

- ✅ CLI commands built correctly
- ✅ Timeout handling working
- ✅ Model/region customization working
- ✅ Tests >85% coverage
- ✅ Follows CodeCLIAdapter pattern

**Dependencies**: Task AQ-01

---

### TASK AQ-04: AWS Credential Validation Module

**Effort**: 3 hours | **Priority**: 🟡 HIGH

**Objective**: Validate AWS credentials and IAM permissions for Bedrock access

**Files to Create**:

1. `src/cde_orchestrator/adapters/agents/amazon_q_credentials.py` (NEW)

**Structure**:

```python
class AmazonQCredentials:
    @staticmethod
    def validate() -> Dict[str, bool]:
        """Validate AWS credentials and Bedrock access"""
        pass

    @staticmethod
    def check_bedrock_access() -> bool:
        """Check if user can access Bedrock"""
        pass

    @staticmethod
    def get_available_models() -> List[str]:
        """Get list of available Bedrock models"""
        pass
```

**Subtasks**:

```
[ ] AQ-04.1: Implement credential detection
    - Check ~/.aws/credentials
    - Check AWS_PROFILE environment variable
    - Check for IAM role (EC2, Lambda, ECS)
    - Check STS token

[ ] AQ-04.2: Implement Bedrock access check
    - Use boto3 if available
    - Graceful fallback if boto3 not installed
    - Try to describe foundation models

[ ] AQ-04.3: Add validation result caching
    - Cache results for 30 minutes
    - Invalidate on AWS_PROFILE change

[ ] AQ-04.4: Add 6+ unit tests:
    - test_validate_credentials_success()
    - test_validate_credentials_missing()
    - test_check_bedrock_access_success()
    - test_check_bedrock_access_denied()
    - test_get_available_models_returns_list()
    - test_validation_caching()
```

**Acceptance Criteria**:

- ✅ Credential validation working
- ✅ Graceful handling of missing boto3
- ✅ IAM check functional
- ✅ Tests >80% coverage
- ✅ Useful error messages

**Dependencies**: Task AQ-01, AQ-02

---

## 🎯 Phase 2: Advanced Features (1 day)

### TASK AQ-05: IDE Plugin Detection (VS Code, JetBrains)

**Effort**: 3 hours | **Priority**: 🟢 MEDIUM

**Objective**: Detect Amazon Q IDE extensions and plugins

**Files to Modify**:

1. `src/cde_orchestrator/application/ai_config/amazon_q_detector.py`
   - Enhance existing detection methods

**Subtasks**:

```
[ ] AQ-05.1: Implement VS Code detection
    - Check ~/.vscode/extensions/ (Windows/Mac/Linux)
    - Look for AmazonWebServices.amazon-q-vscode-* pattern
    - Extract version information

[ ] AQ-05.2: Implement JetBrains detection
    - Check ~/.local/share/JetBrains/*/plugins/ (Linux)
    - Check ~/Library/Application\ Support/JetBrains/ (Mac)
    - Check %APPDATA%\JetBrains\ (Windows)

[ ] AQ-05.3: Implement Eclipse detection
    - Check ~/.eclipse/ (Linux/Mac)
    - Check plugin directory

[ ] AQ-05.4: Add 5+ unit tests:
    - test_detect_vscode_extension_found()
    - test_detect_vscode_extension_not_found()
    - test_detect_jetbrains_plugin_found()
    - test_detect_jetbrains_plugin_multiple_versions()
    - test_detect_eclipse_plugin()
```

**Acceptance Criteria**:

- ✅ All 3 IDE types detected
- ✅ Version information extracted
- ✅ Cross-platform paths working
- ✅ Tests >85% coverage

**Dependencies**: Task AQ-01

---

### TASK AQ-06: Bedrock Model Enumeration & Caching

**Effort**: 3 hours | **Priority**: 🟢 MEDIUM

**Objective**: List available Bedrock models with caching

**Files to Modify**:

1. `src/cde_orchestrator/adapters/agents/amazon_q_configurator.py`

**Subtasks**:

```
[ ] AQ-06.1: Implement model listing via boto3
    - bedrock.list_foundation_models()
    - Extract: model ID, name, input/output tokens
    - Filter for code generation models

[ ] AQ-06.2: Add hardcoded fallback models
    - claude-3-sonnet-20240229
    - claude-3-haiku-20240307
    - meta.llama2-70b-v1
    - mistral.mistral-large-2402-v1:0

[ ] AQ-06.3: Implement caching
    - Cache to ~/.cde/amazon-q-models.json
    - 7-day TTL
    - Invalidate on AWS_PROFILE change

[ ] AQ-06.4: Add 4+ unit tests:
    - test_list_models_from_bedrock()
    - test_list_models_fallback()
    - test_models_cached_correctly()
    - test_cache_expiration()
```

**Acceptance Criteria**:

- ✅ Models listed from Bedrock or fallback
- ✅ Caching working with TTL
- ✅ Tests >85% coverage

**Dependencies**: Task AQ-02, AQ-04

---

### TASK AQ-07: Integration Tests - End-to-End Flow

**Effort**: 2 hours | **Priority**: 🟡 HIGH

**Objective**: Comprehensive integration tests for entire Amazon Q flow

**Files to Create**:

1. `tests/integration/test_amazon_q_onboarding.py` (NEW)

**Test Cases**:

```
[ ] AQ-07.1: test_amazon_q_detected_in_onboarding()
    - Setup: Mocked amazon-q CLI
    - Execute: cde_onboardingProject()
    - Assert: Amazon Q in detected agents

[ ] AQ-07.2: test_amazon_q_config_generated()
    - Setup: Mocked AWS credentials
    - Execute: AIAssistantConfigurator.generate_config_files()
    - Assert: AMAZON-Q.md created with Bedrock models

[ ] AQ-07.3: test_cli_adapter_execution()
    - Setup: Mocked amazon-q CLI
    - Execute: AmazonQCLIAdapter.execute()
    - Assert: Command built correctly

[ ] AQ-07.4: test_full_multi_agent_setup()
    - Setup: Copilot + Gemini + Amazon Q all detected
    - Execute: Full onboarding
    - Assert: All 3 configured
```

**Acceptance Criteria**:

- ✅ All integration tests passing
- ✅ >80% coverage on new code
- ✅ No side effects on existing agents

**Dependencies**: All Phase 1 tasks

---

## 🧪 Phase 3: Documentation & Examples (1 day)

### TASK AQ-08: Documentation - Setup Guide

**Effort**: 3 hours | **Priority**: 🟡 HIGH

**Objective**: Create comprehensive setup guide for users

**Files to Create**:

1. `docs/amazon-q-setup.md` (NEW)

**Content**:

```markdown
- Installation instructions (CLI, VS Code, JetBrains)
- AWS credential setup (IAM user, MFA)
- Bedrock model selection guide
- CDE Orchestrator integration steps
- Troubleshooting FAQ
- Example workflows
```

**Subtasks**:

```
[ ] AQ-08.1: Write installation section
[ ] AQ-08.2: Write AWS setup section
[ ] AQ-08.3: Write Bedrock models guide
[ ] AQ-08.4: Write troubleshooting
[ ] AQ-08.5: Add 5+ code examples
```

**Acceptance Criteria**:

- ✅ Clear step-by-step instructions
- ✅ All platforms covered
- ✅ Screenshots/examples included
- ✅ Links to AWS docs

**Dependencies**: All Phase 1 tasks

---

### TASK AQ-09: Update Main Documentation

**Effort**: 2 hours | **Priority**: 🟢 MEDIUM

**Objective**: Update main docs to include Amazon Q

**Files to Modify**:

1. `README.md`
   - Add Amazon Q to agent list

2. `docs/INTEGRATION.md`
   - Add AWS Bedrock section
   - Link to amazon-q-setup.md

3. `specs/api/mcp-tools.md`
   - Document Amazon Q capabilities

**Subtasks**:

```
[ ] AQ-09.1: Update README
[ ] AQ-09.2: Update INTEGRATION.md
[ ] AQ-09.3: Update MCP tools documentation
```

**Acceptance Criteria**:

- ✅ Documentation consistent
- ✅ All links working
- ✅ Examples accurate

**Dependencies**: Task AQ-08

---

### TASK AQ-10: Update Improvement Roadmap

**Effort**: 1 hour | **Priority**: 🟡 HIGH

**Objective**: Mark Amazon Q tasks as complete in roadmap

**Files to Modify**:

1. `specs/tasks/improvement-roadmap.md`

**Changes**:

```
- Add Amazon Q feature section
- Mark all tasks COMPLETED
- Update metrics (test coverage, tool error rate)
- Link to AMAZON-Q.md spec
```

**Subtasks**:

```
[ ] AQ-10.1: Add new section for Amazon Q
[ ] AQ-10.2: Mark all implementation tasks complete
[ ] AQ-10.3: Update metrics in roadmap
[ ] AQ-10.4: Link back to this document
```

**Acceptance Criteria**:

- ✅ Roadmap updated
- ✅ All links working
- ✅ Metrics accurate

**Dependencies**: All implementation tasks

---

## 📊 Quality Metrics

### Code Quality

| Metric | Target | Phase 1 | Phase 2 | Phase 3 |
|--------|--------|---------|---------|---------|
| **Unit Test Coverage** | >85% | 85%+ | 85%+ | N/A |
| **Integration Test Coverage** | >80% | N/A | 80%+ | N/A |
| **Linting Compliance** | 100% | ✅ | ✅ | N/A |
| **Type Hints** | 100% | ✅ | ✅ | N/A |

### Documentation Quality

| Metric | Target | Status |
|--------|--------|--------|
| **Setup Guide Completeness** | 100% | Phase 3 |
| **API Documentation** | 100% | Phase 3 |
| **Example Code Samples** | 5+ | Phase 3 |

---

## 🚀 Execution Strategy

### For Jules

1. **Execute Phase 1 first** (2 days)
   - Core integration tasks (AQ-01 through AQ-04)
   - Run tests after each task
   - Validate no breaking changes

2. **Execute Phase 2** (1 day)
   - Advanced features (AQ-05, AQ-06)
   - End-to-end integration tests (AQ-07)
   - Full coverage >80%

3. **Execute Phase 3** (1 day)
   - Documentation (AQ-08, AQ-09)
   - Update roadmap (AQ-10)
   - Final validation

### CI/CD Integration

All tasks must:

- ✅ Pass pre-commit hooks
- ✅ Pass all pytest tests
- ✅ Maintain >85% coverage
- ✅ No type hints errors (mypy)
- ✅ Markdown linting compliance

---

## 📋 Success Checklist (Jules)

- [ ] All Phase 1 tasks complete (4 tasks)
- [ ] All Phase 2 tasks complete (3 tasks)
- [ ] All Phase 3 tasks complete (3 tasks)
- [ ] Test coverage >85%
- [ ] No breaking changes
- [ ] All documentation complete
- [ ] Roadmap updated
- [ ] PR ready for review

---

## 🔗 Related Documents

- Feature Spec: `specs/features/amazon-q-integration.md`
- Existing AI Config: `specs/features/ai-assistant-config.md`
- PR #2: Hexagonal Architecture Migration
- Main Roadmap: `specs/tasks/improvement-roadmap.md`
