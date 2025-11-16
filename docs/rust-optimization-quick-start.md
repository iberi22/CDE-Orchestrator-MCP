---
title: "Rust Optimizations - Quick Start Guide"
description: "How to use and deploy Rust-accelerated CDE Orchestrator MCP"
type: "guide"
status: "active"
created: "2025-11-16"
updated: "2025-11-16"
author: "GitHub Copilot"
---

# Rust Optimizations - Quick Start Guide

## 🚀 For Developers (Con Cargo)

### Initial Setup

```bash
# 1. Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 2. Install maturin
pip install maturin

# 3. Build Rust module
cd rust_core
maturin develop --release

# ✅ Done! Rust module available
```

### Verify Installation

```python
import cde_rust_core

print(cde_rust_core.scan_documentation_py("."))
# ✅ Works! Returns JSON with scanned documents
```

### Rebuild After Changes

```bash
cd rust_core
maturin develop --release
```

---

## 📦 For Users (Sin Cargo)

### Installation from Wheel

```bash
# Copy the wheel file to target machine
scp dist/cde_rust_core-0.2.0-cp314-cp314-win_amd64.whl user@server:~/

# On target machine (NO Cargo needed):
pip install cde_rust_core-0.2.0-cp314-cp314-win_amd64.whl

# ✅ Done! Works immediately
```

### Verify Installation

```python
from cde_orchestrator.rust_utils import RUST_AVAILABLE

if RUST_AVAILABLE:
    print("✅ Rust optimizations available")
else:
    print("⚠️ Using Python fallback")
```

---

## 🎯 Usage Examples

### 1. Scan Documentation

```python
from cde_orchestrator.rust_utils import scan_documentation

docs = scan_documentation("./specs")

for doc in docs:
    print(f"{doc.path}: {doc.word_count} words, {len(doc.links)} links")
    if doc.has_frontmatter:
        print(f"  Title: {doc.metadata.title}")
```

### 2. Analyze Quality

```python
from cde_orchestrator.rust_utils import analyze_quality

report = analyze_quality(".")

print(f"Quality Score: {report.quality_score}/100")
print(f"Issues: {len(report.issues)}")

for issue in report.issues:
    print(f"  {issue}")
```

### 3. Validate Workflows

```python
from cde_orchestrator.rust_utils import validate_workflows

report = validate_workflows("./.cde")

if report.valid:
    print(f"✅ All {report.total_files} workflows valid")
else:
    print(f"❌ {report.invalid_files} workflows have issues")
    for issue in report.issues:
        print(f"  {issue.severity}: {issue.message}")
```

---

## 🔧 Building Wheels for Distribution

### Single Platform

```bash
cd rust_core
maturin build --release

# Output: dist/cde_rust_core-0.2.0-cp314-cp314-win_amd64.whl
```

### Multi-Platform (via Docker)

```bash
# Linux
docker run --rm -v $(pwd):/io ghcr.io/pyo3/maturin build --release

# macOS (on Mac)
maturin build --release

# Windows (on Windows)
maturin build --release
```

### Upload to PyPI

```bash
maturin publish
```

---

## ⚡ Performance Tips

### 1. Use for Large Projects

Rust optimizations shine with **100+ documents**:

- < 10 docs: Python is fine (~0.1s)
- 10-100 docs: Rust 2-3x faster
- 100-1000 docs: Rust 6-8x faster ⭐
- 1000+ docs: Rust 8-10x faster ⭐⭐⭐

### 2. Batch Operations

```python
# ❌ BAD: Multiple small scans
for dir in ["specs", "docs", "agent-docs"]:
    scan_documentation(dir)

# ✅ GOOD: Single large scan
scan_documentation(".")  # Scans all subdirectories
```

### 3. Cache Results

```python
# Scan once, reuse multiple times
docs = scan_documentation(".")

# Use for different analyses
with_metadata = [d for d in docs if d.has_frontmatter]
by_type = {}
for doc in docs:
    if doc.metadata:
        by_type.setdefault(doc.metadata.doc_type, []).append(doc)
```

---

## 🐛 Troubleshooting

### "Rust module not available"

```python
from cde_orchestrator.rust_utils import RUST_AVAILABLE

if not RUST_AVAILABLE:
    # Option 1: Install wheel
    # pip install cde_rust_core-0.2.0-*.whl

    # Option 2: Build from source
    # cd rust_core && maturin develop --release

    # Fallback: Uses Python (slower but works)
    pass
```

### "Failed to read X files"

These warnings are normal - permission errors on system directories:

```
⚠️ Warning: Failed to read 5140 files
  - .git/objects: Acceso denegado
  - node_modules: Acceso denegado
```

**Solution**: Exclude directories you don't need:

```python
# Rust automatically skips: .git, .venv, node_modules, __pycache__
```

### Compilation Errors (Python 3.14)

```bash
# Set forward compatibility flag
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

# Or in PowerShell:
$env:PYO3_USE_ABI3_FORWARD_COMPATIBILITY = "1"

maturin develop --release
```

---

## 📊 Benchmarking

### Run Performance Tests

```bash
# Test all optimizations
python test_all_rust_optimizations.py

# Test specific function
python test_rust_direct.py

# Run Criterion benchmarks (Rust)
cd rust_core
cargo bench
```

### Expected Results

```
scan_documentation: ~1.1s for 911 documents
analyze_quality: ~1.0s for quality analysis
validate_workflows: ~0.001s for 6 YAML files

Total: ~2.2s vs ~15s Python (6-8x faster)
```

---

## 🎓 API Reference

### RustDocumentationScanner

```python
from cde_orchestrator.rust_utils import RustDocumentationScanner

scanner = RustDocumentationScanner()

# Check availability
if scanner.is_available:
    # Methods
    docs = scanner.scan_documentation(path)
    report = scanner.analyze_quality(path)
    validation = scanner.validate_workflows(path)
```

### Data Classes

```python
from cde_orchestrator.rust_utils import (
    Document,              # Scanned document with metadata
    QualityReport,         # Quality analysis results
    WorkflowValidationReport,  # Workflow validation results
    YamlFrontmatter,       # Parsed YAML metadata
    LinkInfo,              # Link information
    WorkflowValidationIssue,  # Validation issue
)
```

---

## 🔐 Security Notes

### File Permissions

Rust scanner respects file permissions:

- ✅ Skips files it can't read
- ✅ Continues processing other files
- ✅ Logs warnings but doesn't fail

### Path Validation

```python
# Always validates paths before processing
try:
    docs = scan_documentation("./specs")
except ValueError as e:
    print(f"Invalid path: {e}")
```

---

## 📝 Next Steps

1. **Deploy**: Copy wheel to production servers
2. **Monitor**: Check performance improvements
3. **Optimize**: Add more Rust functions if needed
4. **Maintain**: Rebuild wheels when dependencies change

**Questions?** Check `agent-docs/execution/EXECUTIONS-rust-optimization-complete-2025-11-16.md`
