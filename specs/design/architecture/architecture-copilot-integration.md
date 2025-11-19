---
title: "CDE Orchestrator MCP - Copilot CLI Integration"
description: "Headless Copilot CLI adapter for code generation with YOLO mode support"
type: "design"
status: "active"
created: "2025-11-18"
updated: "2025-11-18"
author: "CDE Orchestrator Team"
tags:
  - "architecture"
  - "copilot"
  - "code-generation"
  - "adapter"
llm_summary: |
  Copilot CLI adapter implementation. Supports headless execution, YOLO mode (auto-apply),
  workflow-driven prompts, and context injection. Implements ICodeExecutor port.
---

# Copilot CLI Integration

> **Part of**: [Architecture Documentation](README.md)
> **Purpose**: Execute code generation via GitHub Copilot CLI
> **Layer**: Adapters (Infrastructure)

## Overview

The `CopilotCLIAdapter` implements the `ICodeExecutor` port to enable headless GitHub Copilot execution within CDE workflows.

**Key Features**:

- **Headless Execution**: Run Copilot without interactive prompts
- **YOLO Mode**: Auto-apply changes without confirmation
- **Context Injection**: Include workflow artifacts in prompts
- **Result Parsing**: Extract modified files and diffs

---

## Implementation

```python
# src/cde_orchestrator/adapters/copilot_cli_adapter.py

import asyncio
import json
from typing import Dict, Any, List
from dataclasses import dataclass
from ..domain.ports import ICodeExecutor

@dataclass
class ExecutionResult:
    """Result of code execution."""
    success: bool
    modified_files: List[str]
    diff: str
    log: str
    metadata: Dict[str, Any]

class CopilotCLIAdapter(ICodeExecutor):
    """
    Adapter for GitHub Copilot CLI headless execution.

    Features:
        - YOLO mode support (auto-apply changes)
        - Workflow-driven prompts
        - Context injection from CDE state

    Requirements:
        - `gh copilot` CLI installed
        - Authentication configured (`gh auth login`)
    """

    def __init__(self, yolo_default: bool = False):
        self.yolo_default = yolo_default
        self._check_cli_available()

    def _check_cli_available(self):
        """Verify Copilot CLI is installed."""
        import shutil
        if not shutil.which("gh"):
            raise RuntimeError("GitHub CLI (gh) not found in PATH")
        # Could also check: gh copilot --version

    async def execute_prompt(
        self,
        project_path: str,
        prompt: str,
        context: Dict[str, Any]
    ) -> ExecutionResult:
        """
        Execute code generation with Copilot.

        Implementation:
            1. Build Copilot CLI command
            2. Inject context from workflow
            3. Execute in project directory
            4. Parse output and collect changes

        Args:
            project_path: Absolute path to project
            prompt: Natural language instruction
            context: Additional context (yolo flag, artifacts, etc)

        Returns:
            ExecutionResult with modified files and diff
        """
        yolo = context.get("yolo", self.yolo_default)

        # Build command
        cmd = self._build_copilot_command(prompt, yolo)

        # Execute
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=project_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        # Parse results
        result = self._parse_execution_result(
            stdout.decode(),
            stderr.decode(),
            process.returncode
        )

        return result

    def _build_copilot_command(self, prompt: str, yolo: bool) -> List[str]:
        """
        Build Copilot CLI command.

        Examples:
            Normal: gh copilot suggest "create user auth"
            YOLO:   gh copilot suggest --apply "create user auth"
        """
        cmd = ["gh", "copilot", "suggest"]

        if yolo:
            cmd.append("--apply")  # Auto-apply without confirmation

        cmd.append(prompt)
        return cmd

    def _parse_execution_result(
        self,
        stdout: str,
        stderr: str,
        return_code: int
    ) -> ExecutionResult:
        """
        Parse Copilot CLI output into structured result.

        Note: Parsing logic depends on Copilot CLI output format,
              which may change. Update this method if format changes.
        """
        success = return_code == 0

        # Extract modified files from output
        # (This is simplified; actual parsing depends on Copilot output format)
        modified_files = []
        if "Modified:" in stdout:
            # Parse file list
            # Example: "Modified: src/models.py, src/utils.py"
            for line in stdout.split('\n'):
                if line.startswith("Modified:"):
                    files_str = line.replace("Modified:", "").strip()
                    modified_files = [f.strip() for f in files_str.split(',')]

        return ExecutionResult(
            success=success,
            modified_files=modified_files,
            diff=stdout,  # Copilot may include diff in output
            log=f"{stdout}\n{stderr}",
            metadata={"return_code": return_code}
        )

    def supports_yolo_mode(self) -> bool:
        """Copilot CLI supports auto-apply."""
        return True
```

---

## Usage Example

```python
# In use case
executor = CopilotCLIAdapter(yolo_default=False)

result = await executor.execute_prompt(
    project_path="/path/to/project",
    prompt="Create User model with email and password fields",
    context={"yolo": True}  # Override default
)

if result.success:
    print(f"Modified files: {result.modified_files}")
    print(f"Diff:\n{result.diff}")
else:
    print(f"Error: {result.log}")
```

---

## YOLO Mode

**YOLO Mode** = "You Only Live Once" - auto-apply changes without confirmation.

**When to Use**:

- ✅ In automated workflows
- ✅ When agent trusts Copilot output
- ✅ For simple, low-risk changes

**When NOT to Use**:

- ❌ On production code without review
- ❌ For complex refactoring
- ❌ When learning new codebase

```python
# Enable YOLO globally
executor = CopilotCLIAdapter(yolo_default=True)

# Or per-call
result = await executor.execute_prompt(
    project_path="/path/to/project",
    prompt="...",
    context={"yolo": True}
)
```

---

## Context Injection

Pass workflow artifacts as context:

```python
# In use case
context = {
    "yolo": True,
    "specification": feature.artifacts.get("specification"),
    "task_breakdown": feature.artifacts.get("task_breakdown"),
    "design_document": feature.artifacts.get("design")
}

# Augment prompt with context
augmented_prompt = f"""
{user_prompt}

Context from workflow:
- Specification: {context['specification']}
- Tasks: {context['task_breakdown']}
"""

result = await executor.execute_prompt(
    project_path=project.path,
    prompt=augmented_prompt,
    context=context
)
```

---

## Error Handling

```python
async def execute_with_retry(self, prompt: str, max_retries: int = 3):
    """Execute with automatic retry on failure."""
    for attempt in range(max_retries):
        try:
            result = await self.execute_prompt(
                project_path=self.project_path,
                prompt=prompt,
                context={}
            )
            if result.success:
                return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

---

## Testing

```python
# Mock for testing
class MockCopilotExecutor(ICodeExecutor):
    async def execute_prompt(self, project_path, prompt, context):
        return ExecutionResult(
            success=True,
            modified_files=["src/models.py"],
            diff="+ class User:\n+     pass",
            log="Generated User model",
            metadata={}
        )

    def supports_yolo_mode(self):
        return True

# Use in tests
async def test_execute_code_use_case():
    mock_executor = MockCopilotExecutor()
    use_case = ExecuteCodeUseCase(repo, mock_executor)

    result = await use_case.execute("proj-123", "Create User model")

    assert result["status"] == "success"
    assert "src/models.py" in result["files_changed"]
```

---

## Alternative Executors

### LocalLLMAdapter

For running local models instead of Copilot:

```python
class LocalLLMAdapter(ICodeExecutor):
    """Execute code generation with local LLM (Ollama, LLaMA, etc)"""

    async def execute_prompt(self, project_path, prompt, context):
        # Call local model API
        response = await self.llm_client.generate(prompt)
        # Apply changes
        return ExecutionResult(...)
```

### DirectAPIAdapter

For using Copilot API directly:

```python
class DirectAPIAdapter(ICodeExecutor):
    """Use Copilot API instead of CLI"""

    async def execute_prompt(self, project_path, prompt, context):
        # Call Copilot REST API
        response = await self.api_client.post("/completions", {
            "prompt": prompt,
            "context": context
        })
        return ExecutionResult(...)
```

---

## Next Steps

- **Understand Ports**: See [Ports Documentation](architecture-ports.md)
- **Wire with DI**: See [DI Container](architecture-di-container.md)
- **Use in Workflows**: See [Use Cases](architecture-use-cases.md)

---

*This document is part of the modular architecture documentation. See [README](README.md) for full navigation.*
