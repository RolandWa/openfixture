"""OpenFixture KiCAD Plugin - PCB Test Fixture Generator.

This module provides KiCAD ActionPlugin registration for the OpenFixture
toolbar button. When clicked, it launches the fixture generation dialog.
"""

import os
import sys
from pathlib import Path

# Ensure openfixture_support is importable
plugin_dir = Path(__file__).parent
if str(plugin_dir) not in sys.path:
    sys.path.insert(0, str(plugin_dir))

try:
    import pcbnew
    from openfixture import OpenFixturePlugin
    
    # Register the plugin with KiCAD
    OpenFixturePlugin().register()
    
except ImportError as e:
    # If pcbnew is not available, we're probably in development mode
    pass

__version__ = "1.0.0"
