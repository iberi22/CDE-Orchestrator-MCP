#!/usr/bin/env python3
"""
Auto-download and install optimized Rust wheels from GitHub releases.

This tool automatically detects your platform and Python version,
downloads the appropriate pre-compiled Rust wheel, and installs it.
"""

import json
import platform
import subprocess
import sys
import urllib.request
from pathlib import Path


def get_platform_tag() -> str:
    """Get the platform tag for wheel selection."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        return "win_amd64"
    elif system == "linux":
        return "manylinux_2_17_x86_64.manylinux2014_x86_64"
    elif system == "darwin":
        if machine == "arm64":
            return "macosx_11_0_arm64"
        else:
            return "macosx_10_12_x86_64"
    else:
        raise ValueError(f"Unsupported platform: {system}")


def get_python_tag() -> str:
    """Get the Python version tag (e.g., cp314)."""
    version_info = sys.version_info
    return f"cp{version_info.major}{version_info.minor}"


def download_rust_wheel(repo: str = "iberi22/CDE-Orchestrator-MCP", tag: str = "latest") -> bool:
    """Download the appropriate Rust wheel from GitHub releases."""

    platform_tag = get_platform_tag()
    python_tag = get_python_tag()

    print(f"🔍 Detecting platform: {platform_tag}")
    print(f"🐍 Python version: {python_tag}")

    # Get release info from GitHub API
    api_url = f"https://api.github.com/repos/{repo}/releases/tags/{tag}"
    print(f"📡 Fetching release info from: {api_url}")

    try:
        with urllib.request.urlopen(api_url) as response:
            release_data = json.loads(response.read())
    except Exception as e:
        print(f"❌ Failed to fetch release info: {e}")
        print("\n💡 Tip: Make sure the 'latest' release exists in GitHub")
        return False

    # Find matching wheel
    wheel_url = None
    wheel_name = None

    for asset in release_data.get("assets", []):
        name = asset["name"]
        if name.endswith(".whl") and python_tag in name and platform_tag in name:
            wheel_url = asset["browser_download_url"]
            wheel_name = name
            break

    if not wheel_url:
        print(f"❌ No wheel found for {python_tag} on {platform_tag}")
        print("\n📦 Available wheels:")
        for asset in release_data.get("assets", []):
            if asset["name"].endswith(".whl"):
                print(f"  - {asset['name']}")
        return False

    print(f"✅ Found wheel: {wheel_name}")
    print(f"📥 Downloading from: {wheel_url}")

    # Download wheel
    temp_dir = Path("temp-wheels")
    temp_dir.mkdir(exist_ok=True)
    wheel_path = temp_dir / wheel_name

    try:
        urllib.request.urlretrieve(wheel_url, wheel_path)
        print(f"✅ Downloaded to: {wheel_path}")
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return False

    # Install wheel
    print("🔧 Installing wheel...")
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--force-reinstall",
                str(wheel_path),
            ],
            check=True,
        )
        print("✅ Rust module installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        return False


def verify_installation() -> bool:
    """Verify that the Rust module is working."""
    print("\n🧪 Verifying installation...")
    try:
        import cde_rust_core

        print("✅ cde_rust_core module loaded successfully")
        print(
            f"📦 Available functions: {[f for f in dir(cde_rust_core) if not f.startswith('_')]}"
        )
        return True
    except ImportError as e:
        print(f"❌ Failed to import cde_rust_core: {e}")
        return False


def main() -> None:
    """Main entry point."""
    print("🚀 CDE Orchestrator - Rust Wheel Auto-Installer\n")

    # Check if already installed
    try:
        import cde_rust_core

        print("ℹ️  Rust module already installed")
        response = input("Do you want to reinstall? (y/N): ")
        if response.lower() != "y":
            print("✅ Using existing installation")
            return
    except ImportError:
        pass

    # Download and install
    if download_rust_wheel():
        verify_installation()
    else:
        print("\n❌ Installation failed")
        print("\n💡 Fallback: Compile from source")
        print("   cd rust_core && maturin develop --release")
        sys.exit(1)


if __name__ == "__main__":
    main()
