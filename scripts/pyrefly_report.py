#!/usr/bin/env python3
"""
Pyrefly Type Checking Report Generator

Ejecuta Pyrefly en el proyecto y genera un reporte detallado de errores de tipos.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def run_pyrefly() -> str:
    """Ejecuta Pyrefly y captura la salida."""
    try:
        result = subprocess.run(
            ["pyrefly", "check", "src", "--json"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        print("⏱️  Pyrefly timeout after 60 seconds", file=sys.stderr)
        return ""
    except FileNotFoundError:
        print(
            "❌ Pyrefly not found. Install with: pip install pyrefly", file=sys.stderr
        )
        sys.exit(1)


def categorize_errors(output: str) -> Dict[str, List[Dict[str, str]]]:
    """Categoriza errores por tipo."""
    categories: Dict[str, List[Dict[str, str]]] = {
        "missing-attribute": [],
        "missing-import": [],
        "bad-assignment": [],
        "bad-argument-type": [],
        "not-iterable": [],
        "bad-index": [],
        "unbound-name": [],
        "deprecated": [],
        "other": [],
    }

    lines = output.split("\n")

    for line in lines:
        if "ERROR" in line or "WARN" in line:
            # Extraer tipo de error entre corchetes
            if "[" in line and "]" in line:
                error_type = line.split("[")[-1].split("]")[0]
                file_path = (
                    line.split("-->")[-1].strip() if "-->" in line else "unknown"
                )

                error_info = {
                    "type": error_type,
                    "message": (
                        line.split("]")[0].split("ERROR")[-1].strip()
                        if "ERROR" in line
                        else line.split("]")[0].split("WARN")[-1].strip()
                    ),
                    "file": file_path,
                    "severity": "ERROR" if "ERROR" in line else "WARN",
                }

                if error_type in categories:
                    categories[error_type].append(error_info)
                else:
                    categories["other"].append(error_info)

    return categories


def generate_markdown_report(categories: Dict[str, List[Dict[str, str]]]) -> str:
    """Genera reporte en formato Markdown."""
    total_errors = sum(len(errors) for errors in categories.values())

    report = f"""---
title: "Pyrefly Type Checking Report"
description: "Análisis de tipos estáticos del proyecto CDE Orchestrator MCP"
type: "execution"
status: "active"
created: "{datetime.now().strftime('%Y-%m-%d')}"
updated: "{datetime.now().strftime('%Y-%m-%d')}"
author: "Pyrefly Type Checker"
---

# Pyrefly Type Checking Report

**Fecha**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total de errores**: {total_errors}

## 📊 Resumen por Categoría

"""

    # Tabla resumen
    report += "| Categoría | Cantidad | Criticidad |\n"
    report += "|-----------|----------|------------|\n"

    critical_categories = ["missing-attribute", "missing-import", "bad-assignment"]

    for category, errors in sorted(
        categories.items(), key=lambda x: len(x[1]), reverse=True
    ):
        if errors:
            criticality = "🔴 Alta" if category in critical_categories else "🟡 Media"
            report += f"| `{category}` | {len(errors)} | {criticality} |\n"

    report += "\n## 🔍 Detalles por Categoría\n\n"

    # Detalles por categoría
    for category, errors in sorted(
        categories.items(), key=lambda x: len(x[1]), reverse=True
    ):
        if errors:
            report += f"### {category} ({len(errors)} errores)\n\n"

            # Agrupar por archivo
            files_map = {}
            for error in errors:
                file = (
                    error["file"].split(":")[0]
                    if ":" in error["file"]
                    else error["file"]
                )
                if file not in files_map:
                    files_map[file] = []
                files_map[file].append(error)

            for file, file_errors in sorted(files_map.items()):
                report += f"#### `{file}`\n\n"
                for error in file_errors[:3]:  # Mostrar máximo 3 por archivo
                    report += f"- **{error['severity']}**: {error['message']}\n"
                    if error["file"] != "unknown":
                        report += f"  - Ubicación: `{error['file']}`\n"
                if len(file_errors) > 3:
                    report += f"\n  *...y {len(file_errors) - 3} errores más en este archivo*\n"
                report += "\n"

    # Recomendaciones
    report += """
## 💡 Recomendaciones

### Prioridad Alta 🔴

1. **Missing Attributes**: Revisar accesos a atributos que pueden ser `None`
   - Usar `Optional[]` type hints
   - Agregar validaciones `if obj is not None:`
   - Usar `getattr()` con valores por defecto

2. **Missing Imports**: Agregar dependencias faltantes
   - `julius_agent_sdk`: Verificar instalación
   - `plyer`: Para notificaciones del sistema
   - `websocket`: Para comunicación en tiempo real

3. **Bad Assignments**: Corregir tipos incompatibles
   - Revisar inicializaciones con `None`
   - Usar `Union[]` o `Optional[]` cuando sea necesario

### Prioridad Media 🟡

4. **Deprecated Warnings**: Actualizar código obsoleto
   - Reemplazar `pydantic.BaseModel.dict()` por `model_dump()`
   - Actualizar a APIs modernas

5. **Type Inference**: Mejorar hints de tipos
   - Agregar type hints explícitos en funciones
   - Usar `TypedDict` para dictionaries estructurados

## 🛠️ Próximos Pasos

1. **Fase 1**: Corregir errores críticos (missing-attribute, missing-import)
2. **Fase 2**: Resolver bad-assignments y type incompatibilities
3. **Fase 3**: Actualizar código deprecated
4. **Fase 4**: Mejorar type hints generales
5. **Fase 5**: Integrar Pyrefly en CI/CD

## 📝 Notas

- Este reporte fue generado automáticamente por Pyrefly
- Pyrefly es un type checker de Meta/Facebook escrito en Rust
- Más rápido que mypy con inferencia de tipos flow-sensitive
- Configuración: `pyrefly.toml` y `pyproject.toml`

"""

    return report


def main():
    print("🔍 Ejecutando Pyrefly type checker...")
    output = run_pyrefly()

    if not output:
        print("⚠️  No se pudo obtener salida de Pyrefly, generando reporte básico...")
        output = subprocess.run(
            ["pyrefly", "check", "src"], capture_output=True, text=True
        ).stdout

    print("📊 Categorizando errores...")
    categories = categorize_errors(output)

    print("📝 Generando reporte Markdown...")
    report = generate_markdown_report(categories)

    # Guardar reporte
    report_dir = Path("agent-docs/execution")
    report_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    report_file = report_dir / f"EXECUTIONS-pyrefly-type-check-{timestamp}.md"

    report_file.write_text(report, encoding="utf-8")

    print(f"✅ Reporte generado: {report_file}")
    print(
        f"📈 Total de errores encontrados: {sum(len(e) for e in categories.values())}"
    )

    # Mostrar top 3 categorías
    print("\n🔝 Top 3 categorías de errores:")
    for category, errors in sorted(
        categories.items(), key=lambda x: len(x[1]), reverse=True
    )[:3]:
        if errors:
            print(f"   - {category}: {len(errors)} errores")


if __name__ == "__main__":
    main()
