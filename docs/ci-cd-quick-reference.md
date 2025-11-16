# CI/CD Quick Reference

## ✅ Build Status

**Latest Run**: [#19403109507](https://github.com/iberi22/CDE-Orchestrator-MCP/actions/runs/19403109507)
**Status**: ✅ SUCCESS (13/13 artifacts)
**Build Time**: ~4 minutes
**Coverage**: Windows/Linux/macOS × Python 3.11-3.14

---

## 🚀 Quick Commands

### Check Build Status
```bash
gh run list --workflow="Build and Publish Wheels" --limit 3
```

### Download Latest Wheels
```bash
gh run download 19403109507
```

### View Artifacts
```bash
gh api /repos/iberi22/CDE-Orchestrator-MCP/actions/runs/19403109507/artifacts \
  --jq '.artifacts[] | .name'
```

### Watch Current Build
```bash
gh run watch --exit-status
```

---

## 📦 Installation Options

### From GitHub Artifacts
```bash
# Download wheel
gh run download 19403109507 --name wheels-windows-latest-py3.14

# Install
pip install cde_rust_core-0.2.0-cp314-cp314-win_amd64.whl
```

### From PyPI (Future)
```bash
pip install cde-rust-core
```

### From Source
```bash
cd rust_core
maturin build --release
pip install ../target/wheels/cde_rust_core-*.whl
```

---

## 🔧 Build Matrix

| Platform | Python Versions | Build Time |
|----------|----------------|------------|
| Windows | 3.11, 3.12, 3.13, 3.14 | 2-4 min |
| Ubuntu | 3.11, 3.12, 3.13, 3.14 | 40-50 sec |
| macOS | 3.11, 3.12, 3.13, 3.14 | 50-80 sec |

**Total Artifacts**: 13 (12 wheels + 1 sdist)

---

## ⚙️ Workflow Triggers

- ✅ Push to `main` (paths: `rust_core/**`, `pyproject.toml`)
- ✅ Pull requests (same paths)
- ✅ Manual dispatch
- ✅ Release published (for PyPI)

---

## 🐛 Common Issues

### Build Fails on Python 3.14
Set `PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1` environment variable.

### Windows Tests Fail with Unicode Error
Remove emojis from test output (use plain ASCII text).

### sdist Build Fails
Use `--manifest-path rust_core/Cargo.toml` from project root.

---

## 📊 Performance

**Best Times**:
- Ubuntu Linux: 38 seconds
- macOS: 47 seconds
- Windows: 1m55s

**Average Pipeline**: 4 minutes (parallel execution)

---

## 📚 Documentation

- Complete Guide: `docs/ci-cd-setup-complete.md`
- Rust Quick Start: `docs/rust-optimization-quick-start.md`
- Workflow File: `.github/workflows/build-wheels.yml`

---

**Last Updated**: 2025-11-16
**Maintained By**: CDE Orchestrator MCP Team
