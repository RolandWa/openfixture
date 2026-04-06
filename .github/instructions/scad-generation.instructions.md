---
description: OpenSCAD fixture generation patterns and parameter conventions. Use when editing openfixture.scad, adding features, or debugging fixture geometry.
applyTo: "**/*.scad"
---

# OpenSCAD Fixture Generation

## Parameter Passing Convention

GenFixture.py passes parameters via OpenSCAD's `-D` command-line flag:

```python
# In GenFixture.py
cmd = [openscad_exe, 
       '-D', f'mode="{mode}"',              # String: quoted
       '-D', f'mat_th={value}',              # Number: unquoted
       '-D', f'test_points_top={array}',     # Array: unquoted
       '-D', f'pcb_outline="{path}"',        # Path: quoted, forward slashes
       '-o', output_file, 
       scad_file]
```

**Quoting rules**:
- Strings and paths: **quoted** (`mode="lasercut"`)
- Numbers and arrays: **unquoted** (`mat_th=3.0`, `test_points=[[1,2],[3,4]]`)
- Windows paths: Convert backslashes to forward slashes before passing

## Core Parameters

```openscad
// Required parameters (passed by GenFixture.py)
mode = "lasercut";              // "lasercut", "testcut", or "3dmodel"
mat_th = 3.0;                    // Material thickness (mm)
pcb_th = 1.6;                    // PCB thickness (mm)
test_points_top = [[x1,y1], [x2,y2], ...];    // Top test points
test_points_bottom = [[x1,y1], [x2,y2], ...]; // Bottom test points
pcb_outline = "path/to/outline.dxf";          // Board outline DXF

// Hardware parameters
screw_len = 16.0;                // Assembly screw length
screw_d = 3.0;                   // Screw diameter (M3)
nut_th = 2.4;                    // Hex nut thickness
nut_f2f = 5.45;                  // Hex nut flat-to-flat
nut_c2c = 6.10;                  // Hex nut corner-to-corner
pivot_d = 3.0;                   // Hinge pivot diameter
border = 0.8;                    // PCB support border width

// Pogo pin parameters
pogo_d = 1.02;                   // Pogo pin diameter
pogo_uncompressed_length = 16.0; // Pogo pin max length
pogo_travel = 2.5;               // Pogo pin compression stroke
```

## Module Pattern

**Standard module structure**:
```openscad
module fixture_part(params) {
    difference() {
        // Positive geometry (material to keep)
        base_shape();
        
        // Negative geometry (material to remove)
        mounting_holes();
        pogo_pin_holes();
        clearance_cutouts();
    }
}
```

## Coordinate System

- **Origin**: Top-left corner of PCB outline
- **X-axis**: Right is positive
- **Y-axis**: Down is positive (matches KiCAD screen coordinates)
- **Z-axis**: Up is positive (layer stacking)

**Layer stack** (from bottom to top):
```
Z=0:              Bottom fixture plate
Z=mat_th:         Bottom pogo holder
Z=mat_th*2:       PCB position (clamped)
Z=mat_th*2+pcb_th: Top of PCB
Z=mat_th*3:       Top pogo holder
Z=mat_th*4:       Top fixture plate
```

## Pogo Pin Placement

**Critical constraints**:
1. Hole diameter: `pogo_d` (typically 1.02mm for snug fit)
2. Depth: Through material thickness (`mat_th`)
3. Position: Exact test point coordinates from KiCAD
4. Compression: Allow `pogo_travel` stroke distance

```openscad
module pogo_holes(test_points, layer_z) {
    for (point = test_points) {
        translate([point[0], point[1], layer_z])
            cylinder(h = mat_th + 0.1, d = pogo_d, $fn = 20);
    }
}
```

## DXF Import Pattern

**Board outline import**:
```openscad
module pcb_outline_shape() {
    linear_extrude(height = pcb_th)
        import(file = pcb_outline, layer = "0");  // DXF layer "0"
}
```

**Important**: 
- DXF must use forward slashes even on Windows
- GenFixture.py handles path conversion automatically
- Layer name is typically "0" for single-layer DXF exports

## Mode Handling

```openscad
if (mode == "lasercut") {
    // 2D projection for laser cutting
    projection(cut = false) {
        layout_2d();  // Arrange parts for efficient cutting
    }
}
else if (mode == "testcut") {
    // Small validation piece (subset of test points)
    test_piece();
}
else if (mode == "3dmodel") {
    // Full 3D assembly for visualization
    assembled_fixture();
}
```

## Laser Cut Layout

**Optimize material usage**:
- Arrange parts with minimal waste
- Leave ~2mm spacing between parts for laser kerf
- Label parts with engraved text
- Include assembly markers (alignment holes)

```openscad
module layout_2d() {
    // Part 1: Top plate
    translate([0, 0]) top_plate();
    
    // Part 2: Bottom plate (flipped for symmetry)
    translate([board_width + 5, 0]) mirror([1, 0, 0]) bottom_plate();
    
    // Part 3: Pogo holders
    translate([0, board_height + 5]) pogo_holder_top();
    translate([holder_width + 5, board_height + 5]) pogo_holder_bottom();
}
```

## Common Gotchas

### 1. Pogo Pin Alignment
**Problem**: Pogo pins misaligned between top/bottom fixtures  
**Solution**: Use same test point coordinates, account for PCB thickness

```openscad
// Bottom fixture: pogos point UP
translate([0, 0, mat_th])
    rotate([0, 0, 0])
        pogo_holes(test_points_bottom, 0);

// Top fixture: pogos point DOWN (mirrored)
translate([0, 0, mat_th*3])
    rotate([180, 0, 0])
        pogo_holes(test_points_top, 0);
```

### 2. Hinge Mechanism Clearance
**Problem**: Fixture doesn't open/close smoothly  
**Solution**: Add clearance to pivot holes (0.2-0.3mm)

```openscad
pivot_clearance = 0.3;
cylinder(d = pivot_d + pivot_clearance, h = mat_th);
```

### 3. Material Thickness Tolerance
**Problem**: Parts don't fit after laser cutting  
**Solution**: Account for laser kerf (~0.1-0.2mm)

```openscad
kerf_offset = 0.15;  // Adjust for your laser
offset(delta = -kerf_offset) base_shape();
```

## Rendering Performance

**Speed up OpenSCAD rendering**:
```openscad
$fn = mode == "lasercut" ? 20 : 50;  // Lower resolution for DXF export
```

**Preview modes**:
- `F5` (Preview): Fast, good for development
- `F6` (Render): Slow, required for STL export
- Command-line: Use `-o file.dxf` for automatic rendering

## Testing Strategy

1. **testcut mode**: Generate single test point validation piece
2. **3dmodel mode**: Verify assembly in 3D before committing to DXF
3. **lasercut mode**: Final DXF output for production

## Extension Points

When adding new features:

1. **Add parameters** to GenFixture.py:
   ```python
   parser.add_argument('--new_param', type=float, default=1.0)
   ```

2. **Pass to OpenSCAD**:
   ```python
   cmd.extend(['-D', f'new_param={args.new_param}'])
   ```

3. **Use in SCAD**:
   ```openscad
   new_param = 1.0;  // Default value
   // Use in geometry...
   ```

4. **Document** in fixture_config.toml:
   ```toml
   [hardware]
   new_param_mm = 1.0
   ```
