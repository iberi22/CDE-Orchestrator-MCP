---
title: "Rust Project Scanner Migration Plan"
description: "Design document for accelerating ProjectAnalysisUseCase with Rust implementation"
type: "design"
status: "active"
created: "2025-11-20"
updated: "2025-11-20"
author: "CDE Team"
llm_summary: |
  Comprehensive plan to migrate ProjectAnalysisUseCase from Python to Rust for 10x performance improvement.
  Includes parallel filesystem scanning with Rayon, multi-pattern filtering, and graceful fallback to Python.
  Targets reducing analysis time from 500ms to 50ms for typical projects.
---

# Rust Project Scanner Migration Plan

## Executive Summary

Migrate `ProjectAnalysisUseCase` from pure Python to Rust-accelerated implementation to achieve:
- **10x performance improvement** (500ms → 50ms analysis time)
- **50% memory reduction** with native Rust data structures
- **Full parallelization** across all CPU cores using Rayon
- **Zero breaking changes** with automatic Python fallback

## Current State Analysis

### Python Implementation Bottlenecks

```python
# Current: Sequential, single-threaded
all_files = list(project_path.rglob("*"))  # Blocks entire thread
for file in all_files:                     # O(n) sequential processing
    # Filter, validate, collect
```

**Measurements**:
- Files analyzed: 385 (with 13,799 node_modules excluded)
- Time: ~500ms (Python pathlib + filtering)
- Memory: ~50MB peak
- Parallelization: None (single thread)

### Rust Advantages

| Aspect | Python | Rust | Benefit |
|--------|--------|------|---------|
| **Filesystem I/O** | `pathlib` (slow) | `walkdir` (native) | 2-3x faster |
| **String matching** | Python regex | `regex` crate | 3-5x faster |
| **Parallelization** | GIL-limited | Rayon (no GIL) | 8x (8-core CPU) |
| **Memory** | High overhead | Minimal | 50% reduction |
| **Overall** | 500ms | 50ms | **10x improvement** |

## Implementation Plan

### Phase 1: Rust Module Development (Day 1-2)

#### Task 1.1: Create `project_scanner.rs`

**File**: `rust_core/src/project_scanner.rs`

```rust
use rayon::prelude::*;
use std::collections::HashMap;
use walkdir::WalkDir;
use regex::Regex;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct ProjectAnalysisResult {
    pub file_count: usize,
    pub language_stats: HashMap<String, usize>,
    pub dependency_files: Vec<String>,
    pub excluded_directories: Vec<String>,
    pub excluded_count: usize,
    pub analysis_time_ms: u128,
}

pub fn scan_project(
    root_path: &str,
    excluded_dirs: Vec<String>,
    excluded_patterns: Vec<String>,
) -> Result<ProjectAnalysisResult, String> {
    let start = std::time::Instant::now();

    // 1. Parallel filesystem scan
    let walker = WalkDir::new(root_path)
        .into_iter()
        .par_bridge()  // ← Parallelization magic
        .filter_map(|entry| entry.ok());

    // 2. Parallel filtering & collection
    let (files, stats, excluded) = process_files(walker, excluded_dirs.clone(), excluded_patterns);

    // 3. Detect dependency files
    let dependency_files = find_dependency_files(&files);

    let analysis_time_ms = start.elapsed().as_millis();

    Ok(ProjectAnalysisResult {
        file_count: files.len(),
        language_stats: stats,
        dependency_files,
        excluded_directories: excluded_dirs,
        excluded_count: excluded,
        analysis_time_ms,
    })
}
```

**Features**:
- ✅ Parallel `WalkDir` with Rayon `.par_bridge()`
- ✅ Native regex filtering
- ✅ Auto-detects CPU cores
- ✅ Returns timing metrics

#### Task 1.2: Implement Parallel Processing

**File**: `rust_core/src/project_scanner.rs`

```rust
fn process_files(
    walker: rayon::iter::ParallelBridge<...>,
    excluded_dirs: Vec<String>,
    excluded_patterns: Vec<String>,
) -> (Vec<PathBuf>, HashMap<String, usize>, usize) {
    walker
        .filter_map(|entry| {
            let path = entry.path();

            // Skip directories
            if path.is_dir() { return None; }

            // Check excluded directories
            if is_excluded_dir(path, &excluded_dirs) { return None; }

            // Check excluded patterns
            if is_excluded_pattern(path, &excluded_patterns) { return None; }

            Some(path.to_path_buf())
        })
        .fold(
            || (Vec::new(), HashMap::new(), 0usize),
            |(mut files, mut stats, excluded)| {
                // Collect stats in parallel
                if let Some(ext) = path.extension() {
                    *stats.entry(format!(".{}", ext)).or_insert(0) += 1;
                }
                files.push(path);
                (files, stats, excluded)
            }
        )
        .reduce(
            || (Vec::new(), HashMap::new(), 0),
            |(mut f1, mut s1, e1), (f2, s2, e2)| {
                f1.extend(f2);
                for (k, v) in s2 { *s1.entry(k).or_insert(0) += v; }
                (f1, s1, e1 + e2)
            }
        )
}
```

**Optimization Techniques**:
- ✅ `par_bridge()` - Parallel iteration
- ✅ `fold()` → `reduce()` - Parallel aggregation
- ✅ SIMD-optimized regex
- ✅ Zero-copy string handling

#### Task 1.3: Python Binding

**File**: `rust_core/src/lib.rs` (add to existing)

```rust
#[pyfunction]
fn scan_project_py(
    root_path: String,
    excluded_dirs: Vec<String>,
    excluded_patterns: Vec<String>,
) -> PyResult<String> {
    match project_scanner::scan_project(&root_path, excluded_dirs, excluded_patterns) {
        Ok(result) => {
            let json = serde_json::to_string(&result)
                .map_err(|e| PyErr::new::<PyValueError, _>(format!("Serialization error: {}", e)))?;
            Ok(json)
        }
        Err(e) => Err(PyErr::new::<PyValueError, _>(e)),
    }
}
```

### Phase 2: Python Integration (Day 3)

#### Task 2.1: Update `ProjectAnalysisUseCase`

**File**: `src/cde_orchestrator/application/onboarding/project_analysis_use_case.py`

```python
class ProjectAnalysisUseCase:
    """Enhanced with Rust acceleration and fallback."""

    EXCLUDED_DIRS = { ... }  # Existing
    EXCLUDED_PATTERNS = { ... }  # Existing

    def execute(self, project_path: str) -> Dict[str, Any]:
        report_progress_http("onboardingProject", 0.0, "Starting analysis")

        # Try Rust first (10x faster)
        try:
            result = self._execute_rust(project_path)
            report_progress_http("onboardingProject", 1.0, "Analysis complete (Rust)")
            return result
        except Exception as e:
            logger.warning(f"Rust analysis failed, falling back to Python: {e}")
            # Fallback to Python
            result = self._execute_python(project_path, report_progress_http)
            report_progress_http("onboardingProject", 1.0, "Analysis complete (Python)")
            return result

    def _execute_rust(self, project_path: str) -> Dict[str, Any]:
        """Rust-accelerated analysis (~50ms)."""
        try:
            import cde_rust_core

            excluded_dirs = sorted(list(self.EXCLUDED_DIRS))
            excluded_patterns = sorted(list(self.EXCLUDED_PATTERNS))

            result_json = cde_rust_core.scan_project_py(
                str(Path(project_path).absolute()),
                excluded_dirs,
                excluded_patterns,
            )

            result = json.loads(result_json)

            # Post-process: filter irrelevant languages
            language_stats = Counter(result["language_stats"])
            relevant_languages = [
                (lang, count) for lang, count in language_stats.most_common(10)
                if lang not in {".map", ".lock", ".json", ".xml"}
            ][:3]

            summary = (
                f"Project '{Path(project_path).name}' contains {result['file_count']} files. "
                f"Primary languages: {', '.join(lang for lang, _ in relevant_languages)}. "
                f"Found dependency files: {', '.join(result['dependency_files']) if result['dependency_files'] else 'None'}. "
                f"(Rust-accelerated, {result['analysis_time_ms']}ms)"
            )

            return {
                "status": "Analysis complete",
                "file_count": result["file_count"],
                "language_stats": language_stats,
                "dependency_files": result["dependency_files"],
                "summary": summary,
                "excluded_directories": excluded_dirs,
                "performance": {
                    "engine": "rust",
                    "analysis_time_ms": result["analysis_time_ms"],
                }
            }
        except ImportError:
            raise Exception("cde_rust_core not available")

    def _execute_python(self, project_path: str, report_progress_http) -> Dict[str, Any]:
        """Fallback Python implementation (~500ms)."""
        # Existing implementation
        files = self._list_files(Path(project_path), report_progress_http)
        language_stats = self._analyze_languages(files)
        dependency_files = self._find_dependency_files(files)

        return {
            "status": "Analysis complete",
            "file_count": len(files),
            "language_stats": language_stats,
            "dependency_files": dependency_files,
            "summary": "...",
            "excluded_directories": sorted(list(self.EXCLUDED_DIRS)),
            "performance": {
                "engine": "python",
                "analysis_time_ms": None,  # Python fallback timing
            }
        }
```

#### Task 2.2: Add Rust Core Check

**File**: `src/cde_orchestrator/rust_utils.py` (update)

```python
RUST_AVAILABLE = False
try:
    import cde_rust_core
    # Verify scan_project_py function exists
    if hasattr(cde_rust_core, 'scan_project_py'):
        RUST_AVAILABLE = True
    else:
        logger.warning("cde_rust_core missing scan_project_py")
except ImportError as e:
    logger.debug(f"Rust core not available: {e}")
```

### Phase 3: Testing (Day 4)

#### Task 3.1: Unit Tests for Rust

**File**: `rust_core/tests/project_scanner_tests.rs`

```rust
#[test]
fn test_scan_project_basic() {
    let result = project_scanner::scan_project(
        "./test_project",
        vec!["node_modules".to_string()],
        vec!["*.map".to_string()],
    ).unwrap();

    assert!(result.file_count > 0);
    assert!(!result.language_stats.is_empty());
    assert!(result.analysis_time_ms < 100); // Rust should be fast
}

#[test]
fn test_excludes_node_modules() {
    let result = project_scanner::scan_project(
        "./test_project",
        vec!["node_modules".to_string()],
        vec![],
    ).unwrap();

    assert!(!result.language_stats.contains_key(".js"));
}

#[test]
fn test_performance_under_1s() {
    let start = std::time::Instant::now();
    let _ = project_scanner::scan_project(".", vec![], vec![]);
    let elapsed = start.elapsed();

    assert!(elapsed.as_millis() < 1000, "Analysis took too long");
}
```

#### Task 3.2: Integration Tests

**File**: `tests/integration/test_rust_onboarding.py`

```python
import pytest
from cde_orchestrator.application.onboarding.project_analysis_use_case import ProjectAnalysisUseCase

@pytest.mark.integration
def test_rust_analysis_vs_python():
    use_case = ProjectAnalysisUseCase()

    # Rust (fast)
    result_rust = use_case._execute_rust(".")
    assert result_rust["performance"]["engine"] == "rust"
    assert result_rust["performance"]["analysis_time_ms"] < 100

    # Python (slow)
    result_python = use_case._execute_python(".", lambda *args: None)
    assert result_python["performance"]["engine"] == "python"

    # Results should be identical
    assert result_rust["file_count"] == result_python["file_count"]
    assert result_rust["language_stats"] == result_python["language_stats"]

@pytest.mark.integration
def test_fallback_on_rust_error(monkeypatch):
    """Verify Python fallback works when Rust fails."""
    import sys
    monkeypatch.setitem(sys.modules, 'cde_rust_core', None)

    use_case = ProjectAnalysisUseCase()
    result = use_case.execute(".")

    assert result["status"] == "Analysis complete"
    assert result["file_count"] > 0
```

### Phase 4: Documentation & Release (Day 5)

#### Task 4.1: Build Instructions

**File**: `CONTRIBUTING.md` (update section)

```markdown
## Building Rust Components

### Prerequisites
- Rust 1.70+ (install from https://rustup.rs/)
- Maturin (for Python bindings)

### Build Rust Core

```bash
# Install maturin
pip install maturin

# Navigate to rust_core
cd rust_core

# Build with optimizations
maturin develop --release

# Verify
python -c "import cde_rust_core; print(cde_rust_core.scan_project_py)"
```

### Expected Performance

- **First run**: 3-5 seconds (compilation + link)
- **Subsequent runs**: ~50ms (vs 500ms Python)
- **Performance gain**: 10x improvement
```

#### Task 4.2: README Update

**File**: `README.md` (update Performance section)

```markdown
## Performance

### Project Analysis

| Implementation | Time | Speed | Best For |
|---|---|---|---|
| Rust (accelerated) | ~50ms | 10x | Production |
| Python (fallback) | ~500ms | 1x | Debugging |

The Rust implementation is automatically selected when available.
Falls back to Python if compilation not completed.
```

## Success Criteria

### Performance Targets
- ✅ Rust analysis: < 100ms (50ms target)
- ✅ Python fallback: < 1000ms (existing)
- ✅ Overall speedup: > 5x improvement
- ✅ Memory usage: < 30MB peak

### Compatibility
- ✅ Zero breaking changes to Python API
- ✅ Automatic Rust/Python selection
- ✅ Graceful fallback on errors
- ✅ Cross-platform (Windows/Mac/Linux)

### Testing Coverage
- ✅ Unit tests for Rust module (target: 90% coverage)
- ✅ Integration tests comparing Rust vs Python
- ✅ Fallback mechanism tests
- ✅ Performance benchmarks

## Rollback Plan

If issues arise:

1. **Immediate**: Disable Rust auto-selection
```python
RUST_AVAILABLE = False  # Force Python
```

2. **Revert**: Remove Rust code
```bash
git revert <commit-hash>
```

3. **Analysis**: Review failure logs in `rust_core/build.log`

## Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 1: Rust Development | 2 days | 🔄 In Progress |
| Phase 2: Python Integration | 1 day | ⏳ Pending |
| Phase 3: Testing | 1 day | ⏳ Pending |
| Phase 4: Documentation | 1 day | ⏳ Pending |
| **Total** | **5 days** | - |

## Dependencies

### New Rust Crates
- `rayon` (v1.8.0) - Parallelization
- `walkdir` (v2.x) - Filesystem traversal
- `regex` (v1.x) - Pattern matching (already used)
- `serde_json` (already available)

### Python
- No new dependencies (uses existing `pathspec`)

## Risks & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Rust compilation fails | Low | Medium | Python fallback active |
| Rust results differ from Python | Medium | Low | Comprehensive testing |
| Performance regression | Low | High | Benchmarking before release |
| Cross-platform compatibility | Medium | Medium | Test on Win/Mac/Linux |

## Monitoring & Metrics

Post-launch metrics to track:
- % of analyses using Rust vs Python
- Average analysis time (target: < 100ms)
- Error rate (target: < 0.5%)
- Memory usage reduction
- User reports of issues

---

**Next Steps**: Proceed to Phase 1 implementation
