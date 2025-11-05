"""
Helper script to setup sys.path for forge imports.

Usage:
    from scripts.setup_forge_path import setup_forge_path
    setup_forge_path()

    # Now you can import from forge
    from forge.generator import BasicAppsRegPackage
"""

import sys
from pathlib import Path


def setup_forge_path():
    """Add forge and its submodules to sys.path for imports."""

    # Get repository root (parent of scripts directory)
    repo_root = Path(__file__).parent.parent

    # Add forge to path
    forge_path = repo_root / "forge"
    if forge_path.exists():
        sys.path.insert(0, str(forge_path))
    else:
        raise FileNotFoundError(
            f"Forge submodule not found at {forge_path}. "
            "Run 'git submodule update --init --recursive' first."
        )

    # Add forge's lib dependencies to path
    libs_path = forge_path / "libs"
    if libs_path.exists():
        for lib_dir in libs_path.iterdir():
            if lib_dir.is_dir() and not lib_dir.name.startswith('.'):
                sys.path.insert(0, str(lib_dir))

    return forge_path


def verify_forge_imports():
    """Verify that forge can be imported successfully."""
    try:
        from forge.generator import BasicAppsRegPackage
        print("✅ Forge imports working correctly")
        return True
    except ImportError as e:
        print(f"❌ Forge import failed: {e}")
        return False


if __name__ == "__main__":
    # When run as a script, setup path and verify
    print("Setting up forge path...")
    forge_path = setup_forge_path()
    print(f"✅ Forge path: {forge_path}")

    print("\nVerifying forge imports...")
    verify_forge_imports()
