---
title: "Jules Dual-Mode Architecture: API + CLI Fallback"
description: "Intelligent fallback system for Jules agent: API-first with automatic CLI fallback and guided onboarding"
type: "design"
status: "draft"
created: "2025-11-09"
updated: "2025-11-09"
author: "CDE Team"
llm_summary: |
  Dual-mode Jules architecture with intelligent fallback. API-first approach
  with automatic CLI fallback when API key unavailable. Includes guided
  onboarding, status detection, and seamless user experience.
---

# Jules Dual-Mode Architecture: API + CLI Fallback

## 🎯 Problem Statement

**Current State**:
- Jules integration requires `JULES_API_KEY` in `.env`
- If API key missing → hard failure with error message
- User must manually configure API key
- No fallback to Jules CLI (which is already installed)

**User Pain Points**:
1. ❌ "I have Jules CLI working, why can't I use it?"
2. ❌ "I don't want to set up API keys for simple tasks"
3. ❌ "Error messages are unhelpful - what do I do next?"
4. ❌ "I don't know if Jules is even installed"

**Goals**:
- ✅ Detect Jules availability (API vs CLI)
- ✅ Automatic fallback to CLI if API unavailable
- ✅ Guided onboarding for missing setup
- ✅ Clear status messages and next steps
- ✅ Professional UX regardless of mode

---

## 🏗️ Architecture Overview

### Execution Modes

```
┌─────────────────────────────────────────────────────────────┐
│  Agent Request: "cde_delegateToJules(...)"                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
                    ┌───────────────┐
                    │  Jules Facade │
                    │  (Smart Router)│
                    └───────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        ↓                                       ↓
┌──────────────────┐                  ┌──────────────────┐
│  MODE 1: API     │                  │  MODE 2: CLI     │
│  (Async Agent)   │                  │  (Sync Execution)│
└──────────────────┘                  └──────────────────┘
│                                     │
│ • Full repo context                │ • Local execution
│ • Async sessions                   │ • Interactive TUI
│ • Plan approval                    │ • Fast feedback
│ • Web monitoring                   │ • No API required
│ • 100k+ lines                      │ • Good for simple tasks
│                                     │
│ Requires:                          │ Requires:
│ - JULES_API_KEY                    │ - `jules` CLI installed
│ - jules-agent-sdk                  │ - Git repo initialized
│ - Repo on jules.google             │ - Google account login
└──────────────────┘                  └──────────────────┘
```

### Decision Flow

```python
async def execute_with_jules(user_prompt, project_path, context):
    """Intelligent Jules execution with fallback."""

    # 1. Detect available modes
    modes = detect_jules_modes()
    # Returns: {"api": bool, "cli": bool}

    # 2. Select best mode
    selected_mode = select_mode(modes, context)
    # Priority: API > CLI > Guided Setup

    # 3. Execute with selected mode
    if selected_mode == "api":
        return await execute_jules_api(...)
    elif selected_mode == "cli":
        return await execute_jules_cli(...)
    else:
        return generate_setup_guide(modes)
```

---

## 🔧 Component Design

### 1. Jules Facade (Smart Router)

**Purpose**: Single entry point that detects mode and delegates

**File**: `src/cde_orchestrator/adapters/agents/jules_facade.py`

```python
class JulesFacade(ICodeExecutor):
    """
    Intelligent Jules executor with automatic mode selection.

    Modes:
        1. API Mode: Async agent via jules-agent-sdk (preferred)
        2. CLI Mode: Direct CLI execution with interactive TUI
        3. Setup Mode: Guided onboarding if neither available
    """

    def __init__(self):
        self.api_adapter: Optional[JulesAPIAdapter] = None
        self.cli_adapter: Optional[JulesCLIAdapter] = None

    async def execute_prompt(
        self,
        project_path: Path,
        prompt: str,
        context: Dict[str, Any]
    ) -> str:
        # 1. Detect modes
        modes = await self._detect_modes()

        # 2. Select mode
        mode = self._select_mode(modes, context)

        # 3. Execute
        if mode == "api":
            return await self._execute_api(...)
        elif mode == "cli":
            return await self._execute_cli(...)
        else:
            return self._generate_setup_guide(modes)
```

### 2. Mode Detection

**Purpose**: Check what's available on the system

```python
async def detect_jules_modes() -> Dict[str, Any]:
    """
    Detect available Jules modes.

    Returns:
        {
            "api": {
                "available": bool,
                "has_api_key": bool,
                "has_sdk": bool,
                "sdk_version": str | None
            },
            "cli": {
                "available": bool,
                "installed": bool,
                "version": str | None,
                "logged_in": bool,
                "path": str | None
            },
            "preferred_mode": "api" | "cli" | "setup"
        }
    """
    result = {
        "api": await _check_api_mode(),
        "cli": await _check_cli_mode(),
    }

    # Determine preferred mode
    if result["api"]["available"]:
        result["preferred_mode"] = "api"
    elif result["cli"]["available"]:
        result["preferred_mode"] = "cli"
    else:
        result["preferred_mode"] = "setup"

    return result

async def _check_api_mode() -> Dict[str, Any]:
    """Check Jules API mode availability."""
    has_api_key = bool(os.getenv("JULES_API_KEY"))
    has_sdk = importlib.util.find_spec("jules_agent_sdk") is not None

    sdk_version = None
    if has_sdk:
        try:
            import jules_agent_sdk
            sdk_version = jules_agent_sdk.__version__
        except:
            pass

    return {
        "available": has_api_key and has_sdk,
        "has_api_key": has_api_key,
        "has_sdk": has_sdk,
        "sdk_version": sdk_version
    }

async def _check_cli_mode() -> Dict[str, Any]:
    """Check Jules CLI availability."""
    # Check if jules CLI is installed
    jules_path = shutil.which("jules")
    installed = jules_path is not None

    version = None
    logged_in = False

    if installed:
        # Get version
        try:
            result = subprocess.run(
                ["jules", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            version = result.stdout.strip()
        except:
            pass

        # Check login status (try to list sessions)
        try:
            result = subprocess.run(
                ["jules", "remote", "list", "--session"],
                capture_output=True,
                text=True,
                timeout=10
            )
            logged_in = result.returncode == 0
        except:
            logged_in = False

    return {
        "available": installed and logged_in,
        "installed": installed,
        "version": version,
        "logged_in": logged_in,
        "path": jules_path
    }
```

### 3. CLI Adapter

**Purpose**: Execute Jules via CLI with proper error handling

**File**: `src/cde_orchestrator/adapters/agents/jules_cli_adapter.py`

```python
class JulesCLIAdapter(ICodeExecutor):
    """
    Jules CLI adapter for local execution.

    Features:
        - Interactive TUI (if terminal available)
        - Headless mode (background execution)
        - Session tracking
        - Result parsing

    Limitations:
        - No async sessions (blocks until complete)
        - Less context than API (limited by CLI)
        - No plan approval workflow
    """

    async def execute_prompt(
        self,
        project_path: Path,
        prompt: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Execute task via Jules CLI.

        Steps:
            1. Change to project directory
            2. Create Jules session: `jules new "prompt"`
            3. Wait for completion (or return session ID)
            4. Pull results: `jules remote pull --session ID`
            5. Parse output and return
        """
        # Get execution mode from context
        mode = context.get("cli_mode", "headless")  # "interactive" | "headless"

        if mode == "interactive":
            return await self._execute_interactive(project_path, prompt, context)
        else:
            return await self._execute_headless(project_path, prompt, context)

    async def _execute_headless(
        self,
        project_path: Path,
        prompt: str,
        context: Dict[str, Any]
    ) -> str:
        """Execute in background and poll for completion."""

        # 1. Create session
        result = subprocess.run(
            ["jules", "new", prompt],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise JulesCLIError(f"Failed to create session: {result.stderr}")

        # Extract session ID from output
        # Output format: "Session created: 123456"
        session_id = self._extract_session_id(result.stdout)

        # 2. Poll for completion
        timeout = context.get("timeout", 1800)
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = await self._check_session_status(session_id)

            if status == "COMPLETED":
                break
            elif status == "FAILED":
                raise JulesCLIError(f"Session {session_id} failed")

            await asyncio.sleep(10)  # Poll every 10 seconds

        # 3. Pull results
        return await self._pull_session_results(session_id, project_path)

    async def _execute_interactive(
        self,
        project_path: Path,
        prompt: str,
        context: Dict[str, Any]
    ) -> str:
        """Launch interactive TUI and wait for user completion."""

        # Launch TUI (blocks until user exits)
        result = subprocess.run(
            ["jules", "new", prompt],
            cwd=project_path,
            # No capture_output - let TUI display
            timeout=context.get("timeout", 3600)
        )

        if result.returncode != 0:
            raise JulesCLIError("Interactive session failed or cancelled")

        # After TUI exits, we don't have session ID directly
        # User completed task manually, return success
        return json.dumps({
            "success": True,
            "mode": "interactive",
            "message": "Jules interactive session completed. Check your working directory for changes.",
            "next_steps": [
                "Review changes with: git diff",
                "Test changes",
                "Commit when ready: git commit -am 'feat: <description>'"
            ]
        })
```

### 4. Guided Setup (When Nothing Available)

```python
def generate_setup_guide(modes: Dict[str, Any]) -> str:
    """
    Generate helpful setup guide based on what's missing.

    Returns JSON with:
        - status: "setup_required"
        - missing: List of what's not configured
        - options: Available setup paths
        - instructions: Step-by-step for each option
    """

    guide = {
        "status": "setup_required",
        "message": "Jules is not fully configured. Choose a setup option:",
        "options": []
    }

    # Option 1: API Mode (preferred for complex tasks)
    api_option = {
        "mode": "api",
        "title": "🚀 Jules API Mode (Recommended)",
        "description": "Full async agent with web monitoring",
        "pros": [
            "Full repository context (100k+ lines)",
            "Async execution (doesn't block)",
            "Plan approval workflow",
            "Web UI for monitoring"
        ],
        "cons": [
            "Requires API key setup",
            "Repository must be on jules.google"
        ],
        "setup_steps": []
    }

    if not modes["api"]["has_sdk"]:
        api_option["setup_steps"].append({
            "step": 1,
            "action": "Install jules-agent-sdk",
            "command": "pip install jules-agent-sdk"
        })

    if not modes["api"]["has_api_key"]:
        api_option["setup_steps"].extend([
            {
                "step": 2,
                "action": "Get API key from Jules",
                "url": "https://jules.google/",
                "instructions": [
                    "1. Go to https://jules.google/",
                    "2. Sign in with Google account",
                    "3. Navigate to Settings → API Keys",
                    "4. Create new API key",
                    "5. Copy the key"
                ]
            },
            {
                "step": 3,
                "action": "Add API key to .env",
                "command": 'echo "JULES_API_KEY=your-key-here" >> .env',
                "file": ".env",
                "content": "JULES_API_KEY=your-actual-key"
            }
        ])

    guide["options"].append(api_option)

    # Option 2: CLI Mode (easier setup)
    cli_option = {
        "mode": "cli",
        "title": "⚡ Jules CLI Mode (Quick Start)",
        "description": "Local execution with interactive TUI",
        "pros": [
            "No API key required",
            "Easy setup (just login)",
            "Works offline",
            "Good for simple tasks"
        ],
        "cons": [
            "Blocks during execution",
            "Less context than API",
            "No web monitoring"
        ],
        "setup_steps": []
    }

    if not modes["cli"]["installed"]:
        cli_option["setup_steps"].append({
            "step": 1,
            "action": "Install Jules CLI",
            "instructions": [
                "Download from: https://jules.google/cli",
                "Or use package manager:",
                "  macOS: brew install jules",
                "  Linux: See https://jules.google/docs/cli",
                "  Windows: Download installer"
            ]
        })

    if modes["cli"]["installed"] and not modes["cli"]["logged_in"]:
        cli_option["setup_steps"].append({
            "step": 2,
            "action": "Login to Jules",
            "command": "jules login",
            "instructions": [
                "1. Run: jules login",
                "2. Follow browser authentication",
                "3. Verify: jules remote list --session"
            ]
        })

    guide["options"].append(cli_option)

    # Quick recommendation
    if not modes["api"]["available"] and modes["cli"]["installed"]:
        guide["recommendation"] = "cli"
        guide["recommendation_reason"] = "Jules CLI is already installed. Just need to login."
    elif not modes["api"]["available"] and not modes["cli"]["installed"]:
        guide["recommendation"] = "cli"
        guide["recommendation_reason"] = "CLI mode is easier to set up (no API key needed)."
    else:
        guide["recommendation"] = "api"
        guide["recommendation_reason"] = "API mode provides better experience for complex tasks."

    return json.dumps(guide, indent=2)
```

---

## 🔄 Integration with Workflows

### Update MCP Tool: `cde_delegateToJules`

```python
@tool_handler
async def cde_delegateToJules(
    user_prompt: str,
    project_path: str = ".",
    mode: str = "auto",  # NEW: "auto" | "api" | "cli" | "interactive"
    **kwargs
) -> str:
    """
    🤖 Delegate task to Jules (API or CLI with automatic fallback).

    **Modes**:
        - "auto" (default): Use API if available, fallback to CLI
        - "api": Force API mode (fails if unavailable)
        - "cli": Force CLI mode (headless execution)
        - "interactive": Force CLI mode (interactive TUI)

    **Args**:
        mode: Execution mode (default: "auto" for intelligent selection)
        ... (rest of params same as before)
    """

    from cde_orchestrator.adapters.agents import JulesFacade

    # Create facade (handles mode detection internally)
    facade = JulesFacade()

    # Prepare context
    context = {
        "mode_preference": mode,
        **kwargs
    }

    # Execute with intelligent fallback
    result = await facade.execute_prompt(
        project_path=Path(project_path),
        prompt=user_prompt,
        context=context
    )

    return result
```

### Status Reporting to Agent

When API unavailable but CLI works, return helpful message:

```json
{
  "status": "fallback_to_cli",
  "mode": "cli_headless",
  "message": "✅ Jules API unavailable, using CLI mode (headless execution)",
  "session_id": "789012",
  "next_steps": [
    "Task is executing in background via Jules CLI",
    "Session ID: 789012",
    "To check status: jules remote list --session",
    "To view in TUI: jules (then select session 789012)",
    "Results will be available when session completes"
  ],
  "upgrade_tip": "For better experience, set up Jules API: https://jules.google/ → API Keys → Add JULES_API_KEY to .env"
}
```

---

## 📊 User Experience Flows

### Flow 1: API Available (Best Case)

```
User: "cde_delegateToJules('Add auth')"
  ↓
Facade: Detects API available
  ↓
Execute: Jules API (async agent)
  ↓
Return: {
  "mode": "api",
  "session_id": "...",
  "session_url": "https://jules.google/sessions/...",
  "message": "✅ Task delegated to Jules (API mode). Monitor at URL above."
}
```

### Flow 2: API Unavailable, CLI Available (Fallback)

```
User: "cde_delegateToJules('Add auth')"
  ↓
Facade: API unavailable → Fallback to CLI
  ↓
Execute: Jules CLI (headless)
  ↓
Return: {
  "mode": "cli_headless",
  "session_id": "...",
  "message": "⚡ Using Jules CLI mode (API unavailable)",
  "tip": "Set up API mode for better experience: https://jules.google/"
}
```

### Flow 3: Nothing Available (Setup Guide)

```
User: "cde_delegateToJules('Add auth')"
  ↓
Facade: Neither API nor CLI available
  ↓
Return: Setup Guide JSON with options:
  {
    "status": "setup_required",
    "options": [
      {
        "mode": "api",
        "steps": ["Install SDK", "Get API key", "Add to .env"]
      },
      {
        "mode": "cli",
        "steps": ["Install CLI", "Run jules login"]
      }
    ],
    "recommendation": "cli",
    "reason": "Easier setup (no API key needed)"
  }
```

---

## ✅ Implementation Checklist

### Phase 1: Core Infrastructure (2-4 hours)
- [ ] Create `jules_facade.py` with mode detection
- [ ] Implement `detect_jules_modes()` function
- [ ] Create `jules_cli_adapter.py` with headless execution
- [ ] Implement `generate_setup_guide()` function
- [ ] Unit tests for mode detection

### Phase 2: Integration (2 hours)
- [ ] Update `cde_delegateToJules` MCP tool with new `mode` parameter
- [ ] Update `cde_listAvailableAgents` to show mode details
- [ ] Update `cde_selectAgent` to consider available modes
- [ ] Integration tests

### Phase 3: UX Polish (1 hour)
- [ ] Add progress reporting for CLI mode
- [ ] Improve error messages with actionable steps
- [ ] Add examples to tool docstrings
- [ ] Update AGENTS.md documentation

### Phase 4: Advanced Features (Optional, 2-4 hours)
- [ ] Interactive CLI mode (launch TUI)
- [ ] Session management (list, pull, resume)
- [ ] Parallel sessions support
- [ ] Auto-upgrade suggestions

---

## 📝 Documentation Updates

### Update AGENTS.md

```markdown
## Jules Integration

CDE Orchestrator supports Jules in two modes:

### 1. API Mode (Recommended for Complex Tasks)
- Full async agent with 100k+ lines context
- Web monitoring at https://jules.google/
- Requires: JULES_API_KEY in .env

### 2. CLI Mode (Quick Start)
- Local execution with interactive TUI
- No API key required
- Requires: `jules` CLI installed + login

### Automatic Fallback
MCP automatically selects best available mode. If API unavailable, falls back to CLI mode seamlessly.

**Setup CLI Mode**:
```bash
# Install (if not installed)
brew install jules  # macOS
# Or download from https://jules.google/cli

# Login
jules login

# Verify
jules remote list --session
```

**Setup API Mode**:
```bash
# 1. Install SDK
pip install jules-agent-sdk

# 2. Get API key from https://jules.google/ → Settings → API Keys

# 3. Add to .env
echo "JULES_API_KEY=your-key-here" >> .env
```
```

---

## 🎯 Benefits

### For Users
✅ **Zero Configuration Friction**: Works out of the box if Jules CLI installed
✅ **Intelligent Fallback**: Seamless degradation to CLI mode
✅ **Clear Guidance**: Helpful setup instructions when needed
✅ **Flexible**: Choose mode based on task complexity

### For Developers
✅ **Clean Architecture**: Facade pattern with clear separation
✅ **Testable**: Easy to mock modes for testing
✅ **Extensible**: Easy to add new execution modes
✅ **Professional**: Robust error handling and user feedback

---

## 🔮 Future Enhancements

### Phase 2+ (Post-MVP)
1. **Hybrid Mode**: Use API for planning, CLI for execution
2. **Session Resume**: Resume interrupted CLI sessions
3. **Parallel Tasks**: Multiple Jules CLI sessions in parallel
4. **Auto-Detection**: Detect when API key added and auto-upgrade
5. **Performance Metrics**: Compare API vs CLI execution times
6. **Cost Tracking**: API usage vs CLI local execution

---

## 📊 Decision Matrix

| Scenario | Mode | Rationale |
|----------|------|-----------|
| Complex refactoring (8+ hours) | API | Full context, async, monitoring |
| Simple fix (< 1 hour) | CLI | Fast feedback, local |
| API key not set | CLI | Automatic fallback |
| CLI not logged in | Setup Guide | Clear instructions |
| Neither available | Setup Guide | User chooses path |
| User prefers interactive | CLI Interactive | Launch TUI |

---

## 🚀 Rollout Plan

### Week 1: Core Implementation
- Implement facade, mode detection, CLI adapter
- Unit tests for all components
- Integration with existing JulesAPIAdapter

### Week 2: Integration & Testing
- Update MCP tools with new mode parameter
- End-to-end testing with real Jules CLI
- Documentation updates

### Week 3: Polish & Deploy
- UX improvements
- Error message refinement
- Deploy to production
- User feedback collection

---

**Status**: Ready for Implementation 🚀
**Effort**: ~8-12 hours total
**Impact**: Major UX improvement, removes configuration barrier
