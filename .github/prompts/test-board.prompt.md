---
description: Generate test fixture from KiCAD PCB file with material presets and validation. Use when creating fixture, generating DXF, or testing new board design.
---

# Generate Test Fixture from PCB

Generate a complete laser-cuttable test fixture from a KiCAD PCB file.

## Inputs

Ask the user for:

1. **PCB file path** (*.kicad_pcb)
   - Validate file exists
   - Extract board name from filename

2. **Material preset** (choose one):
   - `3mm-acrylic`: Standard 3mm acrylic sheets
   - `3mm-plywood`: 3mm plywood (budget option)
   - `2.5mm-acrylic`: Thinner acrylic for compact fixtures
   - `custom`: User provides material thickness

3. **Test layer** (choose one):
   - `F.Cu`: Top layer testing
   - `B.Cu`: Bottom layer testing
   - `both`: Generate fixtures for both sides

4. **Output directory** (optional)
   - Default: `fixture-{boardname}`

## Material Preset Parameters

```toml
# 3mm-acrylic
mat_th = 3.0
screw_len = 16.0
washer_th = 1.0
nut_f2f = 5.45

# 3mm-plywood
mat_th = 3.0
screw_len = 16.0
washer_th = 0.8
nut_f2f = 5.45

# 2.5mm-acrylic
mat_th = 2.5
screw_len = 14.0
washer_th = 0.8
nut_f2f = 5.45
```

PCB thickness defaults to 1.6mm (adjust if different).

## Workflow

1. **Validate inputs**:
   - Check PCB file exists and is valid KiCAD format
   - Create output directory if needed
   - Load or create `fixture_config.toml` with selected preset

2. **Generate fixture**:
   ```powershell
   python GenFixture.py `
       --board "{pcb_file}" `
       --mat_th {material_thickness} `
       --pcb_th 1.6 `
       --layer {test_layer} `
       --screw_len {screw_length} `
       --out {output_dir}
   ```

3. **Validate output**:
   - Check for required files:
     - `{board}-outline.dxf`
     - `{board}-fixture.dxf`
     - `{board}-fixture.png`
     - `{board}-test.dxf`
   - Verify file sizes > 0
   - Report test point count from logs

4. **Generate summary**:
   - List all output files with sizes
   - Show test point statistics (top/bottom counts)
   - Display fixture preview path
   - Provide laser cutting recommendations:
     - Material settings for selected preset
     - Layer colors for organization
     - Assembly instructions link

## Error Handling

- **No test points found**: 
  - Check if SMD pads have paste mask (should be removed)
  - Verify correct layer selected
  - Suggest using Eco2.User layer to force-include specific pads

- **OpenSCAD timeout**:
  - Board might be too complex
  - Try `testcut` mode first to verify basic operation
  - Check OpenSCAD installation

- **DXF export failed**:
  - Validate Edge.Cuts layer exists
  - Check for overlapping or invalid geometry

## Success Output

```
✅ Test Fixture Generated Successfully!

📁 Output Directory: fixture-{boardname}/
📊 Test Points: {count_top} top, {count_bottom} bottom
📐 Board Dimensions: {width} x {height} mm
🎨 Preview: {boardname}-fixture.png

📋 Output Files:
  - {boardname}-outline.dxf (board outline)
  - {boardname}-fixture.dxf (LASER CUT THIS)
  - {boardname}-test.dxf (validation piece)
  - {boardname}-track.dxf (alignment verification)

🔧 Material: {preset}
   Thickness: {mat_th}mm
   Screws: M3 x {screw_len}mm
   
⚡ Next Steps:
   1. Review fixture preview PNG
   2. Send fixture.dxf to laser cutter
   3. Use material settings: {laser_power}/{speed}
   4. Assemble with M3 screws and pogo pins
```
