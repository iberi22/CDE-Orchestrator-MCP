#!/usr/bin/env python3
"""
Script para limpiar archivos huérfanos del root del proyecto.
Mueve archivos según governance rules y mantiene historia de Git.
"""
import subprocess
import sys
from pathlib import Path

# Definición de movimientos (from_root -> destination)
MOVES = {
    # Documentación de configuración
    "BEDROCK_SETUP.md": "docs/bedrock-configuration.md",
    # Documentación de características completadas (ejecutadas)
    "MCP_STATUS_BAR_COMPLETE.md": "docs/mcp-status-bar-complete-implementation.md",
    "PHASE_2AB_COMPLETE.md": "agent-docs/execution/execution-phase2ab-complete-2025-11-06.md",
    "PHASE_2C_LAUNCH_README.md": "docs/phase-2c-launch-readme.md",
    "PHASE_2C_LAUNCH_SUMMARY.md": "agent-docs/execution/execution-phase2c-launch-summary-2025-11.md",
    "QUICK_START_MVP.md": "docs/quick-start-mvp.md",
    "READY_TO_EXECUTE.md": "agent-docs/execution/execution-ready-2025-11.md",
    "STATUS_BAR_TEST_GUIDE.md": "docs/status-bar-test-guide.md",
    "TESTING_STATUS_BAR.md": "docs/testing-status-bar.md",
}

# Definición de eliminaciones (basura)
DELETES = {
    "doc1.md",  # Archivo de 7 bytes sin contenido
}


def run_git_cmd(cmd: list[str]) -> bool:
    """Ejecutar comando git."""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=".", capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return False
    return True


def main() -> int:
    root = Path(".")

    print("=" * 70)
    print("LIMPIEZA DE ARCHIVOS HUÉRFANOS DEL ROOT")
    print("=" * 70)

    # Verificar cambios no comprometidos
    result = subprocess.run(
        ["git", "status", "--porcelain"], capture_output=True, text=True
    )
    if result.stdout.strip():
        print("\n⚠️  ADVERTENCIA: Hay cambios no comprometidos en Git")
        print("Por favor, haz commit o stash de los cambios antes de continuar")
        print("\nCambios detectados:")
        print(result.stdout)
        return 1

    print("\n✅ Git limpie (sin cambios pendientes)")

    # MOVIMIENTOS
    print("\n" + "=" * 70)
    print("FASE 1: MOVER ARCHIVOS")
    print("=" * 70)

    moved = 0
    for src, dst in MOVES.items():
        src_path = root / src
        dst_path = root / dst

        if not src_path.exists():
            print(f"\n❌ Archivo no encontrado: {src}")
            continue

        # Crear directorio destino si no existe
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"\n📦 {src} → {dst}")
        if run_git_cmd(["git", "mv", src, dst]):
            moved += 1
            print("   ✅ Movido exitosamente")
        else:
            print("   ❌ Error al mover")

    print(f"\n✅ Total movidos: {moved}/{len(MOVES)}")

    # ELIMINACIONES
    print("\n" + "=" * 70)
    print("FASE 2: ELIMINAR ARCHIVOS BASURA")
    print("=" * 70)

    deleted = 0
    for src in DELETES:
        src_path = root / src

        if not src_path.exists():
            print(f"\n❌ Archivo no encontrado: {src}")
            continue

        print(f"\n🗑️  Eliminar: {src}")
        if run_git_cmd(["git", "rm", src]):
            deleted += 1
            print("   ✅ Eliminado exitosamente")
        else:
            print("   ❌ Error al eliminar")

    print(f"\n✅ Total eliminados: {deleted}/{len(DELETES)}")

    # COMMIT
    print("\n" + "=" * 70)
    print("FASE 3: COMMIT DE CAMBIOS")
    print("=" * 70)

    changes = moved + deleted
    if changes == 0:
        print("\n⚠️  No hay cambios que confirmar")
        return 0

    print(f"\n📝 Confirmando {changes} cambios...")

    commit_msg = "refactor(docs): Reorganizar archivos raíz según governance rules\n\n"
    commit_msg += f"- Movidos {moved} archivos a directorios apropiados\n"
    if deleted > 0:
        commit_msg += f"- Eliminados {deleted} archivos basura\n"
    commit_msg += "\nSee: specs/governance/DOCUMENTATION_GOVERNANCE.md"

    if run_git_cmd(["git", "commit", "-m", commit_msg]):
        print("\n✅ Commit realizado exitosamente")
    else:
        print("\n❌ Error al hacer commit")
        return 1

    # RESUMEN
    print("\n" + "=" * 70)
    print("✅ LIMPIEZA COMPLETADA")
    print("=" * 70)
    print(
        f"""
RESUMEN:
  ✅ Archivos movidos:   {moved}
  ✅ Archivos eliminados: {deleted}
  ✅ Cambios confirmados: {changes}

PRÓXIMOS PASOS:
  1. Verificar cambios: git log --oneline -1
  2. Ejecutar validación: python scripts/validation/validate-docs.py --all
  3. Verificar score: Debería haber mejorado
"""
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
