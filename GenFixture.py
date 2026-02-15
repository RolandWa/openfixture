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
                
            # Load parameters from TOML
            board_cfg = data.get('board', {})
            config.pcb_th = board_cfg.get('thickness_mm', DEFAULT_PCB_TH)
            
            material_cfg = data.get('material', {})
            config.mat_th = material_cfg.get('thickness_mm', 0.0)
            
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
            
            config.rev = data.get('revision')
            
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
        
        # Board data
        self.origin = [float("inf"), float("inf")]
        self.dims = [0.0, 0.0]
        self.min_y = float("inf")
        self.test_points: List[Tuple[float, float]] = []
        
    def __str__(self) -> str:
        return (f"Fixture: origin=({self.origin[0]:.02f},{self.origin[1]:.02f}) "
                f"dims=({self.dims[0]:.02f},{self.dims[1]:.02f}) "
                f"min_y={self.min_y:.02f}")
    
    def set_layers(self, layer: int = -1, ilayer: int = -1, flayer: int = -1):
        """
        Set layer configuration
        
        Args:
            layer: Test point layer (F.Cu or B.Cu)
            ilayer: Ignore layer (Eco1.User)
            flayer: Force layer (Eco2.User)
        """
        if layer != -1:
            self.layer = layer
        if ilayer != -1:
            self.ignore_layer = ilayer
        if flayer != -1:
            self.force_layer = flayer
        
        # Setup paste layer and mirror flag
        if self.layer == pcbnew.F_Cu:
            self.paste = pcbnew.F_Paste
            self.mirror = False
        else:
            self.paste = pcbnew.B_Paste
            self.mirror = True
    
    def round_value(self, x: float, base: float = 0.01) -> float:
        """Round value to specified precision"""
        return round(base * round(x / base), 2)
    
    def plot_dxf(self, path: str, layer_to_check: str):
        """
        Export DXF file for specified layer
        
        Args:
            path: Output directory
            layer_to_check: "outline" for Edge.Cuts, "track" for copper layer
        """
        # Save auxiliary origin (KiCAD 8 compatibility)
        # In KiCAD 9, GetAuxOrigin/SetAuxOrigin were removed
        aux_origin_save = None
        has_aux_origin = hasattr(self.brd, 'GetAuxOrigin')
        
        if has_aux_origin:
            try:
                aux_origin_save = self.brd.GetAuxOrigin()
            except AttributeError:
                logger.warning("GetAuxOrigin not available, continuing without it")
                has_aux_origin = False
        
        # Set new aux origin to upper left side of board (KiCAD 8 only)
        if has_aux_origin:
            try:
                origin_point = pcbnew.VECTOR2I(
                    pcbnew.FromMM(self.origin[0]),
                    pcbnew.FromMM(self.origin[1])
                )
                self.brd.SetAuxOrigin(origin_point)
            except AttributeError:
                logger.warning("SetAuxOrigin not available, using plot origin instead")
                has_aux_origin = False
        
        # Get pointers to controllers
        pctl = pcbnew.PLOT_CONTROLLER(self.brd)
        popt = pctl.GetPlotOptions()
        
        # Setup output directory
        popt.SetOutputDirectory(path)
        
        # Set plot options - handle KiCAD 8/9 API differences
        try:
            # KiCAD 9.0+ uses different enum names
            popt.SetDXFPlotUnits(pcbnew.DXF_PLOTTER_UNITS_MILLIMETERS)
        except AttributeError:
            try:
                # KiCAD 8.0 enum name
                popt.SetDXFPlotUnits(pcbnew.DXF_UNITS_MILLIMETERS)
            except AttributeError:
                logger.warning("Could not set DXF units, using default")
        
        # SetDXFPlotPolygonMode (may be removed in KiCAD 9)
        try:
            popt.SetDXFPlotPolygonMode(True)
        except AttributeError:
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
        
        # SetAutoScale/SetScale (may be removed in KiCAD 9)
        try:
            popt.SetAutoScale(False)
            popt.SetScale(1)
        except AttributeError:
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
        
        # Open file and plot layer
        if layer_to_check == "outline":
            pctl.SetLayer(pcbnew.Edge_Cuts)
            pctl.OpenPlotfile("outline", pcbnew.PLOT_FORMAT_DXF, "Edges")
        elif layer_to_check == "track":
            pctl.SetLayer(self.layer)
            pctl.OpenPlotfile("track", pcbnew.PLOT_FORMAT_DXF, "track")
        
        # Plot layer
        pctl.PlotLayer()
        
        # Close plot
        pctl.ClosePlot()
        
        # Restore origin (KiCAD 8 only)
        if has_aux_origin and aux_origin_save is not None:
            try:
                self.brd.SetAuxOrigin(aux_origin_save)
            except AttributeError:
                pass
        
        logger.info(f"Exported DXF: {layer_to_check}")
    
    def get_test_points(self):
        """
        Extract test point coordinates from PCB pads
        
        Test point criteria:
        - On selected layer (F.Cu or B.Cu)
        - SMD pad type
        - No paste mask (exposed copper)
        - On force layer OR not on ignore layer
        """
        logger.info("Extracting test points...")
        logger.info("Test point matrix:")
        
        # Iterate over all footprints (modern API: GetFootprints instead of GetModules)
        for footprint in self.brd.GetFootprints():
            # Iterate over all pads
            for pad in footprint.Pads():
                # Check if pad is on selected layer
                if not pad.IsOnLayer(self.layer):
                    continue
                
                # Check if forcing this pad
                if pad.IsOnLayer(self.force_layer):
                    pass  # Include regardless
                # Check ignore conditions
                elif (pad.IsOnLayer(self.ignore_layer) or
                      pad.IsOnLayer(self.paste) or
                      pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD):
                    continue
                
                # Get position (modern API returns VECTOR2I)
                pos = pad.GetPosition()
                tp_x = pcbnew.ToMM(pos.x)
                tp_y = pcbnew.ToMM(pos.y)
                
                # Round x and y, invert x if mirrored
                if not self.mirror:
                    x = self.round_value(tp_x - self.origin[0])
                else:
                    x = self.dims[0] - self.round_value(tp_x - self.origin[0])
                y = self.round_value(tp_y - self.origin[1])
                
                logger.info(f"  tp[{pad.GetNetname()}] = ({x:.2f}, {y:.2f})")
                
                # Track minimum y coordinate
                if y < self.min_y:
                    self.min_y = y
                
                # Save coordinates
                self.test_points.append((x, y))
        
        logger.info(f"Found {len(self.test_points)} test points")
    
    def get_origin_dimensions(self):
        """
        Calculate PCB origin (top-left) and dimensions
        
        Considers both Edge.Cuts outline and component bounding boxes
        """
        if self.brd is None:
            return
        
        max_x = 0
        max_y = 0
        
        # Get all drawings (board outline)
        for drawing in self.brd.GetDrawings():
            if drawing.GetLayerName() == 'Edge.Cuts':
                bb = drawing.GetBoundingBox()
                
                x = pcbnew.ToMM(bb.GetX())
                y = pcbnew.ToMM(bb.GetY())
                
                # Track minimum (origin)
                if x < self.origin[0]:
                    self.origin[0] = self.round_value(x)
                if y < self.origin[1]:
                    self.origin[1] = self.round_value(y)
                
                # Track maximum (dimensions)
                if x > max_x:
                    max_x = x
                if y > max_y:
                    max_y = y
        
        # Get all footprints for bounding boxes (modern API)
        for footprint in self.brd.GetFootprints():
            bb = footprint.GetBoundingBox()
            
            x = pcbnew.ToMM(bb.GetX())
            y = pcbnew.ToMM(bb.GetY())
            w = pcbnew.ToMM(bb.GetWidth())
            h = pcbnew.ToMM(bb.GetHeight())
            
            # Track minimum (origin) - use exact values
            if x < self.origin[0]:
                self.origin[0] = x
            if y < self.origin[1]:
                self.origin[1] = y
            
            # Track maximum (dimensions)
            if x + w > max_x:
                max_x = x + w
            if y + h > max_y:
                max_y = y + h
        
        # Calculate final dimensions
        self.dims[0] = self.round_value(max_x - self.origin[0])
        self.dims[1] = self.round_value(max_y - self.origin[1])
        
        logger.info(f"Board dimensions: {self.dims[0]:.2f} x {self.dims[1]:.2f} mm")
        logger.info(f"Board origin: ({self.origin[0]:.2f}, {self.origin[1]:.2f})")
    
    def get_test_point_str(self) -> str:
        """Format test points as OpenSCAD array string"""
        tps = "["
        for tp in self.test_points:
            tps += f"[{tp[0]:.02f},{tp[1]:.02f}],"
        return tps + "]"
    
    def generate(self, path: str):
        """
        Main generation workflow
        
        Args:
            path: Output directory path
        """
        logger.info("Starting fixture generation...")
        
        # Get origin and board dimensions
        self.get_origin_dimensions()
        
        # Get test points
        self.get_test_points()
        
        # Test for failure to find test points
        if len(self.test_points) == 0:
            logger.error("No test points found!")
            logger.error("Verify that the pcbnew file has test points specified")
            logger.error("or use the --flayer option to force test points")
            return False
        
        # Plot DXF files
        self.plot_dxf(path, "outline")
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
        
        # Common args
        args_dict = {
            'test_points': self.get_test_point_str(),
            'tp_min_y': f"{self.min_y:.02f}",
            'mat_th': f"{self.config.mat_th:.02f}",
            'pcb_th': f"{self.config.pcb_th:.02f}",
            'pcb_x': f"{self.dims[0]:.02f}",
            'pcb_y': f"{self.dims[1]:.02f}",
            'screw_thr_len': f"{self.config.screw_len:.02f}",
            'screw_d': f"{self.config.screw_d:.02f}",
        }
        
        # Path separators - store raw paths, quoting happens in command builder
        outline_path = os.path.join(path, f"{self.prj_name}-outline.dxf").replace("\\", "/")
        track_path = os.path.join(path, f"{self.prj_name}-track.dxf").replace("\\", "/")
        args_dict['pcb_outline'] = outline_path
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
            if isinstance(value, str) and ('/' in value or '\\' in value or ' ' in value):
                # Path-like string - add quotes
                cmd.extend(['-D', f'{key}="{value}"'])
            else:
                # Numeric or already formatted - no quotes
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
                       help='Test point layer: F.Cu or B.Cu')
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
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Convert output path to absolute
    out_dir = os.path.abspath(args.out)
    
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
    if args.layer:
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
    
    fixture.set_layers(layer=layer, flayer=flayer, ilayer=ilayer)
    
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
