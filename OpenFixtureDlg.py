# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version Oct 26 2018)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class OpenFixtureDlg
###########################################################################

class OpenFixtureDlg ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Open Fixture Parameter", pos = wx.DefaultPosition, size = wx.Size( 287,517 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer1 = wx.BoxSizer( wx.VERTICAL )

		self.m_comment = wx.StaticText( self, wx.ID_ANY, u"Board Parameter", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_comment.Wrap( -1 )

		bSizer1.Add( self.m_comment, 0, wx.ALL|wx.EXPAND, 5 )

		bSizer2 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_ = wx.StaticText( self, wx.ID_ANY, u"PCB thickness in mm", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_.Wrap( -1 )

		bSizer2.Add( self.m_, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_PcbTh = wx.TextCtrl( self, wx.ID_ANY, u"1.6", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_PcbTh.SetMinSize( wx.Size( 1000,-1 ) )

		bSizer2.Add( self.m_PcbTh, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer1.Add( bSizer2, 0, 0, 5 )

		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText34 = wx.StaticText( self, wx.ID_ANY, u"Revision", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText34.Wrap( -1 )

		bSizer3.Add( self.m_staticText34, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_rev = wx.TextCtrl( self, wx.ID_ANY, u"0.1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_rev.SetMinSize( wx.Size( 1000,-1 ) )

		bSizer3.Add( self.m_rev, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer1.Add( bSizer3, 1, wx.EXPAND, 5 )

		bSizer3 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText31 = wx.StaticText( self, wx.ID_ANY, u"Layer for pogo pins", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText31.Wrap( -1 )

		bSizer3.Add( self.m_staticText31, 1, wx.ALL, 5 )

		self.m_checkLayerTop = wx.CheckBox( self, wx.ID_ANY, u"Top Layer", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkLayerTop.SetValue(True)
		bSizer3.Add( self.m_checkLayerTop, 0, wx.ALL, 5 )

		self.m_checkLayerBottom = wx.CheckBox( self, wx.ID_ANY, u"Bottom Layer", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer3.Add( self.m_checkLayerBottom, 0, wx.ALL, 5 )


		bSizer1.Add( bSizer3, 1, wx.EXPAND, 5 )

		self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer1.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )

		self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, u"Screw parameter", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText7.Wrap( -1 )

		bSizer1.Add( self.m_staticText7, 0, wx.ALL, 5 )

		bSizer4 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText33 = wx.StaticText( self, wx.ID_ANY, u"Screw length", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText33.Wrap( -1 )

		bSizer4.Add( self.m_staticText33, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_screwLen = wx.TextCtrl( self, wx.ID_ANY, u"16.0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_screwLen.SetMinSize( wx.Size( 1000,-1 ) )

		bSizer4.Add( self.m_screwLen, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer1.Add( bSizer4, 1, wx.EXPAND, 5 )

		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText32 = wx.StaticText( self, wx.ID_ANY, u"Screw diameter", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText32.Wrap( -1 )

		bSizer5.Add( self.m_staticText32, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_screwDia = wx.TextCtrl( self, wx.ID_ANY, u"3.0", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_screwDia.SetMinSize( wx.Size( 1000,-1 ) )

		bSizer5.Add( self.m_screwDia, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer1.Add( bSizer5, 1, wx.EXPAND, 5 )

		self.m_staticline11 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer1.Add( self.m_staticline11, 0, wx.EXPAND |wx.ALL, 5 )

		self.m_staticText71 = wx.StaticText( self, wx.ID_ANY, u"Nut parameter", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText71.Wrap( -1 )

		bSizer1.Add( self.m_staticText71, 0, wx.ALL, 5 )

		bSizer6 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText321 = wx.StaticText( self, wx.ID_ANY, u"Nut TH", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText321.Wrap( -1 )

		bSizer6.Add( self.m_staticText321, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_nutTh = wx.TextCtrl( self, wx.ID_ANY, u"2.4", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_nutTh.SetMinSize( wx.Size( 1000,-1 ) )

		bSizer6.Add( self.m_nutTh, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer1.Add( bSizer6, 1, wx.EXPAND, 5 )

		bSizer7 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText3211 = wx.StaticText( self, wx.ID_ANY, u"Nut F2F", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3211.Wrap( -1 )

		bSizer7.Add( self.m_staticText3211, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_nutF2F = wx.TextCtrl( self, wx.ID_ANY, u"5.45", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_nutF2F.SetMinSize( wx.Size( 1000,-1 ) )

		bSizer7.Add( self.m_nutF2F, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer1.Add( bSizer7, 1, wx.EXPAND, 5 )

		bSizer8 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_nutC2C = wx.StaticText( self, wx.ID_ANY, u"Nut C2C", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_nutC2C.Wrap( -1 )

		bSizer8.Add( self.m_nutC2C, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_distanceMM1111 = wx.TextCtrl( self, wx.ID_ANY, u"6.10", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_distanceMM1111.SetMinSize( wx.Size( 1000,-1 ) )

		bSizer8.Add( self.m_distanceMM1111, 1, wx.ALL|wx.EXPAND, 5 )


		bSizer1.Add( bSizer8, 1, wx.EXPAND, 5 )

		self.m_staticline111 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer1.Add( self.m_staticline111, 0, wx.EXPAND |wx.ALL, 5 )

		self.m_staticline1111 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer1.Add( self.m_staticline1111, 0, wx.EXPAND |wx.ALL, 5 )

		bSizer9 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_washerTh = wx.StaticText( self, wx.ID_ANY, u"Washer TH", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_washerTh.Wrap( -1 )

		bSizer9.Add( self.m_washerTh, 0, wx.ALL, 5 )

		self.m_distanceMM11111 = wx.TextCtrl( self, wx.ID_ANY, u"1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_distanceMM11111.SetMinSize( wx.Size( 1000,-1 ) )

		bSizer9.Add( self.m_distanceMM11111, 0, wx.ALL, 5 )


		bSizer1.Add( bSizer9, 1, wx.EXPAND, 5 )

		bSizer10 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_pogoLen = wx.StaticText( self, wx.ID_ANY, u"POGO UNCOMPRESSED LENGTH", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_pogoLen.Wrap( -1 )

		bSizer10.Add( self.m_pogoLen, 0, wx.ALL, 5 )

		self.m_distanceMM111111 = wx.TextCtrl( self, wx.ID_ANY, u"16", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_distanceMM111111.SetMinSize( wx.Size( 1000,-1 ) )

		bSizer10.Add( self.m_distanceMM111111, 0, wx.ALL, 5 )


		bSizer1.Add( bSizer10, 1, wx.EXPAND, 5 )

		bSizer11 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_buttonCreate = wx.Button( self, wx.ID_OK, u"Create", wx.DefaultPosition, wx.DefaultSize, 0 )

		self.m_buttonCreate.SetDefault()
		bSizer11.Add( self.m_buttonCreate, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.m_buttonCancel = wx.Button( self, wx.ID_CANCEL, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer11.Add( self.m_buttonCancel, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer1.Add( bSizer11, 0, wx.ALIGN_RIGHT|wx.EXPAND, 5 )


		self.SetSizer( bSizer1 )
		self.Layout()

		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


