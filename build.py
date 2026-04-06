"""
OpenFixture Build System

Builds a KiCAD ActionPlugin package for OpenFixture that can be installed
via KiCAD's Plugin and Content Manager or deployed to local KiCAD installation.

Usage:
    python build.py              # build package directory + ZIP
    python build.py --deploy     # build + install to local KiCAD
    python build.py --zip        # build ZIP only (no deploy)
    python build.py --clean      # remove build directory

Outputs (in build/):
    com_github_RolandWa_openfixture/    Package directory (ready to copy)
    OpenFixture-2.0.0.zip               ZIP for manual install or distribution

ZIP installation:
    1. Open KiCAD → Plugin and Content Manager
    2. "Install from File…" → select OpenFixture-<version>.zip
    — OR —
    Extract ZIP into:
      Windows:  Documents/KiCad/9.0/3rdparty/plugins/
      macOS:    ~/Documents/KiCad/9.0/3rdparty/plugins/
      Linux:    ~/.local/share/KiCad/9.0/3rdparty/plugins/
"""

import os
import re
import sys
import json
import shutil
import stat
import logging
import platform
import zipfile
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
PLUGIN_DIR_NAME = "com_github_RolandWa_openfixture"
PLUGIN_IDENTIFIER = "com.github.RolandWa.openfixture"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _read_version(project_root: Path) -> str:
    """Extract version from setup.py or src/__init__.py."""
    # Try setup.py first
    setup_file = project_root / "setup.py"
    if setup_file.exists():
        content = setup_file.read_text(encoding="utf-8")
        match = re.search(r'version\s*=\s*["\']([^"\'\n]+)["\']', content)
        if match:
            return match.group(1)
    
    # Try src/__init__.py
    init_file = project_root / "src" / "__init__.py"
    if init_file.exists():
        content = init_file.read_text(encoding="utf-8")
        match = re.search(r'__version__\s*=\s*["\']([^"\'\n]+)["\']', content)
        if match:
            return match.group(1)
    
    return "2.0.0"


def _kicad_3rdparty_plugins_dir() -> Optional[Path]:
    """Return the 3rdparty/plugins directory KiCad actually scans.

    On Windows with OneDrive folder-redirection the shell Documents folder
    may differ from %USERPROFILE%\\Documents.  KiCad follows the shell
    folder, so we parse pcbnew.json to find the real path.
    """
    appdata = os.environ.get("APPDATA", "")
    if appdata:
        pcbnew_json = Path(appdata) / "kicad" / "9.0" / "pcbnew.json"
        if pcbnew_json.exists():
            try:
                data = json.loads(pcbnew_json.read_text(encoding="utf-8"))
                for entry in data.get("action_plugins", []):
                    if isinstance(entry, dict):
                        for key in entry:
                            if "3rdparty" in key:
                                idx = key.find("3rdparty")
                                raw = key[:idx].replace("\\\\", "\\")
                                return Path(raw) / "3rdparty" / "plugins"
            except Exception:
                pass

    if platform.system() == "Windows":
        docs = Path(os.environ.get("USERPROFILE", "")) / "Documents"
        return docs / "KiCad" / "9.0" / "3rdparty" / "plugins"
    elif platform.system() == "Darwin":
        return (
            Path.home() / "Documents" / "KiCad" / "9.0" / "3rdparty" / "plugins"
        )
    else:
        return (
            Path.home()
            / ".local"
            / "share"
            / "kicad"
            / "9.0"
            / "3rdparty"
            / "plugins"
        )


def _force_rmtree(path: Path):
    """Remove a directory tree, handling OneDrive locks and read-only files."""
    def _on_error(func, fpath, _exc_info):
        os.chmod(fpath, stat.S_IWRITE)
        func(fpath)

    try:
        shutil.rmtree(path, onerror=_on_error)
    except PermissionError:
        import time
        alt = path.with_name(f"{path.name}_old_{int(time.time())}")
        path.rename(alt)
        logger.warning(f"  Renamed locked dir → {alt.name}")


# ---------------------------------------------------------------------------
# Build system
# ---------------------------------------------------------------------------
class OpenFixtureBuildSystem:
    """Build system for OpenFixture KiCAD plugin."""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent
        self.build_dir = self.project_root / "build"
        self.version = _read_version(self.project_root)
        self.package_dir = self.build_dir / PLUGIN_DIR_NAME
        self.zip_path = self.build_dir / f"OpenFixture-{self.version}.zip"

    # -- clean --------------------------------------------------------------
    def clean(self):
        """Remove and recreate the package directory inside build/."""
        logger.info("Cleaning build directory...")
        self.build_dir.mkdir(exist_ok=True)
        if self.package_dir.exists():
            _force_rmtree(self.package_dir)
        # Remove old ZIP if possible
        if self.zip_path.exists():
            try:
                self.zip_path.unlink()
            except PermissionError:
                logger.warning(f"  Cannot remove locked {self.zip_path.name} — will overwrite")
        logger.info("[OK] Build directory ready")

    # -- copy sources -------------------------------------------------------
    def _copy_sources(self):
        """Assemble the plugin tree under build/<PLUGIN_DIR_NAME>/."""
        pkg = self.package_dir
        pkg.mkdir(parents=True, exist_ok=True)

        # Copy openfixture.py (main plugin file)
        src_plugin = self.project_root / "src" / "openfixture.py"
        if src_plugin.exists():
            shutil.copy2(src_plugin, pkg / "openfixture.py")
            logger.info("  [OK] openfixture.py")
        else:
            logger.error("  [FAIL] src/openfixture.py not found!")

        # Copy openfixture_support/ package
        src_support = self.project_root / "src" / "openfixture_support"
        if src_support.exists():
            shutil.copytree(
                src_support,
                pkg / "openfixture_support",
                ignore=shutil.ignore_patterns(
                    "__pycache__", "*.pyc", "*.pyo", "*.backup",
                ),
            )
            n = len(list((pkg / "openfixture_support").rglob("*.py")))
            logger.info(f"  [OK] openfixture_support/ ({n} .py files)")

        # Create __init__.py for KiCAD plugin registration
        init_content = '''"""OpenFixture - PCB Test Fixture Generator for KiCAD

Automated laser-cuttable PCB test fixture generation.
"""

import os
import sys
from pathlib import Path

# Add plugin directory to path
plugin_dir = Path(__file__).parent
if str(plugin_dir) not in sys.path:
    sys.path.insert(0, str(plugin_dir))

try:
    import pcbnew
    
    # Import and register the plugin
    from openfixture import OpenFixturePlugin
    OpenFixturePlugin().register()
    
except ImportError:
    # KiCAD not available (development mode)
    pass

__version__ = "''' + self.version + '''"
'''
        (pkg / "__init__.py").write_text(init_content, encoding="utf-8")
        logger.info("  [OK] __init__.py (plugin registration)")

        # Create plugin.json for KiCAD
        plugin_json = {
            "$schema": "https://go.kicad.org/pcm/schemas/v1",
            "name": "OpenFixture",
            "description": "Automated PCB test fixture generator for laser cutting",
            "description_full": "OpenFixture automatically generates laser-cuttable PCB test fixtures from KiCAD board files. Extracts test points, generates OpenSCAD 3D models, and exports DXF files for laser cutting.",
            "identifier": PLUGIN_IDENTIFIER,
            "type": "plugin",
            "author": {
                "name": "Roland Wa",
                "contact": {"web": "https://github.com/RolandWa/openfixture"},
            },
            "license": "CC-BY-SA-4.0",
            "resources": {
                "homepage": "https://github.com/RolandWa/openfixture",
            },
            "versions": [
                {
                    "version": self.version,
                    "status": "stable",
                    "kicad_version": "8.0",
                    "kicad_version_max": "9.99",
                }
            ],
        }
        (pkg / "plugin.json").write_text(
            json.dumps(plugin_json, indent=2), encoding="utf-8"
        )
        logger.info("  [OK] plugin.json")

        # Create metadata.json for KiCAD PCM
        metadata = {
            "$schema": "https://go.kicad.org/pcm/schemas/v1",
            "name": "OpenFixture",
            "description": "Automated PCB test fixture generator",
            "description_full": "OpenFixture automatically generates laser-cuttable PCB test fixtures from KiCAD board files. It extracts test points, generates parametric OpenSCAD models, and exports DXF files ready for laser cutting.",
            "identifier": PLUGIN_IDENTIFIER,
            "type": "plugin",
            "author": {
                "name": "Roland Wa",
                "contact": {"web": "https://github.com/RolandWa/openfixture"},
            },
            "license": "CC-BY-SA-4.0",
            "resources": {
                "homepage": "https://github.com/RolandWa/openfixture",
            },
            "versions": [
                {
                    "version": self.version,
                    "status": "stable",
                    "kicad_version": "8.0",
                }
            ],
        }
        (pkg / "metadata.json").write_text(
            json.dumps(metadata, indent=2), encoding="utf-8"
        )
        logger.info("  [OK] metadata.json")

        # Copy icon
        icon = self.project_root / "OpenFixture.png"
        if icon.exists():
            shutil.copy2(icon, pkg / "OpenFixture.png")
            logger.info("  [OK] OpenFixture.png")

        # Copy documentation files
        for fname in ("README.md", "LICENSE.md", "POGO_PINS.md", "MIGRATION_GUIDE.md", "SECURITY.md"):
            f = self.project_root / fname
            if f.exists():
                shutil.copy2(f, pkg / fname)
                logger.info(f"  [OK] {fname}")

    # -- validate -----------------------------------------------------------
    def _validate(self) -> bool:
        """Check that all required files exist in the assembled package."""
        required = [
            "__init__.py",
            "openfixture.py",
            "plugin.json",
            "metadata.json",
            "OpenFixture.png",
            "openfixture_support/__init__.py",
            "openfixture_support/GenFixture.py",
            "openfixture_support/openfixture.scad",
        ]
        missing = [f for f in required if not (self.package_dir / f).exists()]
        if missing:
            logger.error(f"  [FAIL] Missing: {missing}")
            return False
        logger.info("[OK] Validation passed")
        return True

    # -- create ZIP ---------------------------------------------------------
    def _create_zip(self) -> Path:
        """Create a ZIP file suitable for KiCAD 'Install from File…'.

        Structure inside the ZIP:
            metadata.json                       ← PCM requires this at root
            plugins/
              com_github_RolandWa_openfixture/
                __init__.py
                openfixture.py
                openfixture_support/
                ...
        """
        logger.info(f"\nCreating ZIP: {self.zip_path.name}")
        
        with zipfile.ZipFile(self.zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add metadata.json at root
            zf.write(
                self.package_dir / "metadata.json",
                "metadata.json"
            )
            
            # Add all package files under plugins/
            for item in self.package_dir.rglob("*"):
                if item.is_file():
                    arcname = Path("plugins") / PLUGIN_DIR_NAME / item.relative_to(self.package_dir)
                    zf.write(item, arcname)
        
        logger.info(f"[OK] Created {self.zip_path.name} ({self.zip_path.stat().st_size:,} bytes)")
        return self.zip_path

    # -- deploy -------------------------------------------------------------
    def deploy(self):
        """Install the built package to local KiCAD installation."""
        plugins_dir = _kicad_3rdparty_plugins_dir()
        if not plugins_dir:
            logger.error("[FAIL] Cannot determine KiCAD plugins directory")
            return False

        target_dir = plugins_dir / PLUGIN_DIR_NAME
        logger.info(f"\nDeploying to: {target_dir}")

        # Remove existing installation
        if target_dir.exists():
            logger.info("  Removing existing installation...")
            _force_rmtree(target_dir)

        # Copy package directory
        shutil.copytree(self.package_dir, target_dir)
        logger.info("[OK] Deployment complete")
        logger.info("\n  Restart KiCAD to load the updated plugin")
        logger.info("  Access via: Tools → External Plugins → OpenFixture Generator")
        return True

    # -- build --------------------------------------------------------------
    def build(self, create_zip=True):
        """Full build: clean, copy, validate, optionally create ZIP."""
        logger.info(f"=== Building OpenFixture v{self.version} ===\n")
        
        self.clean()
        logger.info("\nCopying sources...")
        self._copy_sources()
        
        logger.info("\nValidating package...")
        if not self._validate():
            return False
        
        if create_zip:
            self._create_zip()
        
        logger.info(f"\n=== Build complete ===")
        logger.info(f"Package directory: {self.package_dir}")
        if create_zip:
            logger.info(f"ZIP file: {self.zip_path}")
        return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenFixture build system")
    parser.add_argument("--clean", action="store_true", help="Clean build directory only")
    parser.add_argument("--deploy", action="store_true", help="Build and deploy to KiCAD")
    parser.add_argument("--zip", action="store_true", help="Build ZIP only (no deploy)")
    parser.add_argument("--no-zip", action="store_true", help="Build package dir only (no ZIP)")
    
    args = parser.parse_args()
    
    builder = OpenFixtureBuildSystem()
    
    if args.clean:
        builder.clean()
    elif args.deploy:
        if builder.build(create_zip=True):
            builder.deploy()
    elif args.zip:
        builder.build(create_zip=True)
    elif args.no_zip:
        builder.build(create_zip=False)
    else:
        # Default: build with ZIP
        builder.build(create_zip=True)


if __name__ == "__main__":
    main()
