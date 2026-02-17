#!/usr/bin/env python3
"""
OpenFixture KiCAD Plugin - Modernized Version
KiCAD 8.0+ / 9.0+ Compatible

Action Plugin for KiCAD PCB Editor that generates test fixtures
Updated with modern pcbnew API and improved error handling

Original Author:
    Elliot Buller - Tiny Labs Inc (2016)
    http://tinylabs.io/openfixture

Modernization & v2 Update:
    Community Contributors (2026)
    - Updated to KiCAD 8.0/9.0 API
    - Created modern multi-tab UI with wx.Notebook
    - Added TOML configuration auto-loading
    - Added material presets and progress dialogs
    - Improved error handling and user feedback

License: CC-BY-SA 4.0
"""

import pcbnew
import sys
import os
import wx
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorDialog(wx.Dialog):
    """
    Scrollable error dialog for displaying long error messages
    """
    
    def __init__(self, parent, title, message, details=None):
        wx.Dialog.__init__(
            self, 
            parent, 
            id=wx.ID_ANY,
            title=title,
            size=wx.Size(700, 500),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Error icon and message
        header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Add error icon (if available)
        icon = wx.ArtProvider.GetBitmap(wx.ART_ERROR, wx.ART_MESSAGE_BOX, (32, 32))
        if icon.IsOk():
            icon_bitmap = wx.StaticBitmap(self, wx.ID_ANY, icon)
            header_sizer.Add(icon_bitmap, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        
        # Main message
        message_text = wx.StaticText(self, wx.ID_ANY, message)
        message_font = message_text.GetFont()
        message_font.PointSize += 1
        message_font = message_font.Bold()
        message_text.SetFont(message_font)
        header_sizer.Add(message_text, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 10)
        
        sizer.Add(header_sizer, 0, wx.EXPAND)
        
        if details:
            # Details label
            details_label = wx.StaticText(self, wx.ID_ANY, "Error Details:")
            sizer.Add(details_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
            
            # Scrollable text control for details
            self.details_text = wx.TextCtrl(
                self, 
                wx.ID_ANY,
                value=details,
                style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP
            )
            self.details_text.SetFont(wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
            sizer.Add(self.details_text, 1, wx.ALL | wx.EXPAND, 10)
            
            # Copy button
            copy_btn = wx.Button(self, wx.ID_ANY, "Copy to Clipboard")
            copy_btn.Bind(wx.EVT_BUTTON, self._on_copy)
            sizer.Add(copy_btn, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
        
        # OK button
        ok_btn = wx.Button(self, wx.ID_OK, "OK")
        sizer.Add(ok_btn, 0, wx.ALL | wx.ALIGN_CENTER, 10)
        
        self.SetSizer(sizer)
        self.Centre(wx.BOTH)
    
    def _on_copy(self, event):
        """Copy error details to clipboard"""
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(wx.TextDataObject(self.details_text.GetValue()))
            wx.TheClipboard.Close()
            wx.MessageBox("Error details copied to clipboard", "Copied", wx.OK | wx.ICON_INFORMATION)


class OpenFixtureDialog(wx.Dialog):
    """
    Modern dialog for OpenFixture generation
    Replaces auto-generated OpenFixtureDlg with better UX
    """
    
    def __init__(self, parent, board_path: str):
        wx.Dialog.__init__(
            self, 
            parent, 
            id=wx.ID_ANY,
            title="OpenFixture Generator",
            pos=wx.DefaultPosition,
            size=wx.Size(500, 700),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        
        self.board_path = board_path
        self.board_name = Path(board_path).stem
        
        # Load configuration if available
        self.config_path = None
        self._find_config_file()
        
        self._create_ui()
        self._load_defaults()
        
        self.Centre(wx.BOTH)
    
    def _find_config_file(self):
        """Search for fixture_config.toml in project directory"""
        board_dir = Path(self.board_path).parent
        config_file = board_dir / "fixture_config.toml"
        
        if config_file.exists():
            self.config_path = str(config_file)
            logger.info(f"Found configuration file: {self.config_path}")
    
    def _create_ui(self):
        """Create dialog UI"""
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Header
        header = wx.StaticText(self, wx.ID_ANY, "Generate Test Fixture")
        header_font = header.GetFont()
        header_font.PointSize += 2
        header_font = header_font.Bold()
        header.SetFont(header_font)
        main_sizer.Add(header, 0, wx.ALL | wx.EXPAND, 10)
        
        # Board info
        board_info = wx.StaticText(self, wx.ID_ANY, f"Board: {self.board_name}")
        main_sizer.Add(board_info, 0, wx.ALL | wx.EXPAND, 10)
        
        if self.config_path:
            config_info = wx.StaticText(self, wx.ID_ANY, f"Config: {Path(self.config_path).name}")
            config_info.SetForegroundColour(wx.Colour(0, 128, 0))
            main_sizer.Add(config_info, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 10)
        
        # Notebook for organized parameters
        notebook = wx.Notebook(self, wx.ID_ANY)
        
        # Board Panel
        board_panel = self._create_board_panel(notebook)
        notebook.AddPage(board_panel, "Board")
        
        # Material Panel
        material_panel = self._create_material_panel(notebook)
        notebook.AddPage(material_panel, "Material")
        
        # Hardware Panel
        hardware_panel = self._create_hardware_panel(notebook)
        notebook.AddPage(hardware_panel, "Hardware")
        
        # Advanced Panel
        advanced_panel = self._create_advanced_panel(notebook)
        notebook.AddPage(advanced_panel, "Advanced")
        
        main_sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 10)
        
        # Output directory
        output_sizer = wx.BoxSizer(wx.HORIZONTAL)
        output_label = wx.StaticText(self, wx.ID_ANY, "Output:")
        output_sizer.Add(output_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        
        self.output_text = wx.TextCtrl(self, wx.ID_ANY, f"fixture-rev_01")
        output_sizer.Add(self.output_text, 1, wx.ALL, 5)
        
        main_sizer.Add(output_sizer, 0, wx.ALL | wx.EXPAND, 5)
        
        # Buttons
        button_sizer = wx.StdDialogButtonSizer()
        
        generate_btn = wx.Button(self, wx.ID_OK, "Generate Fixture")
        generate_btn.SetDefault()
        button_sizer.AddButton(generate_btn)
        
        cancel_btn = wx.Button(self, wx.ID_CANCEL, "Cancel")
        button_sizer.AddButton(cancel_btn)
        
        button_sizer.Realize()
        main_sizer.Add(button_sizer, 0, wx.ALL | wx.ALIGN_RIGHT, 10)
        
        self.SetSizer(main_sizer)
        self.Layout()
    
    def _create_board_panel(self, parent):
        """Create board parameters panel"""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # PCB thickness
        sizer.Add(wx.StaticText(panel, wx.ID_ANY, "PCB Parameters:"), 0, wx.ALL, 5)
        
        thickness_sizer = wx.BoxSizer(wx.HORIZONTAL)
        thickness_sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Thickness (mm):"), 0, 
                          wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.pcb_thickness = wx.TextCtrl(panel, wx.ID_ANY, "1.6")
        thickness_sizer.Add(self.pcb_thickness, 1, wx.ALL, 5)
        sizer.Add(thickness_sizer, 0, wx.EXPAND)
        
        # Revision
        rev_sizer = wx.BoxSizer(wx.HORIZONTAL)
        rev_sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Revision:"), 0,
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.revision = wx.TextCtrl(panel, wx.ID_ANY, "rev_01")
        rev_sizer.Add(self.revision, 1, wx.ALL, 5)
        sizer.Add(rev_sizer, 0, wx.EXPAND)
        
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 10)
        
        # Test point layer
        sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Layer for pogo pins:"), 0, wx.ALL, 5)
        
        self.layer_top = wx.CheckBox(panel, wx.ID_ANY, "Top Layer (F.Cu)")
        self.layer_bottom = wx.CheckBox(panel, wx.ID_ANY, "Bottom Layer (B.Cu)")
        self.layer_top.SetValue(True)
        
        # Bind events for mutual exclusion (radio button behavior)
        self.layer_top.Bind(wx.EVT_CHECKBOX, self._on_layer_top_checked)
        self.layer_bottom.Bind(wx.EVT_CHECKBOX, self._on_layer_bottom_checked)
        
        sizer.Add(self.layer_top, 0, wx.ALL, 5)
        sizer.Add(self.layer_bottom, 0, wx.ALL, 5)
        
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 10)
        
        # Pad type selection
        sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Pad Types to Include:"), 0, wx.ALL, 5)
        
        self.include_smd = wx.CheckBox(panel, wx.ID_ANY, "SMD pads (surface mount test points)")
        self.include_smd.SetValue(True)
        sizer.Add(self.include_smd, 0, wx.ALL, 5)
        
        self.include_pth = wx.CheckBox(panel, wx.ID_ANY, "PTH pads (through-hole pins/connectors)")
        self.include_pth.SetValue(True)
        sizer.Add(self.include_pth, 0, wx.ALL, 5)
        
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 10)
        
        # Help text
        help_text = wx.StaticText(panel, wx.ID_ANY,
            "Test points detected:\n"
            "• Pads without solder paste mask\n"
            "• TP* reference designators (Test Point symbols)\n"
            "• Eco2.User layer: force include specific pads\n"
            "• Eco1.User layer: exclude specific pads\n\n"
            "NOTE: Select ONE side only (Top OR Bottom).\n"
            "Physical fixture supports single-sided testing.\n"
            "PTH pads allow testing connectors from opposite side.")
        help_text.SetForegroundColour(wx.Colour(100, 100, 100))
        sizer.Add(help_text, 0, wx.ALL, 10)
        
        panel.SetSizer(sizer)
        return panel
    
    def _create_material_panel(self, parent):
        """Create material parameters panel"""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Laser Cut Material:"), 0, wx.ALL, 5)
        
        # Material thickness
        mat_sizer = wx.BoxSizer(wx.HORIZONTAL)
        mat_sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Thickness (mm):"), 0,
                     wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.material_thickness = wx.TextCtrl(panel, wx.ID_ANY, "3.0")
        mat_sizer.Add(self.material_thickness, 1, wx.ALL, 5)
        sizer.Add(mat_sizer, 0, wx.EXPAND)
        
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 10)
        
        # Common presets
        sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Common Materials:"), 0, wx.ALL, 5)
        
        presets = [
            ("Acrylic 2.5mm", "2.45"),
            ("Acrylic 3mm", "3.0"),
            ("Acrylic 4mm", "4.0"),
            ("Plywood 3mm", "3.0"),
            ("Plywood 5mm", "5.0"),
        ]
        
        for name, thickness in presets:
            btn = wx.Button(panel, wx.ID_ANY, name)
            btn.Bind(wx.EVT_BUTTON, lambda evt, t=thickness: self.material_thickness.SetValue(t))
            sizer.Add(btn, 0, wx.ALL | wx.EXPAND, 2)
        
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 10)
        
        # Help text
        help_text = wx.StaticText(panel, wx.ID_ANY,
            "Measure material thickness with calipers.\n"
            "Laser-cut materials can vary ±0.1mm.\n"
            "Use test cut to verify fit before full cut.")
        help_text.SetForegroundColour(wx.Colour(100, 100, 100))
        sizer.Add(help_text, 0, wx.ALL, 10)
        
        panel.SetSizer(sizer)
        return panel
    
    def _create_hardware_panel(self, parent):
        """Create hardware parameters panel"""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Screw parameters
        sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Screw Parameters (M3 recommended):"), 0, wx.ALL, 5)
        
        screw_len_sizer = wx.BoxSizer(wx.HORIZONTAL)
        screw_len_sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Length (mm):"), 0,
                           wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.screw_length = wx.TextCtrl(panel, wx.ID_ANY, "16.0")
        screw_len_sizer.Add(self.screw_length, 1, wx.ALL, 5)
        sizer.Add(screw_len_sizer, 0, wx.EXPAND)
        
        screw_dia_sizer = wx.BoxSizer(wx.HORIZONTAL)
        screw_dia_sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Diameter (mm):"), 0,
                           wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.screw_diameter = wx.TextCtrl(panel, wx.ID_ANY, "3.0")
        screw_dia_sizer.Add(self.screw_diameter, 1, wx.ALL, 5)
        sizer.Add(screw_dia_sizer, 0, wx.EXPAND)
        
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 10)
        
        # Nut parameters
        sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Hex Nut Parameters (M3):"), 0, wx.ALL, 5)
        
        nut_th_sizer = wx.BoxSizer(wx.HORIZONTAL)
        nut_th_sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Thickness (mm):"), 0,
                        wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.nut_thickness = wx.TextCtrl(panel, wx.ID_ANY, "2.4")
        nut_th_sizer.Add(self.nut_thickness, 1, wx.ALL, 5)
        sizer.Add(nut_th_sizer, 0, wx.EXPAND)
        
        nut_f2f_sizer = wx.BoxSizer(wx.HORIZONTAL)
        nut_f2f_sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Flat-to-Flat (mm):"), 0,
                         wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.nut_f2f = wx.TextCtrl(panel, wx.ID_ANY, "5.45")
        nut_f2f_sizer.Add(self.nut_f2f, 1, wx.ALL, 5)
        sizer.Add(nut_f2f_sizer, 0, wx.EXPAND)
        
        nut_c2c_sizer = wx.BoxSizer(wx.HORIZONTAL)
        nut_c2c_sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Corner-to-Corner (mm):"), 0,
                         wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.nut_c2c = wx.TextCtrl(panel, wx.ID_ANY, "6.10")
        nut_c2c_sizer.Add(self.nut_c2c, 1, wx.ALL, 5)
        sizer.Add(nut_c2c_sizer, 0, wx.EXPAND)
        
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 10)
        
        # Help text
        help_text = wx.StaticText(panel, wx.ID_ANY,
            "Measure screw threaded length only (not head).\n"
            "Measure nut dimensions with calipers.\n"
            "Sizes vary by manufacturer!")
        help_text.SetForegroundColour(wx.Colour(100, 100, 100))
        sizer.Add(help_text, 0, wx.ALL, 10)
        
        panel.SetSizer(sizer)
        return panel
    
    def _create_advanced_panel(self, parent):
        """Create advanced parameters panel"""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Washer
        washer_sizer = wx.BoxSizer(wx.HORIZONTAL)
        washer_sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Washer Thickness (mm):"), 0,
                        wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.washer_thickness = wx.TextCtrl(panel, wx.ID_ANY, "1.0")
        washer_sizer.Add(self.washer_thickness, 1, wx.ALL, 5)
        sizer.Add(washer_sizer, 0, wx.EXPAND)
        
        # Border
        border_sizer = wx.BoxSizer(wx.HORIZONTAL)
        border_sizer.Add(wx.StaticText(panel, wx.ID_ANY, "PCB Support Border (mm):"), 0,
                        wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.border = wx.TextCtrl(panel, wx.ID_ANY, "1.0")
        border_sizer.Add(self.border, 1, wx.ALL, 5)
        sizer.Add(border_sizer, 0, wx.EXPAND)
        
        # Pogo pin length
        pogo_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pogo_sizer.Add(wx.StaticText(panel, wx.ID_ANY, "Pogo Pin Length (mm):"), 0,
                      wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        self.pogo_length = wx.TextCtrl(panel, wx.ID_ANY, "16.0")
        pogo_sizer.Add(self.pogo_length, 1, wx.ALL, 5)
        sizer.Add(pogo_sizer, 0, wx.EXPAND)
        
        sizer.Add(wx.StaticLine(panel), 0, wx.EXPAND | wx.ALL, 10)
        
        # Verbose logging checkbox
        self.verbose_logging = wx.CheckBox(panel, wx.ID_ANY, "Enable Verbose Logging (creates log file)")
        self.verbose_logging.SetValue(False)
        sizer.Add(self.verbose_logging, 0, wx.ALL, 10)
        
        # Help text
        help_text = wx.StaticText(panel, wx.ID_ANY,
            "Optional parameters for fine-tuning.\n"
            "Leave at defaults for most applications.")
        help_text.SetForegroundColour(wx.Colour(100, 100, 100))
        sizer.Add(help_text, 0, wx.ALL, 10)
        
        panel.SetSizer(sizer)
        return panel
    
    def _on_layer_top_checked(self, event):
        """Handle top layer checkbox - ensure mutual exclusion"""
        if self.layer_top.GetValue():
            # Top checked, uncheck bottom
            self.layer_bottom.SetValue(False)
        elif not self.layer_bottom.GetValue():
            # If unchecking top and bottom is not checked, recheck top (at least one must be selected)
            self.layer_top.SetValue(True)
    
    def _on_layer_bottom_checked(self, event):
        """Handle bottom layer checkbox - ensure mutual exclusion"""
        if self.layer_bottom.GetValue():
            # Bottom checked, uncheck top
            self.layer_top.SetValue(False)
        elif not self.layer_top.GetValue():
            # If unchecking bottom and top is not checked, recheck bottom (at least one must be selected)
            self.layer_bottom.SetValue(True)
    
    def _load_defaults(self):
        """Load default values from config file if available"""
        if not self.config_path:
            return
        
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                return
        
        try:
            with open(self.config_path, 'rb') as f:
                config = tomllib.load(f)
            
            # Load board parameters
            if 'board' in config:
                board = config['board']
                if 'thickness_mm' in board:
                    self.pcb_thickness.SetValue(str(board['thickness_mm']))
                if 'test_layer' in board:
                    if board['test_layer'] == 'B.Cu':
                        self.layer_top.SetValue(False)
                        self.layer_bottom.SetValue(True)
                    # Note: 'both' mode not supported by physical fixture design
                    # If config specifies 'both', default to top layer
                    elif board['test_layer'] == 'both':
                        self.layer_top.SetValue(True)
                        self.layer_bottom.SetValue(False)
            
            # Load material parameters
            if 'material' in config:
                material = config['material']
                if 'thickness_mm' in material:
                    self.material_thickness.SetValue(str(material['thickness_mm']))
            
            # Load hardware parameters
            if 'hardware' in config:
                hw = config['hardware']
                if 'screw_length_mm' in hw:
                    self.screw_length.SetValue(str(hw['screw_length_mm']))
                if 'screw_diameter_mm' in hw:
                    self.screw_diameter.SetValue(str(hw['screw_diameter_mm']))
                if 'nut_thickness_mm' in hw:
                    self.nut_thickness.SetValue(str(hw['nut_thickness_mm']))
                if 'nut_flat_to_flat_mm' in hw:
                    self.nut_f2f.SetValue(str(hw['nut_flat_to_flat_mm']))
                if 'nut_corner_to_corner_mm' in hw:
                    self.nut_c2c.SetValue(str(hw['nut_corner_to_corner_mm']))
                if 'washer_thickness_mm' in hw:
                    self.washer_thickness.SetValue(str(hw['washer_thickness_mm']))
                if 'border_mm' in hw:
                    self.border.SetValue(str(hw['border_mm']))
                if 'pogo_uncompressed_length_mm' in hw:
                    self.pogo_length.SetValue(str(hw['pogo_uncompressed_length_mm']))
            
            # Load advanced/debugging parameters
            if 'advanced' in config:
                advanced = config['advanced']
                if 'verbose_logging' in advanced:
                    self.verbose_logging.SetValue(bool(advanced['verbose_logging']))
            
            # Load test point detection parameters
            if 'test_points' in config:
                tp = config['test_points']
                if 'include_smd_pads' in tp:
                    self.include_smd.SetValue(bool(tp['include_smd_pads']))
                if 'include_pth_pads' in tp:
                    self.include_pth.SetValue(bool(tp['include_pth_pads']))
            
            logger.info("Loaded defaults from configuration file")
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    
    def get_parameters(self) -> dict:
        """Get all parameters from dialog"""
        # Determine selected layer based on checkboxes (mutually exclusive)
        top_checked = self.layer_top.GetValue()
        bottom_checked = self.layer_bottom.GetValue()
        
        # Due to mutual exclusion, only one can be true at a time
        if top_checked:
            layer = 'F.Cu'
        elif bottom_checked:
            layer = 'B.Cu'
        else:
            # Fallback (should not happen with mutual exclusion)
            layer = 'F.Cu'
        
        return {
            'board': self.board_path,
            'pcb_th': self.pcb_thickness.GetValue(),
            'mat_th': self.material_thickness.GetValue(),
            'rev': self.revision.GetValue(),
            'layer': layer,
            'screw_len': self.screw_length.GetValue(),
            'screw_d': self.screw_diameter.GetValue(),
            'nut_th': self.nut_thickness.GetValue(),
            'nut_f2f': self.nut_f2f.GetValue(),
            'nut_c2c': self.nut_c2c.GetValue(),
            'washer_th': self.washer_thickness.GetValue(),
            'border': self.border.GetValue(),
            'pogo_length': self.pogo_length.GetValue(),
            'output': self.output_text.GetValue(),
            'verbose': self.verbose_logging.GetValue(),
            'include_smd': self.include_smd.GetValue(),
            'include_pth': self.include_pth.GetValue(),
        }


class OpenFixturePlugin(pcbnew.ActionPlugin):
    """
    OpenFixture Action Plugin for KiCAD 8.0+
    
    Generates laser-cuttable PCB test fixtures from KiCAD board files
    """
    
    def defaults(self):
        """Set plugin metadata"""
        self.name = "OpenFixture Generator"
        self.category = "Manufacturing"
        self.description = "Generate laser-cuttable PCB test fixtures automatically"
        self.show_toolbar_button = True
        
        # Icon file - check if it exists before setting
        icon_path = os.path.join(os.path.dirname(__file__), "OpenFixture.png")
        if os.path.exists(icon_path):
            self.icon_file_name = icon_path
        else:
            # Check openfixture_support subdirectory
            icon_path_alt = os.path.join(os.path.dirname(__file__), "openfixture_support", "OpenFixture.png")
            if os.path.exists(icon_path_alt):
                self.icon_file_name = icon_path_alt
            # If no icon found, KiCAD will use default icon
    
    def Run(self):
        """Main plugin entry point"""
        try:
            # Get current board
            board = pcbnew.GetBoard()
            board_path = board.GetFileName()
            
            if not board_path:
                wx.MessageBox(
                    "Please save the board file before generating fixture.",
                    "Board Not Saved",
                    wx.OK | wx.ICON_WARNING
                )
                return
            
            # Get PCBNew frame
            pcbnew_frame = None
            for window in wx.GetTopLevelWindows():
                if window.GetName() == 'PcbFrame':
                    pcbnew_frame = window
                    break
            
            if not pcbnew_frame:
                logger.error("Could not find PCBNew frame")
                return
            
            # Show dialog
            dialog = OpenFixtureDialog(pcbnew_frame, board_path)
            
            if dialog.ShowModal() == wx.ID_OK:
                params = dialog.get_parameters()
                self._generate_fixture(params, pcbnew_frame)
            
            dialog.Destroy()
            
        except Exception as e:
            logger.error(f"Plugin error: {e}", exc_info=True)
            wx.MessageBox(
                f"Error running OpenFixture plugin:\n{str(e)}",
                "Plugin Error",
                wx.OK | wx.ICON_ERROR
            )
    
    def _find_python_executable(self) -> str:
        """
        Find the correct Python executable for running GenFixture
        
        In KiCAD plugins, sys.executable may point to KiCAD itself,
        so we need to find the actual Python interpreter.
        """
        # Try common Python locations for KiCAD 9.0
        possible_paths = [
            r"C:\Program Files\KiCad\9.0\bin\python.exe",
            r"C:\Program Files\KiCad\8.0\bin\python.exe",
            r"C:\Program Files\KiCad\bin\python.exe",
        ]
        
        # Check if any of the known paths exist
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Using Python: {path}")
                return path
        
        # Fallback: check if sys.executable is actually Python
        if 'python' in sys.executable.lower():
            logger.info(f"Using Python from sys.executable: {sys.executable}")
            return sys.executable
        
        # Last resort: try to find python in PATH
        import shutil
        python_path = shutil.which('python') or shutil.which('python3')
        if python_path:
            logger.info(f"Using Python from PATH: {python_path}")
            return python_path
        
        # If all else fails, return sys.executable and hope for the best
        logger.warning(f"Could not find Python, using sys.executable: {sys.executable}")
        return sys.executable
    
    def _check_openscad(self) -> tuple[bool, str]:
        """
        Check if OpenSCAD is installed and accessible
        
        Returns:
            tuple: (is_installed, path_or_error_message)
        """
        import shutil
        
        # Common OpenSCAD installation paths
        possible_paths = [
            r"C:\Program Files\OpenSCAD\openscad.exe",
            r"C:\Program Files (x86)\OpenSCAD\openscad.exe",
        ]
        
        # Check known paths first
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found OpenSCAD at: {path}")
                return True, path
        
        # Try to find OpenSCAD in PATH
        openscad_path = shutil.which('openscad')
        if openscad_path:
            logger.info(f"Found OpenSCAD in PATH: {openscad_path}")
            return True, openscad_path
        
        # Not found
        error_msg = (
            "OpenSCAD is not installed or not found.\n\n"
            "OpenSCAD is required to generate 3D models and DXF files.\n\n"
            "Please install OpenSCAD from:\n"
            "https://openscad.org/downloads.html\n\n"
            "After installation, restart KiCAD and try again."
        )
        return False, error_msg
    
    def _verify_output_files(self, output_dir: Path, prefix: str, layer: str = None) -> tuple[bool, list, list]:
        """
        Verify that expected output files were generated
        
        Args:
            output_dir: Output directory path
            prefix: File prefix (e.g., board name)
            layer: Layer selection ('F.Cu', 'B.Cu', or 'both')
        
        Returns:
            tuple: (all_ok, found_files, missing_files)
        """
        expected_files = [
            f"{prefix}-fixture.dxf",
            f"{prefix}-outline.dxf",
        ]
        
        # Add appropriate track file(s) based on layer selection
        if layer == 'both':
            expected_files.extend([
                f"{prefix}-track_top.dxf",
                f"{prefix}-track_bottom.dxf",
            ])
        else:
            expected_files.append(f"{prefix}-track.dxf")
        
        optional_files = [
            f"{prefix}-fixture.png",
            f"{prefix}-test.dxf",
        ]
        
        found_files = []
        missing_files = []
        
        # Check expected files
        for filename in expected_files:
            filepath = output_dir / filename
            if filepath.exists() and filepath.stat().st_size > 0:
                found_files.append(filename)
                logger.info(f"Verified: {filename} ({filepath.stat().st_size} bytes)")
            else:
                missing_files.append(filename)
                logger.warning(f"Missing or empty: {filename}")
        
        # Check optional files (log but don't require)
        for filename in optional_files:
            filepath = output_dir / filename
            if filepath.exists() and filepath.stat().st_size > 0:
                found_files.append(filename)
                logger.info(f"Found optional: {filename} ({filepath.stat().st_size} bytes)")
        
        all_ok = len(missing_files) == 0
        return all_ok, found_files, missing_files
    
    def _parse_error_message(self, error_text: str) -> str:
        """
        Parse error output and provide user-friendly error messages
        
        Args:
            error_text: Raw error output from GenFixture
        
        Returns:
            User-friendly error message
        """
        error_lower = error_text.lower()
        
        # Check for common errors
        if "no test points found" in error_lower:
            return (
                "No test points found on the PCB!\n\n"
                "Test points must be:\n"
                "• SMD pads\n"
                "• Without solder paste mask\n"
                "• On the selected layer (F.Cu, B.Cu, or both)\n\n"
                "Tip: Use pad properties to remove paste mask.\n"
                "Tip: Use Eco2.User layer to force include specific pads."
            )
        
        if "openscad" in error_lower and ("not found" in error_lower or "no such file" in error_lower):
            return (
                "OpenSCAD is not installed or not in PATH.\n\n"
                "Please install OpenSCAD from:\n"
                "https://openscad.org/downloads.html\n\n"
                "After installation, add it to your PATH or install to:\n"
                "C:\\Program Files\\OpenSCAD\\"
            )
        
        if "failed to load board" in error_lower or "cannot open" in error_lower:
            return (
                "Failed to load the PCB file.\n\n"
                "Possible causes:\n"
                "• File is corrupted or not a valid KiCAD PCB file\n"
                "• File is currently open in another application\n"
                "• Insufficient permissions to read the file\n\n"
                "Try saving the board and running the plugin again."
            )
        
        if "modulenotfounderror" in error_lower or "importerror" in error_lower:
            return (
                "Python module import error.\n\n"
                "This may indicate a KiCAD Python installation issue.\n"
                "Try reinstalling or updating KiCAD to the latest version."
            )
        
        # Return original error if we can't categorize it
        # Don't truncate - full error will be shown in scrollable dialog
        return "An error occurred during fixture generation.\n\nSee details below for the full error message."
    
    def _generate_fixture(self, params: dict, parent):
        """Execute fixture generation with comprehensive error handling"""
        # Check OpenSCAD installation first
        openscad_ok, openscad_msg = self._check_openscad()
        if not openscad_ok:
            wx.MessageBox(
                openscad_msg,
                "OpenSCAD Not Found",
                wx.OK | wx.ICON_WARNING
            )
            # Continue anyway - user might have OpenSCAD in a custom location
            logger.warning("OpenSCAD not detected, continuing anyway...")
        
        # Find GenFixture.py - check multiple locations
        plugin_dir = Path(__file__).parent
        
        # Search priority:
        # 1. Same directory as plugin
        # 2. openfixture_support subdirectory (for organized installations)
        # 3. Parent directory (for development)
        search_paths = [
            plugin_dir / "GenFixture.py",
            plugin_dir / "openfixture_support" / "GenFixture.py",
            plugin_dir.parent / "GenFixture.py"
        ]
        
        genfixture_path = None
        for path in search_paths:
            if path.exists():
                genfixture_path = path
                logger.info(f"Found GenFixture.py at: {path}")
                break
        
        if not genfixture_path:
            wx.MessageBox(
                "Could not find GenFixture.py.\n\n"
                "Expected locations:\n"
                f"• {plugin_dir}\n"
                f"• {plugin_dir / 'openfixture_support'}\n\n"
                "Please ensure the files are properly synced.",
                "Missing Generator",
                wx.OK | wx.ICON_ERROR
            )
            return
        
        # Build command
        board_dir = Path(params['board']).parent
        output_dir = board_dir / params['output']
        
        # Find Python executable - KiCAD's sys.executable might point to KiCAD itself
        # We need to find the actual Python interpreter
        python_exe = self._find_python_executable()
        
        cmd = [
            python_exe,
            str(genfixture_path),
            '--board', params['board'],
            '--mat_th', params['mat_th'],
            '--out', str(output_dir),
            '--pcb_th', params['pcb_th'],
            '--layer', params['layer'],
            '--rev', params['rev'],
            '--screw_len', params['screw_len'],
            '--screw_d', params['screw_d'],
            '--nut_th', params['nut_th'],
            '--nut_f2f', params['nut_f2f'],
            '--nut_c2c', params['nut_c2c'],
            '--washer_th', params['washer_th'],
            '--border', params['border'],
            '--pogo-uncompressed-length', params['pogo_length'],
        ]
        
        # Add verbose flag if enabled
        if params.get('verbose', False):
            cmd.append('--verbose')
        
        # Add pad type flags
        if params.get('include_smd', True):
            cmd.append('--include-smd')
        if params.get('include_pth', True):
            cmd.append('--include-pth')
        
        # Show progress dialog
        progress = wx.ProgressDialog(
            "Generating Fixture",
            "Running GenFixture...\nThis may take a few minutes.",
            maximum=100,
            parent=parent,
            style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
        )
        progress.Pulse()
        
        try:
            # Run command
            logger.info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(board_dir)
            )
            
            progress.Update(100)
            progress.Destroy()
            
            if result.returncode == 0:
                # Verify output files were actually created
                board_name = Path(params['board']).stem
                all_ok, found_files, missing_files = self._verify_output_files(
                    output_dir, board_name, params['layer']
                )
                
                if all_ok:
                    # Success - all required files generated
                    file_list = "\n".join([f"  ✅ {f}" for f in found_files])
                    
                    # Check if log file was created (verbose mode)
                    log_msg = ""
                    if params.get('verbose', False):
                        # Find the log file in output directory
                        import glob
                        log_files = glob.glob(str(output_dir / "openfixture_*.log"))
                        if log_files:
                            log_file = Path(log_files[-1]).name  # Get most recent
                            log_msg = f"\n\nVerbose log: {log_file}"
                    
                    wx.MessageBox(
                        f"Fixture generated successfully!\n\n"
                        f"Output directory: {output_dir}\n\n"
                        f"Files generated:\n{file_list}{log_msg}\n\n"
                        f"Opening output directory...",
                        "Success",
                        wx.OK | wx.ICON_INFORMATION
                    )
                    
                    # Open output directory
                    try:
                        if sys.platform == 'win32':
                            os.startfile(str(output_dir))
                        elif sys.platform == 'darwin':
                            subprocess.run(['open', str(output_dir)])
                        else:
                            subprocess.run(['xdg-open', str(output_dir)])
                    except Exception as e:
                        logger.warning(f"Could not open output directory: {e}")
                else:
                    # Some files missing - partial success
                    found_list = "\n".join([f"  ✅ {f}" for f in found_files])
                    missing_list = "\n".join([f"  ❌ {f}" for f in missing_files])
                    wx.MessageBox(
                        f"Generation completed with warnings!\n\n"
                        f"Some expected files were not created:\n\n"
                        f"Found:\n{found_list}\n\n"
                        f"Missing:\n{missing_list}\n\n"
                        f"Check the logs for more details.",
                        "Partial Success",
                        wx.OK | wx.ICON_WARNING
                    )
                    
            else:
                # Error - parse and display user-friendly message
                error_text = result.stderr if result.stderr else result.stdout
                user_friendly_error = self._parse_error_message(error_text)
                
                # Use scrollable error dialog for better error display
                error_dialog = ErrorDialog(
                    parent,
                    "Generation Failed",
                    user_friendly_error,
                    details=error_text
                )
                error_dialog.ShowModal()
                error_dialog.Destroy()
                
                logger.error(f"Generation failed (exit code {result.returncode}): {error_text}")
        
        except Exception as e:
            progress.Destroy()
            
            # Get traceback for detailed error
            import traceback
            error_details = traceback.format_exc()
            
            # Use scrollable error dialog
            error_dialog = ErrorDialog(
                parent,
                "Execution Error",
                f"Error running generator:\n{str(e)}",
                details=error_details
            )
            error_dialog.ShowModal()
            error_dialog.Destroy()
            
            logger.error(f"Execution error: {e}", exc_info=True)


# Register plugin
OpenFixturePlugin().register()
