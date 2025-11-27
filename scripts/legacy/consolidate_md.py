import os

files_plan = [
    "RESUMEN_ESTADO_PROYECTO.md",
    "IMPLEMENTATION_STATUS_GIT_ANALYZER.md",
    "PHASE2_COMPLETE.md",
    "SOLUCION-TOOL-NOT-FOUND.md",
    "IMPLEMENTACION-GIT-ANALYZER.md",
    "GEMINI.md",
    "QUICKSTART_LOCAL.md"
]

files_tasks = [
    "BUGFIX_REPORT.md",
    "LOCAL_VALIDATION_REPORT.md"
]

def consolidate(files, output):
    with open(output, "w") as outfile:
        outfile.write("# Consolidated Legacy Files\n\n")
        for f in files:
            if os.path.exists(f):
                outfile.write(f"\n\n# Source: {f}\n\n")
                outfile.write(open(f).read())
                outfile.write("\n---\n")
                print(f"Consolidated {f}")

consolidate(files_plan, "specs/legacy-migration/consolidated_plan.md")
consolidate(files_tasks, "specs/legacy-migration/consolidated_tasks.md")
