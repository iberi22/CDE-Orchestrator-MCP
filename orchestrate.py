#!/usr/bin/env python3
"""
Meta-Orchestration Launcher

Ejecuta el orquestador de agentes CLI para completar el CDE Orchestrator al 100%.

Uso:
    python orchestrate.py                    # Ejecutar desde Fase 1
    python orchestrate.py --phase phase2     # Ejecutar desde Fase 2
    python orchestrate.py --phase phase1 --agents claude-code,aider  # Agentes específicos
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import List, Optional

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

from src.mcp_tools.full_implementation import FullImplementationOrchestrator


async def main():
    parser = argparse.ArgumentParser(
        description="Meta-orchestration launcher para completar CDE Orchestrator al 100%"
    )

    parser.add_argument(
        "--phase",
        default="phase1",
        choices=["phase1", "phase2", "phase3", "phase4"],
        help="Fase desde la cual comenzar (default: phase1)",
    )

    parser.add_argument(
        "--agents",
        default=None,
        help="Agentes específicos a usar (comma-separated): claude-code,aider,codex",
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Simular sin ejecutar realmente"
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Mostrar logs detallados"
    )

    args = parser.parse_args()

    print("=" * 80)
    print("🚀 CDE ORCHESTRATOR - META-ORCHESTRATION LAUNCHER")
    print("=" * 80)
    print()
    print("📋 Configuración:")
    print(f"   Fase Inicio: {args.phase}")
    print(f"   Agentes: {args.agents or 'AUTO (selección inteligente)'}")
    print(f"   Modo: {'DRY-RUN' if args.dry_run else 'EJECUCIÓN REAL'}")
    print()

    # Crear orquestrador
    project_path = Path(__file__).parent
    orchestrator = FullImplementationOrchestrator(str(project_path))

    # Validar agentes si se especificaron
    agent_list: Optional[List[str]] = None
    if args.agents:
        agent_list = [a.strip() for a in args.agents.split(",")]
        print(f"✓ Agentes solicitados: {agent_list}")

    # Ejecutar
    print("\n" + "=" * 80)
    print("📊 INICIANDO ORQUESTACIÓN...")
    print("=" * 80 + "\n")

    try:
        result = await orchestrator.orchestrate_all_phases(
            start_phase=args.phase, dry_run=args.dry_run, preferred_agents=agent_list
        )

        # Formatear resultado
        print("\n" + "=" * 80)
        print("✅ ORQUESTACIÓN COMPLETADA")
        print("=" * 80 + "\n")

        if isinstance(result, str):
            result_dict = json.loads(result)
        else:
            result_dict = result

        # Mostrar resumen
        percentage = 0  # Inicializar variable
        if "completion" in result_dict:
            completion = result_dict["completion"]
            total = completion.get("total_tasks", 0)
            completed = completion.get("completed_tasks", 0)
            percentage = completion.get("completion_percentage", 0)

            print("📈 Progreso Actual:")
            print(f"   Tareas Completadas: {completed}/{total} ({percentage:.1f}%)")

            if "phases_status" in completion:
                print("\n📊 Por Fase:")
                for phase_id, phase_status in completion["phases_status"].items():
                    p_total = phase_status.get("total", 0)
                    p_completed = phase_status.get("completed", 0)
                    p_hours = phase_status.get("estimated_hours", 0)
                    status_symbol = "✅" if p_completed == p_total else "🔄"
                    print(
                        f"   {status_symbol} {phase_id}: {p_completed}/{p_total} ({p_hours}h)"
                    )
        else:
            # Si no hay completion, mostrar estructura básica del resultado
            print("📋 Resultado de la orquestación:")
            for key, value in result_dict.items():
                if isinstance(value, dict):
                    print(f"   {key}: {len(value)} items")
                else:
                    print(f"   {key}: {value}")

        # Mostrar log de ejecución
        if "execution_log" in result_dict:
            print(
                f"\n📋 Log de Ejecución ({len(result_dict['execution_log'])} eventos):"
            )
            for i, log_entry in enumerate(result_dict["execution_log"][-10:], 1):
                task_id = log_entry.get("task_id", "?")
                agent = log_entry.get("agent", "?")
                status = log_entry.get("status", "?")
                status_symbol = (
                    "✅"
                    if status == "success"
                    else "❌" if status == "failed" else "⏳"
                )
                duration = log_entry.get("duration", 0)
                print(f"   {status_symbol} [{agent}] {task_id} ({duration:.1f}s)")

        # Próximos pasos
        if percentage < 100:
            print("\n🔗 Próximos Pasos:")
            print("   Para continuar desde donde paró:")

            next_phase = None
            if "phases_status" in result_dict.get("completion", {}):
                for phase_id, status in result_dict["completion"][
                    "phases_status"
                ].items():
                    if status.get("completed", 0) < status.get("total", 0):
                        next_phase = phase_id
                        break

            if next_phase:
                print(f"   $ python orchestrate.py --phase {next_phase}")
            else:
                print(
                    f"   $ python orchestrate.py --phase phase{min(4, int(args.phase[-1]) + 1)}"
                )

        print("\n💾 Resultado completo guardado en: orchestration_result.json")
        with open("orchestration_result.json", "w") as f:
            json.dump(result_dict, f, indent=2)

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  ORQUESTACIÓN INTERRUMPIDA POR USUARIO")
        return 1
    except Exception as e:
        print("\n\n❌ ERROR EN ORQUESTACIÓN:")
        print(f"   {str(e)}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
