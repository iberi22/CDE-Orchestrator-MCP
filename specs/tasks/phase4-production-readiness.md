---
title: "Phase 4: Production Readiness & Error Handling"
description: "Harden single-project operations for production use with robust error handling"
type: "task"
status: "active"
created: "2025-11-10"
updated: "2025-11-10"
author: "CDE Agent"
tags:
  - phase4
  - production
  - error-handling
  - logging
  - monitoring
llm_summary: |
  Phase 4 implementation plan for CDE Orchestrator.
  Focus: Production-ready error handling, logging, and monitoring for single project.
  Complements Phase 3 optimization with enterprise-grade reliability.
---

# Phase 4: Production Readiness & Error Handling

> **Status**: 🟡 Planning
> **Start Date**: 2025-11-10
> **Dependencies**: Phase 3 (Single Project Optimization)

---

## 🎯 Objective

Transform CDE Orchestrator from **working** to **production-ready** by adding:
- Comprehensive error handling
- Structured logging
- Health monitoring
- Graceful degradation
- User-friendly error messages

**Philosophy**: A single project managed **perfectly** means handling ALL edge cases gracefully.

---

## 📋 Tasks Overview

| Task | Priority | Effort | Status |
|------|----------|--------|--------|
| PROD-01: Error Handling Framework | 🔴 CRITICAL | 2 days | ⏸️ Not Started |
| PROD-02: Structured Logging | 🔴 CRITICAL | 1 day | ⏸️ Not Started |
| PROD-03: Health Monitoring | 🟠 HIGH | 2 days | ⏸️ Not Started |
| PROD-04: User-Friendly Errors | 🟠 HIGH | 1 day | ⏸️ Not Started |
| PROD-05: Graceful Degradation | 🟡 MEDIUM | 2 days | ⏸️ Not Started |

**Total Effort**: 8 days
**Target Completion**: 2025-11-18

---

## 🔴 PROD-01: Error Handling Framework

**Priority**: 🔴 CRITICAL
**Effort**: 2 days
**Status**: ⏸️ Not Started

### Description

Implement comprehensive error handling with custom exceptions, error codes, and recovery strategies.

### Tasks

- [ ] **PROD-01.1**: Define custom exception hierarchy
  - `CDEError` base class
  - `ProjectError` for project-level issues
  - `FeatureError` for feature workflow issues
  - `StateError` for state management issues
  - `ValidationError` for input validation

- [ ] **PROD-01.2**: Implement error codes system
  - `E001-E099`: Project errors
  - `E100-E199`: Feature errors
  - `E200-E299`: State errors
  - `E300-E399`: Validation errors
  - `E900-E999`: System errors

- [ ] **PROD-01.3**: Add recovery strategies
  - Automatic retry for transient failures
  - State rollback on errors
  - Safe mode (read-only) on critical failures

- [ ] **PROD-01.4**: Error context capture
  - Stack traces
  - State snapshots
  - User actions leading to error

- [ ] **PROD-01.5**: Error reporting
  - Structured error logs
  - User-friendly error messages
  - Suggested fixes

### Implementation

```python
# src/cde_orchestrator/domain/exceptions.py
class CDEError(Exception):
    """Base exception for all CDE errors."""

    def __init__(
        self,
        message: str,
        code: str,
        context: dict[str, Any] | None = None,
        recoverable: bool = True,
    ):
        super().__init__(message)
        self.code = code
        self.context = context or {}
        self.recoverable = recoverable
        self.timestamp = datetime.now(timezone.utc)

class ProjectError(CDEError):
    """Project-level errors (E001-E099)."""
    pass

class FeatureError(CDEError):
    """Feature workflow errors (E100-E199)."""
    pass

class StateError(CDEError):
    """State management errors (E200-E299)."""
    pass

# Example usage
raise ProjectError(
    message="Project not found at path",
    code="E001",
    context={"path": "/invalid/path"},
    recoverable=False
)
```

### Files to Create/Modify

- **Create**: `src/cde_orchestrator/domain/exceptions.py` (~150 lines)
- **Modify**: All domain entities to raise custom exceptions
- **Modify**: All adapters to catch and convert exceptions
- **Create**: `tests/unit/test_error_handling.py` (~200 lines)

### Acceptance Criteria

```python
# All errors have codes
try:
    project.start_feature("...")
except FeatureError as e:
    assert e.code.startswith("E1")
    assert e.recoverable is True
    assert "context" in e.__dict__

# Errors include context
try:
    repo.get_or_create("/invalid")
except ProjectError as e:
    assert e.context["path"] == "/invalid"
    assert e.code == "E001"

# Recovery strategies work
try:
    state_manager.save(project)
except StateError as e:
    if e.recoverable:
        # Retry logic
        state_manager.save(project, force=True)
```

### Tests

- `test_custom_exceptions_hierarchy`
- `test_error_codes_unique`
- `test_error_context_capture`
- `test_recovery_strategies`
- `test_error_to_json_serialization`

---

## 🔴 PROD-02: Structured Logging

**Priority**: 🔴 CRITICAL
**Effort**: 1 day
**Status**: ⏸️ Not Started

### Description

Replace print statements with structured logging using `structlog` for better observability.

### Tasks

- [ ] **PROD-02.1**: Setup structlog configuration
  - JSON output format
  - Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Contextual loggers per module

- [ ] **PROD-02.2**: Add logging to all operations
  - Project creation/loading
  - Feature lifecycle transitions
  - State persistence
  - Adapter operations

- [ ] **PROD-02.3**: Log correlation IDs
  - Trace feature workflows
  - Track operations across components

- [ ] **PROD-02.4**: Performance logging
  - Operation durations
  - Resource usage
  - Bottleneck identification

- [ ] **PROD-02.5**: Log rotation and cleanup
  - Daily rotation
  - Size-based rotation
  - Retention policy (7 days default)

### Implementation

```python
# src/cde_orchestrator/infrastructure/logging.py
import structlog

def setup_logging(level: str = "INFO", output_file: str | None = None):
    """Configure structured logging."""
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

# Usage in entities
logger = structlog.get_logger(__name__)

class Project:
    def start_feature(self, prompt: str) -> Feature:
        log = logger.bind(
            project_id=str(self.id),
            operation="start_feature",
            prompt_length=len(prompt)
        )
        log.info("Starting feature", prompt=prompt[:50])

        try:
            feature = Feature.create(self.id, prompt)
            log.info("Feature created", feature_id=str(feature.id))
            return feature
        except Exception as e:
            log.error("Failed to create feature", error=str(e))
            raise
```

### Files to Create/Modify

- **Create**: `src/cde_orchestrator/infrastructure/logging.py` (~100 lines)
- **Modify**: All domain entities to use logger
- **Modify**: All adapters to use logger
- **Modify**: `src/server.py` to setup logging on startup
- **Create**: `tests/unit/test_logging.py` (~80 lines)

### Acceptance Criteria

```python
# Logs are structured JSON
log_output = """
{"event": "Feature created", "feature_id": "123", "timestamp": "2025-11-10T10:00:00Z"}
"""

# All operations logged
with capture_logs() as logs:
    project.start_feature("Add auth")
    assert len(logs) >= 2  # start + success
    assert logs[0]["operation"] == "start_feature"

# Performance metrics logged
with capture_logs() as logs:
    project.start_feature("Add auth")
    assert "duration_ms" in logs[-1]
```

### Tests

- `test_logging_configuration`
- `test_json_output_format`
- `test_correlation_ids_preserved`
- `test_log_rotation_works`
- `test_performance_metrics_logged`

---

## 🟠 PROD-03: Health Monitoring

**Priority**: 🟠 HIGH
**Effort**: 2 days
**Status**: ⏸️ Not Started

### Description

Add health check endpoints and monitoring for production deployments.

### Tasks

- [ ] **PROD-03.1**: Health check endpoint
  - `/health` - Basic liveness check
  - `/health/ready` - Readiness check
  - `/health/metrics` - Performance metrics

- [ ] **PROD-03.2**: System metrics
  - Memory usage
  - Disk usage (for `.cde/state.json`)
  - Active features count
  - Error rate

- [ ] **PROD-03.3**: Performance metrics
  - Average operation duration
  - P50, P95, P99 latencies
  - Throughput (operations/second)

- [ ] **PROD-03.4**: Alerting thresholds
  - High error rate (>5%)
  - Slow operations (>1s)
  - Disk space low (<100MB)
  - Memory usage high (>80%)

- [ ] **PROD-03.5**: Health dashboard
  - Real-time metrics view
  - Historical trends
  - Alert history

### Implementation

```python
# src/mcp_tools/health.py
from fastmcp import FastMCP

@mcp.tool()
def cde_getHealth() -> str:
    """Get system health status."""
    from cde_orchestrator.infrastructure.health import get_health_status

    status = get_health_status()
    return json.dumps(status, indent=2)

# src/cde_orchestrator/infrastructure/health.py
class HealthMonitor:
    """Monitor system health and performance."""

    def get_status(self) -> dict:
        return {
            "status": "healthy",
            "version": "0.5.0",
            "uptime_seconds": self._get_uptime(),
            "metrics": {
                "memory_mb": self._get_memory_usage(),
                "disk_mb": self._get_disk_usage(),
                "active_features": self._get_active_features(),
                "error_rate": self._get_error_rate(),
            },
            "checks": {
                "state_file_writable": self._check_state_writable(),
                "disk_space": self._check_disk_space(),
                "memory": self._check_memory(),
            }
        }
```

### Files to Create/Modify

- **Create**: `src/cde_orchestrator/infrastructure/health.py` (~200 lines)
- **Create**: `src/mcp_tools/health.py` (~50 lines)
- **Modify**: `src/server.py` to initialize health monitor
- **Create**: `tests/unit/test_health_monitoring.py` (~100 lines)

### Acceptance Criteria

```python
# Health endpoint returns status
result = cde_getHealth()
health = json.loads(result)
assert health["status"] == "healthy"
assert "metrics" in health
assert "checks" in health

# Metrics are accurate
assert health["metrics"]["memory_mb"] > 0
assert health["metrics"]["disk_mb"] > 0

# Checks detect issues
# (simulate low disk space)
health = get_health_status()
assert health["checks"]["disk_space"] == "warning"
```

### Tests

- `test_health_endpoint_returns_status`
- `test_metrics_calculation_accurate`
- `test_checks_detect_issues`
- `test_alert_thresholds_work`

---

## 🟠 PROD-04: User-Friendly Errors

**Priority**: 🟠 HIGH
**Effort**: 1 day
**Status**: ⏸️ Not Started

### Description

Convert technical errors into user-friendly messages with suggested fixes.

### Tasks

- [ ] **PROD-04.1**: Error message templates
  - Clear, concise descriptions
  - Actionable suggestions
  - Relevant documentation links

- [ ] **PROD-04.2**: Error severity levels
  - INFO: Informational (no action needed)
  - WARNING: Potential issue (review recommended)
  - ERROR: Operation failed (action required)
  - CRITICAL: System failure (immediate attention)

- [ ] **PROD-04.3**: Suggested fixes
  - Common solutions
  - Commands to run
  - Configuration changes

- [ ] **PROD-04.4**: Error documentation
  - Error code catalog
  - Troubleshooting guide
  - FAQ section

### Implementation

```python
# src/cde_orchestrator/domain/errors/messages.py
ERROR_MESSAGES = {
    "E001": {
        "title": "Project Not Found",
        "description": "The project path '{path}' does not exist or is not accessible.",
        "suggestions": [
            "Verify the path is correct",
            "Check file permissions",
            "Create the project directory: mkdir -p {path}"
        ],
        "docs": "https://cde.dev/docs/errors/e001"
    },
    "E101": {
        "title": "Feature Creation Failed",
        "description": "Cannot start feature in {status} status. Project must be ACTIVE.",
        "suggestions": [
            "Activate the project: project.activate()",
            "Check project status: cde_getProjectInfo()"
        ],
        "docs": "https://cde.dev/docs/errors/e101"
    }
}

class ErrorFormatter:
    """Format errors for end users."""

    @staticmethod
    def format(error: CDEError) -> str:
        template = ERROR_MESSAGES.get(error.code, {})

        return f"""
❌ {template.get('title', 'Error')}

{template.get('description', str(error)).format(**error.context)}

💡 Suggestions:
{chr(10).join(f"  • {s.format(**error.context)}" for s in template.get('suggestions', []))}

📖 More info: {template.get('docs', 'https://cde.dev/docs/errors')}
        """.strip()
```

### Files to Create/Modify

- **Create**: `src/cde_orchestrator/domain/errors/messages.py` (~300 lines)
- **Create**: `src/cde_orchestrator/domain/errors/formatter.py` (~100 lines)
- **Modify**: All MCP tools to format errors
- **Create**: `docs/errors/catalog.md` (~500 lines)
- **Create**: `tests/unit/test_error_formatting.py` (~80 lines)

### Acceptance Criteria

```python
# Errors are user-friendly
try:
    project.start_feature("...")
except FeatureError as e:
    message = ErrorFormatter.format(e)
    assert "💡 Suggestions:" in message
    assert "📖 More info:" in message
    assert e.code in message

# Suggestions are actionable
formatted = ErrorFormatter.format(error)
assert "project.activate()" in formatted
```

### Tests

- `test_error_formatting_includes_suggestions`
- `test_context_interpolation_works`
- `test_all_errors_have_messages`
- `test_documentation_links_valid`

---

## 🟡 PROD-05: Graceful Degradation

**Priority**: 🟡 MEDIUM
**Effort**: 2 days
**Status**: ⏸️ Not Started

### Description

Implement fallback strategies when components fail, ensuring system remains partially functional.

### Tasks

- [ ] **PROD-05.1**: Read-only mode
  - Activate when state persistence fails
  - Allow queries but block mutations
  - Clear indicator to user

- [ ] **PROD-05.2**: Feature partial completion
  - Save progress at each phase
  - Resume from last successful phase
  - Rollback unsuccessful phases

- [ ] **PROD-05.3**: State recovery
  - Load from last known good state
  - Automatic backup restoration
  - Manual recovery commands

- [ ] **PROD-05.4**: Circuit breaker pattern
  - Detect repeated failures
  - Temporarily disable failing operations
  - Auto-recovery after cooldown

### Implementation

```python
# src/cde_orchestrator/infrastructure/circuit_breaker.py
class CircuitBreaker:
    """Implement circuit breaker pattern."""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = "closed"  # closed, open, half_open
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
            else:
                raise CircuitBreakerOpenError()

        try:
            result = func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise
```

### Files to Create/Modify

- **Create**: `src/cde_orchestrator/infrastructure/circuit_breaker.py` (~150 lines)
- **Modify**: `src/cde_orchestrator/adapters/filesystem_project_repository.py` (add read-only mode)
- **Modify**: Domain entities to support partial completion
- **Create**: `tests/unit/test_graceful_degradation.py` (~120 lines)

### Acceptance Criteria

```python
# Read-only mode activates
with simulate_disk_full():
    project = repo.get_or_create("/path")
    assert project.read_only is True

    with pytest.raises(ReadOnlyModeError):
        project.start_feature("...")

# Circuit breaker works
for _ in range(5):
    try:
        failing_operation()
    except:
        pass

with pytest.raises(CircuitBreakerOpenError):
    failing_operation()  # Blocked by circuit breaker
```

### Tests

- `test_read_only_mode_blocks_mutations`
- `test_circuit_breaker_opens_after_failures`
- `test_state_recovery_from_backup`
- `test_partial_feature_completion`

---

## 📊 Success Metrics

### Quantitative

- ✅ **100% coverage** of error handling in domain layer
- ✅ **All errors** have user-friendly messages
- ✅ **All operations** logged with structured data
- ✅ **Health endpoint** responds in <50ms
- ✅ **<1% error rate** in production

### Qualitative

- ✅ Errors are **actionable** (users know what to do)
- ✅ Logs are **searchable** (JSON format)
- ✅ System **degrades gracefully** (no hard crashes)
- ✅ Recovery is **automatic** when possible
- ✅ Monitoring is **real-time**

---

## 🔗 Dependencies

### Required Before Start

- ✅ Phase 3 complete (Single Project Optimization)
- ✅ All tests passing (39/39)
- ✅ Performance validated (<100ms operations)

### Parallel Work Possible

- PROD-01 and PROD-02 can run in parallel
- PROD-03 can start after PROD-02
- PROD-04 depends on PROD-01
- PROD-05 depends on PROD-01 and PROD-03

---

## 📈 Expected Outcomes

### Error Handling

- **Before**: Generic `ValueError`, `FileNotFoundError`
- **After**: Specific `ProjectError(code="E001")` with context

### Logging

- **Before**: `print(f"Starting feature...")`
- **After**: `logger.info("Feature created", feature_id="...", duration_ms=42)`

### Monitoring

- **Before**: No visibility into system health
- **After**: Real-time metrics, alerts on issues

### User Experience

- **Before**: "ValueError: Project must be ACTIVE"
- **After**: Clear error with 3 actionable suggestions + docs link

---

## 🎯 Next Steps

### Immediate (This Week)

1. Review this plan with team
2. Prioritize tasks (already done)
3. Start PROD-01 (Error Handling Framework)
4. Start PROD-02 (Structured Logging) in parallel

### Short-term (Next 2 Weeks)

1. Complete PROD-01 and PROD-02
2. Start PROD-03 (Health Monitoring)
3. Start PROD-04 (User-Friendly Errors)

### Medium-term (Next Month)

1. Complete PROD-05 (Graceful Degradation)
2. Validate in production-like environment
3. User acceptance testing
4. Documentation updates

---

## 📚 Related Documents

- [Phase 3: Single Project Optimization](../execution/execution-phase3-single-project-optimization-2025-11-10.md)
- [CHANGELOG.md](../../CHANGELOG.md)
- [Improvement Roadmap](improvement-roadmap.md)

---

**Phase 4 Status**: 🟡 **PLANNING COMPLETE**

*Ready to start implementation when Phase 3 is confirmed stable.*
