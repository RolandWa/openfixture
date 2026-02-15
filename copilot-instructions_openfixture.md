# Copilot Instructions: OpenFixture - Automated PCB Test Fixture Generator

**Purpose**: Guide AI assistants in understanding, maintaining, and extending the OpenFixture system  
**Target**: Python developers working with KiCAD PCB automation and OpenSCAD parametric design  
**Last Updated**: February 15, 2026 (Added Security Section)  
**Security Status**: ✅ SECURE - Safe for public repositories

---

## 1. Project Overview

### 1.1 What is OpenFixture?

**OpenFixture** is an automated test fixture generator that creates laser-cuttable PCB test fixtures directly from KiCAD board files. It eliminates manual fixture design by:
- ✅ Extracting test point locations from KiCAD PCB files
- ✅ Generating parametric OpenSCAD 3D models
- ✅ Producing laser-cuttable DXF files for rapid assembly
- ✅ Supporting custom material thicknesses and hardware

**Typical Use Case**:
```
KiCAD PCB File (.kicad_pcb) 
    ↓
GenFixture.py (Python extraction)
    ↓
OpenSCAD (Parametric generation)
    ↓
Laser-Cuttable DXF + 3D Model + Validation
```

---

### 1.2 System Architecture

```
┌────────────────────────┐
│   KiCAD PCB Editor     │
│  (.kicad_pcb file)     │
└──────────┬─────────────┘
           │
           ├─────────────────────────────────────┐
           │                                     │
           ▼                                     ▼
┌──────────────────────┐           ┌───────────────────────┐
│   openfixture.py     │           │  GenFixture.py        │
│  (KiCAD Plugin)      │           │  (Command-line tool)  │
│                      │           │                       │
│  • wxPython Dialog   │           │  • pcbnew API         │
│  • Parameter GUI     │           │  • Test point extract │
│  • Calls GenFixture  │           │  • DXF export         │
└──────────────────────┘           │  • OpenSCAD launcher  │
           │                       └───────────┬───────────┘
           │                                   │
           └───────────────┬───────────────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │  genfixture.bat/.sh  │
                │  (Wrapper Scripts)   │
                │                      │
                │  • Project-specific  │
                │  • Material params   │
                │  • Hardware specs    │
                └──────────┬───────────┘
                           │
                           ▼
            ┌──────────────────────────────┐
            │    openfixture.scad          │
            │    (OpenSCAD Model)          │
            │                              │
            │  • Parametric fixture design │
            │  • Pogo pin placement        │
            │  • Hinge mechanism           │
            │  • Laser-cut parts layout    │
            └──────────┬───────────────────┘
                       │
                       ▼
            ┌──────────────────────────┐
            │   Output Files           │
            ├──────────────────────────┤
            │  • fixture.dxf (laser)   │
            │  • fixture.png (preview) │
            │  • test.dxf (validation) │
            │  • outline.dxf (board)   │
            │  • track.dxf (verify)    │
            └──────────────────────────┘
```

---

## 2. Core Components

### 2.1 GenFixture.py - Main Processing Script

**Purpose**: Extract PCB data and generate OpenSCAD parameters

**Key Responsibilities**:
1. **Parse KiCAD PCB file** using pcbnew API
2. **Extract test points** from pads (SMD pads without paste mask)
3. **Calculate board dimensions** from Edge.Cuts and component bounding boxes
4. **Export DXF files** (outline, tracks for validation)
5. **Launch OpenSCAD** with calculated parameters

**Class Structure**:
```python
class GenFixture:
    # Layer assignments
    layer = F_Cu          # Test point layer (F.Cu or B.Cu)
    paste = F_Paste       # Paste layer (to exclude pads)
    ignore_layer = Eco1_User   # Force ignore test points
    force_layer = Eco2_User    # Force include as test points
    
    # Board data
    brd = None           # pcbnew.BOARD object
    origin = [inf, inf]  # Board origin (top-left)
    dims = [0, 0]        # Board dimensions (x, y)
    min_y = inf          # Minimum Y coordinate (for hinge placement)
    test_points = []     # List of [x, y] test point coordinates
    
    # Hardware parameters
    mat_th = 0           # Material thickness (mm)
    pcb_th = 1.6         # PCB thickness (mm)
    screw_len = 14       # Assembly screw length (mm)
    screw_d = 3.0        # Screw diameter (mm)
    
    # Optional parameters
    rev = None           # PCB revision string
    washer_th = None     # Washer thickness (mm)
    nut_f2f = None       # Nut flat-to-flat (mm)
    nut_c2c = None       # Nut corner-to-corner (mm)
    nut_th = None        # Nut thickness (mm)
    pivot_d = None       # Pivot diameter (mm)
    border = None        # PCB support border (mm)
    pogo_uncompressed_length = None  # Pogo pin length (mm)
```

**Key Methods**:

```python
def GetOriginDimensions(self):
    """
    Calculate PCB origin (top-left) and dimensions
    
    Algorithm:
    1. Iterate Edge.Cuts layer for board outline
    2. Iterate all modules for component bounding boxes
    3. Track min_x, min_y (origin), max_x, max_y (dimensions)
    4. Round to 0.01mm precision
    
    Note: Components can extend beyond Edge.Cuts!
    """
    for line in self.brd.GetDrawings():
        if line.GetLayerName() == 'Edge.Cuts':
            bb = line.GetBoundingBox()
            # Track min/max coordinates
    
    for modu in self.brd.GetModules():
        bb = modu.GetFootprintRect()
        # Track component boundaries

def GetTestPoints(self):
    """
    Extract test point coordinates from PCB pads
    
    Test Point Rules:
    1. Pad is on selected layer (F.Cu or B.Cu)
    2. Pad is SMD type (not THT)
    3. Pad does NOT have paste mask (exposed copper)
    4. Pad is on force_layer (Eco2.User) OR
    5. Pad is NOT on ignore_layer (Eco1.User)
    
    Coordinates:
    - Relative to board origin (0,0 at top-left)
    - Mirrored if working on back layer
    - Rounded to 0.01mm precision
    """
    for m in self.brd.GetModules():
        for p in m.Pads():
            if (p.IsOnLayer(self.layer) and
                p.GetAttribute() == PAD_ATTRIB_SMD and
                not p.IsOnLayer(self.paste)):
                # Extract and transform coordinates

def PlotDXF(self, path, LayerToCheck):
    """
    Export DXF files for OpenSCAD import
    
    Exports:
    - "outline": Edge.Cuts layer (board outline)
    - "track": Selected copper layer (test point verification)
    
    DXF Settings:
    - Units: Millimeters
    - Origin: Aux origin (set to board top-left)
    - Polygon mode: True (filled shapes)
    - Mirror: True if back layer
    """
    pctl = PLOT_CONTROLLER(self.brd)
    popt = pctl.GetPlotOptions()
    popt.SetDXFPlotUnits(DXF_PLOTTER.DXF_UNIT_MILLIMETERS)
    popt.SetUseAuxOrigin(True)
    # Export DXF

def Generate(self, path):
    """
    Main generation workflow
    
    Steps:
    1. GetOriginDimensions() - Calculate board size
    2. GetTestPoints() - Extract test point locations
    3. PlotDXF() - Export outline and tracks
    4. Build OpenSCAD command line arguments
    5. Call openscad 3 times:
       a. testcut mode - Generate validation piece
       b. 3dmodel mode - Generate PNG rendering
       c. lasercut mode - Generate laser-cuttable DXF
    
    Note: Different argument format for Windows vs Linux!
    """
```

---

### 2.2 Command-Line Usage

**Basic Usage**:
```bash
python GenFixture.py --board <file.kicad_pcb> \
                     --mat_th <thickness_mm> \
                     --out <output_dir> \
                     [OPTIONS]
```

**Required Arguments**:
- `--board`: Path to .kicad_pcb file
- `--mat_th`: Material thickness in mm (e.g., 3.0 for acrylic)
- `--out`: Output directory path

**Common Optional Arguments**:
```bash
--pcb_th 1.6              # PCB thickness (default: 1.6mm)
--layer B.Cu              # Test point layer (F.Cu or B.Cu)
--screw_len 16.0          # Screw thread length (default: 14mm)
--screw_d 3.0             # Screw diameter (default: 3mm)
--rev "rev_01"            # Revision string (default: from PCB)
--flayer Eco2.User        # Force layer (mark pads as test points)
--ilayer Eco1.User        # Ignore layer (exclude pads)
```

**Hardware Optional Arguments**:
```bash
--washer_th 1.0           # Washer thickness for hinge
--nut_th 2.4              # Hex nut thickness
--nut_f2f 5.45            # Hex nut flat-to-flat dimension
--nut_c2c 6.10            # Hex nut corner-to-corner dimension
--pivot_d 3.0             # Pivot hole diameter
--border 0.8              # PCB support border width
--pogo-uncompressed-length 16  # Pogo pin extended length
```

**Example**:
```bash
python GenFixture.py \
  --board example_board.kicad_pcb \
  --layer B.Cu \
  --mat_th 2.45 \
  --pcb_th 0.8 \
  --out fixture \
  --screw_len 16.0 \
  --nut_f2f 5.45 \
  --border 0.8
```

---

### 2.3 Wrapper Scripts (genfixture.bat / genfixture.sh)

**Purpose**: Project-specific convenience wrappers

**Pattern** (Windows):
```batch
@echo off
REM Project-specific fixture parameters

REM Add OpenSCAD to PATH
IF EXIST "C:\Program Files\OpenSCAD" SET PATH=%PATH%;"C:\Program Files\OpenSCAD\"

set BOARD=%1          # First argument is .kicad_pcb file

REM PCB-specific parameters
set PCB=0.8           # PCB thickness
set LAYER=B.Cu        # Test point layer
set REV=rev_11        # Revision
set OUTPUT=fixture-%REV%

REM Material parameters
set MAT=2.45          # Acrylic thickness
set BORDER=0.8        # Support border

REM Hardware parameters
set SCREW_LEN=16.0
set SCREW_D=3.0
set WASHER_TH=1.0
set NUT_TH=2.4
set NUT_F2F=5.45
set NUT_C2C=6.10
set POGO_UNCOMPRESSED_LENGTH=16

REM Call GenFixture with all parameters
"c:\Program Files\KiCad\bin\python.exe" GenFixture.py ^
  --board %BOARD% --layer %LAYER% --rev %REV% ^
  --mat_th %MAT% --pcb_th %PCB% --out %OUTPUT% ^
  --screw_len %SCREW_LEN% --screw_d %SCREW_D% ^
  --washer_th %WASHER_TH% --nut_th %NUT_TH% ^
  --nut_f2f %NUT_F2F% --nut_c2c %NUT_C2C% ^
  --border %BORDER% ^
  --pogo-uncompressed-length %POGO_UNCOMPRESSED_LENGTH%
```

**Pattern** (Linux/Mac):
```bash
#!/bin/sh
# Project-specific fixture parameters

BOARD=$1
OUTPUT="fixture-v10"

# PCB parameters
PCB=0.8
LAYER='B.Cu'
REV='rev.10'

# Material parameters
MAT=2.45
BORDER=0.8

# Hardware parameters
SCREW_LEN=16.0
SCREW_D=3.0
WASHER_TH=1.0
NUT_TH=2.4
NUT_F2F=5.45
NUT_C2C=6.10

# Call GenFixture
python GenFixture.py --board $BOARD --layer $LAYER --rev $REV \
  --mat_th $MAT --pcb_th $PCB --out $OUTPUT \
  --screw_len $SCREW_LEN --screw_d $SCREW_D \
  --washer_th $WASHER_TH --nut_th $NUT_TH \
  --nut_f2f $NUT_F2F --nut_c2c $NUT_C2C \
  --border $BORDER
```

**Usage**:
```bash
# Windows
genfixture.bat C:\path\to\board.kicad_pcb

# Linux/Mac
./genfixture.sh /path/to/board.kicad_pcb
```

---

### 2.4 KiCAD Plugin (openfixture.py + OpenFixtureDlg.py)

**Purpose**: GUI integration for KiCAD PCB Editor

**File Structure**:
```
openfixture.py          # Plugin main class
OpenFixtureDlg.py       # wxPython dialog (wxFormBuilder generated)
OpenFixture.png         # Toolbar icon
```

**Plugin Registration**:
```python
class OpenFixture(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Open Fixture"
        self.category = "CAD automatic fixture tool"
        self.description = "Create automatically fixture using OpenSCAD"
        self.icon_file_name = os.path.join(
            os.path.dirname(__file__), 
            "./OpenFixture.png"
        )
    
    def Run(self):
        """Called when user clicks toolbar button"""
        pcb = pcbnew.GetBoard()
        _pcbnew_frame = [x for x in wx.GetTopLevelWindows() 
                         if x.GetName() == 'PcbFrame'][0]
        
        # Show parameter dialog
        dialog = OpenFixture_Dlg(_pcbnew_frame)
        modal_result = dialog.ShowModal()

# Register plugin (KiCAD auto-discovers this)
OpenFixture().register()
```

**Installation Path**:
- **Windows**: `%USERPROFILE%\Documents\KiCad\<version>\3rdparty\plugins\`
- **Linux**: `~/.local/share/kicad/<version>/3rdparty/plugins/`
- **macOS**: `~/Library/Application Support/kicad/<version>/3rdparty/plugins/`

**Dialog Parameters** (OpenFixtureDlg.py):
```python
class OpenFixtureDlg(wx.Dialog):
    """
    wxFormBuilder-generated dialog with fixture parameters
    
    Controls:
    - m_PcbTh: PCB thickness (default: 1.6mm)
    - m_rev: Revision string (default: "0.1")
    - m_checkLayerTop: Top layer checkbox
    - m_checkLayerBottom: Bottom layer checkbox
    - m_screwLen: Screw length (default: 16.0mm)
    - m_screwDia: Screw diameter (default: 3.0mm)
    - m_nutTh: Nut thickness (default: 2.4mm)
    - m_nutF2F: Nut flat-to-flat (default: 5.45mm)
    - m_distanceMM1111: Nut corner-to-corner (default: 6.10mm)
    - m_distanceMM11111: Washer thickness (default: 1.0mm)
    - m_distanceMM111111: Pogo pin length (default: 16mm)
    - m_buttonCreate: Generate fixture button
    - m_buttonCancel: Cancel button
    """
```

**Note**: Current implementation has hardcoded path in `onCreateClick()` - this should be updated to use dialog values!

---

## 3. 🔒 SECURITY & DATA PRIVACY (HIGH PRIORITY)

### 3.1 Security Overview

**CRITICAL**: This project contains security measures to prevent sensitive personal data from being committed to the repository. All contributors and AI assistants MUST follow these guidelines.

**Security Principle**: Never commit personal paths, usernames, company names, or any identifying information to version control.

---

### 3.2 Protected Data Types

**NEVER commit files containing**:

1. **Personal File Paths**:
   - ❌ `C:\Users\JohnDoe\...`
   - ❌ `/home/username/...`
   - ❌ OneDrive paths with names/companies
   - ✅ Use environment variables or config templates

2. **Personal Information**:
   - ❌ Usernames (except in author attribution)
   - ❌ Company names (except in author attribution)
   - ❌ Email addresses (except public project contacts)
   - ❌ Computer names, network paths

3. **Configuration Data**:
   - ❌ `sync_to_kicad_config.ps1` (personal config)
   - ❌ `*_local.toml`, `*_config_local.*`
   - ❌ IDE workspace files with paths
   - ✅ Use `.template` files for examples

4. **Development Artifacts**:
   - ❌ Personal test boards with identifying names
   - ❌ Example paths from your machine
   - ❌ Debug output with sensitive data

---

### 3.3 Security Files & Configuration

**Files in Repository**:

```
.gitignore                          # Comprehensive exclusion rules
sync_to_kicad_config.ps1.template  # Template (safe to commit)
sync_to_kicad_config.ps1            # Personal config (NEVER commit)
SECURITY.md                         # Security guidelines
```

**.gitignore Coverage**:
```gitignore
# Personal configuration (CRITICAL)
sync_to_kicad_config.ps1
*_config_local.ps1
*_local.toml
*.local.*

# IDE directories (contains personal paths)
.vscode/
.idea/

# Copy files (often contain test data)
*Copy*.py
*Copy*.bat
*Copy*.sh
*Copy*.md

# Generated outputs
fixture*/
*.dxf  # Except examples
*.log
```

---

### 3.4 Secure Coding Patterns

**Pattern 1: External Configuration**

❌ **BAD - Hardcoded Path**:
```powershell
# sync_to_kicad.ps1
$PluginsDir = "C:\Users\JohnDoe\Documents\KiCad\9.0\3rdparty\plugins"
```

✅ **GOOD - External Config**:
```powershell
# sync_to_kicad.ps1
$ConfigFile = Join-Path $RepoDir "sync_to_kicad_config.ps1"
if (Test-Path $ConfigFile) {
    . $ConfigFile  # Loads $PluginsDir from external file
}
```

**Pattern 2: Auto-Detection with Fallback**

✅ **GOOD - Standard Paths**:
```powershell
$DefaultPaths = @(
    "$env:APPDATA\kicad\9.0\3rdparty\plugins",
    "$HOME/.local/share/kicad/9.0/3rdparty/plugins"
)
foreach ($Path in $DefaultPaths) {
    if (Test-Path $Path) {
        $PluginsDir = $Path
        break
    }
}
```

**Pattern 3: Relative Paths**

✅ **GOOD - Repository-Relative**:
```python
from pathlib import Path

# Get repository root
repo_dir = Path(__file__).parent.parent
config_file = repo_dir / "fixture_config.toml"
```

❌ **BAD - Absolute Path**:
```python
config_file = "C:/Users/JohnDoe/projects/openfixture/fixture_config.toml"
```

**Pattern 4: Template System**

✅ **GOOD - Template + Personal Config**:
```powershell
# Commit: sync_to_kicad_config.ps1.template
# User creates: sync_to_kicad_config.ps1 (local only)

# In documentation:
"Copy sync_to_kicad_config.ps1.template to sync_to_kicad_config.ps1"
```

---

### 3.5 Security Checklist for Code Changes

Before committing any code:

- [ ] **No personal paths**: Search for `C:\Users`, `/home/username`
- [ ] **No usernames**: Search for your username in paths
- [ ] **No company names**: Check for company-specific paths
- [ ] **Use templates**: New config? Create `.template` version
- [ ] **Update .gitignore**: New sensitive file types? Add pattern
- [ ] **Test with others**: Will this work on different machines?
- [ ] **Check git status**: `git status --ignored` to verify exclusions
- [ ] **Review diff**: `git diff` before commit

**Quick Verification**:
```bash
# Search for potentially sensitive data
git grep "C:\\Users\\"
git grep "your-username"
git grep "your-company"

# Check what's being ignored
git status --ignored

# Verify config file is excluded
git check-ignore sync_to_kicad_config.ps1
```

---

### 3.6 Security Guidelines for AI Assistants

When generating or modifying code:

1. **Never generate hardcoded paths**
   - Use environment variables: `$env:APPDATA`, `$HOME`, `%USERPROFILE%`
   - Use relative paths: `$PSScriptRoot`, `__file__`
   - Use standard locations: `~/.local/share`, `$env:APPDATA`

2. **Always use configuration files**
   - Create `.template` files for examples
   - Load config from external files
   - Provide auto-detection as fallback

3. **Document security in code**
   - Add comments explaining security measures
   - Reference SECURITY.md in docstrings
   - Warn about sensitive data in function docs

4. **Default to secure**
   - When suggesting paths, use placeholders: `<your-path-here>`
   - When creating examples, use generic names: `user`, `username`
   - Always mention .gitignore when adding new file types

5. **Validate before committing**
   - When asked to commit, first check for sensitive data
   - Suggest running security verification commands
   - Remind user to review changes

**Example AI Response**:
```
"I'll create the script with a configuration template system. 
The personal config file will be excluded from git via .gitignore.
Remember to copy the template and never commit your personal config!"
```

---

### 3.7 Quick Security Reference

**⚡ Fast Pre-Commit Checks**

```bash
# One-line security scan (run before every commit)
git diff --cached | grep -iE "(C:\\\\Users|/home/[^/]+/|OneDrive.*-|username|company)" && echo "⚠️  STOP: Sensitive data found!" || echo "✅ Clean"

# PowerShell version
git diff --cached | Select-String -Pattern "C:\\Users\\[^\\]+|OneDrive.*-.*Inc" -CaseSensitive:$false
```

**🔒 Common Mistakes to Avoid**

| ❌ Don't Do This | ✅ Do This Instead |
|-----------------|-------------------|
| `C:\Users\John\...` | `$env:USERPROFILE\...` or config file |
| `$PluginsDir = "C:\My\Path"` | Load from `sync_to_kicad_config.ps1` |
| `example_board.kicad_pcb` in repo | Add `*.kicad_pcb` to `.gitignore` |
| Author: "John Doe - ACME Corp" | Author: Project contact only |
| `git add .` blindly | `git diff --cached` first, then commit |

**🛡️ Security Best Practices**

1. **Always use configuration templates**
   - Commit: `config.template` 
   - Ignore: `config.local` or actual config file
   - Document: How to copy and customize

2. **Verify before pushing**
   ```bash
   # What will be pushed?
   git log origin/master..HEAD --oneline
   
   # Check commit messages too
   git log --oneline -5 | grep -iE "company|username"
   ```

3. **If you accidentally commit sensitive data**
   ```bash
   # Amend last commit (if not pushed)
   git commit --amend
   
   # Remove from history (if already pushed - use carefully)
   git reset --hard HEAD~1
   git push --force
   ```

**📋 File Types to Always Protect**

```gitignore
# Configuration files with paths
*_config.ps1          # Except .template files
*_local.*             # Any local config
*.local.*             # Alternative pattern

# IDE settings with machine-specific paths
.vscode/settings.json
.idea/workspace.xml

# Personal test data
*_test_local.*
*_personal.*
my_*.*
```

**💡 Pro Tips**

- Set up a git pre-commit hook to auto-scan for sensitive data
- Use `git secrets` tool or similar for automatic detection
- Keep personal config in a separate, non-tracked directory
- Review PR diffs carefully - GitHub shows full paths in diffs
- Use environment variable names that don't reveal info: ❌ `ACME_CORP_PATH` ✅ `KICAD_PLUGIN_DIR`

---

### 3.7 Handling Existing Sensitive Data

If sensitive data is already committed:

**Option 1: Rewrite Recent History** (if not pushed):
```bash
git rebase -i HEAD~5  # Last 5 commits
# Mark commits with "edit" or "drop"
```

**Option 2: BFG Repo Cleaner** (for entire history):
```bash
# Download from: https://rtyley.github.io/bfg-repo-cleaner/
java -jar bfg.jar --delete-files "sync_to_kicad_config.ps1"
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

**Option 3: Filter Branch** (manual):
```bash
git filter-branch --tree-filter \
  'rm -f sync_to_kicad_config.ps1' HEAD
```

⚠️ **WARNING**: These rewrite history. Coordinate with team before using!

---

### 3.8 Security Resources

**Documentation**:
- [SECURITY.md](SECURITY.md) - Comprehensive security guidelines
- [SECURITY_REVIEW_SUMMARY.md](SECURITY_REVIEW_SUMMARY.md) - Audit report
- [.gitignore](.gitignore) - Exclusion patterns with comments

**Quick Reference**:
```bash
# Before committing:
git diff                          # Review changes
git status --ignored             # Check ignored files
grep -r "your-username" .        # Search for personal data

# After committing (before push):
git log -p -1                    # Review last commit
git show HEAD:path/to/file       # Check specific file
```

**External Resources**:
- GitHub: [Removing Sensitive Data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- OWASP: [Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)

---

### 3.9 Security Status

**Current Security Posture**: ✅ SECURE

**Implemented Protections**:
- ✅ Comprehensive .gitignore (165 lines)
- ✅ Configuration template system
- ✅ Auto-detection for standard paths
- ✅ Security documentation (280+ lines)
- ✅ All hardcoded paths removed from tracked files
- ✅ IDE configurations excluded
- ✅ Personal config files excluded

**Verified Clean**:
- ✅ No personal usernames in code paths
- ✅ No company names in file paths
- ✅ No hardcoded sensitive data
- ✅ Author attribution only (legitimate)
- ✅ Documentation examples only (for education)

**Last Security Audit**: February 15, 2026

---

## 4. OpenSCAD Integration

### 4.1 openfixture.scad Overview

**Purpose**: Parametric 3D model of test fixture with laser-cut export

**Key Features**:
- ✅ Parametric design (all dimensions calculated from inputs)
- ✅ Multiple output modes (3D model, laser-cut DXF, validation)
- ✅ Hinged clamshell design for easy PCB loading
- ✅ Pogo pin receptacle placement at test points
- ✅ M3 hardware assembly (screws, nuts, washers)
- ✅ Automatic hinge placement based on test point geometry

**Output Modes**:
```openscad
// Mode selection (set by GenFixture.py)
mode = "3dmodel";      // 3D rendering (PNG output)
mode = "lasercut";     // Laser-cuttable DXF layout
mode = "validate";     // Overlay track DXF for verification
mode = "testcut";      // Small test piece for material fit
```

---

### 4.2 Key Parameters

**Input from GenFixture.py**:
```openscad
// Test point array [[x1,y1], [x2,y2], ...]
test_points = [[17.95,5.83], [35.47,27.73], ...];

// Minimum Y coordinate of test points (for hinge placement)
tp_min_y = 13.7;

// PCB files (DXF exports)
pcb_outline = "./fixture/example_board-outline.dxf";
pcb_track = "./fixture/example_board-track.dxf";

// PCB dimensions
pcb_x = 54;          // PCB width (mm)
pcb_y = 30;          // PCB height (mm)
pcb_th = 1.6;        // PCB thickness (mm)
pcb_support_border = 1;  // Support ledge width (mm)

// Revision string
rev = "rev.1";

// Material thickness
mat_th = 3.0;

// Hardware dimensions
screw_thr_len = 16;     // Screw thread length (mm)
screw_d = 3.0;          // Screw diameter (mm)
nut_od_f2f = 5.45;      // Nut flat-to-flat (mm)
nut_od_c2c = 6.0;       // Nut corner-to-corner (mm)
nut_th = 2.25;          // Nut thickness (mm)
washer_th = 0;          // Washer thickness (mm, optional)

// Pogo pin dimensions
pogo_r = 1.5 / 2;                    // Receptacle radius (mm)
pogo_uncompressed_length = 8;        // Uncompressed length (mm)
pogo_compression = 1;                // Target compression (mm)
```

**Derived Calculations**:
```openscad
// Hinge placement algorithm
// Ensures pogo pins contact PCB at ~89.5° angle under compression
min_angle = 89.5;

// Calculate required back offset from hinge to furthest test point
active_y_back_offset = (pow(pogo_compression, 2) / 
                        (cos(min_angle) * 2 * pogo_compression)) 
                       - pivot_support_r - tp_min_y;

// Active work area offsets (for hardware clearance)
active_x_offset = 2 * mat_th + nut_od_f2f + 2;
active_y_offset = 2 * mat_th + nut_od_f2f + 2;

// Head (top clamshell) dimensions
head_x = work_area_x + 2 * active_x_offset;
head_y = work_area_y + active_y_offset + active_y_back_offset;
head_z = screw_thr_len - nut_th;

// Base (bottom clamshell) dimensions
base_x = head_x + 2 * mat_th;
base_y = head_y + pivot_support_d;
base_z = screw_thr_len + 3 * mat_th;
```

---

### 4.3 Key Modules

**Test Cut Module**:
```openscad
module testcut() {
    // Small test piece to verify:
    // 1. Material thickness fits tongue/groove joints
    // 2. Screw holes are correct size
    // 3. T-nut capture mechanism works
    // 4. Hex nut holes fit properly
}
```

**Head Side Module**:
```openscad
module head_side() {
    // Side panel of top clamshell
    // Features:
    // - Pivot point (rounded corner)
    // - Tongue/groove joints
    // - T-nut screw holes
}
```

**Base Module**:
```openscad
module base() {
    // Bottom clamshell assembly
    // Features:
    // - PCB support ledge
    // - Pogo pin receptacle holes
    // - Pivot point
    // - Locking mechanism
}
```

**Head Module**:
```openscad
module head() {
    // Top clamshell assembly
    // Features:
    // - Pogo pin compression surface
    // - PCB outline cutout
    // - Hinged attachment to base
}
```

**Laser Cut Layout**:
```openscad
module lasercut() {
    // Arranges all parts on a single sheet for laser cutting
    // Layout:
    // - Base (largest part)
    // - Head panels
    // - Side panels
    // - Support structures
    // - Locking tabs
    // All parts padded by laser_pad spacing
}
```

---

## 5. Data Flow & File Formats

### 5.1 Input: KiCAD PCB File (.kicad_pcb)

**Format**: S-expression text file

**Relevant Data Extracted**:
```lisp
(kicad_pcb
  (general
    (thickness 1.6)          ; PCB thickness
    (revision "rev_11")      ; Revision
  )
  
  (module Package_TO_SOT_SMD:SOT-23
    (at 25.4 15.24)          ; Module position
    (pad "1" smd rect
      (at 0 0.95)            ; Pad offset
      (size 0.8 0.9)         ; Pad size
      (layers F.Cu F.Mask)   ; No F.Paste = test point!
    )
  )
  
  (gr_line                   ; Board outline
    (start 0 0)
    (end 50 0)
    (layer Edge.Cuts)
  )
)
```

**Test Point Selection Logic**:
1. Iterate all modules (footprints)
2. Iterate all pads in each module
3. Include pad if:
   - On selected layer (F.Cu or B.Cu)
   - Is SMD pad (`PAD_ATTRIB_SMD`)
   - NOT on paste layer (F.Paste or B.Paste)
   - NOT on ignore layer (Eco1.User) OR
   - ON force layer (Eco2.User)

**Layer Manipulation**:
```python
# Mark pad as test point (force include)
# Add Eco2.User to pad layers in KiCAD

# Exclude pad from test point (ignore)
# Add Eco1.User to pad layers in KiCAD
```

---

### 5.2 Intermediate: DXF Files

**Generated by GenFixture.py**:

**outline.dxf**:
- **Content**: Board outline from Edge.Cuts layer
- **Purpose**: Imported by OpenSCAD for PCB cutout
- **Coordinate System**: Origin at top-left of board

**track.dxf**:
- **Content**: Copper tracks from selected layer (F.Cu or B.Cu)
- **Purpose**: Visual verification of test point alignment
- **Usage**: Overlay in OpenSCAD validate mode

**Export Configuration**:
```python
popt.SetDXFPlotUnits(DXF_PLOTTER.DXF_UNIT_MILLIMETERS)
popt.SetDXFPlotPolygonMode(True)     # Filled shapes
popt.SetUseAuxOrigin(True)           # Origin at board top-left
popt.SetMirror(self.mirror)          # Mirror if back layer
```

---

### 5.3 Output: Generated Files

**fixture.dxf** (lasercut mode):
- **Content**: All fixture parts laid out for laser cutting
- **Format**: 2D DXF, millimeters
- **Usage**: Send to laser cutter service
- **Materials**: Acrylic, plywood, MDF, etc.
- **Parts Included**:
  - Base plate
  - Head plates
  - Side panels (2x)
  - Support structures
  - Locking tabs

**fixture.png** (3dmodel mode):
- **Content**: 3D rendered image of assembled fixture
- **Purpose**: Visual preview before fabrication
- **Shows**: Complete assembly with PCB, pogo pins, hardware

**test.dxf** (testcut mode):
- **Content**: Small test piece
- **Purpose**: Verify material fit before full cut
- **Tests**:
  - Tongue/groove joint fit
  - Screw hole sizing
  - Nut capture mechanism
  - T-nut alignment

---

## 6. Hardware & Assembly

### 6.1 Bill of Materials (BOM)

**Required Hardware** (for typical fixture):
```
Quantity  Part              Size        Notes
--------  ----              ----        -----
4-6       Machine Screws    M3×16mm     Thread length ≥14mm
4-6       Hex Nuts          M3          Flat-to-flat: 5.45mm
4-6       Washers           M3          Thickness: 1mm (optional)
N         Pogo Pins         -           N = number of test points
N         Pogo Receptacles  -           2-part recommended
1         Laser Cut Parts   -           From fixture.dxf
```

**Material Selection**:
- **Acrylic**: 2.45mm–3mm (most common)
- **Plywood**: 3mm birch (budget option)
- **MDF**: Not recommended (low precision)

**Pogo Pin Specifications**:
- **Type**: 2-part receptacle + replaceable pin
- **Pitch**: 1.27mm or 2.54mm (standard SMD pitch)
- **Force**: 75–100g typical
- **Travel**: 1mm compression target
- **Receptacle Diameter**: 1.5mm (undersized, drill to final size)

---

### 6.2 Assembly Instructions

**Step 1: Test Material Fit**
```
1. Laser cut test.dxf on your material
2. Verify tongue/groove joints fit snugly
3. Test screw and nut hole sizing
4. Adjust material thickness parameter if needed
```

**Step 2: Cut Fixture Parts**
```
1. Laser cut fixture.dxf
2. Separate parts (base, head, sides, tabs)
3. Remove any residue/char from edges
```

**Step 3: Install Pogo Receptacles**
```
1. Carefully drill out pogo holes (#50 drill bit = 1.78mm)
2. Press-fit pogo receptacles into base
3. Verify perpendicular alignment
```

**Step 4: Assemble Base**
```
1. Insert side panels into base (tongue/groove joints)
2. Install T-nuts in screw channels
3. Tighten screws to secure sides
```

**Step 5: Assemble Head**
```
1. Attach head panels to head plate
2. Install capture nuts for locking mechanism
3. Attach to base via pivot screws (leave loose for movement)
```

**Step 6: Final Adjustments**
```
1. Test clamshell operation (should open/close smoothly)
2. Load PCB into fixture
3. Close head and verify pogo pin alignment
4. Adjust pogo pin compression (should be ~1mm)
```

---

### 6.3 Fixture Dimensions & Constraints

**Minimum Board Size**: ~20mm × 20mm (below this, fixture becomes impractical)

**Maximum Board Size**: Limited by:
- Laser cutter bed size (typically 300mm × 400mm)
- Material availability
- Pogo pin force (more pins = harder to close)

**Hinge Placement**:
```
The hinge is automatically positioned to ensure pogo pins
contact the PCB at ~89.5° angle under 1mm compression.

This is calculated from:
- tp_min_y: Distance from top edge to nearest test point
- pogo_uncompressed_length: Extended pogo pin length
- pogo_compression: Target compression (1mm typical)
- min_angle: 89.5° (near perpendicular contact)
```

**Clearance Requirements**:
```
active_x_offset = 2 * mat_th + nut_od_f2f + 2
  Provides space for:
  - Side panel material
  - Screw head clearance
  - Assembly tolerance

active_y_offset = 2 * mat_th + nut_od_f2f + 2
  Provides space for:
  - Front panel material
  - Latching mechanism
  - PCB insertion clearance

active_y_back_offset = (calculated from hinge geometry)
  Provides space for:
  - Hinge pivot point
  - Test point access at correct angle
  - PCB removal clearance
```

---

## 7. Workflow Patterns

### 7.1 Initial Fixture Generation

**Workflow**:
```
1. Design PCB in KiCAD
   - Ensure test pads have NO paste mask
   - Optionally mark pads with Eco2.User (force) or Eco1.User (ignore)

2. Measure physical parameters
   - Material thickness (calipers)
   - PCB thickness
   - Screw dimensions
   - Nut dimensions

3. Create project-specific wrapper script
   - Copy genfixture.sh or genfixture.bat
   - Update all parameters
   - Save as <project>_fixture.sh/.bat

4. Run fixture generation
   ./my_project_fixture.sh path/to/board.kicad_pcb

5. Review outputs
   - fixture.png: Visual verification
   - track.dxf overlay: Test point alignment
   - fixture.dxf: Laser-cut ready

6. Test cut validation
   - Cut test.dxf
   - Verify all fits
   - Adjust parameters if needed

7. Production cut
   - Send fixture.dxf to laser service
   - Order pogo pins and hardware
   - Assemble fixture

8. Test and iterate
   - Load PCB and verify alignment
   - Adjust compression if needed
   - Document any issues
```

---

### 7.2 PCB Revision Updates

**When PCB layout changes**:
```
1. Export updated .kicad_pcb file

2. Check if test points changed
   - Same locations? → Re-run script (no edits needed)
   - New test points? → Re-run script (fixture auto-updates)
   - Different PCB size? → Update pcb_x/pcb_y, re-run

3. Re-run generation
   ./my_project_fixture.sh path/to/board_v2.kicad_pcb

4. Compare outputs
   - Use version control (Git) to see diffs
   - fixture.dxf changes = new laser cut needed
   - fixture.png changes = visual verification

5. Fabricate updated fixture
   - Cut new fixture.dxf
   - Reuse hardware if possible
   - Update revision marking
```

---

### 7.3 Multi-Board Projects

**Strategy for multiple PCB variants**:

**Option 1: Wrapper Script per Board**
```bash
# board_v1_fixture.sh
BOARD="board_v1.kicad_pcb"
OUTPUT="fixture-v1"
PCB=1.6
# ... run GenFixture.py

# board_v2_fixture.sh
BOARD="board_v2.kicad_pcb"
OUTPUT="fixture-v2"
PCB=0.8  # Different thickness!
# ... run GenFixture.py
```

**Option 2: Master Script with Arguments**
```bash
#!/bin/sh
# fixture_gen.sh <board_file> <output_dir> <pcb_thickness>

BOARD=$1
OUTPUT=$2
PCB=$3

# Shared parameters (same across all boards)
MAT=2.45
SCREW_LEN=16.0
# ...

python GenFixture.py --board $BOARD --out $OUTPUT --pcb_th $PCB ...
```

**Usage**:
```bash
./fixture_gen.sh board_v1.kicad_pcb fixture-v1 1.6
./fixture_gen.sh board_v2.kicad_pcb fixture-v2 0.8
./fixture_gen.sh board_v3.kicad_pcb fixture-v3 1.2
```

---

### 7.4 Version Control Best Practices

**Git Strategy**:
```
.gitignore:
--------------------
# Ignore generated files
fixture-*/           # Output directories
*.png               # Rendered images
*.dxf               # DXF exports

# Keep these:
# *.py (all Python scripts)
# *.sh, *.bat (wrapper scripts)
# *.scad (OpenSCAD model)
# *.md (documentation)
```

**Commit Message Pattern**:
```
feat: Add fixture generation for Board_v2
- PCB thickness: 0.8mm
- Test points: 12
- Material: 2.45mm acrylic

fix: Adjust hinge offset for smaller boards
- Reduced active_y_back_offset calculation
- Added min_board_size constraint

docs: Update BOM for new screw length
- Changed from M3×14mm to M3×16mm
- Updated nut specifications
```

---

## 8. Common Issues & Troubleshooting

### 8.1 Test Point Detection Issues

**Problem**: No test points found
```
WARNING, ABORTING: No test points found!
Verify that the pcbnew file has test points specified
or use the --flayer option to force test points
```

**Causes & Solutions**:

**Cause 1: All pads have paste mask**
```
Solution: In KiCAD Pad Properties:
1. Double-click pad
2. Uncheck "Paste" in Copper and Tech Layers section
3. This exposes pad for test probe access
```

**Cause 2: Pads are THT (through-hole)**
```
Solution: GenFixture only detects SMD pads
- Use SMD test pads
- Or add Eco2.User layer to THT pads (force include)
```

**Cause 3: Wrong layer selected**
```
Solution: Verify --layer argument
- Use "F.Cu" for top-side testing
- Use "B.Cu" for bottom-side testing
```

**Cause 4: Pads marked as ignored**
```
Solution: Check Eco1.User layer
- Eco1.User = force ignore (excluded from test points)
- Remove this layer from pads you want to test
```

---

### 8.2 OpenSCAD Execution Errors

**Problem**: OpenSCAD not found
```
'openscad' is not recognized as an internal or external command
```

**Solution (Windows)**:
```batch
REM Add to PATH in genfixture.bat
IF EXIST "C:\Program Files\OpenSCAD" SET PATH=%PATH%;"C:\Program Files\OpenSCAD\"

REM Or install OpenSCAD to default location
REM Download from: https://openscad.org/downloads.html
```

**Solution (Linux)**:
```bash
# Install OpenSCAD
sudo apt-get install openscad

# Or use snap
sudo snap install openscad
```

---

### 8.3 Coordinate/Alignment Issues

**Problem**: Pogo pins misaligned with test pads

**Diagnosis**:
```
1. Open track.dxf in fixture output directory
2. Compare with pogo pin locations in fixture.dxf
3. Look for offset patterns
```

**Cause 1: Origin mismatch**
```
Solution: Verify board origin calculation
- Check GetOriginDimensions() output
- Board origin should be at top-left corner
- Both Edge.Cuts and components affect origin
```

**Cause 2: Mirror issues (back side)**
```
Solution: Verify mirror setting
- self.mirror = True if layer == B.Cu
- Coordinates should flip: x_new = pcb_width - x_old
- Check pcb_th setting (affects Z-axis offset)
```

**Cause 3: Rounding errors**
```
Solution: Check Round() precision
- Default: 0.01mm (10 microns)
- Laser cutter tolerance: ~0.1mm
- Manual adjustment: tp_correction_offset_x/y in .scad
```

---

### 8.4 Material/Hardware Fit Issues

**Problem**: Tongue/groove joints too tight/loose

**Solution**:
```openscad
// Adjust kerf in openfixture.scad
kerf = 0.125;  // Increase if joints too tight
kerf = 0.100;  // Decrease if joints too loose

// Kerf accounts for laser beam width
// Typically 0.1-0.2mm for acrylic
```

**Problem**: Screws don't fit

**Solution**:
```python
# In genfixture.sh/.bat, verify:
--screw_d 3.0      # M3 = 3.0mm
--screw_len 16.0   # Measure threaded length only

# If screws are imperial:
# #4-40 ≈ 2.9mm diameter
# #6-32 ≈ 3.5mm diameter
```

**Problem**: Nuts don't fit in captures

**Solution**:
```bash
# Measure actual nut dimensions with calipers
# Flat-to-flat (hexagon side):
--nut_f2f 5.45

# Corner-to-corner (hexagon diagonal):
--nut_c2c 6.10

# Thickness:
--nut_th 2.4

# Note: Nut dimensions vary by manufacturer!
```

---

### 8.5 Pogo Pin Issues

**Problem**: Pogo pins not making contact

**Diagnosis**:
```
1. Measure pogo pin uncompressed length
2. Check pogo_compression in .scad (should be ~1mm)
3. Verify PCB is fully seated in fixture
4. Check hinge geometry (min_angle = 89.5°)
```

**Solution**:
```bash
# Adjust pogo pin length parameter
--pogo-uncompressed-length 16  # Increase for more compression

# Or modify OpenSCAD directly:
pogo_uncompressed_length = 16;   # Extended length (mm)
pogo_compression = 1.5;           # Increase compression target
```

**Problem**: Pogo pins too tight (hard to close fixture)

**Solution**:
```
1. Reduce number of test points (use ignore layer)
2. Use lower-force pogo pins (50g vs 100g)
3. Increase pogo receptacle diameter slightly
4. Consider spring-loaded fixture design
```

---

### 8.6 OpenSCAD Rendering Issues

**Problem**: Invalid DXF import errors

**Diagnosis**:
```
TRACE: DXF Import: File 'outline.dxf' ($fn defaults to 0)
ERROR: Could not import DXF file
```

**Cause 1: Missing DXF files**
```
Solution: Verify GenFixture.py completed successfully
- Check output directory for outline.dxf and track.dxf
- Re-run GenFixture.py if files missing
```

**Cause 2: Path separators (Windows)**
```
Problem: Path uses backslashes in .scad
pcb_outline = "C:\path\to\file.dxf"  # ERROR!

Solution: GenFixture.py handles this:
- Windows: Uses \\ for paths
- Linux/Mac: Uses / for paths
```

**Cause 3: Invalid DXF version**
```
Solution: KiCAD exports DXF R12 (compatible)
- If editing DXF manually, save as R12 format
- OpenSCAD supports DXF R12, R14, R2000
```

---

## 9. Advanced Customization

### 8.1 Modifying OpenSCAD Design

**Common Customizations**:

**1. Change pogo pin size**:
```openscad
// Current:
pogo_r = 1.5 / 2;  // 1.5mm diameter

// For larger pins (2mm):
pogo_r = 2.0 / 2;
```

**2. Adjust locking mechanism**:
```openscad
// Current:
tab_width = 3 * mat_th;
tab_length = 4 * mat_th + washer_th;

// For stronger latch (wider tab):
tab_width = 4 * mat_th;
```

**3. Add alignment pins**:
```openscad
module alignment_pin() {
    // Add 2mm dowel pin holes at PCB corners
    translate([pcb_x/2, pcb_y/2])
    circle(r=1.0);
}

// Add to base() and head() modules
```

**4. Change work area size** (reusable base):
```openscad
// Instead of:
work_area_x = pcb_x;
work_area_y = pcb_y;

// Use fixed size:
work_area_x = 100;  // Fits all boards ≤100mm
work_area_y = 100;

// Then create board-specific "carrier" inserts
```

---

### 8.2 Extending GenFixture.py

**Add Custom Test Point Filter**:
```python
# In GetTestPoints() method, add filtering logic:

def GetTestPoints(self):
    for m in self.brd.GetModules():
        for p in m.Pads():
            # Existing filters...
            if (p.IsOnLayer(self.layer) and
                p.GetAttribute() == PAD_ATTRIB_SMD and
                not p.IsOnLayer(self.paste)):
                
                # NEW: Filter by net name
                net_name = p.GetNetname()
                if net_name.startswith("GND"):
                    continue  # Skip ground pads
                
                # NEW: Filter by pad size
                size = p.GetSize()
                if size.x < FromMM(0.5):  # Skip tiny pads
                    continue
                
                # Extract coordinates (existing code)
                tp = ToMM(p.GetPosition())
                # ...
```

**Add CSV Export**:
```python
# After GetTestPoints(), export to CSV:

def ExportTestPointsCSV(self, path):
    import csv
    
    csv_path = os.path.join(path, self.prj_name + "-testpoints.csv")
    
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['X_mm', 'Y_mm', 'Net', 'Pin'])
        
        for tp in self.test_points:
            writer.writerow([tp[0], tp[1], tp[2], tp[3]])
    
    print(f"Test points exported: {csv_path}")

# Call in Generate():
self.ExportTestPointsCSV(path)
```

**Add BOM Generation**:
```python
def GenerateBOM(self, path):
    bom = {
        "Screws": f"M{self.screw_d} × {self.screw_len}mm",
        "Nuts": f"M{self.screw_d} Hex",
        "Washers": f"M{self.screw_d} ({self.washer_th}mm thick)" if self.washer_th else "N/A",
        "Pogo Pins": len(self.test_points),
        "Material": f"{self.mat_th}mm thick, {self.dims[0]} × {self.dims[1]}mm",
    }
    
    bom_path = os.path.join(path, self.prj_name + "-BOM.txt")
    
    with open(bom_path, 'w') as f:
        f.write(f"BOM for {self.prj_name} Fixture\n")
        f.write("=" * 40 + "\n\n")
        for item, qty in bom.items():
            f.write(f"{item:20} {qty}\n")
    
    print(f"BOM generated: {bom_path}")
```

---

### 8.3 KiCAD Plugin Improvements

**Current Issue**: Hardcoded path in OpenFixture_Dlg.onCreateClick()

**Solution**: Read GUI values and construct command:
```python
def onCreateClick(self, event):
    # Get current board
    board = pcbnew.GetBoard()
    board_path = board.GetFileName()
    
    # Get values from dialog
    pcb_th = self.m_PcbTh.GetValue()
    rev = self.m_rev.GetValue()
    layer = "F.Cu" if self.m_checkLayerTop.GetValue() else "B.Cu"
    screw_len = self.m_screwLen.GetValue()
    screw_d = self.m_screwDia.GetValue()
    nut_th = self.m_nutTh.GetValue()
    nut_f2f = self.m_nutF2F.GetValue()
    washer_th = self.m_distanceMM11111.GetValue()
    pogo_len = self.m_distanceMM111111.GetValue()
    
    # Get material thickness (add to dialog!)
    mat_th = "2.45"  # TODO: Add to dialog
    
    # Construct command
    cmd = [
        "python", "GenFixture.py",
        "--board", board_path,
        "--layer", layer,
        "--rev", rev,
        "--mat_th", mat_th,
        "--pcb_th", pcb_th,
        "--out", f"fixture-{rev}",
        "--screw_len", screw_len,
        "--screw_d", screw_d,
        "--nut_th", nut_th,
        "--nut_f2f", nut_f2f,
        "--washer_th", washer_th,
        "--pogo-uncompressed-length", pogo_len,
    ]
    
    # Run command
    import subprocess
    subprocess.run(cmd)
    
    # Show completion message
    wx.MessageBox(f"Fixture generated in fixture-{rev}/", 
                  "Complete", wx.OK | wx.ICON_INFORMATION)
    
    return self.EndModal(wx.ID_OK)
```

**Add Material Thickness to Dialog** (requires editing OpenFixtureDlg.py in wxFormBuilder).

---

## 10. Best Practices

### 9.1 PCB Design for Testing

**Do's**:
- ✅ Place test pads in accessible locations (avoid under components)
- ✅ Use consistent test pad size (≥0.5mm diameter for pogo pins)
- ✅ Remove solder mask AND paste mask from test pads
- ✅ Use clear net naming for troubleshooting
- ✅ Group test points in grid pattern when possible

**Don'ts**:
- ❌ Don't place test points on PCB edges (clearance needed)
- ❌ Don't mix THT and SMD test points (GenFixture only handles SMD)
- ❌ Don't use paste-covered pads as test points
- ❌ Don't place test points under tall components (pogo clearance)
- ❌ Don't space test points <2mm apart (pogo pin crosstalk)

**Test Pad Recommendations**:
```
Size: 1.0–1.5mm diameter (circular) or 0.8×1.2mm (oval)
Clearance: 0.3mm to adjacent copper
Finish: ENIG or bare copper (avoid HASL if possible)
Marking: Silkscreen label for manual testing
```

---

### 9.2 Material Selection

**Acrylic** (best for most cases):
- ✅ Precise laser cutting (±0.05mm)
- ✅ Transparent (visual inspection)
- ✅ Rigid (dimensional stability)
- ❌ Can crack under stress
- ❌ More expensive than plywood

**Plywood** (budget option):
- ✅ Inexpensive
- ✅ Strong (less brittle)
- ✅ Easy to source
- ❌ Lower precision (±0.2mm)
- ❌ Opaque (no visual inspection)
- ❌ Variable thickness (measure each sheet!)

**MDF** (not recommended):
- ❌ Inconsistent density
- ❌ Poor edge quality
- ❌ Absorbs moisture (dimensional changes)
- ❌ Messy to cut

**Thickness Selection**:
```
2.5mm: Minimum (flexible, suitable for small fixtures)
3.0mm: Standard (good balance of strength and precision)
4.0mm: Heavy duty (large fixtures, many test points)
5.0mm: Maximum (overkill for most applications)
```

---

### 9.3 Pogo Pin Selection

**Receptacle vs. Spring-loaded**:
- **Receptacle** (recommended): Replaceable pins, easier drilling
- **Spring-loaded**: Integrated, but non-replaceable

**Force Selection**:
```
50g: Low force (many test points, hand pressure)
75g: Medium force (typical, good contact)
100g: High force (robust contact, fewer test points)
150g: Very high force (difficult to close fixture)
```

**Pin Diameter**:
```
0.68mm (0.027"): Fine pitch, ≤0.5mm pads
1.02mm (0.040"): Standard, 0.5–1.0mm pads
1.50mm (0.059"): Large pads, >1.0mm
2.00mm (0.079"): Power pads, high current
```

**Travel/Compression**:
```
Recommended: 1mm compression at contact
Minimum: 0.5mm (unreliable contact)
Maximum: 2mm (excessive force, pin damage)
```

---

### 9.4 Maintenance & Troubleshooting

**Regular Maintenance**:
```
1. Clean pogo pins after every 50–100 uses
   - Isopropyl alcohol (IPA)
   - Cotton swabs
   - Avoid compressed air (embeds debris)

2. Inspect pogo pin alignment
   - Check for bent pins
   - Verify perpendicular insertion
   - Replace damaged pins immediately

3. Check screw tightness
   - Loose screws → misalignment
   - Tighten to finger-tight + 1/4 turn

4. Verify fixture flatness
   - Lay on granite surface plate
   - Check for warping/bowing
   - Re-cut if >0.5mm out of flat
```

**Lifecycle**:
```
Pogo pins: 10,000–100,000 cycles (depending on force/quality)
Laser cut parts: Indefinite (if stored flat and dry)
Screws/nuts: 500+ assembly cycles
```

---

## 11. References & Resources

### 10.1 Dependencies

**Required Software**:
- **KiCAD** 7.0+ (pcbnew API): https://www.kicad.org/
- **OpenSCAD** 2015.03+: https://openscad.org/
- **Python** 3.6+ (included with KiCAD on Windows)

**Python Modules** (standard library):
```python
import os, sys              # File system operations
import argparse             # Command-line parsing
from pcbnew import *        # KiCAD API
import wx                   # GUI (for plugin only)
import subprocess           # OpenSCAD execution
```

---

### 10.2 External Documentation

**KiCAD Python API**:
- Official Docs: https://docs.kicad.org/doxygen/
- pcbnew Reference: Search for `pcbnew.BOARD`, `pcbnew.PAD`, etc.

**OpenSCAD**:
- Language Reference: https://openscad.org/documentation.html
- DXF Import: https://en.wikibooks.org/wiki/OpenSCAD_User_Manual/Importing_Geometry

**Laser Cutting**:
- Material Properties: https://www.troteclaser.com/en/knowledge/material-database
- Kerf Compensation: Varies by machine (test cuts recommended)

**Pogo Pins**:
- Specifications: Check manufacturer datasheet
- Common Vendors: Mill-Max, Harwin, Omron, TE Connectivity

---

### 10.3 Project Resources

**OpenFixture Documentation**:
- Main Site: http://tinylabs.io/openfixture
- BOM: http://tinylabs.io/openfixture-bom
- Assembly: http://tinylabs.io/openfixture-assembly
- KiCAD Export: http://tinylabs.io/openfixture-kicad-export

**Repository**:
- GitHub: https://github.com/tinylabs/openfixture (original)
- License: Creative Commons (CC BY-SA 4.0)

**Contributors**:

**Original Author**:
- Elliot Buller - Tiny Labs Inc (elliot@tinylabs.io)
- Website: http://tinylabs.io/openfixture
- Repository: https://github.com/tinylabs/openfixture

**v2 Modernization (February 2026)**:
- Community Contributors
- Updated to KiCAD 8.0/9.0 with modern pcbnew API
- Added TOML configuration system
- Modernized to Python 3.8+ with type hints
- Enhanced plugin UI and error handling

---

## 12. Quick Reference

### 11.1 Command Cheat Sheet

```bash
# Basic usage
python GenFixture.py --board file.kicad_pcb --mat_th 3.0 --out fixture/

# Full parameters
python GenFixture.py \
  --board board.kicad_pcb \        # Input PCB file
  --mat_th 2.45 \                  # Material thickness
  --pcb_th 1.6 \                   # PCB thickness
  --out fixture-v1 \               # Output directory
  --layer B.Cu \                   # Test point layer
  --rev rev_01 \                   # Revision string
  --screw_len 16.0 \               # Screw length
  --screw_d 3.0 \                  # Screw diameter
  --nut_th 2.4 \                   # Nut thickness
  --nut_f2f 5.45 \                 # Nut flat-to-flat
  --nut_c2c 6.10 \                 # Nut corner-to-corner
  --washer_th 1.0 \                # Washer thickness
  --border 0.8 \                   # PCB support border
  --pogo-uncompressed-length 16    # Pogo pin length
```

---

### 11.2 File Structure Summary

```
openfixture/
├── GenFixture.py              # Main script (498 lines)
├── openfixture.py             # KiCAD plugin (60 lines)
├── OpenFixtureDlg.py          # GUI dialog (228 lines)
├── openfixture.scad           # OpenSCAD model (926 lines)
├── genfixture.bat             # Windows wrapper
├── genfixture.sh              # Linux/Mac wrapper
├── README.md                  # Project documentation
├── osh_logo.dxf               # Logo graphic (optional)
└── copilot-instructions_openfixture.md  # This file

fixture-<rev>/                 # Output directory
├── <board>-outline.dxf        # Board outline
├── <board>-track.dxf          # Copper tracks (verification)
├── <board>-test.dxf           # Test cut piece
├── <board>-fixture.dxf        # MAIN OUTPUT: Laser-cut parts
└── <board>-fixture.png        # 3D Preview rendering
```

---

### 11.3 Common Parameter Values

**Material Thickness** (mat_th):
```
Acrylic:  2.45mm, 3.00mm, 4.00mm
Plywood:  3.00mm, 5.00mm
```

**PCB Thickness** (pcb_th):
```
Standard: 1.6mm
Thin:     0.8mm, 1.0mm
Thick:    2.0mm, 2.4mm
```

**M3 Hardware** (most common):
```
screw_d:  3.0mm
screw_len: 14mm, 16mm, 20mm
nut_th:   2.4mm
nut_f2f:  5.45mm
nut_c2c:  6.10mm
```

**Layer Names**:
```
F.Cu:       Front copper (top side)
B.Cu:       Back copper (bottom side)
Eco1.User:  User layer 1 (ignore marker)
Eco2.User:  User layer 2 (force marker)
```

---

## 13. Version History

**Version 1.0** (Original Release - 2016):
- Initial OpenFixture implementation
- Basic test point extraction
- OpenSCAD parametric generation
- Laser-cut DXF export

**Version 1.x** (Community Contributions):
- Windows batch file support
- Back-side test point support (B.Cu)
- Optional parameter expansion
- Validation mode (track overlay)

**Version 2.0** (Modernization - February 2026):
- **KiCAD 8.0/9.0 compatibility** - Updated to modern pcbnew API
- **Python 3 full support** - Removed Python 2 dependencies
- **TOML configuration system** - Project-specific config files
- **Improved plugin UI** - Multi-tab dialog with presets
- **Better error handling** - Comprehensive logging and validation
- **Type hints** - Full type annotations for better IDE support
- **Modular architecture** - Clean separation of concerns
- **See**: `MIGRATION_GUIDE_v2.md` for upgrade instructions

---

## 14. OpenFixture v2 - Modern Version Overview

### 13.1 New Files in v2

```
OpenFixture Project Structure (v2):
├── GenFixture_v2.py           # Modernized generator (KiCAD 8+)
├── openfixture_v2.py          # Modern plugin with better UI
├── fixture_config.toml        # Configuration file template
├── genfixture_v2.bat          # Windows wrapper v2
├── genfixture_v2.sh           # Linux/Mac wrapper v2
├── MIGRATION_GUIDE_v2.md      # Upgrade guide
│
├── GenFixture.py              # Original generator (legacy)
├── openfixture.py             # Original plugin (legacy)
├── genfixture.bat             # Original wrapper (legacy)
└── genfixture.sh              # Original wrapper (legacy)
```

### 13.2 Key Modernizations

**Modern KiCAD API Usage**:
```python
# v2 uses explicit imports and modern API
import pcbnew  # Not: from pcbnew import *

# Modern layer constants
layer = pcbnew.F_Cu  # Not: F_Cu

# Modern geometry types
origin = pcbnew.VECTOR2I(x, y)  # Not: wxPoint(x, y)

# Modern conversion functions
mm_val = pcbnew.ToMM(internal_units)  # Explicit namespace

# Modern methods
for footprint in board.GetFootprints():  # Not: GetModules()
    for pad in footprint.Pads():
        # Process pads
```

**TOML Configuration**:
```toml
# fixture_config.toml
[board]
thickness_mm = 1.6
test_layer = "F.Cu"

[material]
thickness_mm = 3.0

[hardware]
screw_diameter_mm = 3.0
screw_length_mm = 16.0
nut_thickness_mm = 2.4
nut_flat_to_flat_mm = 5.45
nut_corner_to_corner_mm = 6.10
washer_thickness_mm = 1.0
border_mm = 0.8
pogo_uncompressed_length_mm = 16.0
```

**Configuration Class**:
```python
class FixtureConfig:
    """Configuration container with TOML support"""
    
    @classmethod
    def from_toml(cls, toml_path: str) -> 'FixtureConfig':
        """Load configuration from TOML file"""
        # Supports both tomllib (Python 3.11+) and tomli
        import tomllib  # or: import tomli as tomllib
        
        config = cls()
        with open(toml_path, 'rb') as f:
            data = tomllib.load(f)
        
        # Parse configuration sections
        config.pcb_th = data.get('board', {}).get('thickness_mm', 1.6)
        # ... etc
        
        return config
```

**Modern Plugin with Better UI**:
```python
class OpenFixtureDialog(wx.Dialog):
    """Modern multi-tab dialog"""
    
    def __init__(self, parent, board_path: str):
        # Organized into tabs:
        # - Board parameters
        # - Material parameters  
        # - Hardware parameters
        # - Advanced options
        
        notebook = wx.Notebook(self)
        notebook.AddPage(self._create_board_panel(), "Board")
        notebook.AddPage(self._create_material_panel(), "Material")
        # ... etc
    
    def _load_defaults(self):
        """Auto-load from fixture_config.toml if available"""
        if Path('fixture_config.toml').exists():
            config = tomllib.load(...)
            # Populate UI fields from config
```

**Comprehensive Error Handling**:
```python
# v2 uses Python logging module
import logging
logger = logging.getLogger(__name__)

try:
    board = pcbnew.LoadBoard(args.board)
    logger.info(f"Loaded board: {args.board}")
except Exception as e:
    logger.error(f"Failed to load board: {e}", exc_info=True)
    return 1

# Progress feedback
logger.info("Extracting test points...")
logger.info(f"Found {len(test_points)} test points")
logger.info(f"Board dimensions: {dims[0]:.2f} x {dims[1]:.2f} mm")
```

### 13.3 Using v2

**Command-line with Config File**:
```bash
# Create fixture_config.toml in project directory
# Then run with config:
python3 GenFixture_v2.py \
    --board board.kicad_pcb \
    --config fixture_config.toml \
    --out fixture-rev_01

# Config values are defaults, CLI args override
python3 GenFixture_v2.py \
    --board board.kicad_pcb \
    --config fixture_config.toml \
    --mat_th 4.0 \  # Overrides config value
    --out fixture-rev_01
```

**Wrapper Script**:
```bash
# Automatically detects fixture_config.toml
./genfixture_v2.sh board.kicad_pcb

# Or use old-style with parameters
# (edit genfixture_v2.sh to set defaults)
```

**KiCAD Plugin**:
```
1. Copy to plugins directory:
   - openfixture_v2.py
   - GenFixture_v2.py
   - OpenFixture.png (icon)

2. Restart KiCAD

3. Tools → External Plugins → OpenFixture Generator

4. Fill in parameters (or use defaults from fixture_config.toml)

5. Click "Generate Fixture"

6. Output directory opens automatically on success
```

### 13.4 Migration from v1 to v2

**See**: `MIGRATION_GUIDE_v2.md` for complete upgrade instructions

**Quick Migration**:
```bash
# 1. Install alongside existing version
cp GenFixture_v2.py ./
cp openfixture_v2.py ./plugins/
cp fixture_config.toml ./

# 2. Test with existing project
python3 GenFixture_v2.py --board test.kicad_pcb --mat_th 3.0 --out test

# 3. Compare output with v1
diff -r fixture-v1/ test/

# 4. Switch when comfortable
mv genfixture.sh genfixture_v1.sh
cp genfixture_v2.sh genfixture.sh
```

**Compatibility**:
- ✅ v2 generates identical fixture geometry to v1
- ✅ v2 works with existing OpenSCAD files
- ✅ v2 can run side-by-side with v1
- ⚠️ v2 requires KiCAD 8.0+ (use v1 for older KiCAD)
- ⚠️ v2 requires Python 3.8+ (use v1 for Python 2)

### 13.5 When to Use v1 vs v2

**Use v1 (Original) if**:
- Using KiCAD 6.0 or 7.0
- Python 2 environment
- Existing workflow works fine
- Can't upgrade KiCAD yet

**Use v2 (Modern) if**:
- Using KiCAD 8.0 or 9.0 ✅ **Recommended**
- Python 3 environment
- Want TOML configuration
- Want better error messages
- Want modern plugin UI
- Starting a new project

### 13.6 V2 Feature Highlights

**Type Safety**:
```python
# v2 uses type hints throughout
def get_test_points(self) -> None:
    """Extract test points from PCB"""
    # Type hints make IDE autocomplete work better
    
def get_origin_dimensions(self) -> None:
    """Calculate board origin and dimensions"""
    # Explicit return types

def generate(self, path: str) -> bool:
    """Main generation workflow
    
    Args:
        path: Output directory path
        
    Returns:
        True if successful, False otherwise
    """
```

**Better Progress Feedback**:
```python
# v2 provides detailed progress information
logger.info("Starting fixture generation...")
logger.info("Extracting test points...")
logger.info("  tp[VCC] = (25.40, 12.70)")
logger.info("  tp[GND] = (30.48, 12.70)")
logger.info(f"Found {len(test_points)} test points")
logger.info("Board dimensions: 54.00 x 30.00 mm")
logger.info("Generating fixture with OpenSCAD...")
logger.info("Fixture generation completed successfully!")
```

**Plugin Progress Dialog**:
```python
# v2 shows progress during generation
progress = wx.ProgressDialog(
    "Generating Fixture",
    "Running GenFixture...\nThis may take a few minutes.",
    maximum=100,
    parent=parent,
    style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
)
progress.Pulse()

# ... run generation ...

progress.Update(100)
progress.Destroy()
```

**Automatic Results Display**:
```python
# v2 opens output directory on success
if success:
    wx.MessageBox("Fixture generated successfully!", ...)
    
    # Platform-specific open
    if sys.platform == 'win32':
        os.startfile(str(output_dir))
    elif sys.platform == 'darwin':
        subprocess.run(['open', str(output_dir)])
    else:
        subprocess.run(['xdg-open', str(output_dir)])
```

---

## 15. KiCAD 9.0+ API Compatibility (Production Tested)

**Status**: ✅ FULLY COMPATIBLE - Tested February 15, 2026  
**Testing**: Real board (101.82 x 69.53 mm, 51 test points) - All outputs generated successfully

### 15.1 Breaking Changes in KiCAD 9.0+

KiCAD 9.0 introduced multiple breaking API changes. OpenFixture implements **backward-compatible wrappers** that work with both KiCAD 8.0 and 9.0+.

#### **Issue 1: GetAuxOrigin/SetAuxOrigin Removal**

**Problem**:
```python
# KiCAD 8.0 - WORKS
aux_origin = self.brd.GetAuxOrigin()
self.brd.SetAuxOrigin(pcbnew.VECTOR2I(x, y))

# KiCAD 9.0+ - REMOVED (AttributeError)
aux_origin = self.brd.GetAuxOrigin()  # ❌ Crashes
```

**Solution - Backward Compatible**:
```python
# Check availability before use
aux_origin_save = None
has_aux_origin = hasattr(self.brd, 'GetAuxOrigin')

if has_aux_origin:
    try:
        aux_origin_save = self.brd.GetAuxOrigin()
    except AttributeError:
        logger.warning("GetAuxOrigin not available")
        has_aux_origin = False

# Use conditionally
if has_aux_origin:
    try:
        self.brd.SetAuxOrigin(new_origin)
    except AttributeError:
        logger.warning("SetAuxOrigin not available")
```

#### **Issue 2: DXF Units Constant Rename**

**Problem**:
```python
# KiCAD 8.0
popt.SetDXFPlotUnits(pcbnew.DXF_UNITS_MILLIMETERS)  # WORKS

# KiCAD 9.0+
popt.SetDXFPlotUnits(pcbnew.DXF_UNITS_MILLIMETERS)  # ❌ No such attribute
popt.SetDXFPlotUnits(pcbnew.DXF_PLOTTER_UNITS_MILLIMETERS)  # ✅ New name
```

**Solution - Auto-Detection**:
```python
# Try KiCAD 9.0+ first, fallback to KiCAD 8.0
try:
    popt.SetDXFPlotUnits(pcbnew.DXF_PLOTTER_UNITS_MILLIMETERS)  # KiCAD 9
except AttributeError:
    try:
        popt.SetDXFPlotUnits(pcbnew.DXF_UNITS_MILLIMETERS)  # KiCAD 8
    except AttributeError:
        logger.warning("Could not set DXF units, using default")
```

#### **Issue 3: Plot Parameter Methods Removed**

**Problem - Multiple methods removed in KiCAD 9.0+**:
```python
# KiCAD 8.0 - ALL WORK
popt.SetLineWidth(pcbnew.FromMM(0.1))
popt.SetColor(pcbnew.COLOR4D(0, 0, 0, 1.0))
popt.SetExcludeEdgeLayer(False)
popt.SetSubtractMaskFromSilk(False)

# KiCAD 9.0+ - ALL REMOVED (AttributeError)
popt.SetLineWidth(...)  # ❌ Crashes
popt.SetColor(...)  # ❌ Crashes
popt.SetExcludeEdgeLayer(...)  # ❌ Crashes
popt.SetSubtractMaskFromSilk(...)  # ❌ Crashes
```

**Solution - Wrap All Optional Methods**:
```python
# SetLineWidth (KiCAD 8 only, removed in KiCAD 9)
try:
    popt.SetLineWidth(pcbnew.FromMM(0.1))
except AttributeError:
    pass  # KiCAD 9 doesn't have SetLineWidth

# SetColor (KiCAD 8 only, removed in KiCAD 9)
try:
    popt.SetColor(pcbnew.COLOR4D(0, 0, 0, 1.0))
except AttributeError:
    pass  # KiCAD 9 doesn't have SetColor

# SetExcludeEdgeLayer (KiCAD 8 only, removed in KiCAD 9)
try:
    popt.SetExcludeEdgeLayer(False)
except AttributeError:
    pass  # KiCAD 9 doesn't have SetExcludeEdgeLayer

# SetSubtractMaskFromSilk (KiCAD 8 only, may be removed in KiCAD 9)
try:
    popt.SetSubtractMaskFromSilk(False)
except AttributeError:
    pass  # KiCAD 9 doesn't have SetSubtractMaskFromSilk
```

**Complete Backward-Compatible plot_dxf() Method**:
```python
def plot_dxf(self, path: str, layer_to_check: str):
    """Export DXF with KiCAD 8/9 compatibility"""
    
    # Save auxiliary origin (KiCAD 8 only)
    aux_origin_save = None
    has_aux_origin = hasattr(self.brd, 'GetAuxOrigin')
    
    if has_aux_origin:
        try:
            aux_origin_save = self.brd.GetAuxOrigin()
        except AttributeError:
            has_aux_origin = False
    
    # Set new aux origin (KiCAD 8 only)
    if has_aux_origin:
        try:
            origin_point = pcbnew.VECTOR2I(
                pcbnew.FromMM(self.origin[0]),
                pcbnew.FromMM(self.origin[1])
            )
            self.brd.SetAuxOrigin(origin_point)
        except AttributeError:
            has_aux_origin = False
    
    # Get plot controller
    pctl = pcbnew.PLOT_CONTROLLER(self.brd)
    popt = pctl.GetPlotOptions()
    
    popt.SetOutputDirectory(path)
    
    # DXF units - KiCAD 9/8 compatibility
    try:
        popt.SetDXFPlotUnits(pcbnew.DXF_PLOTTER_UNITS_MILLIMETERS)  # KiCAD 9
    except AttributeError:
        try:
            popt.SetDXFPlotUnits(pcbnew.DXF_UNITS_MILLIMETERS)  # KiCAD 8
        except AttributeError:
            logger.warning("Could not set DXF units, using default")
    
    # All plot parameters wrapped for compatibility
    try:
        popt.SetDXFPlotPolygonMode(True)
    except AttributeError:
        pass
    
    try:
        popt.SetPlotFrameRef(False)
    except AttributeError:
        pass
    
    try:
        popt.SetLineWidth(pcbnew.FromMM(0.1))
    except AttributeError:
        pass
    
    try:
        popt.SetAutoScale(False)
        popt.SetScale(1)
    except AttributeError:
        pass
    
    try:
        popt.SetMirror(self.mirror)
    except AttributeError:
        pass
    
    try:
        popt.SetUseGerberAttributes(False)
    except AttributeError:
        pass
    
    try:
        popt.SetExcludeEdgeLayer(False)
    except AttributeError:
        pass
    
    try:
        popt.SetSubtractMaskFromSilk(False)
    except AttributeError:
        pass
    
    # Use auxiliary origin if available
    if has_aux_origin:
        try:
            popt.SetUseAuxOrigin(True)
        except AttributeError:
            pass
    
    try:
        popt.SetColor(pcbnew.COLOR4D(0, 0, 0, 1.0))
    except AttributeError:
        pass
    
    # Core plot methods (work in both versions)
    if layer_to_check == "outline":
        pctl.SetLayer(pcbnew.Edge_Cuts)
        pctl.OpenPlotfile("outline", pcbnew.PLOT_FORMAT_DXF, "Edges")
    elif layer_to_check == "track":
        pctl.SetLayer(self.layer)
        pctl.OpenPlotfile("track", pcbnew.PLOT_FORMAT_DXF, "track")
    
    pctl.PlotLayer()
    pctl.ClosePlot()
    
    # Restore origin (KiCAD 8 only)
    if has_aux_origin and aux_origin_save is not None:
        try:
            self.brd.SetAuxOrigin(aux_origin_save)
        except AttributeError:
            pass
    
    logger.info(f"Exported DXF: {layer_to_check}")
```

### 15.2 OpenSCAD Integration Improvements

#### **Issue: OpenSCAD Command Execution Failures**

**Original Problem**:
```python
# OLD - Using os.system() (no error handling)
os.system(f'openscad {args} -D "mode=\\"testcut\\"" -o {output} openfixture.scad')
# Issues:
# - No error checking
# - Shell quoting issues
# - Relative path to openfixture.scad fails
# - openscad not in PATH
```

**Solution - Robust OpenSCAD Execution**:
```python
import subprocess
import shutil
from pathlib import Path

def _find_openscad(self) -> Optional[str]:
    """Find OpenSCAD executable"""
    # Try PATH first
    openscad = shutil.which('openscad')
    if openscad:
        return openscad
    
    # Try common Windows paths
    if os.name == 'nt':
        common_paths = [
            r"C:\Program Files\OpenSCAD\openscad.exe",
            r"C:\Program Files (x86)\OpenSCAD\openscad.exe",
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
    
    return None

def _run_openscad(self, openscad_exe: str, scad_file: Path, 
                  args_dict: Dict, mode: str, output: str, 
                  render: bool = False) -> bool:
    """Run OpenSCAD with proper error handling"""
    
    # Build command list (avoids shell quoting issues)
    cmd = [str(openscad_exe)]
    
    if render:
        cmd.append('--render')
    
    # Add mode parameter
    cmd.extend(['-D', f'mode="{mode}"'])
    
    # Add all other parameters
    for key, value in args_dict.items():
        if isinstance(value, str) and ('/' in value or '\\' in value or ' ' in value):
            # Path-like string - add quotes
            cmd.extend(['-D', f'{key}="{value}"'])
        else:
            # Numeric or already formatted
            cmd.extend(['-D', f'{key}={value}'])
    
    # Add output and input files
    cmd.extend(['-o', str(output), str(scad_file)])
    
    logger.info(f"Running OpenSCAD command with {len(args_dict)} parameters")
    
    try:
        # Use subprocess with list (no shell) to avoid quoting issues
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            logger.error(f"OpenSCAD failed with return code {result.returncode}")
            if result.stderr:
                logger.error(f"OpenSCAD error: {result.stderr}")
            return False
        
        # Verify output file created
        if not os.path.exists(output):
            logger.error(f"OpenSCAD did not create output file: {output}")
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        logger.error(f"OpenSCAD timed out after 120 seconds")
        return False
    except Exception as e:
        logger.error(f"Failed to run OpenSCAD: {e}")
        return False

def generate(self, path: str) -> bool:
    """Main generation with OpenSCAD integration"""
    
    # Find OpenSCAD
    openscad_exe = self._find_openscad()
    if not openscad_exe:
        logger.error("OpenSCAD not found! Install from https://openscad.org/")
        return False
    
    # Find openfixture.scad (in same directory as script)
    script_dir = Path(__file__).parent
    scad_file = script_dir / "openfixture.scad"
    if not scad_file.exists():
        logger.error(f"openfixture.scad not found at {scad_file}")
        return False
    
    # Build arguments dictionary
    args_dict = self._build_openscad_args(path)
    
    # Generate three files with error checking
    success = True
    
    # Test cut
    logger.info("Generating test cut DXF...")
    if not self._run_openscad(openscad_exe, scad_file, args_dict, 
                              "testcut", testout):
        logger.error("Failed to generate test cut DXF")
        success = False
    
    # 3D preview
    logger.info("Generating 3D preview PNG...")
    if not self._run_openscad(openscad_exe, scad_file, args_dict, 
                              "3dmodel", pngout, render=True):
        logger.warning("Failed to generate 3D preview PNG")
        # Don't fail - preview is optional
    
    # Fixture DXF
    logger.info("Generating fixture DXF...")
    if not self._run_openscad(openscad_exe, scad_file, args_dict, 
                              "lasercut", dxfout):
        logger.error("Failed to generate fixture DXF")
        success = False
    
    return success
```

**Key Improvements**:
- ✅ Automatic OpenSCAD executable detection
- ✅ subprocess.run() instead of os.system() for error handling
- ✅ Command list avoids shell quoting complexity
- ✅ 120-second timeout prevents hangs
- ✅ Output file verification
- ✅ Detailed error logging with stderr capture
- ✅ Proper path handling for openfixture.scad

### 15.3 Enhanced Error Handling in Plugin

**Scrollable Error Dialog** (replaces truncated MessageBox):
```python
class ErrorDialog(wx.Dialog):
    """Scrollable error dialog with copy-to-clipboard support"""
    
    def __init__(self, parent, title, message):
        super().__init__(parent, title=title, size=(700, 500))
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Error icon
        icon_sizer = wx.BoxSizer(wx.HORIZONTAL)
        icon = wx.StaticBitmap(panel, bitmap=wx.ArtProvider.GetBitmap(
            wx.ART_ERROR, wx.ART_MESSAGE_BOX, (32, 32)))
        icon_sizer.Add(icon, 0, wx.ALL, 10)
        
        # Title
        title_text = wx.StaticText(panel, label="Error Details:")
        title_text.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, 
                                   wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        icon_sizer.Add(title_text, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 10)
        sizer.Add(icon_sizer, 0, wx.EXPAND)
        
        # Scrollable text area
        text_ctrl = wx.TextCtrl(panel, value=message, 
                               style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP)
        text_ctrl.SetFont(wx.Font(9, wx.FONTFAMILY_TELETYPE, 
                                 wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        sizer.Add(text_ctrl, 1, wx.EXPAND | wx.ALL, 10)
        
        # Buttons
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        copy_btn = wx.Button(panel, label="Copy to Clipboard")
        copy_btn.Bind(wx.EVT_BUTTON, lambda e: self._copy_to_clipboard(message))
        button_sizer.Add(copy_btn, 0, wx.ALL, 5)
        
        ok_btn = wx.Button(panel, wx.ID_OK, label="OK")
        button_sizer.Add(ok_btn, 0, wx.ALL, 5)
        sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        
        panel.SetSizer(sizer)
    
    def _copy_to_clipboard(self, text):
        """Copy error message to clipboard"""
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(text))
            wx.TheClipboard.Close()
            wx.MessageBox("Error details copied to clipboard", 
                         "Copied", wx.OK | wx.ICON_INFORMATION)
```

**Output File Verification**:
```python
def _verify_output_files(self, output_dir: Path, board_name: str) -> Tuple[bool, List[str], List[str]]:
    """Verify all expected output files were created"""
    
    expected_files = [
        f"{board_name}-outline.dxf",
        f"{board_name}-track.dxf",
        f"{board_name}-fixture.dxf",
    ]
    
    found = []
    missing = []
    
    for filename in expected_files:
        file_path = output_dir / filename
        if file_path.exists() and file_path.stat().st_size > 0:
            found.append(filename)
        else:
            missing.append(filename)
    
    return len(missing) == 0, found, missing
```

**Intelligent Error Message Parsing**:
```python
def _parse_error_message(self, stderr: str, returncode: int) -> str:
    """Parse error output and provide user-friendly message"""
    
    if "No test points found" in stderr:
        return ("No test points detected on the PCB.\n\n"
                "Possible causes:\n"
                "• Pads need paste mask removed to be detected as test points\n"
                "• Use --flayer option to force all pads as test points\n"
                "• Check that your board has SMD pads")
    
    if "OpenSCAD" in stderr and "not found" in stderr:
        return ("OpenSCAD is not installed or not in PATH.\n\n"
                "Download from: https://openscad.org/")
    
    if returncode == 1 and "openfixture.scad" in stderr:
        return ("OpenSCAD script error.\n\n"
                "Check that openfixture.scad is in the correct location:\n"
                "KiCAD plugins directory → openfixture_support/")
    
    return stderr  # Return raw error if no match
```

### 15.4 Complete Compatibility Matrix

| Feature | KiCAD 8.0 | KiCAD 9.0+ | Implementation |
|---------|-----------|------------|----------------|
| Board loading | ✅ LoadBoard() | ✅ LoadBoard() | No change |
| Footprint iteration | ✅ GetFootprints() | ✅ GetFootprints() | No change |
| Auxiliary origin | ✅ Get/SetAuxOrigin | ❌ Removed | hasattr() check + try-except |
| DXF units constant | ✅ DXF_UNITS_MILLIMETERS | ✅ DXF_PLOTTER_UNITS_MILLIMETERS | Try new first, fallback to old |
| SetLineWidth | ✅ Available | ❌ Removed | try-except wrapper |
| SetColor | ✅ Available | ❌ Removed | try-except wrapper |
| SetExcludeEdgeLayer | ✅ Available | ❌ Removed | try-except wrapper |
| SetSubtractMaskFromSilk | ✅ Available | ❌ Removed | try-except wrapper |
| Plot controller | ✅ PLOT_CONTROLLER | ✅ PLOT_CONTROLLER | No change |
| DXF export | ✅ PlotLayer() | ✅ PlotLayer() | No change |

### 15.5 Testing Results

**Test Configuration** (February 15, 2026):
- **Board**: example_board.kicad_pcb
- **Dimensions**: 101.82 x 69.53 mm
- **Test Points**: 51 points detected
- **KiCAD Version**: 9.0
- **Python Version**: 3.11.5 (bundled with KiCAD)

**Output Files Generated** ✅:
```
✅ example_board-outline.dxf  (27 KB)
✅ example_board-track.dxf    (2.7 MB)
✅ example_board-test.dxf     (3.8 KB)
✅ example_board-fixture.dxf  (215 KB)
✅ example_board-fixture.png  (11.7 KB)
```

**All tests passed**:
- ✅ Plugin loads in KiCAD Tools menu
- ✅ Dialog opens with all parameters
- ✅ Board file parsing successful
- ✅ Test point extraction working
- ✅ DXF exports complete (both outline and track)
- ✅ OpenSCAD execution successful
- ✅ All output files valid and readable

### 15.6 Deployment Script Updates

The `sync_to_kicad.ps1` script has been updated to sync only active production files (v2 suffix removed):

```powershell
$PluginFiles = @(
    "openfixture.py",           # Main plugin (was openfixture_v2.py)
    "OpenFixtureDlg.py",
    "OpenFixture.png"
)

$SupportFiles = @(
    "GenFixture.py",            # Main generator (was GenFixture_v2.py)
    "openfixture.scad",
    "osh_logo.dxf",
    "fixture_config.toml",
    "genfixture.bat",           # Wrappers (was genfixture_v2.*)
    "genfixture.sh"
)

$DocumentationFiles = @(
    "README.md",
    "MIGRATION_GUIDE.md",       # Migration guide (was MIGRATION_GUIDE_v2.md)
    "MODERNIZATION_SUMMARY.md",
    "SECURITY.md",
    "copilot-instructions_openfixture.md"
)
```

### 15.7 Key Takeaways for AI Assistants

When working with OpenFixture and KiCAD 9.0+:

1. **Always wrap deprecated API calls in try-except blocks**
   - Don't assume methods exist
   - Use hasattr() for major feature detection
   - Log warnings but continue execution when possible

2. **Test constant names with try-except cascades**
   - Try modern name first (KiCAD 9+)
   - Fallback to legacy name (KiCAD 8)
   - Handle complete failure gracefully

3. **Use subprocess instead of os.system**
   - Build command as list, not string
   - Capture stderr for debugging
   - Implement timeouts for long operations
   - Verify output files after execution

4. **Provide detailed error messages**
   - Parse error output intelligently
   - Suggest actionable solutions
   - Include file paths and system info

5. **Maintain backward compatibility**
   - Code must work on both KiCAD 8.0 and 9.0+
   - Test on both versions when possible
   - Document version-specific behavior

---

## 16. Supplementary Documentation References

For deeper technical details on KiCAD Python development, refer to these supplementary documents:

### 16.1 KiCAD Python API Reference
**File**: `copilot-instructions_kicad_python_api.md`  
**Purpose**: Comprehensive pcbnew module API documentation  
**Contents**:
- Board access and properties
- Layer management and iteration
- Track, via, and arc manipulation
- Footprint and pad operations
- Zone and fill algorithms
- Net and connectivity queries
- Gerber and DXF export methods
- Drawing board items (shapes, text, groups)

**When to use**: When you need detailed API signatures, parameter types, or examples of specific pcbnew methods beyond what OpenFixture uses.

### 16.2 KiCAD Plugin Structure Guide
**File**: `copilot-instructions_kicad_plugin_structure.md`  
**Purpose**: Plugin architecture patterns and best practices  
**Contents**:
- ActionPlugin vs scripting plugins
- Plugin lifecycle (discovery, registration, execution)
- File structure patterns (single-file vs modular)
- Reload and development workflows
- Configuration management
- UI integration (toolbar, menus, dialogs)
- Error handling patterns

**When to use**: When creating new KiCAD plugins or restructuring existing ones, or when you need to understand plugin lifecycle details.

### 16.3 Removed Files (Not Relevant to OpenFixture)

The following copilot instruction files have been removed as they are specific to DRC (Design Rule Check) plugins and not applicable to OpenFixture's test fixture generation:

- ~~`copilot-instructions_drc_algorithms.md`~~ - Spatial indexing for clearance checks
- ~~`copilot-instructions_modular_drc_design.md`~~ - Modular DRC checker architecture
- ~~`copilot-instructions_toml_configuration.md`~~ - DRC-specific TOML rule configuration

**Note**: OpenFixture uses `fixture_config.toml` for fixture parameters, but the structure is simpler than DRC configs and is documented in Section 5 above.

---

**END OF COPILOT INSTRUCTIONS**

For questions, contributions, or issues, contact the original author or refer to:
- http://tinylabs.io/openfixture
- GitHub Issues (if repository available)
- Migration Guide: `MIGRATION_GUIDE.md`
- Modernization Summary: `MODERNIZATION_SUMMARY.md`
