---
title: "Phase 2 Optimization Strategy - Rust Project Scanner"
description: "Detailed plan for debugging file count discrepancy and optimizing performance"
type: "design"
status: "active"
created: "2025-11-20"
updated: "2025-11-20"
author: "CDE Team"
llm_summary: |
  Phase 2 focuses on resolving the file count discrepancy (443 vs 387 files) and
  optimizing performance from 1210ms to <100ms target. Includes debugging strategy,
  performance profiling approach, and detailed comparison methodology.
---

# Phase 2: Optimization & Fine-Tuning Strategy

**Status**: Planning
**Priority**: CRITICAL
**Timeline**: 2-3 hours
**Blockers**: File count accuracy (must match Python before release)

## Problem Statement

### Issue 1: File Count Discrepancy

**Observed**:
- Python implementation: **387 files**
- Rust implementation: **443 files**
- **Variance**: +56 files (+14.5%)

**Hypothesis**:
1. `.json` files from `node_modules` not being excluded in Rust
2. Directory path component matching is looser than Python
3. Pattern matching logic misses certain file types
4. Excluded patterns not applied consistently

### Issue 2: Performance Not Optimized

**Observed**:
- Rust implementation: **1210ms** (first run)
- Python implementation: **~500ms**
- **Target**: **<100ms** (10x improvement)

**Hypothesis**:
1. Module loading overhead on first run (~200-300ms)
2. Rayon thread pool initialization
3. Regex compilation for each excluded pattern
4. Fold/reduce aggregation not optimal

## Debugging Strategy

### Phase 2.1: File Count Investigation

#### Step 1: Capture Detailed Logs

Create a debug version that logs all analyzed files:

```python
# In project_analysis_use_case.py - add debug logging
def _execute_rust_debug(self, project_path: str) -> Dict[str, Any]:
    """Debug version with detailed file logging"""
    import json

    excluded_dirs = list(self.EXCLUDED_DIRS)
    excluded_patterns = list(self.EXCLUDED_PATTERNS)

    # Call Rust with debug flag (add later)
    result = cde_rust_core.scan_project_py(
        root_path=str(project_path),
        excluded_dirs=excluded_dirs,
        excluded_patterns=excluded_patterns
    )

    result_dict = json.loads(result)

    # Log all analyzed files
    logger.info(f"Rust found {result_dict['file_count']} files")

    return result_dict

# In project_scanner.rs - add file logging
fn scan_project(...) -> Result<ProjectAnalysisResult> {
    let mut analyzed_files = Vec::new();
    let mut excluded_files = Vec::new();

    // During iteration:
    if should_include_file(path) {
        analyzed_files.push(path.to_string());
    } else {
        excluded_files.push(path.to_string());
    }

    // Export for debugging
}
```

#### Step 2: Compare Results

Create comparison script:

```python
# debug_file_count.py
import json
from pathlib import Path

# Run both implementations
python_result = python_scan(project_path)
rust_result = rust_scan(project_path)

python_files = set(python_result['files'])
rust_files = set(rust_result['files'])

# Find differences
only_in_rust = rust_files - python_files
only_in_python = python_files - rust_files

print(f"Rust only: {len(only_in_rust)}")
print(f"Python only: {len(only_in_python)}")

# Categorize by extension
rust_only_by_ext = {}
for f in only_in_rust:
    ext = Path(f).suffix or 'no-ext'
    rust_only_by_ext[ext] = rust_only_by_ext.get(ext, 0) + 1

print("\nRust detects extra files by type:")
for ext, count in sorted(rust_only_by_ext.items(), key=lambda x: x[1], reverse=True):
    print(f"  {ext}: {count}")
```

#### Step 3: Analyze Exclusion Logic

Check `is_in_excluded_dir()` function:

```rust
fn is_in_excluded_dir(path: &Path, excluded_dirs: &[String]) -> bool {
    // Current: checks path components
    let path_str = path.to_string_lossy();
    for dir in excluded_dirs {
        if path_str.contains(&format!("/{}", dir)) ||
           path_str.contains(&format!("\\{}", dir)) {
            return true;
        }
    }
    false
}

// Potential bug: "node_modules" should match:
// - C:\project\node_modules\jquery\package.json
// - C:\project\src\node_modules\local\file.js
// But NOT: my_node_modules_dir\file.js

// Better approach:
fn is_in_excluded_dir(path: &Path, excluded_dirs: &[String]) -> bool {
    for component in path.components() {
        if let Some(dir_name) = component.as_os_str().to_str() {
            if excluded_dirs.contains(&dir_name.to_string()) {
                return true;
            }
        }
    }
    false
}
```

### Phase 2.2: Performance Profiling

#### Step 1: Measure Component Breakdown

```rust
// In project_scanner.rs - add timing instrumentation
pub fn scan_project(...) -> Result<ProjectAnalysisResult> {
    let start_total = Instant::now();

    let start_walk = Instant::now();
    let dir = WalkDir::new(root_path).into_iter();
    let walk_time = start_walk.elapsed();

    let start_parallel = Instant::now();
    let (files, stats, deps) = dir.filter_map(|ok|)
        .par_bridge()
        .fold(|| /* ... */)
        .reduce(|| /* ... */);
    let parallel_time = start_parallel.elapsed();

    let total_time = start_total.elapsed();

    logger.info!("Timing breakdown:");
    logger.info!("  Walk setup: {}ms", walk_time.as_millis());
    logger.info!("  Parallel processing: {}ms", parallel_time.as_millis());
    logger.info!("  Total: {}ms", total_time.as_millis());
}
```

#### Step 2: Warm-Start Benchmarking

```python
# benchmark_warmstart.py
import time
import cde_rust_core

project_path = "."
excluded_dirs = list(EXCLUDED_DIRS)
excluded_patterns = list(EXCLUDED_PATTERNS)

# Cold start (module just loaded)
start = time.time()
result1 = cde_rust_core.scan_project_py(project_path, excluded_dirs, excluded_patterns)
cold_time = time.time() - start
print(f"Cold start: {cold_time*1000:.1f}ms")

# Warm starts (3 iterations)
for i in range(3):
    start = time.time()
    result = cde_rust_core.scan_project_py(project_path, excluded_dirs, excluded_patterns)
    warm_time = time.time() - start
    print(f"Warm start {i+1}: {warm_time*1000:.1f}ms")

# Analyze results
print(f"\nComparison:")
print(f"  Cold: {cold_time*1000:.1f}ms")
print(f"  Warm avg: {(warm_time*3/3)*1000:.1f}ms")
print(f"  Improvement: {(cold_time/warm_time):.1f}x")
```

#### Step 3: Profile with Flamegraph

```bash
# On Linux/Mac (requires flamegraph):
cd rust_core
cargo install flamegraph
cargo flamegraph --bin project_scanner

# Output: flamegraph.svg showing which functions consume most time
```

### Phase 2.3: Optimization Approaches

#### Option A: Cache Regex Patterns

Instead of compiling regex for each invocation:

```rust
// In lib.rs - use lazy_static or once_cell
use once_cell::sync::Lazy;
use regex::Regex;

static PATTERN_CACHE: Lazy<HashMap<String, Regex>> = Lazy::new(|| {
    HashMap::new()
});

fn get_or_compile_pattern(pattern: &str) -> Result<&Regex> {
    // Check cache, compile if missing
}
```

#### Option B: Optimize Directory Exclusion

```rust
// Pre-compile excluded_dirs into a HashSet for O(1) lookup
fn scan_project_optimized(
    root_path: &str,
    excluded_dirs: Vec<String>,
    excluded_patterns: Vec<String>,
) -> Result<ProjectAnalysisResult> {
    let excluded_set: HashSet<_> = excluded_dirs.into_iter().collect();

    // Use HashSet instead of Vec for faster lookup
}
```

#### Option C: Reduce Allocations

```rust
// Use Vec::with_capacity() to pre-allocate memory
let mut files = Vec::with_capacity(500);  // Expected ~500 files
let mut excluded = Vec::with_capacity(35000);  // Expected ~35k excluded
```

## Phase 2 Execution Plan

### Week 1

1. **Debug Session (1 hour)**
   - [ ] Run comparison script
   - [ ] Identify which file types cause discrepancy
   - [ ] Locate excluded directory logic bug

2. **Fix Discrepancy (1 hour)**
   - [ ] Update `is_in_excluded_dir()` to use component matching
   - [ ] Test against Python results
   - [ ] Verify 387-file result

3. **Performance Profiling (1 hour)**
   - [ ] Add timing instrumentation
   - [ ] Run benchmark script
   - [ ] Identify bottleneck components

### Week 2

4. **Optimization (2 hours)**
   - [ ] Implement caching for regex patterns
   - [ ] Optimize directory lookup (HashSet)
   - [ ] Reduce allocations with pre-sizing

5. **Re-benchmark (1 hour)**
   - [ ] Warm-start performance measurement
   - [ ] Compare before/after
   - [ ] Verify improvement trajectory toward <100ms

### Week 3

6. **Testing & Validation (2 hours)**
   - [ ] Comprehensive test suite
   - [ ] Cross-platform validation
   - [ ] Regression testing

## Success Criteria

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **File Count** | 443 | 387 | 🟡 To Debug |
| **Warm-Start Time** | TBD | <100ms | 🟡 To Measure |
| **Cold-Start Time** | 1210ms | <500ms | 🟡 To Optimize |
| **Memory Usage** | TBD | <50MB | ⏳ To Measure |
| **Test Coverage** | ~30% | >80% | 🟡 To Implement |

## Tools & Techniques

- **Debugging**: `println!` macros, logging crate
- **Profiling**: `cargo flamegraph`, `time` crate
- **Benchmarking**: `criterion` crate (consider for Phase 2.2)
- **Comparison**: Custom Python script comparing outputs
- **Optimization**: `HashSet`, `once_cell`, lazy compilation

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Optimization breaks accuracy | HIGH | Keep fallback to Python available |
| Performance still suboptimal | MEDIUM | Document current performance, plan Phase 3 |
| Cross-platform issues | MEDIUM | Test on Windows/Mac/Linux before release |

## Exit Criteria

✅ Phase 2 Complete when:
1. File count exactly matches Python (387 files)
2. Warm-start performance <200ms (documented)
3. Comprehensive test suite (>80% coverage)
4. No regressions in accuracy
5. Ready for Phase 3 integration

---

**Next Steps**: Execute Phase 2 debugging to understand file count discrepancy

**Estimated Effort**: 6-8 hours
**Team**: CDE Engineering
**Review Date**: After Phase 2 completion
