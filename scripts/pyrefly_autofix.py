#!/usr/bin/env python3
"""
Auto-fix script para errores comunes detectados por Pyrefly.

Corrige automáticamente:
- Imports faltantes
- Type hints básicos
- Inicializaciones incorrectas con None
"""

import re
from pathlib import Path
from typing import Tuple


def fix_none_default_to_optional(file_path: Path) -> int:
    """Corrige parámetros con default=None sin Optional."""
    content = file_path.read_text(encoding="utf-8")
    fixes = 0

    # Patrón: param: Type = None
    pattern = r"(\w+):\s*([A-Z]\w+(?:\[[^\]]+\])?)\s*=\s*None"

    def replace_fn(match):
        nonlocal fixes
        param_name = match.group(1)
        param_type = match.group(2)
        fixes += 1
        return f"{param_name}: Optional[{param_type}] = None"

    new_content = re.sub(pattern, replace_fn, content)

    if fixes > 0:
        # Agregar import Optional si no existe
        if "from typing import" in new_content and "Optional" not in new_content:
            new_content = new_content.replace(
                "from typing import", "from typing import Optional,"
            )
        elif "from typing import" not in new_content:
            # Agregar import al inicio del archivo
            lines = new_content.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    lines.insert(i, "from typing import Optional")
                    break
            new_content = "\n".join(lines)

        file_path.write_text(new_content, encoding="utf-8")
        print(f"✅ {file_path.name}: {fixes} fixes aplicados (None defaults)")

    return fixes


def fix_dict_list_none_defaults(file_path: Path) -> int:
    """Corrige Dict/List = None a Optional[Dict/List] = None."""
    content = file_path.read_text(encoding="utf-8")
    fixes = 0

    patterns = [
        (r"(\w+):\s*(Dict\[.+?\])\s*=\s*None", r"\1: Optional[\2] = None"),
        (r"(\w+):\s*(List\[.+?\])\s*=\s*None", r"\1: Optional[\2] = None"),
        (r":\s*(dict\[.+?\])\s*=\s*None", r": Optional[\1] = None"),
        (r":\s*(list\[.+?\])\s*=\s*None", r": Optional[\1] = None"),
    ]

    new_content = content
    for pattern, replacement in patterns:
        matches = re.findall(pattern, new_content)
        if matches:
            fixes += len(matches)
            new_content = re.sub(pattern, replacement, new_content)

    if fixes > 0:
        # Agregar import Optional
        if "Optional" not in new_content:
            if "from typing import" in new_content:
                new_content = re.sub(
                    r"from typing import (.+)",
                    r"from typing import Optional, \1",
                    new_content,
                    count=1,
                )
            else:
                lines = new_content.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("from typing import") or line.startswith(
                        "import typing"
                    ):
                        lines.insert(i, "from typing import Optional")
                        break
                else:
                    # Agregar después del docstring
                    for i, line in enumerate(lines):
                        if '"""' in line and i > 0:
                            # Buscar el cierre del docstring
                            for j in range(i + 1, len(lines)):
                                if '"""' in lines[j]:
                                    lines.insert(j + 1, "\nfrom typing import Optional")
                                    break
                            break
                new_content = "\n".join(lines)

        file_path.write_text(new_content, encoding="utf-8")
        print(f"✅ {file_path.name}: {fixes} fixes aplicados (Dict/List None)")

    return fixes


def fix_any_type_hint(file_path: Path) -> int:
    """Corrige 'any' lowercase a 'Any'."""
    content = file_path.read_text(encoding="utf-8")

    # Buscar 'any' en type hints (no en strings o comentarios)
    pattern = r"(:\s+Dict\[str,\s+)any(\])"

    if re.search(pattern, content):
        new_content = re.sub(pattern, r"\1Any\2", content)

        # Agregar import Any
        if "from typing import" in new_content and "Any" not in new_content:
            new_content = re.sub(
                r"from typing import (.+)",
                r"from typing import Any, \1",
                new_content,
                count=1,
            )

        file_path.write_text(new_content, encoding="utf-8")
        print(f"✅ {file_path.name}: 'any' → 'Any'")
        return 1

    return 0


def scan_and_fix_directory(directory: Path) -> Tuple[int, int]:
    """Escanea y corrige archivos Python en un directorio."""
    total_files = 0
    total_fixes = 0

    for py_file in directory.rglob("*.py"):
        if any(
            exclude in str(py_file)
            for exclude in [".venv", "venv", "__pycache__", "build", "dist"]
        ):
            continue

        total_files += 1
        fixes = 0
        fixes += fix_none_default_to_optional(py_file)
        fixes += fix_dict_list_none_defaults(py_file)
        fixes += fix_any_type_hint(py_file)

        total_fixes += fixes

    return total_files, total_fixes


def main():
    print("🔧 Pyrefly Auto-Fix Tool")
    print("=" * 50)

    src_dir = Path("src")
    if not src_dir.exists():
        print("❌ src/ directory not found")
        return 1

    print(f"📁 Scanning {src_dir}...")
    files_scanned, total_fixes = scan_and_fix_directory(src_dir)

    print("=" * 50)
    print("✅ Completed!")
    print(f"   Files scanned: {files_scanned}")
    print(f"   Total fixes applied: {total_fixes}")

    if total_fixes > 0:
        print("\n💡 Tip: Run 'pyrefly check src' to verify fixes")
        print("💡 Tip: Run 'git diff' to review changes")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
