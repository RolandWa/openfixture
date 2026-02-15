# Copilot Instructions: KiCAD Python API Reference

**Purpose**: Guide AI assistants in using KiCAD's Python API (pcbnew module)  
**Target**: Python developers working with KiCAD 7.0+ / 9.0+ PCB data structures  
**Last Updated**: February 15, 2026

---

## 1. API Overview

The **pcbnew** module provides Python bindings for KiCAD's PCB data structures. It allows:
- Reading PCB board layout data
- Modifying tracks, footprints, zones, layers
- Creating new board items (shapes, text, groups)
- Querying connectivity, net information
- Exporting Gerber files, BOM, reports

**Import**:
```python
import pcbnew
```

**Documentation**: https://docs.kicad.org/doxygen/

---

## 2. Board Access

### 2.1 Get Current Board

```python
# In Action Plugin (Run() method)
board = pcbnew.GetBoard()

# In standalone script
board = pcbnew.LoadBoard("/path/to/file.kicad_pcb")
```

**Type**: `pcbnew.BOARD` object

---

### 2.2 Board Properties

```python
board = pcbnew.GetBoard()

# Basic info
filename = board.GetFileName()          # Full path to .kicad_pcb file
name = os.path.basename(filename)       # Filename only

# Dimensions
bbox = board.GetBoardEdgesBoundingBox()
width_mm = pcbnew.ToMM(bbox.GetWidth())
height_mm = pcbnew.ToMM(bbox.GetHeight())

# Layer count
layer_count = board.GetCopperLayerCount()  # 2, 4, 6, 8, ...

# Design rules
default_track_width = board.GetDesignSettings().GetCurrentTrackWidth()
default_via_size = board.GetDesignSettings().GetCurrentViaSize()
```

---

### 2.3 Save Board

```python
# Save modifications
board.Save(board.GetFileName())

# Save as new file
board.Save("/path/to/new_file.kicad_pcb")
```

---

## 3. Layers

### 3.1 Layer IDs and Names

```python
board = pcbnew.GetBoard()

# Get layer ID from name
layer_id = board.GetLayerID("F.Cu")          # Front copper
layer_id = board.GetLayerID("B.Cu")          # Back copper  
layer_id = board.GetLayerID("In1.Cu")        # Inner layer 1
layer_id = board.GetLayerID("Cmts.User")     # User comments (for markers)

# Get layer name from ID
layer_name = board.GetLayerName(layer_id)

# Standard layer names (KiCAD 9.x)
# Copper layers: F.Cu, In1.Cu, In2.Cu, ..., B.Cu
# Technical layers: F.SilkS, B.SilkS, F.Mask, B.Mask, Edge.Cuts
# User layers: Cmts.User, Dwgs.User, Eco1.User, Eco2.User
```

---

### 3.2 Iterate All Layers

```python
# Enabled layers only
for layer_id in board.GetEnabledLayers().Seq():
    layer_name = board.GetLayerName(layer_id)
    print(f"Layer {layer_id}: {layer_name}")

# Copper layers only
for i in range(board.GetCopperLayerCount()):
    if i == 0:
        layer_id = board.GetLayerID("F.Cu")
    elif i == board.GetCopperLayerCount() - 1:
        layer_id = board.GetLayerID("B.Cu")
    else:
        layer_id = board.GetLayerID(f"In{i}.Cu")
    
    print(f"Copper layer {i}: {board.GetLayerName(layer_id)}")
```

---

## 4. Tracks and Vias

### 4.1 Access Tracks

```python
board = pcbnew.GetBoard()

# Get all tracks (includes segments and vias)
tracks = board.GetTracks()

# Iterate tracks
for item in tracks:
    if isinstance(item, pcbnew.PCB_TRACK):
        # Regular track segment
        start = item.GetStart()       # pcbnew.VECTOR2I
        end = item.GetEnd()           # pcbnew.VECTOR2I
        width = item.GetWidth()       # Internal units
        layer = item.GetLayer()       # Layer ID
        net = item.GetNetname()       # Net name string
        
    elif isinstance(item, pcbnew.PCB_VIA):
        # Via
        pos = item.GetPosition()      # pcbnew.VECTOR2I
        diameter = item.GetWidth()    # Via outer diameter
        drill = item.GetDrillValue()  # Via drill size
        net = item.GetNetname()       # Net name
        
        # Via layer span
        top_layer = item.TopLayer()
        bottom_layer = item.BottomLayer()
```

**Type Hierarchy**:
```
PCB_TRACK (base class)
├── PCB_VIA (inherits from PCB_TRACK)
└── PCB_ARC (arc-shaped track, KiCAD 6+)
```

---

### 4.2 Filter Tracks by Net

```python
# Get specific net
net = board.FindNet("VCC")  # Returns NETINFO_ITEM or None

if net:
    net_code = net.GetNetCode()
    
    # Find all tracks on this net
    for track in board.GetTracks():
        if track.GetNetCode() == net_code:
            print(f"Track on VCC: {pcbnew.ToMM(track.GetLength())} mm")
```

---

### 4.3 Create New Track

```python
# Create track segment
track = pcbnew.PCB_TRACK(board)
track.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(10), pcbnew.FromMM(20)))
track.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(30), pcbnew.FromMM(20)))
track.SetWidth(pcbnew.FromMM(0.25))
track.SetLayer(board.GetLayerID("F.Cu"))

# Assign to net
net = board.FindNet("GND")
if net:
    track.SetNet(net)

# Add to board
board.Add(track)
```

---

## 5. Footprints (Components)

### 5.1 Access Footprints

```python
board = pcbnew.GetBoard()

# Iterate all footprints
for footprint in board.GetFootprints():
    ref = footprint.GetReference()        # e.g., "U1", "C15"
    value = footprint.GetValue()          # e.g., "ATmega328", "100nF"
    pos = footprint.GetPosition()         # pcbnew.VECTOR2I
    orientation = footprint.GetOrientation()  # Degrees * 10 (e.g., 900 = 90°)
    layer = footprint.GetLayer()          # F.Cu or B.Cu
    
    print(f"{ref} = {value} at ({pcbnew.ToMM(pos.x)}, {pcbnew.ToMM(pos.y)})")
```

---

### 5.2 Access Pads

```python
for footprint in board.GetFootprints():
    ref = footprint.GetReference()
    
    # Iterate pads
    for pad in footprint.Pads():
        pad_name = pad.GetName()          # Pin number/name (e.g., "1", "GND")
        pad_pos = pad.GetPosition()       # pcbnew.VECTOR2I
        pad_net = pad.GetNetname()        # Connected net name
        pad_shape = pad.GetShape()        # Circle, Rect, Oval, etc.
        
        print(f"{ref} pad {pad_name}: net={pad_net}")
```

**Pad Shapes**:
```python
pcbnew.PAD_SHAPE_CIRCLE
pcbnew.PAD_SHAPE_RECTANGLE  # Renamed to RECT in KiCAD 9.x
pcbnew.PAD_SHAPE_OVAL
pcbnew.PAD_SHAPE_TRAPEZOID
pcbnew.PAD_SHAPE_ROUNDRECT
```

---

### 5.3 Filter Footprints by Reference

```python
# Find specific IC
ic_ref = "U1"
ic = None

for footprint in board.GetFootprints():
    if footprint.GetReference() == ic_ref:
        ic = footprint
        break

if ic:
    print(f"Found {ic_ref} at ({pcbnew.ToMM(ic.GetPosition().x)}, {pcbnew.ToMM(ic.GetPosition().y)})")
else:
    print(f"{ic_ref} not found")
```

---

### 5.4 Filter Footprints by Prefix

```python
# Find all ICs (U1, U2, U3, ...)
ic_prefixes = ["U", "IC"]

ics = []
for footprint in board.GetFootprints():
    ref = footprint.GetReference()
    if any(ref.startswith(prefix) for prefix in ic_prefixes):
        ics.append(footprint)

print(f"Found {len(ics)} ICs")
```

---

## 6. Zones (Copper Pours)

### 6.1 Access Zones

```python
board = pcbnew.GetBoard()

# Iterate all zones
for zone in board.Zones():
    net = zone.GetNetname()              # Net name (e.g., "GND")
    layer = zone.GetLayer()              # Layer ID
    is_filled = zone.IsFilled()          # Filled or outline only
    
    # Zone outline (polygon)
    outline = zone.Outline()             # pcbnew.SHAPE_POLY_SET
    area_mm2 = pcbnew.ToMM(zone.GetArea()) ** 2  # Approximate area
    
    print(f"Zone on {board.GetLayerName(layer)}, net={net}, filled={is_filled}")
```

---

### 6.2 Test Point Inside Zone

```python
# Check if point is inside filled zone
point = pcbnew.VECTOR2I(pcbnew.FromMM(50), pcbnew.FromMM(50))

for zone in board.Zones():
    if zone.IsFilled():
        # HitTest checks if point is inside filled zone
        if zone.HitTest(point):
            print(f"Point is inside zone on net {zone.GetNetname()}")
```

---

### 6.3 Get Zone Outline Points

```python
for zone in board.Zones():
    outline = zone.Outline()  # SHAPE_POLY_SET
    
    # Iterate contours (outer boundary + holes)
    for i in range(outline.OutlineCount()):
        contour = outline.Outline(i)
        
        # Iterate points in contour
        for j in range(contour.PointCount()):
            point = contour.GetPoint(j)
            x_mm = pcbnew.ToMM(point.x)
            y_mm = pcbnew.ToMM(point.y)
            print(f"Point {j}: ({x_mm}, {y_mm})")
```

---

## 7. Nets and Net Classes

### 7.1 Find Net by Name

```python
board = pcbnew.GetBoard()

# Find net (case-sensitive)
net = board.FindNet("VCC")

if net:
    net_code = net.GetNetCode()         # Unique integer ID
    net_name = net.GetNetname()         # String name
    print(f"Net {net_name} has code {net_code}")
else:
    print("Net VCC not found")
```

---

### 7.2 Iterate All Nets

```python
# Get all nets
netinfo_list = board.GetNetInfo()

for net in netinfo_list.NetsByName():
    net_name = net.GetNetname()
    net_code = net.GetNetCode()
    print(f"Net: {net_name} (code {net_code})")
```

---

### 7.3 Net Classes

```python
# Get net classes (e.g., "HighSpeed", "Power", "Default")
net_classes = board.GetAllNetClasses()

for net_class_name, net_class in net_classes.items():
    print(f"Net class: {net_class_name}")
    print(f"  Track width: {pcbnew.ToMM(net_class.GetTrackWidth())} mm")
    print(f"  Clearance: {pcbnew.ToMM(net_class.GetClearance())} mm")
    print(f"  Via diameter: {pcbnew.ToMM(net_class.GetViaDiameter())} mm")
```

---

### 7.4 Get Net Class for Track/Footprint

```python
# Track net class
for track in board.GetTracks():
    net = track.GetNet()
    if net:
        net_class_name = net.GetNetClassName()
        print(f"Track on net {net.GetNetname()}, class={net_class_name}")

# Pad net class
for footprint in board.GetFootprints():
    for pad in footprint.Pads():
        net = pad.GetNet()
        if net:
            net_class_name = net.GetNetClassName()
            print(f"{footprint.GetReference()} pad {pad.GetName()}: class={net_class_name}")
```

**Common Net Classes**:
- `"Default"` - Unclassified nets
- `"Power"` - Power rails (VCC, GND)
- `"HighSpeed"` - High-speed signals (>50 MHz)
- `"Differential"` - Differential pairs (USB, Ethernet)
- `"Clock"` - Clock signals

---

## 8. Geometry and Distance

### 8.1 VECTOR2I (Position)

```python
# Create position (in internal units, typically nanometers)
pos = pcbnew.VECTOR2I(1000000, 2000000)  # 1mm, 2mm in internal units

# Better: use FromMM
pos = pcbnew.VECTOR2I(pcbnew.FromMM(10), pcbnew.FromMM(20))

# Access coordinates
x = pos.x  # Internal units
y = pos.y

# Convert to mm
x_mm = pcbnew.ToMM(pos.x)
y_mm = pcbnew.ToMM(pos.y)
```

---

### 8.2 Calculate Distance

```python
# 2D Euclidean distance
def get_distance(p1, p2):
    """
    Calculate distance between two points.
    
    Args:
        p1, p2: pcbnew.VECTOR2I
    
    Returns:
        float: Distance in internal units
    """
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    return math.sqrt(dx * dx + dy * dy)

# Usage
pos1 = track.GetStart()
pos2 = via.GetPosition()
distance = get_distance(pos1, pos2)
distance_mm = pcbnew.ToMM(distance)
```

---

### 8.3 Bounding Box

```python
# Track bounding box
bbox = track.GetBoundingBox()
left = bbox.GetLeft()
right = bbox.GetRight()
top = bbox.GetTop()
bottom = bbox.GetBottom()
width = bbox.GetWidth()
height = bbox.GetHeight()

# Check if point inside bounding box
point = pcbnew.VECTOR2I(pcbnew.FromMM(10), pcbnew.FromMM(20))
if bbox.Contains(point):
    print("Point is inside track bounding box")
```

---

### 8.4 Unit Conversion

```python
# mm → internal units
distance_iu = pcbnew.FromMM(2.5)        # 2.5 mm
width_iu = pcbnew.FromMM(0.25)          # 0.25 mm (250 µm)

# internal units → mm
distance_mm = pcbnew.ToMM(2500000)      # 2.5 mm
width_mm = pcbnew.ToMM(250000)          # 0.25 mm

# mils → internal units
distance_iu = pcbnew.FromMils(100)      # 100 mils (2.54 mm)

# inches → internal units
distance_iu = pcbnew.FromMils(1000)     # 1 inch = 1000 mils
```

**Internal Units**: KiCAD uses integer nanometers (1nm) internally for precision

---

## 9. Drawing (Markers, Shapes, Text)

### 9.1 Create PCB Group

```python
# Create group for organizing markers
group = pcbnew.PCB_GROUP(board)
group.SetName("EMC_Violation_1")
board.Add(group)

# Add items to group
group.AddItem(circle)
group.AddItem(text)
```

**Benefits**:
- User can select entire violation with one click
- "Select Items in Group" context menu
- Delete entire group at once

---

### 9.2 Draw Circle

```python
# Create circle marker
circle = pcbnew.PCB_SHAPE(board)
circle.SetShape(pcbnew.SHAPE_T_CIRCLE)  # Circle shape
circle.SetCenter(pcbnew.VECTOR2I(pcbnew.FromMM(50), pcbnew.FromMM(50)))
circle.SetRadius(pcbnew.FromMM(0.8))    # 0.8mm radius
circle.SetWidth(pcbnew.FromMM(0.1))     # 0.1mm line width
circle.SetLayer(board.GetLayerID("Cmts.User"))
circle.SetStroke(pcbnew.STROKE_PARAMS(pcbnew.FromMM(0.1), pcbnew.PLOT_DASH_TYPE_SOLID))

# Add to board
board.Add(circle)

# Add to group (optional)
group.AddItem(circle)
```

**Shape Types** (pcbnew.SHAPE_T_*):
```python
pcbnew.SHAPE_T_CIRCLE
pcbnew.SHAPE_T_RECTANGLE
pcbnew.SHAPE_T_ARC
pcbnew.SHAPE_T_POLYGON
pcbnew.SHAPE_T_BEZIER
```

---

### 9.3 Draw Line/Arrow

```python
# Create line
line = pcbnew.PCB_SHAPE(board)
line.SetShape(pcbnew.SHAPE_T_SEGMENT)   # Line segment
line.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(10), pcbnew.FromMM(20)))
line.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(30), pcbnew.FromMM(40)))
line.SetWidth(pcbnew.FromMM(0.1))
line.SetLayer(board.GetLayerID("Cmts.User"))
board.Add(line)

# Add arrowhead (triangle at end)
def draw_arrow(board, start, end, layer, group):
    """Draw arrow from start to end"""
    # Main line
    line = pcbnew.PCB_SHAPE(board)
    line.SetShape(pcbnew.SHAPE_T_SEGMENT)
    line.SetStart(start)
    line.SetEnd(end)
    line.SetWidth(pcbnew.FromMM(0.1))
    line.SetLayer(layer)
    board.Add(line)
    group.AddItem(line)
    
    # Calculate arrowhead points (30° angle, 0.5mm length)
    dx = end.x - start.x
    dy = end.y - start.y
    length = math.sqrt(dx*dx + dy*dy)
    ux, uy = dx/length, dy/length  # Unit vector
    
    arrow_len = pcbnew.FromMM(0.5)
    angle = math.radians(30)
    
    # Arrowhead side 1
    p1 = pcbnew.VECTOR2I(
        int(end.x - arrow_len * (ux * math.cos(angle) - uy * math.sin(angle))),
        int(end.y - arrow_len * (uy * math.cos(angle) + ux * math.sin(angle)))
    )
    
    # Arrowhead side 2
    p2 = pcbnew.VECTOR2I(
        int(end.x - arrow_len * (ux * math.cos(angle) + uy * math.sin(angle))),
        int(end.y - arrow_len * (uy * math.cos(angle) - ux * math.sin(angle)))
    )
    
    # Draw arrowhead lines
    for p in [p1, p2]:
        arrowhead = pcbnew.PCB_SHAPE(board)
        arrowhead.SetShape(pcbnew.SHAPE_T_SEGMENT)
        arrowhead.SetStart(end)
        arrowhead.SetEnd(p)
        arrowhead.SetWidth(pcbnew.FromMM(0.1))
        arrowhead.SetLayer(layer)
        board.Add(arrowhead)
        group.AddItem(arrowhead)
```

---

### 9.4 Draw Text Label

```python
# Create text label
text = pcbnew.PCB_TEXT(board)
text.SetText("CAP TOO FAR (4.2mm)")
text.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(50), pcbnew.FromMM(52)))
text.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.5), pcbnew.FromMM(0.5)))
text.SetTextThickness(pcbnew.FromMM(0.1))
text.SetLayer(board.GetLayerID("Cmts.User"))
text.SetHorizJustify(pcbnew.GR_TEXT_HJUSTIFY_CENTER)  # Center-aligned
board.Add(text)

# Add to group
group.AddItem(text)
```

**Text Alignment**:
```python
pcbnew.GR_TEXT_HJUSTIFY_LEFT
pcbnew.GR_TEXT_HJUSTIFY_CENTER
pcbnew.GR_TEXT_HJUSTIFY_RIGHT

pcbnew.GR_TEXT_VJUSTIFY_TOP
pcbnew.GR_TEXT_VJUSTIFY_CENTER
pcbnew.GR_TEXT_VJUSTIFY_BOTTOM
```

---

## 10. Connectivity

### 10.1 Get Connected Items

```python
# Get items electrically connected to a pad
for footprint in board.GetFootprints():
    for pad in footprint.Pads():
        # Get all items connected to this pad
        connected_items = pad.GetConnectedItems()
        
        for item in connected_items:
            if isinstance(item, pcbnew.PCB_TRACK):
                print(f"Pad {pad.GetName()} connected to track")
            elif isinstance(item, pcbnew.PAD):
                print(f"Pad {pad.GetName()} connected to another pad")
```

---

### 10.2 Check Net Connectivity

```python
# Check if two pads are on same net
pad1 = footprint1.FindPadByNumber("1")
pad2 = footprint2.FindPadByNumber("2")

if pad1.GetNetCode() == pad2.GetNetCode():
    print(f"Pads are on same net: {pad1.GetNetname()}")
else:
    print("Pads are on different nets")
```

---

## 11. Common Patterns

### 11.1 Pattern Matching (Net Names)

```python
# Case-insensitive substring matching
ground_patterns = ["GND", "GROUND", "VSS", "PGND", "AGND"]

def is_ground_net(net_name):
    """Check if net name matches ground patterns"""
    net_upper = net_name.upper()
    return any(pattern in net_upper for pattern in ground_patterns)

# Usage
for track in board.GetTracks():
    if is_ground_net(track.GetNetname()):
        print(f"Found ground track on net {track.GetNetname()}")
```

---

### 11.2 Net Class Filtering

```python
# Find all tracks in "HighSpeed" net class
high_speed_tracks = []

for track in board.GetTracks():
    net = track.GetNet()
    if net and net.GetNetClassName() == "HighSpeed":
        high_speed_tracks.append(track)

print(f"Found {len(high_speed_tracks)} high-speed tracks")
```

---

### 11.3 Reference Prefix Filtering

```python
# Find all capacitors (C1, C2, C3, ...)
capacitors = []

for footprint in board.GetFootprints():
    ref = footprint.GetReference()
    if ref.startswith("C"):
        capacitors.append(footprint)

print(f"Found {len(capacitors)} capacitors")
```

---

### 11.4 Layer-Specific Queries

```python
# Find all tracks on front copper
front_cu = board.GetLayerID("F.Cu")

front_tracks = []
for track in board.GetTracks():
    if isinstance(track, pcbnew.PCB_TRACK) and track.GetLayer() == front_cu:
        front_tracks.append(track)

print(f"Found {len(front_tracks)} tracks on F.Cu")
```

---

### 11.5 Distance Threshold Checks

```python
# Find all capacitors within 3mm of IC U1
max_distance_mm = 3.0
max_distance = pcbnew.FromMM(max_distance_mm)

ic = None
for footprint in board.GetFootprints():
    if footprint.GetReference() == "U1":
        ic = footprint
        break

if ic:
    ic_pos = ic.GetPosition()
    
    nearby_caps = []
    for footprint in board.GetFootprints():
        ref = footprint.GetReference()
        if ref.startswith("C"):
            cap_pos = footprint.GetPosition()
            distance = get_distance(ic_pos, cap_pos)
            
            if distance <= max_distance:
                nearby_caps.append((ref, pcbnew.ToMM(distance)))
    
    print(f"Found {len(nearby_caps)} capacitors within {max_distance_mm}mm of U1")
    for ref, dist in nearby_caps:
        print(f"  {ref}: {dist:.2f}mm")
```

---

## 12. Performance Optimization

### 12.1 Pre-filter by Layer

```python
# Build dictionary: layer_id → list of zones
zones_by_layer = {}

for zone in board.Zones():
    layer = zone.GetLayer()
    if layer not in zones_by_layer:
        zones_by_layer[layer] = []
    zones_by_layer[layer].append(zone)

# Fast lookup (O(1) instead of O(n))
front_zones = zones_by_layer.get(board.GetLayerID("F.Cu"), [])
```

---

### 12.2 Bounding Box Pre-check

```python
# Check bounding box before expensive operations
point = pcbnew.VECTOR2I(pcbnew.FromMM(50), pcbnew.FromMM(50))

for zone in board.Zones():
    bbox = zone.GetBoundingBox()
    
    # Fast reject: point outside bounding box
    if not bbox.Contains(point):
        continue
    
    # Expensive: detailed HitTest only if inside bbox
    if zone.HitTest(point):
        print("Point is inside zone")
```

---

### 12.3 Spatial Indexing (Grid)

```python
# Build grid-based spatial index for obstacles
class SpatialIndex:
    def __init__(self, obstacles, cell_size_mm=5.0):
        self.grid = {}
        self.cell_size = pcbnew.FromMM(cell_size_mm)
        
        for idx, obstacle in enumerate(obstacles):
            bbox = obstacle['bbox']
            min_cell_x = bbox.GetLeft() // self.cell_size
            max_cell_x = bbox.GetRight() // self.cell_size
            min_cell_y = bbox.GetTop() // self.cell_size
            max_cell_y = bbox.GetBottom() // self.cell_size
            
            for cx in range(min_cell_x, max_cell_x + 1):
                for cy in range(min_cell_y, max_cell_y + 1):
                    key = (cx, cy)
                    if key not in self.grid:
                        self.grid[key] = []
                    self.grid[key].append(idx)
    
    def get_obstacles_near_point(self, point):
        """Get only obstacles near point (O(1) average)"""
        cx = point.x // self.cell_size
        cy = point.y // self.cell_size
        return self.grid.get((cx, cy), [])
```

---

## 13. Error Handling

### 13.1 Safe Board Access

```python
def Run(self):
    board = pcbnew.GetBoard()
    
    # Check if board is valid
    if not board:
        wx.MessageBox("No PCB open", "Error", wx.OK | wx.ICON_ERROR)
        return
    
    # Check if board has data
    if len(list(board.GetTracks())) == 0:
        wx.MessageBox("Board has no tracks", "Warning", wx.OK | wx.ICON_WARNING)
        return
    
    # Proceed with checks
    # ...
```

---

### 13.2 Safe Net Access

```python
# Safe net name access
for track in board.GetTracks():
    net = track.GetNet()
    
    if net:
        net_name = net.GetNetname()
        # Process net
    else:
        # Unconnected track
        print("Track not connected to any net")
```

---

### 13.3 Safe Reference Access

```python
# Check if footprint exists
ic_ref = "U1"
ic = None

for footprint in board.GetFootprints():
    if footprint.GetReference() == ic_ref:
        ic = footprint
        break

if ic is None:
    print(f"Component {ic_ref} not found")
    return

# Proceed with IC checks
# ...
```

---

## 14. Quick Reference

### Essential Functions

```python
# Board access
board = pcbnew.GetBoard()
board = pcbnew.LoadBoard(path)

# Iteration
board.GetTracks()          # All tracks and vias
board.GetFootprints()      # All components
board.Zones()              # All copper pours
footprint.Pads()           # All pads on footprint

# Layer management
board.GetLayerID(name)     # "F.Cu" → layer ID
board.GetLayerName(id)     # Layer ID → "F.Cu"

# Net management
board.FindNet(name)        # Find net by name
track.GetNetname()         # Net name for track
pad.GetNetCode()           # Net code for pad

# Geometry
pcbnew.VECTOR2I(x, y)      # Create position
pcbnew.FromMM(value)       # mm → internal units
pcbnew.ToMM(value)         # Internal units → mm

# Distance
dx = p1.x - p2.x
dy = p1.y - p2.y
distance = math.sqrt(dx*dx + dy*dy)

# Drawing
pcbnew.PCB_GROUP(board)    # Create group
pcbnew.PCB_SHAPE(board)    # Create shape (circle, line, etc.)
pcbnew.PCB_TEXT(board)     # Create text label
```

### Type Reference

```python
# Board items
pcbnew.BOARD              # PCB board
pcbnew.PCB_TRACK          # Track segment
pcbnew.PCB_VIA            # Via
pcbnew.FOOTPRINT          # Component footprint
pcbnew.PAD                # Pad on footprint
pcbnew.ZONE               # Copper pour / filled zone
pcbnew.PCB_SHAPE          # Drawing shape (circle, line, rect, etc.)
pcbnew.PCB_TEXT           # Text label
pcbnew.PCB_GROUP          # Group of items

# Geometry
pcbnew.VECTOR2I           # 2D position (x, y)
pcbnew.BOX2I              # Bounding box (left, top, width, height)
pcbnew.SHAPE_POLY_SET     # Polygon outline

# Nets
pcbnew.NETINFO_ITEM       # Net information
pcbnew.NETCLASS           # Net class (HighSpeed, Power, etc.)
```

---

**End of KiCAD Python API Reference**
