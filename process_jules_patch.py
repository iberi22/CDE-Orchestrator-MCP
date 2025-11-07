#!/usr/bin/env python3
"""
Extraer y aplicar cambios de Jules de forma segura.
Maneja renames y cambios de contenido por separado.
"""

import re
import subprocess
from pathlib import Path
from typing import List, Tuple

def parse_patch(patch_content: str) -> Tuple[List[dict], List[dict]]:
    """
    Parsear patch para extraer:
    1. Renames (rename from/to)
    2. Cambios de contenido (diff hunks)
    """
    renames = []
    content_changes = []

    # Dividir por cada diff
    diffs = re.split(r'^diff --git ', patch_content, flags=re.MULTILINE)[1:]

    for diff in diffs:
        lines = diff.split('\n', 20)  # Primeras líneas

        # Buscar rename
        rename_from = None
        rename_to = None
        for line in lines:
            if line.startswith('rename from '):
                rename_from = line.replace('rename from ', '').strip()
            elif line.startswith('rename to '):
                rename_to = line.replace('rename to ', '').strip()

        if rename_from and rename_to:
            renames.append({
                'from': rename_from,
                'to': rename_to
            })
        else:
            # Es un cambio de contenido
            # Extraer ruta del archivo
            for line in lines[:3]:
                if line.startswith('a/'):
                    filepath = line[2:]
                    content_changes.append({
                        'file': filepath,
                        'diff': diff
                    })
                    break

    return renames, content_changes

def apply_renames(renames: List[dict]) -> Tuple[int, int]:
    """Aplicar renames usando git mv"""
    success = 0
    failed = 0

    for rename in renames:
        from_path = Path(rename['from'])
        to_path = Path(rename['to'])

        # Verificar que source existe
        if not from_path.exists():
            print(f"SKIP: {rename['from']} no existe")
            failed += 1
            continue

        # Verificar que destination no existe (caso sensible)
        if to_path.exists() and str(from_path).lower() != str(to_path).lower():
            print(f"SKIP: {rename['to']} ya existe")
            failed += 1
            continue

        # Si los nombres solo difieren en case, git mv debe funcionar
        result = subprocess.run(
            ['git', 'mv', str(from_path), str(to_path)],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"OK: {rename['from']} -> {rename['to']}")
            success += 1
        else:
            print(f"FAIL: {result.stderr.strip()}")
            # Revertir
            subprocess.run(['git', 'reset', str(from_path)], capture_output=True)
            failed += 1

    return success, failed

def main():
    patch_path = Path('semana2-changes.patch')

    if not patch_path.exists():
        print("FAIL: patch no encontrado")
        return

    print("PARSING: Parseando patch de Jules...")
    patch_content = patch_path.read_text('utf-8', errors='ignore')
    renames, content_changes = parse_patch(patch_content)

    print(f"OK: {len(renames)} renames")
    print(f"OK: {len(content_changes)} cambios de contenido")
    print()

    # Aplicar renames
    print("ACTION: Aplicando renames con git mv...")
    print()
    success, failed = apply_renames(renames)
    print()
    print(f"RESULT: {success} exito, {failed} fallos")
    print()

    # Si hay renames exitosos, hacer commit
    if success > 0:
        result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
        print("STATUS: Estado de git despues de renames:")
        print(result.stdout[:500])
        print()

        # Pedirle al usuario confirmación antes de commit
        print("PENDING: Renames listos para commit")
        print("NEXT: git commit -m 'docs(governance): Normalize filenames to lowercase-hyphens'")

if __name__ == '__main__':
    main()
