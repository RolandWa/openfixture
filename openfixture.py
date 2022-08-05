#!/usr/bin/env python
import pcbnew
import sys
import os
import wx
import subprocess


from . import OpenFixtureDlg

debug = True

def wxLogDebug(msg,show):
    """printing messages only if show is omitted or True"""
    if show:
        wx.LogMessage(msg)
# 
class OpenFixture_Dlg(OpenFixtureDlg.OpenFixtureDlg):
    # from https://github.com/MitjaNemec/Kicad_action_plugins
    # hack for new wxFormBuilder generating code incompatible with old wxPython
    # noinspection PyMethodOverriding
    def SetSizeHints(self, sz1, sz2):
        if wx.__version__ < '4.0':
            self.SetSizeHintsSz(sz1, sz2)
        else:
            super(OpenFixture_Dlg, self).SetSizeHints(sz1, sz2)

    def onCancelClick(self, event):
        return self.EndModal(wx.ID_CANCEL)

    def onCreateClick(self, event):
        wxLogDebug("Click Create",debug)
        subprocess.call("--board C:\\222\\Smart_Tap_Dongle\\Smart_Tap_Dongle.kicad_pcb --layer B.Cu --rev rev_11 --mat_th 2.45 --pcb_th 0.8 --out fixture-rev_11  --screw_len 16.0 --screw_d 3.0 --washer_th 1.0 --nut_th 2.4 --nut_f2f 5.45 --nut_c2c 6.10 --border 0.8 --pogo-uncompressed-length 16", "GenFuxture.py")
        return self.EndModal(wx.ID_OK)

    def __init__(self,  parent):
        import wx
        OpenFixtureDlg.OpenFixtureDlg.__init__(self, parent)
        #self.GetSizer().Fit(self)
        self.SetMinSize(self.GetSize())
        self.m_buttonCancel.Bind(wx.EVT_BUTTON, self.onCancelClick)
        self.m_buttonCreate.Bind(wx.EVT_BUTTON, self.onCreateClick)
        if wx.__version__ < '4.0':
            self.m_buttonCancel.SetToolTipString( u"Create fixture " )
            self.m_buttonCreate.SetToolTipString( u"Create fixture" )
        else:
            self.m_buttonCancel.SetToolTip( u"Create fixture " )
            self.m_buttonCreate.SetToolTip( u"Create fixture" )


class OpenFixture(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Open Fixture"
        self.category = "CAD automatic ficture tool"
        self.description = "Create automaticly fixture using the OpenSCAD"
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "./OpenFixture.png")

    def Run(self):
        #The entry function of the plugin that is executed on user action
        pcb = pcbnew.GetBoard()  
        #from https://github.com/MitjaNemec/Kicad_action_plugins
        #hack wxFormBuilder py2/py3
        # _pcbnew_frame = [x for x in wx.GetTopLevelWindows() if x.GetTitle().lower().startswith('pcbnew')][0]
        _pcbnew_frame = [x for x in wx.GetTopLevelWindows() if x.GetName() == 'PcbFrame'][0]
        aParameters = OpenFixture_Dlg(_pcbnew_frame)
        aParameters.Show()
        
        modal_result = aParameters.ShowModal()
        
        
        #aParameters.Destroy()
#
OpenFixture().register()