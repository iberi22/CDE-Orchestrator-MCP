#!/usr/bin/env python3
"""
Extraer cambios de contenido del patch de Jules y aplicarlos.
Enfocado en archivos que existen en el repositorio actual.
"""

import re
import subprocess
from pathlib import Path
from typing import List, Dict

def extract_hunks(diff_text: str) -> List[Dict]:
    """Extraer todos los hunks de un diff"""
    hunks = []
    lines = diff_text.split('\n')

    # Estado del hunk
    current_hunk_lines = []
    hunk_header = None

    for i, line in enumerate(lines):
        if line.startswith('@@'):
            # Nueva línea de hunk
            if current_hunk_lines and hunk_header:
                hunks.append({
                    'header': hunk_header,
                    'lines': current_hunk_lines
                })
            hunk_header = line
            current_hunk_lines = []
        elif hunk_header is not None:
            current_hunk_lines.append(line)

    # Último hunk
    if current_hunk_lines and hunk_header:
        hunks.append({
            'header': hunk_header,
            'lines': current_hunk_lines
        })

    return hunks

def apply_content_changes():
    """Aplicar cambios de contenido del patch"""
    patch_file = Path('semana2-changes.patch')
    patch_content = patch_file.read_text('utf-8', errors='ignore')

    # Dividir por cada diff
    diffs = re.split(r'^diff --git ', patch_content, flags=re.MULTILINE)[1:]

    print(f"FOUND: {len(diffs)} diffs en patch")
    print()

    applied = 0
    failed = 0

    for i, diff in enumerate(diffs, 1):
        lines = diff.split('\n', 50)

        # Buscar ruta
        filepath = None
        is_rename = False

        for line in lines[:10]:
            if line.startswith('--- a/'):
                filepath = line[6:]
            if line.startswith('rename from'):
                is_rename = True
                break

        if not filepath or is_rename:
            continue

        # Verificar que archivo existe
        path_obj = Path(filepath)
        if not path_obj.exists():
            print(f"SKIP ({i}): {filepath} no existe")
            failed += 1
            continue

        # Extraer hunks
        hunks = extract_hunks(diff)
        if not hunks:
            print(f"SKIP ({i}): {filepath} sin hunks")
            failed += 1
            continue

        # Aplicar patch a este archivo específico
        # Crear patch temporal
        temp_patch = f"temp_patch_{i}.patch"
        temp_content = f"diff --git a/{filepath} b/{filepath}\n"

        # Agregar índice
        for line in lines:
            if line.startswith('index '):
                temp_content += line + "\n"
                break

        # Agregar hunks
        temp_content += "--- a/" + filepath + "\n"
        temp_content += "+++ b/" + filepath + "\n"
        for hunk in hunks:
            temp_content += hunk['header'] + "\n"
            temp_content += "\n".join(hunk['lines']) + "\n"

        # Aplicar con git apply
        try:
            Path(temp_patch).write_text(temp_content, encoding='utf-8')
        except:
            # Si hay problemas de encoding, saltar
            print(f"SKIP ({i}): {filepath} encoding error")
            failed += 1
            continue

        result = subprocess.run(
            ['git', 'apply', temp_patch],
            capture_output=True,
            text=True
        )

        if Path(temp_patch).exists():
            Path(temp_patch).unlink()  # Limpiar temp

        if result.returncode == 0:
            print(f"OK ({i}): {filepath}")
            applied += 1
        else:
            print(f"FAIL ({i}): {filepath} - {result.stderr.split(chr(10))[0][:60]}")
            failed += 1

    print()
    print(f"RESULT: {applied} applied, {failed} failed/skipped")

if __name__ == '__main__':
    apply_content_changes()
