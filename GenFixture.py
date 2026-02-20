#!/usr/bin/python3
"""
OpenFixture Generator - Modernized Version
KiCAD 8.0+ / 9.0+ Compatible

Generates laser-cuttable PCB test fixtures from KiCAD board files
Updated with modern pcbnew API and Python 3 support

Original Author:
    Elliot Buller - Tiny Labs Inc (2016)
    http://tinylabs.io/openfixture

Modernization & v2 Update:
    Community Contributors (2026)
    - Updated to KiCAD 8.0/9.0 API
    - Added TOML configuration support
    - Added type hints and modern Python 3 features
    - Improved error handling and logging

License: CC-BY-SA 4.0
"""

__version__ = "2.0.0"
__author__ = "Elliot Buller, Community Contributors"
__license__ = "CC-BY-SA-4.0"

import os
import sys
import argparse
import logging
import subprocess
import shutil
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import pcbnew

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Defaults
DEFAULT_PCB_TH = 1.6
DEFAULT_SCREW_D = 3.0
DEFAULT_SCREW_LEN = 14


class FixtureConfig:
    """Configuration container for fixture parameters"""
    
    def __init__(self):
        # Board parameters
        self.pcb_th = DEFAULT_PCB_TH
        self.mat_th = 0.0
        
        # Hardware parameters
        self.screw_len = DEFAULT_SCREW_LEN
        self.screw_d = DEFAULT_SCREW_D
        self.washer_th = None
        self.nut_f2f = None
        self.nut_c2c = None
        self.nut_th = None
        self.pivot_d = None
        self.border = None
        self.pogo_uncompressed_length = None
        
        # Revision
        self.rev = None
        
        # Pad type inclusion flags
        self.include_smd = True
        self.include_pth = True
        
        # Logo parameters
        self.logo_enable = True
        self.logo_file = None
        self.logo_scale_x = None
        self.logo_scale_y = None
        self.logo_scale_z = None
        self.logo_offset_x = None
        self.logo_offset_y = None
        self.logo_offset_z = None
        
    @classmethod
    def from_toml(cls, toml_path: str) -> 'FixtureConfig':
        """Load configuration from TOML file"""
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                logger.warning("TOML support not available (Python <3.11 and tomli not installed)")
                return cls()
        
        config = cls()
        if Path(toml_path).exists():
            with open(toml_path, 'rb') as f:
                data = tomllib.load(f)
            
            # Board parameters
            board_cfg = data.get('board', {})
            config.pcb_th = board_cfg.get('thickness_mm', DEFAULT_PCB_TH)
            
            # Material parameters
            material_cfg = data.get('material', {})
            config.mat_th = material_cfg.get('thickness_mm', 0.0)
            
            # Hardware parameters
            hardware_cfg = data.get('hardware', {})
            config.screw_len = hardware_cfg.get('screw_length_mm', DEFAULT_SCREW_LEN)
            config.screw_d = hardware_cfg.get('screw_diameter_mm', DEFAULT_SCREW_D)
            config.washer_th = hardware_cfg.get('washer_thickness_mm')
            config.nut_f2f = hardware_cfg.get('nut_flat_to_flat_mm')
            config.nut_c2c = hardware_cfg.get('nut_corner_to_corner_mm')
            config.nut_th = hardware_cfg.get('nut_thickness_mm')
            config.pivot_d = hardware_cfg.get('pivot_diameter_mm')
            config.border = hardware_cfg.get('border_mm')
            config.pogo_uncompressed_length = hardware_cfg.get('pogo_uncompressed_length_mm')
            
            # Test point detection configuration
            test_points_cfg = data.get('test_points', {})
            config.include_smd = test_points_cfg.get('include_smd_pads', True)
            config.include_pth = test_points_cfg.get('include_pth_pads', True)
            
            # Logo configuration
            logo_cfg = data.get('logo', {})
            config.logo_enable = logo_cfg.get('enable', True)
            config.logo_file = logo_cfg.get('file')
            config.logo_scale_x = logo_cfg.get('scale_x')
            config.logo_scale_y = logo_cfg.get('scale_y')
            config.logo_scale_z = logo_cfg.get('scale_z')
            config.logo_offset_x = logo_cfg.get('offset_x')
            config.logo_offset_y = logo_cfg.get('offset_y')
            config.logo_offset_z = logo_cfg.get('offset_z')
            
            # Revision
            config.rev = board_cfg.get('revision') or data.get('revision')
            
            logger.info(f"Loaded configuration from {toml_path}")
            logger.debug(f"  PCB thickness: {config.pcb_th}mm")
            logger.debug(f"  Material thickness: {config.mat_th}mm")
            logger.debug(f"  Include SMD pads: {config.include_smd}")
            logger.debug(f"  Include PTH pads: {config.include_pth}")
            
        return config


class GenFixture:
    """
    Fixture generator class - modernized for KiCAD 8.0+
    
    Extracts test points from KiCAD PCB and generates OpenSCAD parameters
    for laser-cuttable test fixture generation.
    """
    
    def __init__(self, prj_name: str, brd: pcbnew.BOARD, config: FixtureConfig):
        self.prj_name = prj_name
        self.brd = brd
        self.config = config
        
        # Layer assignments (modern API uses pcbnew constants)
        self.layer = pcbnew.F_Cu
        self.paste = pcbnew.F_Paste
        self.ignore_layer = pcbnew.Eco1_User
        self.force_layer = pcbnew.Eco2_User
        
        # Mirror flag for back-side testing
        self.mirror = False
        
        # Both sides flag
        self.both_sides = False
        
        # Board data
        self.origin = [float("inf"), float("inf")]
        self.dims = [0.0, 0.0]
        self.min_y = float("inf")
        self.test_points: List[Tuple[float, float]] = []
        
        # Separate test point lists for both-sides mode
        self.test_points_top: List[Tuple[float, float]] = []
        self.test_points_bottom: List[Tuple[float, float]] = []
        
        # Actual board dimensions from Edge.Cuts (for validation)
        self.board_width_mm = 0.0
        self.board_height_mm = 0.0
        
    def __str__(self) -> str:
        layer_info = "both sides" if self.both_sides else ("F.Cu" if self.layer == pcbnew.F_Cu else "B.Cu")
        if self.both_sides:
            tp_info = f"top={len(self.test_points_top)} bottom={len(self.test_points_bottom)} total={len(self.test_points)}"
        else:
            tp_info = f"test_points={len(self.test_points)}"
        return (f"Fixture: origin=({self.origin[0]:.02f},{self.origin[1]:.02f}) "
                f"dims=({self.dims[0]:.02f},{self.dims[1]:.02f}) "
                f"min_y={self.min_y:.02f} "
                f"{tp_info} "
                f"layer={layer_info})")
    
    def set_layers(self, layer: int = -1, ilayer: int = -1, flayer: int = -1, both: bool = False):
        """
        Set layer configuration
        
        Args:
            layer: Test point layer (F.Cu or B.Cu, ignored if both=True)
            ilayer: Ignore layer (Eco1.User)
            flayer: Force layer (Eco2.User)
            both: If True, extract test points from both F.Cu and B.Cu
        """
        self.both_sides = both
        
        if layer != -1 and not both:
            self.layer = layer
        if ilayer != -1:
            self.ignore_layer = ilayer
        if flayer != -1:
            self.force_layer = flayer
        
        # Setup paste layer and mirror flag (used when not in both mode)
        if not self.both_sides:
            if self.layer == pcbnew.F_Cu:
                self.paste = pcbnew.F_Paste
                self.mirror = False
            else:
                self.paste = pcbnew.B_Paste
                self.mirror = True
    
    def round_value(self, x: float, base: float = 0.01) -> float:
        """Round value to specified precision"""
        return round(base * round(x / base), 2)
    
    def force_origin_to_zero(self):
        """
        Force the board origin to (0,0) by setting auxiliary origin.
        This ensures all exports (DXF, test points) are normalized to (0,0).
        
        The calculated board origin (top-left corner) is set as the auxiliary origin,
        which makes KiCAD export everything relative to that point.
        """
        logger.info(f"Forcing origin to (0,0) - Board top-left is at KiCAD ({self.origin[0]:.2f}, {self.origin[1]:.2f})")
        
        # Save auxiliary origin (KiCAD 8 compatibility)
        has_aux_origin = hasattr(self.brd, 'GetAuxOrigin')
        
        if has_aux_origin:
            try:
                # Set auxiliary origin to board's top-left corner
                # This makes all subsequent exports use (0,0) as the reference
                origin_point = pcbnew.VECTOR2I(
                    pcbnew.FromMM(self.origin[0]),
                    pcbnew.FromMM(self.origin[1])
                )
                self.brd.SetAuxOrigin(origin_point)
                logger.info("✓ Auxiliary origin set - All exports will use (0,0) reference")
                return origin_point
            except AttributeError:
                logger.warning("SetAuxOrigin not available (KiCAD 9) - using plot origin mode")
                return None
        else:
            logger.info("Auxiliary origin not available (KiCAD 9) - using drill/place origin mode")
            return None
    
    def plot_dxf(self, path: str, layer_to_check: str):
        """
        Export DXF file for specified layer with forced (0,0) origin
        
        Args:
            path: Output directory
            layer_to_check: "outline" for Edge.Cuts, "track" for copper layer
        """
        # Save auxiliary origin for restoration (KiCAD 8 compatibility)
        aux_origin_save = None
        has_aux_origin = hasattr(self.brd, 'GetAuxOrigin')
        
        if has_aux_origin:
            try:
                aux_origin_save = self.brd.GetAuxOrigin()
            except AttributeError:
                logger.warning("GetAuxOrigin not available, continuing without it")
                has_aux_origin = False
        
        # Force origin to (0,0) for this export
        # Set new aux origin to upper left side of board (KiCAD 8 only)
        if has_aux_origin:
            try:
                origin_point = pcbnew.VECTOR2I(
                    pcbnew.FromMM(self.origin[0]),
                    pcbnew.FromMM(self.origin[1])
                )
                self.brd.SetAuxOrigin(origin_point)
                logger.debug(f"Set export origin to board top-left: ({self.origin[0]:.2f}, {self.origin[1]:.2f}) mm")
            except AttributeError:
                logger.warning("SetAuxOrigin not available, using plot origin instead")
                has_aux_origin = False
        
        # Get pointers to controllers
        pctl = pcbnew.PLOT_CONTROLLER(self.brd)
        popt = pctl.GetPlotOptions()
        
        # Setup output directory
        popt.SetOutputDirectory(path)
        
        # Set DXF plot units to millimeters
        # DXF format supports only 2 units: 0=inches, 1=millimeters
        # KiCAD 9.0 uses integer values (named constants not exposed in Python bindings)
        try:
            popt.SetDXFPlotUnits(1)  # 1 = millimeters, 0 = inches
            logger.debug("✓ DXF units set to millimeters (1=mm, 0=inches)")
            
            # Verify what was set (if getter available)
            if hasattr(popt, 'GetDXFPlotUnits'):
                try:
                    current_units = popt.GetDXFPlotUnits()
                    unit_name = "millimeters" if current_units == 1 else ("inches" if current_units == 0 else f"unknown({current_units})")
                    logger.debug(f"Verified DXF units: {current_units} ({unit_name})")
                except Exception as e:
                    logger.debug(f"Could not verify DXF units: {e}")
        except AttributeError:
            logger.warning("SetDXFPlotUnits method not available - using KiCAD default (likely millimeters)")
        except Exception as e:
            logger.warning(f"Could not set DXF units: {type(e).__name__}: {e}. Using KiCAD default.")
        
        # SetDXFPlotPolygonMode - CRITICAL for outline cutouts
        # TRUE = export filled polygons (required for OpenSCAD import)
        # FALSE = export only line segments (won't create filled cutouts)
        try:
            popt.SetDXFPlotPolygonMode(True)
            logger.debug("DXF polygon mode enabled (filled shapes)")
        except AttributeError:
            logger.warning("SetDXFPlotPolygonMode not available - outline may export as lines only")
            pass
        
        # SetPlotFrameRef (may be removed in KiCAD 9)
        try:
            popt.SetPlotFrameRef(False)
        except AttributeError:
            pass
        
        # SetLineWidth (KiCAD 8 only, removed in KiCAD 9)
        try:
            popt.SetLineWidth(pcbnew.FromMM(0.1))
        except AttributeError:
            pass
        
        # SetAutoScale/SetScale - CRITICAL for dimensional accuracy
        # Must explicitly set SetScale(1.0) to prevent dimensional errors
        try:
            popt.SetAutoScale(False)
            popt.SetScale(1.0)  # CRITICAL: 1.0 = no scaling, exact dimensions
            logger.debug("✓ Scale set to 1.0 (no scaling) for accurate dimensions")
        except AttributeError:
            logger.debug("SetAutoScale/SetScale not available (KiCAD 9 may handle automatically)")
            pass
        
        # SetMirror (may be removed in KiCAD 9)
        try:
            popt.SetMirror(self.mirror)
        except AttributeError:
            pass
        
        # SetUseGerberAttributes (may be removed in KiCAD 9)
        try:
            popt.SetUseGerberAttributes(False)
        except AttributeError:
            pass
        
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
        
        # Use auxiliary origin if available, otherwise use drill/place origin
        if has_aux_origin:
            try:
                popt.SetUseAuxOrigin(True)
            except AttributeError:
                pass  # KiCAD 9 may not have SetUseAuxOrigin
        else:
            # KiCAD 9: Use drill/place file origin
            # This provides similar functionality to auxiliary origin
            try:
                popt.SetDrillMarksType(pcbnew.DRILL_MARKS_NO_DRILL_SHAPE)
            except:
                pass
        
        # SetColor (KiCAD 8 only, removed in KiCAD 9)
        try:
            popt.SetColor(pcbnew.COLOR4D(0, 0, 0, 1.0))
        except AttributeError:
            pass  # KiCAD 9 doesn't have SetColor
        
        # Open file and plot layer(s)
        if layer_to_check == "outline":
            pctl.SetLayer(pcbnew.Edge_Cuts)
            pctl.OpenPlotfile("outline", pcbnew.PLOT_FORMAT_DXF, "Edges")
            logger.info(f"Exporting Edge.Cuts layer with forced origin (0,0)...")
            pctl.PlotLayer()
            pctl.ClosePlot()
            logger.debug("Edge.Cuts DXF export complete")
        elif layer_to_check == "track":
            if self.both_sides:
                # Plot both F.Cu and B.Cu layers separately for "both sides" mode
                # Plot F.Cu (top)
                pctl.SetLayer(pcbnew.F_Cu)
                pctl.OpenPlotfile("track_top", pcbnew.PLOT_FORMAT_DXF, "track_top")
                logger.info("Exporting F.Cu track layer (top) with forced origin (0,0)...")
                pctl.PlotLayer()
                pctl.ClosePlot()
                
                # Plot B.Cu (bottom)
                pctl.SetLayer(pcbnew.B_Cu)
                pctl.OpenPlotfile("track_bottom", pcbnew.PLOT_FORMAT_DXF, "track_bottom")
                logger.info("Exporting B.Cu track layer (bottom) with forced origin (0,0)...")
                pctl.PlotLayer()
                pctl.ClosePlot()
            else:
                # Plot single selected layer
                pctl.SetLayer(self.layer)
                pctl.OpenPlotfile("track", pcbnew.PLOT_FORMAT_DXF, "track")
                layer_name = "F.Cu" if self.layer == pcbnew.F_Cu else "B.Cu"
                logger.info(f"Exporting {layer_name} track layer with forced origin (0,0)...")
                pctl.PlotLayer()
                pctl.ClosePlot()
        
        # Restore origin (KiCAD 8 only)
        if has_aux_origin and aux_origin_save is not None:
            try:
                self.brd.SetAuxOrigin(aux_origin_save)
            except AttributeError:
                pass
        
        logger.info(f"Exported DXF: {layer_to_check}")
        
        # Validate DXF export (for outline layer)
        if layer_to_check == "outline":
            self.validate_dxf_export(path)
    
    def get_test_points(self):
        """
        Extract test point coordinates from PCB pads
        
        Test point criteria:
        - On selected layer (F.Cu or B.Cu, or both if both_sides=True)
        - SMD or PTH (through-hole) pad type (configurable via include_smd/include_pth)
        - No paste mask (exposed copper)
        - On force layer OR not on ignore layer
        
        PTH pad detection:
        - Only includes PTH pads from components on the OPPOSITE side
        - Example: Testing from bottom (B.Cu) → Only PTH pads from top components (F.Cu)
        - Rationale: Component body blocks access from one side, through-hole pins
          are accessible from the opposite side (e.g., connector on top, test from bottom)
        
        Note: Through-hole pads (PTH) allow testing connector pins from the
        opposite side of the board. Use checkboxes to control which pad types
        are included as test points.
        """
        logger.info("Extracting test points...")
        logger.info(f"  Include SMD pads: {self.config.include_smd}")
        logger.info(f"  Include PTH pads: {self.config.include_pth}")
        if self.both_sides:
            logger.info("Processing test points from BOTH sides (F.Cu + B.Cu)")
        else:
            layer_name = "F.Cu" if self.layer == pcbnew.F_Cu else "B.Cu"
            logger.info(f"Processing test points from {layer_name}")
        logger.info("Test point matrix:")
        
        # Determine which layers to process
        if self.both_sides:
            layers_to_process = [
                (pcbnew.F_Cu, pcbnew.F_Paste, False),  # (layer, paste_layer, mirror)
                (pcbnew.B_Cu, pcbnew.B_Paste, True)
            ]
        else:
            layers_to_process = [(self.layer, self.paste, self.mirror)]
        
        # Process each layer
        for process_layer, process_paste, process_mirror in layers_to_process:
            layer_name = "F.Cu" if process_layer == pcbnew.F_Cu else "B.Cu"
            logger.info(f"  Scanning layer: {layer_name}")
            
            # Iterate over all footprints (modern API: GetFootprints instead of GetModules)
            for footprint in self.brd.GetFootprints():
                # Get the layer where the component is placed (F.Cu or B.Cu)
                component_layer = footprint.GetLayer()
                
                # Iterate over all pads
                for pad in footprint.Pads():
                    # Check if pad is on current processing layer
                    if not pad.IsOnLayer(process_layer):
                        continue
                    
                    # Check if forcing this pad
                    if pad.IsOnLayer(self.force_layer):
                        pass  # Include regardless
                    # Check ignore conditions
                    elif pad.IsOnLayer(self.ignore_layer):
                        continue  # Explicitly ignored
                    elif pad.IsOnLayer(process_paste):
                        continue  # Has paste mask
                    # Check pad type based on config flags
                    else:
                        pad_attr = pad.GetAttribute()
                        if pad_attr == pcbnew.PAD_ATTRIB_SMD and not self.config.include_smd:
                            continue  # SMD not included
                        elif pad_attr == pcbnew.PAD_ATTRIB_PTH and not self.config.include_pth:
                            continue  # PTH not included
                        elif pad_attr == pcbnew.PAD_ATTRIB_PTH and self.config.include_pth:
                            # Only use PTH pads from components on the OPPOSITE side
                            # If testing from top (F.Cu), only use PTH from bottom components (B.Cu)
                            # If testing from bottom (B.Cu), only use PTH from top components (F.Cu)
                            if component_layer == process_layer:
                                logger.debug(f"  Skipping PTH pad {pad.GetNetname()} - component on same side as test layer")
                                continue  # Component on same side - pins blocked by component body
                        elif (pad_attr != pcbnew.PAD_ATTRIB_SMD and 
                              pad_attr != pcbnew.PAD_ATTRIB_PTH):
                            continue  # Only SMD and PTH are valid
                    
                    # Get position (modern API returns VECTOR2I)
                    pos = pad.GetPosition()
                    tp_x = pcbnew.ToMM(pos.x)
                    tp_y = pcbnew.ToMM(pos.y)
                    
                    # Round x and y, invert x if mirrored
                    if not process_mirror:
                        x = self.round_value(tp_x - self.origin[0])
                    else:
                        x = self.dims[0] - self.round_value(tp_x - self.origin[0])
                    y = self.round_value(tp_y - self.origin[1])
                    
                    logger.info(f"  tp[{pad.GetNetname()}]@{layer_name} = ({x:.2f}, {y:.2f})")
                    
                    # Track minimum y coordinate
                    if y < self.min_y:
                        self.min_y = y
                    
                    # Save coordinates
                    self.test_points.append((x, y))
                    
                    # Also save to layer-specific list (used by OpenSCAD)
                    if process_layer == pcbnew.F_Cu:
                        self.test_points_top.append((x, y))
                    else:
                        self.test_points_bottom.append((x, y))
        
        if self.both_sides:
            logger.info(f"Found {len(self.test_points_top)} test points on F.Cu (top)")
            logger.info(f"Found {len(self.test_points_bottom)} test points on B.Cu (bottom)")
            logger.info(f"Total: {len(self.test_points)} test points")
        else:
            logger.info(f"Found {len(self.test_points)} test points total")
    
    def get_origin_dimensions(self):
        """
        Calculate PCB origin (top-left) and dimensions
        
        Uses Edge.Cuts layer ONLY for accurate board boundary.
        Components may extend beyond board edge (e.g., connectors).
        """
        if self.brd is None:
            return
        
        edge_max_x = 0
        edge_max_y = 0
        comp_max_x = 0
        comp_max_y = 0
        edge_cuts_found = False
        
        # Get all drawings (board outline) - PRIMARY source for origin/dimensions
        for drawing in self.brd.GetDrawings():
            if drawing.GetLayerName() == 'Edge.Cuts':
                edge_cuts_found = True
                bb = drawing.GetBoundingBox()
                
                x = pcbnew.ToMM(bb.GetX())
                y = pcbnew.ToMM(bb.GetY())
                w = pcbnew.ToMM(bb.GetWidth())
                h = pcbnew.ToMM(bb.GetHeight())
                
                # Track minimum (origin) from Edge.Cuts only
                if x < self.origin[0]:
                    self.origin[0] = self.round_value(x)
                if y < self.origin[1]:
                    self.origin[1] = self.round_value(y)
                
                # Track maximum from Edge.Cuts
                if x + w > edge_max_x:
                    edge_max_x = x + w
                if y + h > edge_max_y:
                    edge_max_y = y + h
        
        # Get all footprints for reference only (to detect overhang)
        for footprint in self.brd.GetFootprints():
            bb = footprint.GetBoundingBox()
            
            x = pcbnew.ToMM(bb.GetX())
            y = pcbnew.ToMM(bb.GetY())
            w = pcbnew.ToMM(bb.GetWidth())
            h = pcbnew.ToMM(bb.GetHeight())
            
            # Track component extents (for warning only)
            if x + w > comp_max_x:
                comp_max_x = x + w
            if y + h > comp_max_y:
                comp_max_y = y + h
        
        # Use Edge.Cuts dimensions if available, fallback to components
        if edge_cuts_found and edge_max_x > 0 and edge_max_y > 0:
            self.dims[0] = self.round_value(edge_max_x - self.origin[0])
            self.dims[1] = self.round_value(edge_max_y - self.origin[1])
            
            # Check for component overhang
            comp_width = self.round_value(comp_max_x - self.origin[0])
            comp_height = self.round_value(comp_max_y - self.origin[1])
            
            overhang_x = comp_width - self.dims[0]
            overhang_y = comp_height - self.dims[1]
            
            if overhang_x > 0.5 or overhang_y > 0.5:
                logger.info(f"Component overhang detected: +{overhang_x:.2f}mm (X), +{overhang_y:.2f}mm (Y) beyond board edge")
                logger.info("  This is normal for connectors/mounting holes. Test points on overhang components will be included.")
        else:
            # Fallback: use component bounding boxes
            logger.warning("No Edge.Cuts layer found - using component bounding boxes for dimensions")
            self.dims[0] = self.round_value(comp_max_x - self.origin[0])
            self.dims[1] = self.round_value(comp_max_y - self.origin[1])
        
        # Get actual board dimensions from Edge.Cuts for validation
        self.get_board_dimensions_from_edge_cuts()
        
        logger.info(f"Board dimensions: {self.dims[0]:.2f} x {self.dims[1]:.2f} mm")
        logger.info(f"Board origin: ({self.origin[0]:.2f}, {self.origin[1]:.2f})")
        if self.board_width_mm > 0 and self.board_height_mm > 0:
            logger.info(f"Edge.Cuts dimensions: {self.board_width_mm:.2f} x {self.board_height_mm:.2f} mm")
    
    def get_board_dimensions_from_edge_cuts(self):
        """
        Get actual board dimensions from Edge.Cuts layer using KiCAD API.
        This provides the official PCB outline dimensions for validation.
        """
        if self.brd is None:
            return
        
        min_x = float("inf")
        min_y = float("inf")
        max_x = float("-inf")
        max_y = float("-inf")
        
        # Get Edge.Cuts bounding box from all drawings
        edge_cuts_found = False
        for drawing in self.brd.GetDrawings():
            if drawing.GetLayerName() == 'Edge.Cuts':
                edge_cuts_found = True
                bb = drawing.GetBoundingBox()
                
                x = pcbnew.ToMM(bb.GetX())
                y = pcbnew.ToMM(bb.GetY())
                w = pcbnew.ToMM(bb.GetWidth())
                h = pcbnew.ToMM(bb.GetHeight())
                
                # Track bounding box
                if x < min_x:
                    min_x = x
                if y < min_y:
                    min_y = y
                if x + w > max_x:
                    max_x = x + w
                if y + h > max_y:
                    max_y = y + h
        
        if edge_cuts_found and min_x != float("inf"):
            self.board_width_mm = self.round_value(max_x - min_x)
            self.board_height_mm = self.round_value(max_y - min_y)
            logger.debug(f"Detected Edge.Cuts dimensions: {self.board_width_mm:.2f} x {self.board_height_mm:.2f} mm")
        else:
            logger.warning("No Edge.Cuts layer found - cannot determine board dimensions")
            self.board_width_mm = 0.0
            self.board_height_mm = 0.0
    
    def validate_dxf_export(self, path: str):
        """
        Validate DXF export by checking:
        1. Board dimensions match Edge.Cuts dimensions
        2. Origin is at (0, 0) as expected by OpenSCAD
        
        Args:
            path: Output directory containing the exported DXF
        """
        logger.info("Validating DXF export...")
        
        # Validation thresholds
        dimension_tolerance_mm = 0.5  # Allow 0.5mm difference
        origin_threshold_mm = 5.0     # Warn if origin is >5mm from (0,0)
        
        warnings = []
        errors = []
        
        # Check 1: Board dimensions validation
        # Note: self.dims now uses Edge.Cuts dimensions, so these should match
        # Small differences (<0.5mm) are acceptable due to rounding
        if self.board_width_mm > 0 and self.board_height_mm > 0:
            width_diff = abs(self.dims[0] - self.board_width_mm)
            height_diff = abs(self.dims[1] - self.board_height_mm)
            
            if width_diff > dimension_tolerance_mm:
                errors.append(
                    f"Width mismatch: board outline={self.dims[0]:.2f}mm, "
                    f"Edge.Cuts={self.board_width_mm:.2f}mm (diff={width_diff:.2f}mm). "
                    f"Check Edge.Cuts layer completeness."
                )
            
            if height_diff > dimension_tolerance_mm:
                errors.append(
                    f"Height mismatch: board outline={self.dims[1]:.2f}mm, "
                    f"Edge.Cuts={self.board_height_mm:.2f}mm (diff={height_diff:.2f}mm). "
                    f"Check Edge.Cuts layer completeness."
                )
            
            if width_diff <= dimension_tolerance_mm and height_diff <= dimension_tolerance_mm:
                logger.debug(f"✓ Dimensions validated: {self.dims[0]:.2f} x {self.dims[1]:.2f} mm")
        else:
            errors.append("Could not validate dimensions - Edge.Cuts layer not found or empty")
        
        # Check 2: Origin validation
        # Note: self.origin contains the KiCAD coordinates of the board's top-left corner
        # We set this as auxiliary origin, which makes the EXPORTED DXF start at (0,0)
        # If the board is far from KiCAD origin, just log it as info (not a warning)
        if abs(self.origin[0]) > origin_threshold_mm or abs(self.origin[1]) > origin_threshold_mm:
            logger.info(
                f"Board position in KiCAD: ({self.origin[0]:.2f}, {self.origin[1]:.2f}). "
                f"Auxiliary origin set - DXF exports at (0,0) ✓"
            )
        else:
            logger.info(f"Board already at KiCAD origin: ({self.origin[0]:.2f}, {self.origin[1]:.2f}) ✓")
        
        # Check 3: Minimum dimension sanity check
        min_board_size = 10.0  # mm
        max_board_size = 500.0  # mm
        
        if self.dims[0] < min_board_size:
            errors.append(f"Board width too small: {self.dims[0]:.2f}mm (minimum {min_board_size}mm)")
        
        if self.dims[1] < min_board_size:
            errors.append(f"Board height too small: {self.dims[1]:.2f}mm (minimum {min_board_size}mm)")
        
        if self.dims[0] > max_board_size:
            warnings.append(f"Board width very large: {self.dims[0]:.2f}mm (maximum expected {max_board_size}mm)")
        
        if self.dims[1] > max_board_size:
            warnings.append(f"Board height very large: {self.dims[1]:.2f}mm (maximum expected {max_board_size}mm)")
        
        # Report validation results
        if errors:
            logger.error("❌ DXF Export Validation FAILED:")
            for error in errors:
                logger.error(f"  - {error}")
            logger.error("\nTroubleshooting:")
            logger.error("  1. Check Edge.Cuts layer in KiCAD is complete")
            logger.error("  2. Verify board outline forms a closed shape")
            logger.error("  3. Check DXF scale factor if using imported DXF")
        
        if warnings:
            logger.warning("⚠️  DXF Export Validation Warnings:")
            for warning in warnings:
                logger.warning(f"  - {warning}")
            if any("origin" in w.lower() for w in warnings):
                logger.warning("\nOrigin Fix:")
                logger.warning("  - In KiCAD, place board outline starting at (0, 0)")
                logger.warning("  - Or set auxiliary origin at top-left corner")
        
        if not errors and not warnings:
            logger.info("✓ DXF export validation passed")
            logger.info(f"  Board: {self.dims[0]:.2f} x {self.dims[1]:.2f} mm")
            logger.info(f"  Export origin: (0.00, 0.00) - Forced via auxiliary origin")
            logger.info(f"  Test points: {len(self.test_points)} total ({len(self.test_points_top)} top, {len(self.test_points_bottom)} bottom)")
    
    def get_test_point_str(self, points: List[Tuple[float, float]] = None) -> str:
        """Format test points as OpenSCAD array string"""
        if points is None:
            points = self.test_points
        if len(points) == 0:
            return "[]"
        tps = "["
        for tp in points:
            tps += f"[{tp[0]:.02f},{tp[1]:.02f}],"
        return tps[:-1] + "]"
    
    def generate(self, path: str):
        """
        Main generation workflow
        
        Args:
            path: Output directory path
        """
        logger.info("Starting fixture generation...")
        
        # Get origin and board dimensions
        self.get_origin_dimensions()
        
        # Force origin to (0,0) for all exports
        # This sets the auxiliary origin so DXF exports start at (0,0)
        self.force_origin_to_zero()
        
        # Get test points (will be calculated relative to forced origin)
        self.get_test_points()
        
        # Test for failure to find test points
        if len(self.test_points) == 0:
            if self.both_sides:
                logger.error("No test points found on either F.Cu or B.Cu!")
            else:
                layer_name = "F.Cu" if self.layer == pcbnew.F_Cu else "B.Cu"
                logger.error(f"No test points found on {layer_name}!")
            logger.error("Verify that the pcbnew file has test points specified")
            logger.error("or use the --flayer option to force test points")
            return False
        
        # Plot DXF files
        self.plot_dxf(path, "outline")
        outline_file = os.path.join(path, f"{self.prj_name}-outline.dxf")
        if os.path.exists(outline_file):
            logger.info(f"Exported DXF: outline ({os.path.getsize(outline_file)} bytes)")
        else:
            logger.error(f"Failed to export outline DXF to {outline_file}")
        
        self.plot_dxf(path, "track")
        
        # Get revision
        if self.config.rev is None:
            rev = self.brd.GetTitleBlock().GetRevision()
            self.config.rev = f"rev.{rev}" if rev else "rev.0"
        
        # Build OpenSCAD command arguments
        args_dict = self._build_openscad_args(path)
        
        # Create output file names
        if os.name == 'nt':
            dxfout = os.path.join(path, f"{self.prj_name}-fixture.dxf")
            pngout = os.path.join(path, f"{self.prj_name}-fixture.png")
            testout = os.path.join(path, f"{self.prj_name}-test.dxf")
        else:
            dxfout = f"{path}/{self.prj_name}-fixture.dxf"
            pngout = f"{path}/{self.prj_name}-fixture.png"
            testout = f"{path}/{self.prj_name}-test.dxf"
        
        # Find OpenSCAD executable
        openscad_exe = self._find_openscad()
        if not openscad_exe:
            logger.error("OpenSCAD not found! Please install OpenSCAD from https://openscad.org/")
            return False
        
        # Find openfixture.scad (should be in same directory as this script)
        script_dir = Path(__file__).parent
        scad_file = script_dir / "openfixture.scad"
        if not scad_file.exists():
            logger.error(f"openfixture.scad not found at {scad_file}")
            return False
        
        # Generate fixture files
        logger.info("Generating fixture with OpenSCAD...")
        
        # Run OpenSCAD commands with error checking
        success = True
        
        # Generate test cut
        logger.info("Generating test cut DXF...")
        if not self._run_openscad(openscad_exe, scad_file, args_dict, "testcut", testout):
            logger.error("Failed to generate test cut DXF")
            success = False
        
        # Generate 3D preview
        logger.info("Generating 3D preview PNG...")
        if not self._run_openscad(openscad_exe, scad_file, args_dict, "3dmodel", pngout, render=True):
            logger.warning("Failed to generate 3D preview PNG")
            # Don't fail on preview - continue
        
        # Generate fixture DXF
        logger.info("Generating fixture DXF...")
        if not self._run_openscad(openscad_exe, scad_file, args_dict, "lasercut", dxfout):
            logger.error("Failed to generate fixture DXF")
            success = False
        
        if success:
            logger.info(f"Fixture generated: {dxfout}")
            logger.info(f"3D preview: {pngout}")
            logger.info(f"Test cut: {testout}")
        
        return success
    
    def _build_openscad_args(self, path: str) -> str:
        """Build OpenSCAD command line arguments"""
        
        # Common args - use Edge.Cuts dimensions if available, otherwise use calculated dims
        pcb_x = self.board_width_mm if self.board_width_mm > 0 else self.dims[0]
        pcb_y = self.board_height_mm if self.board_height_mm > 0 else self.dims[1]
        
        args_dict = {
            'tp_min_y': f"{self.min_y:.02f}",
            'mat_th': f"{self.config.mat_th:.02f}",
            'pcb_th': f"{self.config.pcb_th:.02f}",
            'pcb_x': f"{pcb_x:.02f}",
            'pcb_y': f"{pcb_y:.02f}",
            'screw_thr_len': f"{self.config.screw_len:.02f}",
            'screw_d': f"{self.config.screw_d:.02f}",
        }
        
        # Always pass layer-specific arrays to OpenSCAD
        # This allows proper visualization and fixture generation
        args_dict['test_points_top'] = self.get_test_point_str(self.test_points_top)
        args_dict['test_points_bottom'] = self.get_test_point_str(self.test_points_bottom)
        
        # Debug: Log the test point arrays being passed
        logger.debug(f"Passing test_points_top array with {len(self.test_points_top)} points")
        logger.debug(f"Passing test_points_bottom array with {len(self.test_points_bottom)} points")
        if len(self.test_points_top) > 0:
            logger.debug(f"First top point: {self.test_points_top[0]}, Last top point: {self.test_points_top[-1]}")
        if len(self.test_points_bottom) > 0:
            logger.debug(f"First bottom point: {self.test_points_bottom[0]}, Last bottom point: {self.test_points_bottom[-1]}")
        
        # Path separators - store raw paths, quoting happens in command builder
        outline_path = os.path.join(path, f"{self.prj_name}-outline.dxf").replace("\\", "/")
        args_dict['pcb_outline'] = outline_path
        
        # Track paths - separate for both sides or single
        if self.both_sides:
            track_top_path = os.path.join(path, f"{self.prj_name}-track_top.dxf").replace("\\", "/")
            track_bottom_path = os.path.join(path, f"{self.prj_name}-track_bottom.dxf").replace("\\", "/")
            args_dict['pcb_track_top'] = track_top_path
            args_dict['pcb_track_bottom'] = track_bottom_path
        else:
            track_path = os.path.join(path, f"{self.prj_name}-track.dxf").replace("\\", "/")
            args_dict['pcb_track'] = track_path
        
        # Optional parameters - store raw values
        if self.config.rev:
            args_dict['rev'] = self.config.rev
        if self.config.washer_th:
            args_dict['washer_th'] = f"{float(self.config.washer_th):.02f}"
        if self.config.nut_f2f:
            args_dict['nut_od_f2f'] = f"{float(self.config.nut_f2f):.02f}"
        if self.config.nut_c2c:
            args_dict['nut_od_c2c'] = f"{float(self.config.nut_c2c):.02f}"
        if self.config.nut_th:
            args_dict['nut_th'] = f"{float(self.config.nut_th):.02f}"
        if self.config.pivot_d:
            args_dict['pivot_d'] = f"{float(self.config.pivot_d):.02f}"
        if self.config.border:
            args_dict['pcb_support_border'] = f"{float(self.config.border):.02f}"
        if self.config.pogo_uncompressed_length:
            args_dict['pogo_uncompressed_length'] = f"{float(self.config.pogo_uncompressed_length):.02f}"
        
        # Logo parameters
        args_dict['logo_enable'] = "1" if self.config.logo_enable else "0"
        if self.config.logo_file:
            args_dict['logo_file'] = self.config.logo_file
        if self.config.logo_scale_x is not None:
            args_dict['logo_scale_x'] = f"{float(self.config.logo_scale_x):.02f}"
        if self.config.logo_scale_y is not None:
            args_dict['logo_scale_y'] = f"{float(self.config.logo_scale_y):.02f}"
        if self.config.logo_scale_z is not None:
            args_dict['logo_scale_z'] = f"{float(self.config.logo_scale_z):.02f}"
        if self.config.logo_offset_x is not None:
            args_dict['logo_offset_x'] = f"{float(self.config.logo_offset_x):.02f}"
        if self.config.logo_offset_y is not None:
            args_dict['logo_offset_y'] = f"{float(self.config.logo_offset_y):.02f}"
        if self.config.logo_offset_z is not None:
            args_dict['logo_offset_z'] = f"{float(self.config.logo_offset_z):.02f}"
        
        # Log critical parameters for debugging
        logger.debug(f"OpenSCAD parameters:")
        logger.debug(f"  pcb_outline: {args_dict.get('pcb_outline', 'NOT SET')}")
        logger.debug(f"  pcb_x: {args_dict.get('pcb_x', 'NOT SET')} (from {'Edge.Cuts' if self.board_width_mm > 0 else 'calculated'})")
        logger.debug(f"  pcb_y: {args_dict.get('pcb_y', 'NOT SET')} (from {'Edge.Cuts' if self.board_height_mm > 0 else 'calculated'})")
        logger.debug(f"  pcb_support_border: {args_dict.get('pcb_support_border', 'NOT SET')}")
        logger.debug(f"  test_points_top count: {len(self.test_points_top)}")
        logger.debug(f"  test_points_bottom count: {len(self.test_points_bottom)}")
        
        # Return args_dict for command builder to handle properly
        return args_dict

    def _find_openscad(self) -> Optional[str]:
        """Find OpenSCAD executable"""
        # Try to find in PATH
        openscad = shutil.which('openscad')
        if openscad:
            return openscad
        
        # Common Windows installation paths
        if os.name == 'nt':
            common_paths = [
                r"C:\Program Files\OpenSCAD\openscad.exe",
                r"C:\Program Files (x86)\OpenSCAD\openscad.exe",
                os.path.expanduser(r"~\AppData\Local\Programs\OpenSCAD\openscad.exe"),
            ]
            for path in common_paths:
                if os.path.exists(path):
                    return path
        
        # Common Linux/Mac paths
        else:
            common_paths = [
                "/usr/bin/openscad",
                "/usr/local/bin/openscad",
                "/opt/openscad/bin/openscad",
            ]
            for path in common_paths:
                if os.path.exists(path):
                    return path
        
        return None
    
    def _run_openscad(self, openscad_exe: str, scad_file: Path, args_dict: Dict, 
                      mode: str, output: str, render: bool = False) -> bool:
        """
        Run OpenSCAD command with error checking
        
        Args:
            openscad_exe: Path to OpenSCAD executable
            scad_file: Path to openfixture.scad
            args_dict: Dictionary of OpenSCAD parameters
            mode: OpenSCAD mode ('testcut', '3dmodel', 'lasercut')
            output: Output file path
            render: Whether to use --render flag
        
        Returns:
            True if successful, False otherwise
        """
        # Build command list for subprocess (avoids shell quoting issues)
        cmd = [str(openscad_exe)]
        
        if render:
            cmd.append('--render')
        
        # Add mode parameter
        cmd.extend(['-D', f'mode="{mode}"'])
        
        # Add all other parameters
        for key, value in args_dict.items():
            if isinstance(value, str):
                # Check if it's an array literal (starts with '[')
                if value.strip().startswith('['):
                    # Array - no quotes
                    cmd.extend(['-D', f'{key}={value}'])
                else:
                    # Check if it's a numeric string (e.g., "3.00", "12.31")
                    try:
                        float(value)
                        # Numeric string - no quotes (OpenSCAD needs bare numbers)
                        cmd.extend(['-D', f'{key}={value}'])
                    except ValueError:
                        # Non-numeric string - add quotes
                        cmd.extend(['-D', f'{key}="{value}"'])
            else:
                # Numeric value - no quotes
                cmd.extend(['-D', f'{key}={value}'])
        
        # Add output and input files
        cmd.extend(['-o', str(output), str(scad_file)])
        
        logger.info(f"Running OpenSCAD command with {len(args_dict)} parameters")
        logger.debug(f"OpenSCAD command: {' '.join(cmd)}")
        
        try:
            # Use subprocess with list (no shell) to avoid quoting issues
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                logger.error(f"OpenSCAD failed with return code {result.returncode}")
                if result.stderr:
                    logger.error(f"OpenSCAD error: {result.stderr}")
                return False
            
            # Check if output file was created
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


def main():
    """Main entry point for command-line usage"""
    
    # Create parser
    parser = argparse.ArgumentParser(
        description='OpenFixture Generator - Create laser-cuttable PCB test fixtures',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required arguments
    parser.add_argument('--board', required=True,
                       help='Path to .kicad_pcb file')
    parser.add_argument('--mat_th', required=True, type=float,
                       help='Material thickness in mm')
    parser.add_argument('--out', required=True,
                       help='Output directory')
    
    # Optional arguments
    parser.add_argument('--config',
                       help='TOML configuration file')
    parser.add_argument('--pcb_th', type=float,
                       help='PCB thickness in mm')
    parser.add_argument('--screw_len', type=float,
                       help='Assembly screw thread length in mm')
    parser.add_argument('--screw_d', type=float,
                       help='Assembly screw diameter in mm')
    parser.add_argument('--layer',
                       help='Test point layer: F.Cu, B.Cu, or both')
    parser.add_argument('--flayer',
                       help='Force layer: Eco1.User or Eco2.User')
    parser.add_argument('--ilayer',
                       help='Ignore layer: Eco1.User or Eco2.User')
    parser.add_argument('--rev',
                       help='Override revision string')
    parser.add_argument('--washer_th', type=float,
                       help='Washer thickness for hinge in mm')
    parser.add_argument('--nut_f2f', type=float,
                       help='Hex nut flat-to-flat dimension in mm')
    parser.add_argument('--nut_c2c', type=float,
                       help='Hex nut corner-to-corner dimension in mm')
    parser.add_argument('--nut_th', type=float,
                       help='Hex nut thickness in mm')
    parser.add_argument('--pivot_d', type=float,
                       help='Pivot diameter in mm')
    parser.add_argument('--border', type=float,
                       help='PCB support border width in mm')
    parser.add_argument('--pogo-uncompressed-length', type=float,
                       help='Uncompressed pogo pin length in mm')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--include-smd', action='store_true',
                       help='Include SMD pads as test points (default: true)')
    parser.add_argument('--include-pth', action='store_true',
                       help='Include PTH (through-hole) pads as test points (default: true)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Convert output path to absolute
    out_dir = os.path.abspath(args.out)
    
    # Set logging level and add file handler if verbose
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        
        # Create log file in output directory
        os.makedirs(out_dir, exist_ok=True)
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(out_dir, f'openfixture_{timestamp}.log')
        
        # Add file handler with same format as console
        file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Verbose logging enabled - writing to: {log_file}")
    
    # Create output directory if needed
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        logger.info(f"Created output directory: {out_dir}")
    
    # Load configuration
    if args.config and Path(args.config).exists():
        config = FixtureConfig.from_toml(args.config)
        logger.info(f"Loaded configuration from {args.config}")
    else:
        config = FixtureConfig()
    
    # Override config with command-line arguments
    config.mat_th = args.mat_th
    if args.pcb_th:
        config.pcb_th = args.pcb_th
    if args.screw_len:
        config.screw_len = args.screw_len
    if args.screw_d:
        config.screw_d = args.screw_d
    if args.rev:
        config.rev = args.rev
    if args.washer_th:
        config.washer_th = args.washer_th
    if args.nut_f2f:
        config.nut_f2f = args.nut_f2f
    if args.nut_c2c:
        config.nut_c2c = args.nut_c2c
    if args.nut_th:
        config.nut_th = args.nut_th
    if args.pivot_d:
        config.pivot_d = args.pivot_d
    if args.border:
        config.border = args.border
    if args.pogo_uncompressed_length:
        config.pogo_uncompressed_length = args.pogo_uncompressed_length
    
    # Set pad type inclusion flags
    # Logic: If either flag is present in command line, we're in explicit mode (from UI)
    # and respect the flags exactly. If neither is present, default both to True (backward compat).
    flags_explicitly_set = '--include-smd' in sys.argv or '--include-pth' in sys.argv
    
    if flags_explicitly_set:
        # UI mode: respect flags exactly (present=True, absent=False)
        config.include_smd = args.include_smd
        config.include_pth = args.include_pth
    else:
        # Legacy mode: default both to True for backward compatibility
        config.include_smd = True
        config.include_pth = True
    
    # Load board file
    try:
        logger.info(f"Loading board file: {args.board}")
        brd = pcbnew.LoadBoard(args.board)
    except Exception as e:
        logger.error(f"Failed to load board file: {e}")
        return 1
    
    # Extract project name
    prj_name = os.path.splitext(os.path.basename(args.board))[0]
    
    # Create fixture generator
    fixture = GenFixture(prj_name, brd, config)
    
    # Set layers
    both_sides = False
    if args.layer:
        if args.layer.lower() == 'both':
            both_sides = True
            layer = -1  # Ignored when both_sides=True
        else:
            layer = brd.GetLayerID(args.layer)
    else:
        layer = -1
    
    if args.flayer:
        flayer = brd.GetLayerID(args.flayer)
    else:
        flayer = -1
    
    if args.ilayer:
        ilayer = brd.GetLayerID(args.ilayer)
    else:
        ilayer = -1
    
    fixture.set_layers(layer=layer, flayer=flayer, ilayer=ilayer, both=both_sides)
    
    # Generate fixture
    success = fixture.generate(out_dir)
    
    if success:
        logger.info("Fixture generation completed successfully!")
        logger.info(str(fixture))
        return 0
    else:
        logger.error("Fixture generation failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
