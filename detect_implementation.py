#!/usr/bin/env python3
"""
Verificar qué implementación (Rust o Python) se está usando.
"""

from __future__ import annotations

import inspect
import sys
import time
from pathlib import Path
from typing import Any

import src.cde_orchestrator.application.documentation.scan_documentation_use_case as scan_module
from src.cde_orchestrator.application.documentation.scan_documentation_use_case import (
    ScanDocumentationUseCase,
)

# mypy: disable-error-code="misc, assignment"

# Agregar trace para ver cuál se ejecuta
original_print = print


def trace_print(*args: Any, **kwargs: Any) -> None:
    frame = inspect.currentframe()
    if frame and frame.f_back:
        f_back = frame.f_back
        filename = f_back.f_code.co_filename
        lineno = f_back.f_lineno
        if "scan_documentation" in filename or "rust" in filename.lower():
            original_print(
                f"[TRACE {filename.split(chr(92))[-1]}:{lineno}]", *args, **kwargs
            )
        else:
            original_print(*args, **kwargs)


def traced_rust(self: Any, project_path: str) -> Any:  # type: ignore[misc]
    print("🔧 [TRACE] Ejecutando: _scan_with_rust")
    try:
        original_scan_rust = scan_module.ScanDocumentationUseCase._scan_with_rust
        result = original_scan_rust(self, project_path)
        print("✅ [TRACE] _scan_with_rust completó exitosamente")
        return result
    except Exception as e:
        print(f"❌ [TRACE] _scan_with_rust falló: {e}")
        raise


def traced_python(self: Any, project_path: str) -> Any:  # type: ignore[misc]
    print("⚠️  [TRACE] Ejecutando: _scan_with_python (FALLBACK)")
    original_scan_python = scan_module.ScanDocumentationUseCase._scan_with_python
    return original_scan_python(self, project_path)


if __name__ == "__main__":
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent / "src"))

    # Test: Ejecutar scan y detectar camino
    print("=" * 60)
    print("🔍 Detectando qué implementación se usa (Rust vs Python)")
    print("=" * 60)

    use_case = ScanDocumentationUseCase()

    # Patch para tracing
    original_scan_rust = scan_module.ScanDocumentationUseCase._scan_with_rust
    original_scan_python = scan_module.ScanDocumentationUseCase._scan_with_python

    setattr(scan_module.ScanDocumentationUseCase, "_scan_with_rust", traced_rust)
    setattr(scan_module.ScanDocumentationUseCase, "_scan_with_python", traced_python)

    # Ejecutar
    print("\nIniciando escaneo...\n")
    start = time.time()
    result = use_case.execute(".")
    elapsed = time.time() - start

    print(f"\n✅ Escaneo completado en {elapsed:.3f} segundos")
    print(f"✅ Total documentos: {result['total_docs']}")
    print(
        f"\nImplementación detectada: {'RUST CORE' if elapsed < 1.5 else 'Python (posible fallback)'}"
    )
