# OpenFixture - Modern PCB Test Fixture Generator

![License](https://img.shields.io/badge/license-CC%20BY--SA%204.0-green)
![KiCAD](https://img.shields.io/badge/KiCAD-8.0%20%7C%209.0+-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)

**Automated laser-cuttable PCB test fixture generation for KiCAD 8.0 and 9.0+**

OpenFixture is a comprehensive PCB test fixture generator that integrates directly with KiCAD to automatically create laser-cuttable fixtures for your boards. Fully modernized with KiCAD 9.0+ API compatibility, Python 3 support, and enhanced error handling.

---

## 🚀 Key Features

- ✅ **Full KiCAD 9.0+ Compatibility** - Tested and working with KiCAD 9.0 API
- ✅ **Backward Compatible with KiCAD 8.0** - Automatic API version detection
- ✅ **Python 3 Modern Codebase** - Type hints, modern syntax, PEP 8 compliant
- ✅ **TOML Configuration** - Project-specific configuration files
- ✅ **Enhanced Plugin UI** - Multi-tab dialog with material presets
- ✅ **Comprehensive Error Handling** - Detailed logging and user-friendly error dialogs
- ✅ **Automatic OpenSCAD Integration** - Seamless 3D model and DXF generation
- ✅ **Modular Architecture** - Clean, maintainable, well-documented code

---

## 📦 Quick Start

### Installation

```bash
# 1. Clone or download this repository
git clone https://github.com/tinylabs/openfixture.git
cd openfixture

# 2. Install Python dependencies (optional, for TOML support)
pip install tomli  # Only needed for Python < 3.11

# 3. Install KiCAD plugin using sync script (recommended)
# First, set up your personal configuration:
cp sync_to_kicad_config.ps1.template sync_to_kicad_config.ps1
# Edit sync_to_kicad_config.ps1 with your KiCAD plugins path
notepad sync_to_kicad_config.ps1  # Windows
# OR nano sync_to_kicad_config.ps1  # Linux/macOS

# Then run the sync script:
.\sync_to_kicad.ps1  # Windows PowerShell

# Alternative: Manual installation
# Copy to KiCAD plugins directory:
# Windows: %APPDATA%\kicad\<version>\3rdparty\plugins\
# Linux: ~/.local/share/kicad/<version>/3rdparty/plugins/
# macOS: ~/Library/Application Support/kicad/<version>/3rdparty/plugins/

cp openfixture.py <plugins_directory>/
cp GenFixture.py <plugins_directory>/
```

### 🔒 Security Note

Personal configuration files (like `sync_to_kicad_config.ps1`) are excluded from version control to protect your privacy. Always use the `.template` files as a starting point and never commit files containing personal paths. See [SECURITY.md](SECURITY.md) for details.

### Basic Usage

**Command Line**:
```bash
python3 GenFixture.py \
    --board your_board.kicad_pcb \
    --mat_th 3.0 \
    --out fixture-output
```

**With Configuration File**:
```bash
# 1. Create fixture_config.toml in your project directory
# 2. Run with config:
python3 GenFixture.py \
    --board your_board.kicad_pcb \
    --config fixture_config.toml \
    --out fixture-output
```

**KiCAD Plugin**:
```
1. Open your PCB in KiCAD PCB Editor
2. Tools → External Plugins → OpenFixture Generator
3. Configure parameters in dialog
4. Click "Generate Fixture"
5. Output directory opens automatically
```

---

## 📋 Requirements

### Software
- **KiCAD** 8.0 or 9.0+
- **Python** 3.8 or later
- **OpenSCAD** 2015.03 or later
- **Laser cutter** or laser cutting service

### Python Packages
- `pcbnew` (included with KiCAD)
- `tomli` (optional, for Python < 3.11)

### Hardware
- M3 screws (14-20mm length)
- M3 hex nuts
- M3 washers (optional)
- Pogo pins and receptacles
- Laser-cut material (acrylic or plywood, 2-5mm thick)

---

## 🎯 Features

### Test Point Extraction
- Automatic detection of SMD pads without paste mask
- Force include/exclude layers support
- Top and bottom side testing
- Coordinate transformation and mirroring

### Parametric Generation
- OpenSCAD-based 3D model
- Adjustable material thickness
- Custom hardware dimensions
- Configurable pogo pin placement

### Output Files
- **fixture.dxf** - Laser-cuttable parts layout
- **fixture.png** - 3D preview rendering
- **test.dxf** - Material fit test piece
- **outline.dxf** - Board outline reference
- **track.dxf** - Test point verification overlay

---

## ⚙️ Configuration

### TOML Configuration File

Create `fixture_config.toml` in your project directory:

```toml
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

[layers]
force_layer = "Eco2.User"
ignore_layer = "Eco1.User"
```

### Command-Line Arguments

```bash
python3 GenFixture.py \
    --board <file.kicad_pcb>        # Required: PCB file path
    --mat_th <mm>                   # Required: Material thickness
    --out <directory>               # Required: Output directory
    --config <file.toml>            # Optional: Config file
    --pcb_th <mm>                   # Optional: PCB thickness (default: 1.6)
    --layer <F.Cu|B.Cu>            # Optional: Test point layer
    --rev <string>                  # Optional: Revision string
    --screw_len <mm>                # Optional: Screw length (default: 16.0)
    --screw_d <mm>                  # Optional: Screw diameter (default: 3.0)
    --nut_th <mm>                   # Optional: Nut thickness
    --nut_f2f <mm>                  # Optional: Nut flat-to-flat
    --nut_c2c <mm>                  # Optional: Nut corner-to-corner
    --washer_th <mm>                # Optional: Washer thickness
    --border <mm>                   # Optional: PCB support border
    --pogo-uncompressed-length <mm> # Optional: Pogo pin length
    --verbose                       # Optional: Enable verbose logging
```

---

## 📖 Documentation

- **[copilot-instructions_openfixture.md](copilot-instructions_openfixture.md)** - Complete technical documentation
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Upgrade guide from legacy versions
- **[fixture_config.toml](fixture_config.toml)** - Configuration file template

### Original Documentation
- **Main Site**: http://tinylabs.io/openfixture
- **BOM**: http://tinylabs.io/openfixture-bom
- **Assembly**: http://tinylabs.io/openfixture-assembly
- **KiCAD Export**: http://tinylabs.io/openfixture-kicad-export

---

## 🔄 Migration from v1

If you're upgrading from a legacy version, see **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** for detailed upgrade instructions.

**Quick comparison**:

| Feature | Legacy (Original) | Current (KiCAD 9+) |
|---------|---------------|-------------|
| KiCAD 6.0/7.0 | ✅ Full | ⚠️ Limited |
| KiCAD 8.0/9.0 | ❌ No | ✅ Full |
| Python 2 | ✅ Yes | ❌ No |
| Python 3 | ⚠️ Partial | ✅ Full |
| TOML Config | ❌ No | ✅ Yes |
| Type Hints | ❌ No | ✅ Yes |
| Modern UI | ❌ No | ✅ Yes |
| Error Handling | ⚠️ Basic | ✅ Complete |

---

## 🛠️ Development

### File Structure

```
openfixture/
├── GenFixture.py              # Main generator
├── openfixture.py             # KiCAD plugin
├── fixture_config.toml        # Configuration template
├── genfixture.bat             # Windows wrapper
├── genfixture.sh              # Linux/Mac wrapper
├── openfixture.scad           # OpenSCAD model
│
├── GenFixture.py              # Original generator (v1, legacy)
├── openfixture.py             # Original plugin (v1, legacy)
├── genfixture.bat             # Original wrapper (v1, legacy)
├── genfixture.sh              # Original wrapper (v1, legacy)
│
├── copilot-instructions_openfixture.md  # Complete documentation
├── MIGRATION_GUIDE.md                   # Legacy upgrade guide
├── README_v2.md                         # This file
└── README.md                            # Original README
```

### Key Classes

**GenFixture.py**:
```python
class FixtureConfig:
    """Configuration container with TOML support"""

class GenFixture:
    """Main fixture generator with modern KiCAD API"""
    
    def get_test_points(self) -> None
    def get_origin_dimensions(self) -> None
    def plot_dxf(self, path: str, layer: str) -> None
    def generate(self, path: str) -> bool
```

**openfixture.py**:
```python
class OpenFixtureDialog(wx.Dialog):
    """Modern multi-tab parameter dialog"""
    
    def _create_board_panel(self, parent) -> wx.Panel
    def _create_material_panel(self, parent) -> wx.Panel
    def _create_hardware_panel(self, parent) -> wx.Panel
    def get_parameters(self) -> dict

class OpenFixturePlugin(pcbnew.ActionPlugin):
    """KiCAD action plugin entry point"""
    
    def Run(self) -> None
```

---

## 🐛 Troubleshooting

### Common Issues

**"No module named 'tomllib'"**
```bash
# Install tomli for Python < 3.11
pip install tomli

# Or run without config file
python3 GenFixture.py --board test.kicad_pcb --mat_th 3.0 --out fixture
```

**"No test points found"**
- Ensure SMD pads have **no paste mask** in KiCAD
- Or use Eco2.User layer to force include specific pads
- Check that correct layer (F.Cu/B.Cu) is selected

**"Could not find GenFixture.py" (plugin error)**
```
# Ensure both files are in plugins directory:
plugins/
├── openfixture.py
└── GenFixture.py
```

**Plugin not appearing in KiCAD**
1. Check file permissions (must be readable)
2. Verify correct plugins directory for your KiCAD version
3. Restart KiCAD completely
4. Check: Tools → Plugin and Content Manager

### Verbose Logging

Enable detailed logging for troubleshooting:
```bash
python3 GenFixture.py --board test.kicad_pcb --mat_th 3.0 --out fixture --verbose
```

---

## 📝 Examples

### Standard 1.6mm PCB, 3mm Acrylic

```bash
python3 GenFixture.py \
    --board my_board.kicad_pcb \
    --mat_th 3.0 \
    --pcb_th 1.6 \
    --out fixture-rev01 \
    --rev "rev_01"
```

### Thin PCB, 2.5mm Acrylic

```bash
python3 GenFixture.py \
    --board thin_board.kicad_pcb \
    --mat_th 2.45 \
    --pcb_th 0.8 \
    --screw_len 14.0 \
    --out fixture-thin
```

### Bottom Side Testing

```bash
python3 GenFixture.py \
    --board my_board.kicad_pcb \
    --mat_th 3.0 \
    --layer B.Cu \
    --out fixture-bottom
```

### Using Configuration File

```bash
# Create fixture_config.toml with your parameters
# Then simply run:
python3 GenFixture.py \
    --board my_board.kicad_pcb \
    --config fixture_config.toml \
    --out fixture
```

---

## 📜 License

**Creative Commons CC BY-SA 4.0**

You are free to:
- **Share** - Copy and redistribute the material
- **Adapt** - Remix, transform, and build upon the material

Under the following terms:
- **Attribution** - Give appropriate credit
- **ShareAlike** - Distribute under the same license

See: https://creativecommons.org/licenses/by-sa/4.0/

---

## 👤 Contributors

**Original Author**:
- Elliot Buller - Tiny Labs Inc (elliot@tinylabs.io)
- Project Website: http://tinylabs.io/openfixture

**Modernization & KiCAD 9+ Compatibility** (February 2026):
- For contributions, please use GitHub pull requests

**Key Updates**:
- ✅ **KiCAD 9.0+ Full Compatibility** - All breaking API changes fixed with backward compatibility for KiCAD 8.0
- ✅ **Enhanced OpenSCAD Integration** - Robust subprocess execution with proper error handling, timeouts, and path resolution
- ✅ **Python 3.11+ Modernization** - Type hints, pathlib, dataclasses, comprehensive logging
- ✅ **TOML Configuration System** - Project-specific fixture parameters in `fixture_config.toml`
- ✅ **Enhanced Plugin UI** - Scrollable error dialogs with copy-to-clipboard, output file verification
- ✅ **Security Improvements** - Configuration template system, no hardcoded paths, comprehensive .gitignore
- ✅ **Comprehensive Documentation** - Updated README, migration guide, security documentation, AI assistant instructions

---

## 🔗 Links

- **Original Project**: http://tinylabs.io/openfixture
- **OpenSCAD**: https://openscad.org/
- **KiCAD**: https://www.kicad.org/
- **KiCAD Python API**: https://docs.kicad.org/doxygen/

---

## 💡 Tips & Best Practices

### PCB Design
- Place test pads in accessible locations (not under components)
- Use consistent pad size (≥0.5mm diameter)
- Remove **both** solder mask and paste mask from test pads
- Use clear net naming for troubleshooting

### Material Selection
- **Acrylic**: Best precision (±0.05mm), transparent, but can crack
- **Plywood**: Budget-friendly, strong, but lower precision (±0.2mm)
- **Measure actual thickness** with calipers before cutting
- Use **test cut piece** to verify fit before full fixture

### Hardware
- **M3 hardware** is the standard (readily available)
- Measure nut dimensions with calipers (varies by manufacturer)
- Use **2-part pogo pins** (replaceable pins when they break)
- Force: 50-100g typical (too many high-force pins = hard to close)

### Workflow
1. Design PCB in KiCAD with test pads
2. Create `fixture_config.toml` for project
3. Generate fixture with v2
4. Review 3D preview PNG
5. Cut test piece first (verify fit)
6. Cut full fixture
7. Assemble and test

---

## 🆘 Getting Help

1. Check **[copilot-instructions_openfixture.md](copilot-instructions_openfixture.md)** for detailed documentation
2. Review **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** if upgrading from v1
3. Enable `--verbose` logging to diagnose issues
4. Check original docs: http://tinylabs.io/openfixture
5. Verify KiCAD version compatibility (v2 requires 8.0+)

---

**Version**: 2.0.0  
**Last Updated**: February 15, 2026  
**Compatibility**: KiCAD 8.0+, Python 3.8+, OpenSCAD 2015.03+
