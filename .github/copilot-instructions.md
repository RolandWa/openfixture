# OpenFixture - PCB Test Fixture Generator

Automated laser-cuttable PCB test fixture generation integrated with KiCAD 8.0 and 9.0+.

## Project Structure

**Modern src-layout** (Python packaging best practice):
```
openfixture/
├── src/
│   ├── __init__.py                    # Plugin registration
│   ├── openfixture.py                 # KiCAD ActionPlugin
│   └── openfixture_support/           # Core package
│       ├── __init__.py
│       ├── GenFixture.py              # Main processing engine
│       ├── openfixture.scad           # OpenSCAD generator
│       └── fixture_config.toml        # Configuration template
├── build.py                           # KiCAD plugin build system
├── setup.py                           # Package installation
├── pyproject.toml                     # Modern Python packaging
└── .github/
    └── copilot-instructions.md        # This file
```

**Benefits of src-layout**:
- Prevents accidental imports from development directory
- Clear separation between source and built artifacts
- Standard Python packaging structure
- Matches OrthoRoute project pattern

## Architecture

**Dual-interface system**:
- **openfixture.py**: KiCAD plugin (wxPython UI) → calls GenFixture.py
- **GenFixture.py**: Core processing engine (CLI + plugin backend)
- **openfixture.scad**: OpenSCAD parametric fixture generator

**Processing flow**:
```
KiCAD PCB → GenFixture.py (extract test points + export DXF) 
           → OpenSCAD (generate 3D model + laser-cut DXF)
```

See [README.md](../README.md) for features and installation.

## Build & Deployment

**Build KiCAD plugin package**:
```powershell
# Build package + ZIP for distribution
python build.py

# Build and deploy to local KiCAD installation
python build.py --deploy

# Build package directory only (no ZIP)
python build.py --no-zip

# Clean build artifacts
python build.py --clean
```

**Legacy sync script** (still supported):
```powershell
# 1. Configure paths (one-time):
cp sync_to_kicad_config.ps1.template sync_to_kicad_config.ps1
# Edit sync_to_kicad_config.ps1 with your KiCAD plugins path

# 2. Deploy:
.\sync_to_kicad.ps1

# 3. If cache issues (stale imports):
.\clean_and_deploy.ps1
```

**Output directory structure** (after build):
```
build/
└── com_github_RolandWa_openfixture/  # Plugin package
    ├── __init__.py                   # Plugin registration
    ├── openfixture.py                # Main plugin file
    ├── OpenFixture.png               # Icon
    ├── plugin.json                   # KiCAD plugin descriptor
    ├── metadata.json                 # KiCAD PCM metadata
    ├── openfixture_support/          # Core package
    │   ├── GenFixture.py
    │   ├── openfixture.scad
    │   └── fixture_config.toml
    └── README.md                     # Documentation
```

**KiCAD installation structure** (after deploy):
```
KiCAD\9.0\3rdparty\plugins\
└── com_github_RolandWa_openfixture/
    ├── __init__.py
    ├── openfixture.py
    ├── OpenFixture.png
    └── openfixture_support/
        ├── GenFixture.py
        ├── openfixture.scad
        └── fixture_config.toml
```

## Code Conventions

### KiCAD API Compatibility

**Always wrap KiCAD 9.0 breaking changes with try-except**:
```python
# KiCAD 9 removed GetAuxOrigin/SetAuxOrigin
try:
    aux_origin_save = self.brd.GetAuxOrigin()
except AttributeError:
    logger.warning("GetAuxOrigin not available (KiCAD 9+), continuing...")
```

**Use modern API methods**:
- `brd.GetFootprints()` (not `GetModules()`)
- `VECTOR2I` coordinates with direct division (not `wxPoint`, `ToMM()`)
- `DXF_PLOTTER.DXF_PLOTTER_UNITS_MILLIMETERS` constant (KiCAD 9+)

### Python Subprocess Calls

**Always use list-based commands** (avoids shell escaping):
```python
cmd = [openscad_exe, '-D', f'mode="lasercut"', '-o', output_file, scad_file]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
```

**Windows path handling for OpenSCAD**:
```python
# Convert backslashes to forward slashes (OpenSCAD uses Unix paths)
outline_path.replace("\\", "/")
```

### Test Point Extraction Logic

**Inclusion criteria** (implemented in `get_test_points()`):
1. **Force include**: Pad on Eco2.User layer → always include
2. **Force exclude**: Pad on Eco1.User layer → always exclude  
3. **Paste mask check**: Pad has paste → exclude (not a test point)
4. **SMD pads**: Include if `config.include_smd_pads = true`
5. **PTH pads**: Include ONLY when component is on opposite side of test layer
   - Rationale: Component body blocks access from same side
   - Example: Testing bottom layer → include PTH from top-side components only

### Configuration Pattern

**Priority**: CLI args > TOML config > hardcoded defaults

```python
# Try TOML libraries in order:
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # pip install tomli
    except ImportError:
        logger.warning("TOML support unavailable, using defaults")
```

## Common Gotchas

### Deployment Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Plugin doesn't load | Wrong path in config | Re-run sync after editing `sync_to_kicad_config.ps1` |
| Import errors after update | Stale `.pyc` cache | Run `clean_and_deploy.ps1` |
| Changes not visible | Wrong Python executing | Check KiCAD uses bundled Python |

### Test Point Extraction

| Problem | Cause | Solution |
|---------|-------|----------|
| "No test points found" | SMD pads have paste mask | Remove paste mask in footprint editor |
| Missing obvious pads | Wrong layer selected | Check test_layer config (F.Cu, B.Cu, or both) |
| PTH pads not included | Component on same side | By design (component blocks access) |

### OpenSCAD Integration

| Problem | Cause | Solution |
|---------|-------|----------|
| OpenSCAD not found | Not in PATH | Plugin auto-searches common Windows paths |
| Timeout (>120s) | Complex board geometry | Simplify outline or use testcut mode |

## File Organization

**Security-sensitive paths** (excluded from git):
- `sync_to_kicad_config.ps1` - Personal KiCAD installation paths
- `__pycache__/` - Python bytecode cache

**Output files** generated by GenFixture:
- `{board}-outline.dxf` - Board perimeter from Edge.Cuts
- `{board}-track.dxf` - Copper tracks for alignment verification
- `{board}-fixture.dxf` - Laser-cuttable fixture parts
- `{board}-fixture.png` - 3D preview rendering
- `{board}-test.dxf` - Test point validation piece

## Development Resources

- **KiCAD Python API**: [copilot-instructions_kicad_python_api.md](../copilot-instructions_kicad_python_api.md)
- **Migration from v1**: [MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md)
- **Pogo pin specifications**: [POGO_PINS.md](../POGO_PINS.md)
- **Security practices**: [SECURITY.md](../SECURITY.md)
