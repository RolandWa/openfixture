# OpenFixture Z-Axis Component Alignment Analysis

## Component Stack Configuration

### Default Parameters
```openscad
screw_thr_len = 16mm
mat_th = 3mm
pcb_th = 1.6mm
nut_th = 2.25mm
pogo_uncompressed_length = 8mm
pogo_compression = 1mm
pivot_support_r = 4.55mm (calculated from pivot_d + 6)/2
```

### Calculated Dimensions
```openscad
head_z = screw_thr_len - nut_th = 16 - 2.25 = 13.75mm
base_z = screw_thr_len + 3*mat_th = 16 + 9 = 25mm
base_pivot_offset = pivot_support_r + (pogo_uncompressed_length - pogo_compression) - (mat_th - pcb_th)
                  = 4.55 + (8 - 1) - (3 - 1.6)
                  = 4.55 + 7 - 1.4
                  = 10.15mm
```

## Z-Axis Position Breakdown

### BASE ASSEMBLY (Fixed, Z origin at base bottom)

```
Z = 25mm (base_z)                    ═══════════════════════════ Top of base structure
                                     
Z = 22mm (base_z - mat_th)           ┌─────────────────────────┐ ← TOP CARRIER (tight fit)
                                     │  PCB cutout (exact)     │    Clamps PCB from above
                                     └─────────────────────────┘    mat_th = 3mm thick
                                     
Z = 19mm (base_z - 2*mat_th)         ┌─────────────────────────┐ ← BOTTOM CARRIER (inset)
                                     │  PCB cutout (inset 1mm) │    Supports PCB from below
                                     └─────────────────────────┘    mat_th = 3mm thick
                                     
Z = 0mm                              ═══════════════════════════ Base bottom
```

**PCB Position in Carriers:**
- PCB sits between the two carriers
- Top carrier bottom surface: Z = 22mm
- Bottom carrier top surface: Z = 19mm + mat_th = 22mm
- **PCB rests at approximately Z = 22mm**

### HEAD ASSEMBLY (When Closed)

The head pivots at:
```
Pivot Z-position = base_z + base_pivot_offset
                 = 25 + 10.15
                 = 35.15mm
```

When head rotates down (closed position, approximate -8° rotation):

```
Z = 35.15mm                          ●●●●●●●●●●●●●●●●●●●●●●●●●●● ← Pivot hinge point
                                     
Z ≈ 25mm (head_top)                  ┌─────────────────────────┐ ← HEAD TOP PLATE
                                     │  Clearance holes        │    Z = head_z - mat_th
                                     │  for pogo pins          │    = 13.75 - 3 = 10.75mm
                                     └─────────────────────────┘    (relative to head base)
                                     
                                         ↓↓↓ Pogo pins ↓↓↓
                                     
Z ≈ 22mm (contact with PCB)          ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ← Pogo pin tips contact PCB
                                         (compressed 1mm)
                                     
Z ≈ 22mm (head_base)                 ┌─────────────────────────┐ ← HEAD BASE PLATE
                                     │  ● ● ● (pogo holes)     │    Contains ALL pogo pins
                                     │  Both TOP & BOTTOM      │    (top side AND bottom side
                                     │  test points here       │    test points)
                                     └─────────────────────────┘    Z = 0 (relative to head)
```

## Critical Alignment Issue Identified

### ❌ **PROBLEM: Head and Carriers Are NOT Aligned**

**Expected PCB position:** Z = 22mm (between carriers)

**Head base position when closed:** 
```
head_base_z_global = (base_z + base_pivot_offset) - head assembly height
                   = 35.15 - (head_z + adjustments for rotation)
                   ≈ 22-25mm range (depends on rotation angle)
```

### ⚠️ **Architecture Clarification Needed**

**Current Design (in code):**
- **1 head base plate** with pogo holes for BOTH top and bottom test points
- **2 carrier plates** sandwich the PCB
- All pogo pins come from the same direction (head closes down)

**This means:**
- Pogo pins for "top" test points press down directly
- Pogo pins for "bottom" test points must pass THROUGH the PCB somehow
  - OR there's a design assumption that "bottom" means different layer of same-sided access

### 🔧 **What "Top" and "Bottom" Actually Mean**

Looking at the code in `head_base_common()`:
```openscad
// Loop over test points - TOP
for ( i = [0 : 1 : len (test_points_top) - 1] ) {
    circle (r = pogo_r);  // Pogo pin hole
}

// Loop over test points - BOTTOM  
for ( i = [0 : 1 : len (test_points_bottom) - 1] ) {
    circle (r = pogo_r);  // Same pogo pin hole, same plate!
}
```

**Both arrays drill holes in the SAME plate!**

This is a **single-sided fixture** where:
- `test_points_top` = test points on the top copper layer
- `test_points_bottom` = test points on the bottom copper layer
- **All pogo pins access from the TOP** (head closes down)
- PCB is held fixed in carriers
- For bottom-side test points, the pogo pins contact pads on the bottom copper layer that are exposed (no solder mask)

## Answer to User's Question

### Are the 2 carrier boards inline with the 2 head plates?

**There are NOT 2 separate head plates for top/bottom testing.**

**There is:**
1. **1 HEAD BASE plate** (Z ≈ 0 relative to head) - contains ALL pogo pin holes
2. **1 HEAD TOP plate** (Z ≈ 10.75mm relative to head) - structural + pogo clearance
3. **1 BOTTOM CARRIER** (Z = 19mm absolute) - PCB support with 1mm inset
4. **1 TOP CARRIER** (Z = 22mm absolute) - PCB clamp with exact fit

**Alignment when fixture closes:**
- Head base (with pogo pins) presses down on PCB at Z ≈ 22mm ✓
- PCB sits in carriers at Z = 22mm ✓
- **These ARE aligned** - the head closes to bring pogo pins into contact with PCB

**The "2 head plates" misconception:**
- There's only 1 pogo pin plate (head_base)
- Head_top is structural, not a second pogo plate
- Both top and bottom test point arrays use the same head_base plate
