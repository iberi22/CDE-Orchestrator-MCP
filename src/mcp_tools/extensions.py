"""
VS Code Extension Management Tools.

Tools for installing and managing VS Code extensions for CDE features.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

from fastmcp import Context

from ._base import tool_handler


@tool_handler
async def cde_installMcpExtension(
    ctx: Context,
    extension_name: str = "mcp-status-bar",
    force: bool = False
) -> str:
    """
    Install MCP-related VS Code extension.

    Automatically downloads and installs extensions that enhance MCP tool
    functionality in VS Code (e.g., mcp-status-bar for real-time progress).

    Args:
        ctx: FastMCP context (automatically injected)
        extension_name: Name of extension to install
            - "mcp-status-bar" (default): Real-time progress in status bar
        force: If true, reinstall extension even if already present

    Returns:
        JSON with installation result:
            {
                "status": "success|failed",
                "extension_name": str,
                "path": str (path where extension was installed),
                "message": str (details about installation)
            }

    Examples:
        >>> await cde_installMcpExtension(extension_name="mcp-status-bar")
        {
          "status": "success",
          "extension_name": "mcp-status-bar",
          "path": "mcp-status-bar/",
          "message": "Extension installed and activated in VS Code"
        }

    **When to Use**:
    - Call at the start of a workflow to ensure extension is installed
    - Part of onboarding setup for new environments
    - Before running long-running MCP tools that report progress
    """
    await ctx.info(f"🔧 Installing MCP extension: {extension_name}")

    result = await _install_extension(ctx, extension_name, force)
    return json.dumps(result, indent=2)


async def _install_extension(
    ctx: Context,
    extension_name: str,
    force: bool
) -> Dict[str, Any]:
    """
    Internal implementation of extension installation.

    Handles the actual download and installation logic.
    """
    # Get the project root
    project_root = Path.cwd()
    extension_path = project_root / "mcp-status-bar"

    # Map extension names to their sources
    extension_sources = {
        "mcp-status-bar": {
            "repo_path": "mcp-status-bar",
            "description": "Real-time progress tracking in VS Code status bar"
        }
    }

    if extension_name not in extension_sources:
        return {
            "status": "failed",
            "extension_name": extension_name,
            "message": f"Unknown extension: {extension_name}. Available: {', '.join(extension_sources.keys())}"
        }

    source_info = extension_sources[extension_name]

    # Check if extension already exists
    if extension_path.exists() and not force:
        await ctx.info(f"✅ Extension already exists at {extension_path}")
        
        # Try to get extension status
        return {
            "status": "success",
            "extension_name": extension_name,
            "path": str(extension_path),
            "message": "Extension already installed. Use force=true to reinstall."
        }

    # Installation steps
    try:
        await ctx.info(f"📦 Preparing {extension_name}...")

        # Check if Node.js is available
        try:
            subprocess.run(
                ["node", "--version"],
                capture_output=True,
                check=True,
                timeout=5
            )
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return {
                "status": "failed",
                "extension_name": extension_name,
                "message": "Node.js not found. Please install Node.js to use this extension."
            }

        # Check if npm is available
        try:
            subprocess.run(
                ["npm", "--version"],
                capture_output=True,
                check=True,
                timeout=5
            )
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return {
                "status": "failed",
                "extension_name": extension_name,
                "message": "npm not found. Please install npm to use this extension."
            }

        # Check if extension source directory exists
        if not extension_path.exists():
            return {
                "status": "warning",
                "extension_name": extension_name,
                "path": str(extension_path),
                "message": f"Extension source not found at {extension_path}. Please ensure mcp-status-bar/ directory exists."
            }

        # Install dependencies
        await ctx.info(f"📚 Installing dependencies...")
        result = subprocess.run(
            ["npm", "install"],
            cwd=str(extension_path),
            capture_output=True,
            timeout=60
        )

        if result.returncode != 0:
            return {
                "status": "failed",
                "extension_name": extension_name,
                "message": f"npm install failed: {result.stderr.decode()}"
            }

        # Compile TypeScript
        await ctx.info(f"🔨 Compiling TypeScript...")
        result = subprocess.run(
            ["npm", "run", "compile"],
            cwd=str(extension_path),
            capture_output=True,
            timeout=60
        )

        if result.returncode != 0:
            return {
                "status": "failed",
                "extension_name": extension_name,
                "message": f"TypeScript compilation failed: {result.stderr.decode()}"
            }

        # Package extension
        await ctx.info(f"📦 Packaging extension...")
        result = subprocess.run(
            ["npx", "vsce", "package", "--allow-star-activation"],
            cwd=str(extension_path),
            capture_output=True,
            timeout=60
        )

        if result.returncode != 0:
            return {
                "status": "failed",
                "extension_name": extension_name,
                "message": f"vsce package failed: {result.stderr.decode()}"
            }

        # Find .vsix file
        vsix_files = list(extension_path.glob("*.vsix"))
        if not vsix_files:
            return {
                "status": "failed",
                "extension_name": extension_name,
                "message": "No .vsix file generated"
            }

        vsix_file = vsix_files[-1]  # Latest file
        await ctx.info(f"📦 Generated: {vsix_file.name}")

        # Install extension in VS Code
        await ctx.info(f"🔧 Installing in VS Code...")
        result = subprocess.run(
            ["code", "--install-extension", str(vsix_file), "--force"],
            capture_output=True,
            timeout=60
        )

        if result.returncode != 0:
            return {
                "status": "warning",
                "extension_name": extension_name,
                "path": str(extension_path),
                "message": f"Extension packaged but VS Code installation may need manual verification. VSIX: {vsix_file.name}"
            }

        await ctx.info(f"✅ Extension installed successfully!")

        return {
            "status": "success",
            "extension_name": extension_name,
            "path": str(extension_path),
            "message": f"Extension {extension_name} installed and activated in VS Code"
        }

    except subprocess.TimeoutExpired as e:
        return {
            "status": "failed",
            "extension_name": extension_name,
            "message": f"Installation timeout: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "failed",
            "extension_name": extension_name,
            "message": f"Installation error: {str(e)}"
        }
