---
title: "Gemini CLI + MCP Configuration"
description: "Configuration and usage guide for wiring Gemini (AI Studio/CLI) to the CDE Orchestrator MCP server so instructions load and parse reliably."
type: "guide"
status: "active"
created: "2025-11-02"
updated: "2025-11-02"
author: "CDE Orchestrator MCP"
---

# CDE Orchestrator MCP – Gemini Integration

> **Format**: GEMINI.md (Google AI Studio Standard)
> **Target**: Google Gemini AI (AI Studio, Gemini CLI, IDX)
> **Last Updated**: 2025-11-02
> **Priority**: Ensure parsing succeeds with multiple GEMINI.md sources

---

## Purpose

This document defines a minimal, parse-friendly configuration for the Gemini CLI to connect with the local CDE Orchestrator MCP server. It also mirrors the header tokens expected by importers when multiple `GEMINI.md` files exist in the repository.

---

## Gemini CLI MCP Configuration

Place this block in the Gemini CLI configuration (or reference it via your tool’s import mechanism). Adjust the Python entrypoint if you use a venv or wrapper.

```yaml
mcp:
  - name: CDE_Orchestrator
    command: python
    args:
      - src/server.py
    env:
      PYTHONPATH: src
    enabled: true
```

Notes:
- Ensure `src/server.py` is executable from your working directory.
- If using a virtual environment, set `command` to the venv Python path and keep `PYTHONPATH: src`.
- When multiple `GEMINI.md` files exist (root and docs/), both must have a recognizable header block so importers can reconcile parent/child content.

---

## Troubleshooting Parsing Errors

- Error: "Could not find child token in parent raw content"
  - Cause: The importer detected multiple `GEMINI.md` files but could not match the child’s header tokens inside the parent.
  - Fix: Ensure both files start with a consistent header section that includes the lines:
    - `**Format**: GEMINI.md (...)`
    - `**Target**: Google Gemini AI (...)`
    - `**Last Updated**: YYYY-MM-DD`
    - `**Priority**: ...`
  - Also make sure all fenced code blocks are properly closed.

If problems persist, temporarily keep only one `GEMINI.md` in scope for your CLI run, or consolidate content so the importer finds matching tokens.
