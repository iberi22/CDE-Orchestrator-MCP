# Gemini Configuration for CDE Orchestrator

This file configures the gemini-cli to use the local CDE Orchestrator MCP.

```yaml
mcp:
  - name: CDE_Orchestrator
    command: python
    args:
      - src/server.py
    env:
      PYTHONPATH: src
    enabled: true
