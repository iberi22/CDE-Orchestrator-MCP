"""
Auto-generate MCP tool filesystem structure.

Runs on server startup to ensure ./servers/cde/ is always up-to-date.
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    import mcp_tools
    from cde_orchestrator.application.tools.generate_filesystem_use_case import (
        GenerateFilesystemUseCase,
    )

    def main() -> None:
        """Generate filesystem structure."""
        print("🔧 Generating MCP tool filesystem structure...")

        use_case = GenerateFilesystemUseCase()
        result = use_case.execute(mcp_tools_module=mcp_tools, output_dir=project_root)

        print(f"✅ Generated {result['total_tools']} tool files")
        print(f"📁 Output: {result['output_dir']}")
        print("\n📄 Files created:")
        for file in result["generated_files"]:
            print(f"   - {file}")

    if __name__ == "__main__":
        main()

except Exception as e:
    print(f"⚠️  Warning: Could not generate filesystem structure: {e}")
    print("   Server will continue without filesystem-based discovery.")
