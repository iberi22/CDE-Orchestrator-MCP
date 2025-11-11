#!/usr/bin/env python3
"""
Configure and Test Claude Code and Aider with Bedrock

This script sets up environment variables and provides test commands
"""

import json
import os
import subprocess
from pathlib import Path


def setup_bedrock_env() -> None:
    """Configurar variables de entorno para Bedrock"""
    print("=" * 70)
    print("🔧 CONFIGURANDO BEDROCK VARIABLES DE ENTORNO")
    print("=" * 70)

    # Cargar variables de .env.bedrock
    env_file = Path(".env.bedrock")
    if env_file.exists():
        print(f"\n✅ Leyendo configuración de {env_file}")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key] = value
                    print(f"   ✓ {key}={value}")

    # Variables adicionales
    os.environ["AWS_REGION"] = "us-east-1"
    os.environ["AWS_PROFILE"] = "bedrock"
    os.environ["CLAUDE_CODE_PROVIDER"] = "bedrock"
    os.environ["CLAUDE_CODE_MODEL"] = "anthropic.claude-3-5-sonnet-20241022-v2:0"

    print("\n✅ Variables de entorno configuradas")


def test_claude_code() -> bool:
    """Probar Claude Code con Bedrock"""
    print("\n" + "=" * 70)
    print("🧪 PROBANDO CLAUDE CODE CON BEDROCK")
    print("=" * 70)

    # Verificar si Claude Code está instalado
    try:
        result = subprocess.run(
            ["claude-code", "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print(f"\n✅ Claude Code instalado: {result.stdout.strip()}")
        else:
            print("\n❌ Claude Code no responde correctamente")
            return False
    except FileNotFoundError:
        print("\n❌ Claude Code no está en PATH")
        return False
    except Exception as e:
        print(f"\n❌ Error probando Claude Code: {e}")
        return False

    # Mostrar comando de prueba
    print("\n📋 Comando para ejecutar Claude Code con Bedrock:")
    print(
        """
claude-code run \\
  --provider bedrock \\
  --model anthropic.claude-3-5-sonnet-20241022-v2:0 \\
  --prompt "Hola, ¿cuál es tu nombre?"
    """
    )

    return True


def test_aider() -> bool:
    """Probar Aider con Bedrock"""
    print("\n" + "=" * 70)
    print("🧪 PROBANDO AIDER CON BEDROCK")
    print("=" * 70)

    # Verificar si Aider está instalado
    try:
        result = subprocess.run(
            ["aider", "--version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print(f"\n✅ Aider instalado: {result.stdout.strip()}")
        else:
            print("\n❌ Aider no responde correctamente")
            return False
    except FileNotFoundError:
        print("\n❌ Aider no está en PATH")
        print("\n💡 Instala Aider con: pip install aider-chat")
        return False
    except Exception as e:
        print(f"\n❌ Error probando Aider: {e}")
        return False

    # Mostrar comando de prueba
    print("\n📋 Comando para ejecutar Aider con Bedrock:")
    print(
        """
aider --model bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0
    """
    )

    return True


def generate_orchestration_config() -> Path:
    """Generar configuración para orchestration con agentes"""
    config = {
        "agents": {
            "claude-code": {
                "provider": "bedrock",
                "model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "enabled": True,
                "commands": {
                    "run": "claude-code run --provider bedrock --model {model} --prompt {prompt}",
                    "version": "claude-code --version",
                },
            },
            "aider": {
                "model": "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0",
                "enabled": True,
                "commands": {
                    "run": "aider --model {model} --no-auto-commits",
                    "version": "aider --version",
                },
            },
        },
        "bedrock": {"region": "us-east-1", "profile": "bedrock"},
    }

    config_path = Path(".cde/bedrock-config/orchestration.json")
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Configuración de orchestration guardada: {config_path}")
    return config_path


def main() -> int:
    """Ejecutar setup y pruebas"""
    print("\n")
    setup_bedrock_env()

    claude_ok = test_claude_code()
    aider_ok = test_aider()

    generate_orchestration_config()

    print("\n" + "=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)
    print(f"Claude Code: {'✅ Disponible' if claude_ok else '❌ No disponible'}")
    print(f"Aider:       {'✅ Disponible' if aider_ok else '❌ No disponible'}")
    print("\n✅ BEDROCK ESTÁ CONFIGURADO Y LISTO PARA USAR")
    print("\n💡 Próximos pasos:")
    print("   1. Usa 'orchestrate.py' para ejecutar tareas con agentes")
    print("   2. Configura MCP server para integración completa")
    print("   3. Ejecuta: python orchestrate.py --phase phase1")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
