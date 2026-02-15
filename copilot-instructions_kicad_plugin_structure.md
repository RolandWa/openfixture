# Copilot Instructions: KiCAD Plugin Structure

**Purpose**: Guide AI assistants in creating and modifying KiCAD PCB Editor plugins  
**Target**: Python developers working with KiCAD 7.0+ / 9.0+  
**Last Updated**: February 15, 2026

---

## 1. KiCAD Plugin Architecture Overview

### 1.1 Plugin Types

KiCAD supports two types of Python plugins:

#### **Action Plugins** (Used in this project)
- Appear in PCB Editor toolbar and Tools menu
- Triggered by user action (button click, menu selection)
- Can modify board, create markers, show dialogs
- Example: EMC Auditor Plugin

#### **Scripting Plugins**
- Run in KiCAD Python console or external scripts
- Batch processing, automation, Gerber generation
- Example: Board panelization scripts

---

### 1.2 Plugin File Structure

**Minimal Action Plugin** (single file):
```
my_plugin.py               # Main plugin code
my_plugin_icon.png         # Toolbar icon (PNG for KiCAD 9.x, SVG for 8.x)
```

**Modular Action Plugin** (this project's structure):
```
emc_auditor_plugin.py      # Main orchestrator (ActionPlugin class)
via_stitching.py           # Checker module 1
decoupling.py              # Checker module 2
ground_plane.py            # Checker module 3
emi_filtering.py           # Checker module 4
clearance_creepage.py      # Checker module 5
signal_integrity.py        # Checker module 6
emc_rules.toml             # Configuration file
emc_icon.png               # Toolbar icon
```

**Benefits of Modular Structure**:
- ✅ Easier to maintain (smaller files)
- ✅ Separation of concerns (each checker isolated)
- ✅ Easier to test (mock dependencies)
- ✅ Parallel development (multiple devs working on different checkers)

---

### 1.3 Plugin Registration

**Location** (KiCAD 9.0):
- **Windows**: `C:\Users\<username>\Documents\KiCad\9.0\3rdparty\plugins\`
- **Linux**: `~/.local/share/kicad/9.0/3rdparty/plugins/`
- **macOS**: `~/Library/Application Support/kicad/9.0/3rdparty/plugins/`

**Important**: Files must be in plugins directory directly, NOT in a subfolder

**Registration Pattern**:
```python
import pcbnew

class MyPlugin(pcbnew.ActionPlugin):
    """
    KiCAD automatically discovers and registers classes inheriting from ActionPlugin
    """
    
    def defaults(self):
        """
        Called by KiCAD on plugin discovery
        Sets plugin metadata shown in UI
        """
        self.name = "My Plugin"
        self.category = "EMC Check"  # Category in Tools menu
        self.description = "Brief description for tooltip"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "my_icon.png")
    
    def Run(self):
        """
        Called when user clicks toolbar button or menu item
        Main entry point for plugin logic
        """
        board = pcbnew.GetBoard()
        # Your plugin logic here
        wx.MessageBox("Plugin executed!", "Info")

# Register plugin (KiCAD calls this automatically on import)
MyPlugin().register()
```

---

## 2. Plugin Lifecycle

### 2.1 Discovery Phase

```
KiCAD Startup
    │
    ├─ Scan plugins directory
    │    • Look for .py files
    │    • Import each Python module
    │    • Detect ActionPlugin subclasses
    │
    ├─ Call defaults() on each plugin
    │    • Extract metadata (name, category, description)
    │    • Load icon file
    │    • Determine toolbar visibility
    │
    └─ Register in UI
         • Add toolbar button (if show_toolbar_button = True)
         • Add menu item (Tools → External Plugins → [Plugin Name])
```

**Key Point**: `defaults()` is called ONCE at startup, not every run

---

### 2.2 Execution Phase

```
User Action (Click Toolbar Button)
    │
    ├─ KiCAD calls Run() method
    │
    ├─ Plugin executes
    │    • Access board: pcbnew.GetBoard()
    │    • Read/modify PCB data
    │    • Show dialogs (wx.Dialog, wx.MessageBox)
    │    • Create markers/shapes on layers
    │
    └─ Run() returns
         • KiCAD refreshes display if board modified
         • Plugin instance remains in memory
```

**Key Point**: `Run()` is called EVERY TIME user triggers plugin

---

### 2.3 Reload/Update Workflow

**Problem**: KiCAD caches plugins on startup

**Solution**: Restart KiCAD PCB Editor after code changes

**Development Workflow**:
1. Edit plugin code in your repository
2. Run `sync_to_kicad.ps1` to copy files to plugins directory
3. **Restart KiCAD PCB Editor** (don't just close/reopen PCB file)
4. Test plugin on PCB design
5. Repeat

**Alternative** (advanced):
```python
# Force module reload (add to Run() during development)
import importlib
import via_stitching
importlib.reload(via_stitching)
```

---

## 3. Plugin Class Structure

### 3.1 Minimal Plugin Template

```python
import pcbnew
import os

class MinimalPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Minimal Plugin"
        self.category = "Test"
        self.description = "Simplest possible plugin"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "icon.png")
    
    def Run(self):
        board = pcbnew.GetBoard()
        wx.MessageBox(f"PCB has {len(list(board.GetTracks()))} tracks", "Info")

MinimalPlugin().register()
```

---

### 3.2 Plugin with Configuration

```python
import pcbnew
import os
import wx

# TOML configuration support
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Fallback
    except ImportError:
        import toml as tomllib  # Alternative

class ConfigurablePlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Configurable Plugin"
        self.category = "EMC Check"
        self.description = "Plugin with TOML configuration"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "icon.png")
    
    def Run(self):
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), "config.toml")
        try:
            with open(config_path, "rb") as f:
                config = tomllib.load(f)
        except Exception as e:
            wx.MessageBox(f"Config error: {e}", "Error", wx.OK | wx.ICON_ERROR)
            return
        
        # Use configuration
        max_distance = config.get('rules', {}).get('max_distance_mm', 2.0)
        enabled = config.get('rules', {}).get('enabled', True)
        
        if not enabled:
            wx.MessageBox("Plugin disabled in config", "Info")
            return
        
        # Your plugin logic using config parameters
        board = pcbnew.GetBoard()
        # ...

ConfigurablePlugin().register()
```

**Corresponding config.toml**:
```toml
[rules]
enabled = true
max_distance_mm = 2.0
description = "Maximum distance for checks"
```

---

### 3.3 Modular Plugin Architecture (This Project's Pattern)

**Main Plugin** (emc_auditor_plugin.py):
```python
import pcbnew
import os
import wx

# Import checker modules
try:
    from via_stitching import ViaStitchingChecker
except ImportError:
    ViaStitchingChecker = None  # Graceful degradation

class EMCAuditorPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "EMC Auditor"
        self.category = "EMC Check"
        self.description = "Comprehensive EMC verification"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "emc_icon.png")
    
    def Run(self):
        # Load configuration
        config = self.load_config()
        
        # Get board
        board = pcbnew.GetBoard()
        marker_layer = board.GetLayerID("Cmts.User")
        
        # Prepare shared state
        report_lines = []  # Shared report across all checkers
        total_violations = 0
        
        # Run via stitching check (if enabled)
        via_cfg = config.get('via_stitching', {})
        if via_cfg.get('enabled', False) and ViaStitchingChecker:
            checker = ViaStitchingChecker(board, marker_layer, via_cfg, report_lines, True, self)
            violations = checker.check(
                self.draw_error_marker,  # Inject utilities
                self.draw_arrow,
                self.get_distance,
                self.log,
                self.create_group
            )
            total_violations += violations
        
        # Show report dialog
        if total_violations > 0:
            self.show_report(report_lines, total_violations)
        else:
            wx.MessageBox("No violations found!", "EMC Audit Complete", wx.OK)
    
    def draw_error_marker(self, board, pos, msg, layer, group):
        """Utility: Draw violation marker (circle + text)"""
        # Implementation...
        pass
    
    def draw_arrow(self, board, start, end, label, layer, group):
        """Utility: Draw directional arrow"""
        # Implementation...
        pass
    
    def get_distance(self, p1, p2):
        """Utility: Calculate 2D Euclidean distance"""
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        return (dx * dx + dy * dy) ** 0.5

EMCAuditorPlugin().register()
```

**Checker Module** (via_stitching.py):
```python
import pcbnew

class ViaStitchingChecker:
    def __init__(self, board, marker_layer, config, report_lines, verbose, auditor):
        self.board = board
        self.marker_layer = marker_layer
        self.config = config
        self.report_lines = report_lines
        self.verbose = verbose
        self.auditor = auditor  # Reference to main plugin
        self.violation_count = 0
    
    def check(self, draw_marker_func, draw_arrow_func, get_distance_func, log_func, create_group_func):
        """
        Main entry point - performs via stitching verification.
        Utility functions injected from main plugin to avoid duplication.
        """
        # Store injected functions
        self.log = log_func
        self.draw_marker = draw_marker_func
        self.draw_arrow = draw_arrow_func
        self.get_distance = get_distance_func
        
        # Parse configuration
        max_dist_mm = self.config.get('max_distance_mm', 2.0)
        max_dist = pcbnew.FromMM(max_dist_mm)
        
        # Perform checks
        for via in self.board.GetTracks():
            if isinstance(via, pcbnew.PCB_VIA):
                # Check logic...
                if violation_detected:
                    group = create_group_func(self.board, "Via", via_id, self.violation_count)
                    self.draw_marker(self.board, via.GetPosition(), "NO GND VIA", self.marker_layer, group)
                    self.violation_count += 1
        
        self.report_lines.append(f"Via stitching: {self.violation_count} violations")
        return self.violation_count
```

**Benefits**:
- ✅ **No code duplication**: Utilities defined once in main plugin
- ✅ **Easy testing**: Mock utility functions in tests
- ✅ **Clear interface**: Checker only needs check() method
- ✅ **Extensibility**: Add new checkers without modifying existing ones

---

## 4. Icon Integration

### 4.1 Icon Requirements

**Format**:
- **KiCAD 9.x**: PNG (SVG support dropped)
- **KiCAD 8.x and earlier**: SVG or PNG

**Size**:
- **Recommended**: 24×24 pixels (toolbar button size)
- **Fallback**: 16×16, 32×32, 48×48 (KiCAD scales)

**Path**:
```python
self.icon_file_name = os.path.join(os.path.dirname(__file__), "my_icon.png")
```

**Why `os.path.dirname(__file__)`?**
- Works regardless of where KiCAD plugins directory is located
- Portable across Windows/Linux/macOS
- Handles spaces in paths

---

### 4.2 Icon Fallback

**If icon not found**:
- Plugin still registers and works
- No toolbar button appears (but menu item still there)
- No error shown to user

**Best Practice**:
```python
def defaults(self):
    icon_path = os.path.join(os.path.dirname(__file__), "my_icon.png")
    if os.path.exists(icon_path):
        self.icon_file_name = icon_path
    else:
        print(f"WARNING: Icon not found at {icon_path}")
        self.show_toolbar_button = False  # Disable toolbar button
```

---

## 5. Common Patterns

### 5.1 Access Current Board

```python
def Run(self):
    board = pcbnew.GetBoard()  # Current open board in PCB Editor
    
    # Check if board is valid
    if not board:
        wx.MessageBox("No PCB opened!", "Error", wx.OK | wx.ICON_ERROR)
        return
```

---

### 5.2 Show Dialog with Results

```python
import wx

def Run(self):
    # ... perform checks ...
    
    # Simple message box
    wx.MessageBox(f"Found {violations} violations", "Results", wx.OK | wx.ICON_INFORMATION)
    
    # Custom dialog
    dialog = wx.Dialog(None, -1, "Results", size=(400, 300))
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    text = wx.TextCtrl(dialog, -1, report_text, style=wx.TE_MULTILINE | wx.TE_READONLY)
    sizer.Add(text, 1, wx.EXPAND | wx.ALL, 10)
    
    ok_btn = wx.Button(dialog, wx.ID_OK, "OK")
    sizer.Add(ok_btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)
    
    dialog.SetSizer(sizer)
    dialog.ShowModal()
    dialog.Destroy()
```

---

### 5.3 Clear Previous Markers

```python
def clear_previous_markers(self, board):
    """Remove all markers created by this plugin"""
    # Get all groups
    groups = board.Groups()
    
    # Find groups created by this plugin (by naming convention)
    plugin_groups = [g for g in groups if g.GetName().startswith("EMC_")]
    
    # Delete each group (removes all contained items)
    for group in plugin_groups:
        board.Remove(group)
```

**Naming Convention**:
- Use unique prefix for your plugin (e.g., "EMC_", "SI_", "DRC_")
- Allows users to distinguish between different plugin markers
- Enables selective deletion

---

### 5.4 Unit Conversion

```python
# mm to internal units (nanometers)
distance_iu = pcbnew.FromMM(2.5)  # 2.5mm → 2500000 internal units

# internal units to mm
distance_mm = pcbnew.ToMM(2500000)  # 2500000 IU → 2.5mm

# inches to internal units
distance_iu = pcbnew.FromMils(100)  # 100 mils → internal units

# Consistent usage:
config_value_mm = 2.0  # From TOML config
max_dist = pcbnew.FromMM(config_value_mm)  # Convert once

# Compare in internal units
if actual_distance < max_dist:
    # Violation detected
```

**Best Practice**: Store config values in mm (human-readable), convert to internal units at start of check

---

### 5.5 Progress Dialog for Long Operations

```python
import wx

def Run(self):
    board = pcbnew.GetBoard()
    tracks = list(board.GetTracks())
    
    # Show progress dialog if many items
    if len(tracks) > 100:
        progress = wx.ProgressDialog(
            "Processing",
            "Checking tracks...",
            maximum=len(tracks),
            parent=None,
            style=wx.PD_APP_MODAL | wx.PD_CAN_ABORT | wx.PD_ELAPSED_TIME
        )
        
        for i, track in enumerate(tracks):
            # Update progress
            keep_going, skip = progress.Update(i, f"Checking track {i+1}/{len(tracks)}")
            
            # User clicked Cancel
            if not keep_going:
                progress.Destroy()
                wx.MessageBox("Check cancelled by user", "Info")
                return
            
            # Your checking logic
            # ...
        
        progress.Destroy()
```

---

## 6. Testing & Debugging

### 6.1 Console Output

```python
def Run(self):
    # Print to KiCAD Python console (Tools → Scripting Console)
    print("Plugin executed")
    print(f"Board has {len(list(board.GetTracks()))} tracks")
    
    # Python logging module
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("MyPlugin")
    logger.debug("Debug message")
    logger.info("Info message")
```

**View Output**:
- Open **Tools → Scripting Console** in KiCAD PCB Editor
- Console shows print statements and exceptions

---

### 6.2 Error Handling

```python
def Run(self):
    try:
        # Your plugin logic
        board = pcbnew.GetBoard()
        # ...
    except Exception as e:
        import traceback
        error_msg = f"Plugin error: {str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)  # Console
        wx.MessageBox(error_msg, "Error", wx.OK | wx.ICON_ERROR)  # User dialog
```

---

### 6.3 Unit Testing (Recommended)

```python
# tests/test_via_stitching.py
import pytest
import pcbnew
from via_stitching import ViaStitchingChecker

def test_via_stitching_basic():
    # Load test board
    board = pcbnew.LoadBoard("tests/fixtures/test_board.kicad_pcb")
    
    # Setup checker
    config = {'max_distance_mm': 2.0}
    checker = ViaStitchingChecker(board, pcbnew.User_Comments, config, [], False, None)
    
    # Mock utility functions
    def mock_draw(board, pos, msg, layer, group):
        pass
    
    def mock_log(msg, force=False):
        pass
    
    def mock_distance(p1, p2):
        return 1.0  # Mock distance
    
    # Execute
    violations = checker.check(mock_draw, None, mock_distance, mock_log, lambda *args: None)
    
    # Assert
    assert violations >= 0  # At least no crash
```

**Run Tests**:
```bash
pytest tests/
```

---

## 7. Deployment

### 7.1 Manual Installation

1. Copy all plugin files to KiCAD plugins directory:
   ```
   emc_auditor_plugin.py
   via_stitching.py
   decoupling.py
   emc_rules.toml
   emc_icon.png
   ```

2. Restart KiCAD PCB Editor

3. Verify plugin appears in toolbar/menu

---

### 7.2 Automated Sync Script (PowerShell)

**sync_to_kicad.ps1**:
```powershell
# User-specific path (edit this)
$PluginsDir = "C:\Users\YourName\Documents\KiCad\9.0\3rdparty\plugins"

# Files to copy
$Files = @(
    "emc_auditor_plugin.py",
    "via_stitching.py",
    "decoupling.py",
    "ground_plane.py",
    "emi_filtering.py",
    "clearance_creepage.py",
    "signal_integrity.py",
    "emc_rules.toml",
    "emc_icon.png"
)

# Copy each file
foreach ($File in $Files) {
    if (Test-Path $File) {
        Copy-Item $File -Destination $PluginsDir -Force
        Write-Host "✓ Copied $File" -ForegroundColor Green
    } else {
        Write-Host "✗ File not found: $File" -ForegroundColor Red
    }
}

Write-Host "`nDone! Restart KiCAD PCB Editor to load changes." -ForegroundColor Cyan
```

**Usage**:
```powershell
.\sync_to_kicad.ps1
```

---

### 7.3 Distribution (GitHub Release)

**Package Structure**:
```
my-plugin-v1.0.0.zip
├── README.md               # Installation instructions
├── CHANGELOG.md            # Version history
├── LICENSE                 # MIT, GPL, etc.
├── my_plugin.py            # Main plugin
├── module1.py              # Checker modules
├── module2.py
├── config.toml             # Default configuration
└── icon.png                # Toolbar icon
```

**Installation Instructions** (README.md):
```markdown
1. Download latest release: my-plugin-v1.0.0.zip
2. Extract all files to KiCAD plugins directory:
   - Windows: C:\Users\<username>\Documents\KiCad\9.0\3rdparty\plugins\
   - Linux: ~/.local/share/kicad/9.0/3rdparty/plugins/
   - macOS: ~/Library/Application Support/kicad/9.0/3rdparty/plugins/
3. Install Python dependencies: pip install tomli
4. Restart KiCAD PCB Editor
5. Plugin appears in toolbar as [Your Icon]
```

---

## 8. Troubleshooting

### Issue 1: Plugin Doesn't Appear

**Possible Causes**:
- ✗ Files in wrong directory (must be in plugins directory directly)
- ✗ Python syntax error (check console for import errors)
- ✗ Missing `ActionPlugin` subclass
- ✗ Missing `register()` call

**Solution**:
```python
# Check plugin file has all required parts:
import pcbnew

class MyPlugin(pcbnew.ActionPlugin):  # ← Must inherit ActionPlugin
    def defaults(self): pass
    def Run(self): pass

MyPlugin().register()  # ← Must call register()
```

---

### Issue 2: Icon Not Showing

**Possible Causes**:
- ✗ Icon file not found (wrong path)
- ✗ Icon format incorrect (use PNG for KiCAD 9.x)
- ✗ Permission issue (icon file not readable)

**Solution**:
```python
import os

icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
print(f"Looking for icon at: {icon_path}")
print(f"Icon exists: {os.path.exists(icon_path)}")
```

---

### Issue 3: Config File Not Loading

**Possible Causes**:
- ✗ TOML syntax error
- ✗ TOML library not installed
- ✗ Wrong file path

**Solution**:
```python
# Detailed error reporting
config_path = os.path.join(os.path.dirname(__file__), "config.toml")
try:
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
    print("Config loaded successfully")
except FileNotFoundError:
    print(f"Config file not found: {config_path}")
except Exception as e:
    print(f"Config parse error: {e}")
    # Use defaults
    config = {}
```

---

### Issue 4: Changes Not Reflected

**Cause**: KiCAD caches plugins on startup

**Solution**: **Restart KiCAD PCB Editor** after every code change

---

## 9. Best Practices Summary

✅ **DO**:
- Use modular architecture for complex plugins
- Inject utility functions to avoid duplication
- Provide TOML configuration for user customization
- Use descriptive group names for markers
- Show progress dialogs for long operations
- Handle errors gracefully with try/except
- Print debugging info to console
- Test on real PCB designs

❌ **DON'T**:
- Hard-code parameters (use config instead)
- Ignore user cancellation (check progress dialog return)
- Create markers without groups (harder to delete)
- Forget to convert units (use FromMM/ToMM)
- Assume plugin is always enabled (check config)
- Crash on missing config (use defaults)

---

## 10. Quick Reference

### Plugin Class Template
```python
import pcbnew
import os
import wx

class MyPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "My Plugin"
        self.category = "Category"
        self.description = "Description"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "icon.png")
    
    def Run(self):
        board = pcbnew.GetBoard()
        # Your logic here
        wx.MessageBox("Done!", "Info")

MyPlugin().register()
```

### Essential Functions
```python
# Access board
board = pcbnew.GetBoard()

# Unit conversion
pcbnew.FromMM(value_mm)
pcbnew.ToMM(value_iu)

# Dialogs
wx.MessageBox(msg, title, wx.OK)
wx.ProgressDialog(title, message, maximum)

# Board items
board.GetTracks()          # Tracks and vias
board.GetFootprints()      # Components
board.Zones()              # Copper pours
board.GetLayerID(name)     # Layer ID from name
```

---

**End of KiCAD Plugin Structure Guide**
