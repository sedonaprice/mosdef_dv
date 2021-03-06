###
# Licensed under the MIT license. See LICENSE

"""
MOSDEF data viewer:
	Check the reduction for a whole mask quickly!
	
	Matplotlib plotting within a PyQt4 GUI application.
	
Written:
	2014-05-30, SHP

Very helpful demonstration: 
	http://eli.thegreenplace.net/files/prog_code/qt_mpl_bars.py.txt
Useful PyQt4 tutorial:
	http://zetcode.com/gui/pyqt4/
"""

from __future__ import print_function

import sys, os
import re
try:
    raise ValueError("Must use PyQt4 until you get around to translating the slots/connections...")
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
    from PyQt5.QtWidgets import *
except:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *
#from PyQt5.QtWidgets import *
import numpy as np

import matplotlib as mpl
mpl.rcParams['text.usetex'] = False

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
try:
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
except:
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from viewer_lib.database import write_cat_db, query_db
from viewer_lib.viewer_io import read_spec1d_comments, read_spec2d, read_bmep_redshift_slim
from viewer_lib.viewer_io import get_tdhst_vers, read_parent_cat
from viewer_lib.database_options import ChangeDBinfo

from viewer_lib.plot_object import plotObject

from viewer_lib.menu import DV_Menu
from viewer_lib.layout import DV_Layout


class NavigationToolbar(NavigationToolbar):
    # only display the buttons we need
    toolitems = [t for t in NavigationToolbar.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Back', 'Forward', None, 'Save')]
    
    # toolitems = NavigationToolbar.toolitems
    # for t in NavigationToolbar.toolitems:
    #     print(t[0])


class DataViewer(QMainWindow, DV_Menu, DV_Layout):
    """
    MOSDEF DataViewer Calss to examine data reduction and extraction products.
    """
    def __init__(self, parent=None, screen_res=None):
        QMainWindow.__init__(self, parent)
        
        self.setWindowTitle('MOSDEF Data Viewer')
        
        # Set default size of the window:
        if screen_res is not None:
            screen_res_native = screen_res
            mult = 1.55 #1.3
            if screen_res[1]*mult < screen_res[0]:
                screen_res[0] = screen_res[1]*mult
            elif screen_res[0]/mult < screen_res[1]:
                screen_res[1] = screen_res[0]/mult
                
            self.setGeometry(screen_res_native[0], screen_res_native[1], 
                    screen_res[0], screen_res[1])
                    

        # Initial values:
        self.maskname = '-----'
        self.obj_id = -99
        self.primID = -99
        self.primID_v2 = -99
        self.primID_v4 = -99
        self.aper_no = -1
        self.field = '-------'
        self.z = -1.  # Which value should this be set as?
        self.z_mosfire_1d = None
        self.z_spec = None
        self.z_gris = None
        self.z_phot = None
        self.h_mag = None
        self.query_good = 0
        
        self.obj_id_color = None #'darkturquoise'
        self.serendip_ids = None
        self.serendip_colors = None #['orange', 'magenta', 'yellowgreen', 'red', 'MediumSlateBlue']
        
        ##--------------------##
        ##   Create things:   ##
        #self.create_menu()
        #self.create_menu_complicated(self)
        self.create_main_frame(screen_res=screen_res)

        ##--------------------##
        ##   Initialize plot  ##
        self.on_draw()
    
    ############################################################################
    
    ####
    ## Methods to call mpl_toolbar item functions:
    def toolbar_zoom(self):
        self.mpl_toolbar.zoom() 
        
    def toolbar_pan(self):
        self.mpl_toolbar.pan() 
    
    def toolbar_home(self):
        self.mpl_toolbar.home() 
    ####

    def make_toolbar_shortcut(self, name, shortcut, slot, signal="triggered()"):
        # Make shortcuts to go with the MPL toolbar items
        action = QAction(name, self)
        action.setShortcut(shortcut)
        #self.connect(action, SIGNAL(signal), slot)
        self.connect(action, SIGNAL(signal), slot)
        button = QWidget()
        button.addAction(action)
        button.setGeometry(0,0,0,0)
        self.mpl_toolbar.addWidget(button)
        return button

    
    def create_main_frame(self, screen_res=None):
        self.main_frame = QWidget()
        #self.main_frame.setFocusPolicy(Qt.StrongFocus)
        
        # Create the mpl Figure and FigCanvas objects. 
        self.dpi = 100.
        # Set it larger than it ever should be, to take up all the space it can
        self.fig = Figure((20.0, 20.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        # Create the navigation toolbar, tied to the canvas
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        # Create shortcuts:
        self.zoom = self.make_toolbar_shortcut('&Zoom', "Ctrl+O", self.toolbar_zoom)
        self.pan = self.make_toolbar_shortcut('&Pan', "Ctrl+P", self.toolbar_pan)
        self.home = self.make_toolbar_shortcut('&Home', "Esc", self.toolbar_home)
        
        
        ######
        # Other GUI inputs and controls:
        ######
        # Textboxs to get input
        self.lbl_maskNameBox = QLabel("Mask")
        self.maskNameBox = QLineEdit()
        self.maskNameBox.setFixedWidth(80)  # 100
        self.connect(self.maskNameBox, SIGNAL("returnPressed()"), self.on_mask_query)
        #
        self.lbl_objIDBox = QLabel("ID")
        self.objIDBox = QLineEdit()
        self.objIDBox.setFixedWidth(80) # 100
        self.connect(self.objIDBox, SIGNAL("returnPressed()"), self.on_mask_id_button)
        
        # Query buttons
        self.query_mask_button = QPushButton("&Search mask")
        self.query_mask_button.setFixedWidth(130) # 140
        self.connect(self.query_mask_button, SIGNAL('clicked()'), self.on_mask_query)
        #
        self.query_maskid_button = QPushButton("&Search mask, id")
        self.query_maskid_button.setFixedWidth(130) # 140
        self.connect(self.query_maskid_button, SIGNAL('clicked()'), self.on_mask_id_button)
        
        
        # Query all masks:
        self.query_all_masks_button = QPushButton("&Search all masks")
        self.query_all_masks_button.setFixedWidth(130)
        self.connect(self.query_all_masks_button, SIGNAL('clicked()'), self.on_all_mask_query)
        
        
        
        ######################################
        # Matches to the Mask query:
        self.match_lbl = QLabel("Objects in mask:", self)
        
        self.match_list = []#"Ubuntu", "Mandriva", "Fedora", "Red Hat", "Gentoo"]
        self.matches = self.initComboBox(self.match_list)
        
        # Previous, Next buttons
        self.prev_match_button = QPushButton("&Previous")
        self.prev_match_button.setFixedWidth(100)
        self.connect(self.prev_match_button, SIGNAL('clicked()'), self.prev_match)
        self.prev_match_button.setShortcut(QKeySequence("Ctrl+Left"))
        
        self.next_match_button = QPushButton("&Next")
        self.next_match_button.setFixedWidth(100)
        self.connect(self.next_match_button, SIGNAL('clicked()'), self.next_match)
        self.next_match_button.setShortcut(QKeySequence("Ctrl+Right"))
        
        
        #########################################
        # Change redshift for overplotting common lines:
        # Textbox to get input
        self.lbl_redshiftBox = QLabel("z = ")
        self.redshiftBox = QLineEdit()
        self.redshiftBox.setFixedWidth(80)  # 100
        self.connect(self.redshiftBox, SIGNAL("returnPressed()"), self.on_z_update)
        # Change button
        self.redshift_button = QPushButton("&Update z")
        self.redshift_button.setFixedWidth(100) # 140
        self.connect(self.redshift_button, SIGNAL('clicked()'), self.on_z_update)
        #########################################
        
        ######################################
        # Open window/dialog to select/add reduction version:
        self.db_options_button = QPushButton("Set paths")
        self.connect(self.db_options_button, SIGNAL('clicked()'), self.on_db_options)
        ######################################
        
        ######################################
        # Layout with box sizers
        ######################################
        hbox1 = self.make_hbox_widget([self.lbl_maskNameBox, 
                    self.maskNameBox, self.query_mask_button],
                    stretch=0)
                    
        hbox2 = self.make_hbox_widget([self.lbl_objIDBox,
                    self.objIDBox, self.query_maskid_button],
                    stretch=0)
                    
        hbox25 = self.make_hbox_widget([self.query_all_masks_button],
                                stretch=0)
        
        hbox3 = self.make_hbox_widget([self.match_lbl, self.matches],
                    stretch=0)
        hbox4 = self.make_hbox_widget([self.prev_match_button, 
                                        self.next_match_button],
                                        stretch=0)

        hbox5 = self.make_hbox_widget([self.lbl_redshiftBox,
                    self.redshiftBox, 
                    self.redshift_button],
                    stretch=0)
        
        
        #####################################
        # redshift information
        hline_z = self.make_hline()
        
        
        self.lbl_z_1d, self.text_z_1d = self.make_redshift_info('1D', initval=self.z_mosfire_1d)
        self.lbl_z_spec, self.text_z_spec = self.make_redshift_info('spec', initval=self.z_spec)
        self.lbl_z_gris, self.text_z_gris = self.make_redshift_info('gris', initval=self.z_gris)
        self.lbl_z_phot, self.text_z_phot = self.make_redshift_info('phot', initval=self.z_phot)

        self.lbl_h, self.text_h = self.make_hmag_info(initval=self.h_mag)
        
        hbox_hmag = self.make_hbox_widget([self.lbl_h, self.text_h], stretch=2)
        
        hbox_z_1d = self.make_hbox_widget([self.lbl_z_1d, self.text_z_1d], stretch=2)
        hbox_z_spec = self.make_hbox_widget([self.lbl_z_spec, self.text_z_spec], stretch=2)
        hbox_z_gris = self.make_hbox_widget([self.lbl_z_gris, self.text_z_gris], stretch=2)
        hbox_z_phot = self.make_hbox_widget([self.lbl_z_phot, self.text_z_phot], stretch=2)
        
        vbox_z = self.make_vbox_layout([hbox_z_1d,
                            hbox_z_spec, hbox_z_gris, hbox_z_phot])
        
        vbox_hmag = self.make_vbox_layout([hbox_hmag])
                                
        hbox_z_h = self.make_hbox_layout([vbox_z, vbox_hmag], stretch=1)
        vbox_z_h = self.make_vbox_layout([hline_z, hbox_z_h])
        
        #####################################
        # Smoothing, masking options
        hline1 = self.make_hline()
        
        
        self.masksky_cb = QCheckBox("&Mask skylines")
        self.masksky_cb.setChecked(True)   # Temp; default: False
        self.connect(self.masksky_cb, SIGNAL('stateChanged(int)'), self.on_draw)
        
        #h_masksky = self.make_hbox_widget([self.masksky_cb], stretch=1)
        
        # Add quiescent lines:
        self.quilines_cb = QCheckBox("Quiescent lines&")
        self.quilines_cb.setChecked(False)
        self.connect(self.quilines_cb, SIGNAL('stateChanged(int)'), self.on_draw)
        h_masksky = self.make_hbox_widget([self.masksky_cb, self.quilines_cb], stretch=1)
        
        self.smooth_cb = QCheckBox("&Smooth")
        self.smooth_cb.setChecked(True)  # Temp; default: False
        self.connect(self.smooth_cb, SIGNAL('stateChanged(int)'), self.on_draw)
        
        self.smooth_lbl = QLabel(self)
        self.smooth_lbl.setText("# Pixels:")
        self.smooth_num = QLineEdit()
        self.smooth_num.setText("3")
        self.smooth_num.setFixedWidth(30)
        self.connect(self.smooth_num, SIGNAL('editingFinished ()'), self.on_draw)
        
        h_smooth = self.make_hbox_widget([self.smooth_cb, self.smooth_lbl, 
                        self.smooth_num], stretch=1)
        
        
        #vbox_mask = self.make_vbox_layout([hline1, h_masksky, h_smooth], spacing=5)
        vbox_mask = self.make_vbox_layout([hline1, h_masksky, h_smooth])
        
        #####################################
        # Current extracted object
        self.vbox_cur, self.current_info = self.make_current_extract(initprim=self.primID, initaper=self.aper_no, 
                                        initcols=self.obj_id_color)
        
        #####################################
        # Serendip IDs:
        self.vbox_ser, self.serendip_info = self.make_serendip_list(initlist=self.serendip_ids, 
                                        initcols=self.serendip_colors)
                                    
        
        
        #####################################
        # Legend
        
        hline2 = self.make_hline()
    
        leg_lbl = QLabel(self)
        leg_lbl.setText('Legend:')
        h_leg = self.make_hbox_widget([leg_lbl], stretch=1)
        
        h_red = self.make_line_leg('H&alpha;', 'red')
        h_ora = self.make_line_leg('[NII]', 'orange')
        h_mag = self.make_line_leg('[SII]', 'magenta')
        
        h_tea = self.make_line_leg('H&beta;', 'darkturquoise')
        h_yel = self.make_line_leg('[OIII]', 'yellow',line_lbl_wid = 30)
        h_gre = self.make_line_leg('[OII]', 'green')
        
        h_sgn = self.make_line_leg('MgB', 'mediumseagreen', line_lbl_wid=30)
        h_dor = self.make_line_leg('D4000', 'lightcoral', line_lbl_wid=40)
        h_sbl = self.make_line_leg('H&gamma', 'slateblue')
        h_pur = self.make_line_leg('H&delta', 'darkorchid')
        
        
    
        hbox_col_t = self.make_hbox_layout([h_red, h_ora, h_mag],stretch=3)
        hbox_col_b = self.make_hbox_layout([h_tea, h_yel, h_gre],stretch=3)
        hbox_col_r = self.make_hbox_layout([h_sgn, h_dor], stretch=2)
        hbox_col_rr = self.make_hbox_layout([h_sbl, h_pur],stretch=2)
        vbox_l = self.make_vbox_layout([hbox_col_t, hbox_col_b, 
                        hbox_col_r, hbox_col_rr],stretch=2)
        
        vbox_leg = self.make_vbox_layout([hline2, h_leg, vbox_l]) 
        
        # hbox_col_t = self.make_hbox_layout([h_red, h_ora, h_mag],stretch=3)
        # hbox_col_b = self.make_hbox_layout([h_tea, h_gre, h_yel],stretch=3)
        # vbox_l = self.make_vbox_layout([hbox_col_t, hbox_col_b],stretch=2)
        # vbox_leg = self.make_vbox_layout([hline2, vbox_l])
        
        #####################################
        # Extraction comments
        self.vbox_com, self.comment_info = self.make_comments_list()
        
        
        ######################################      
        hline3 = self.make_hline()
        hbox8 = self.make_hbox_widget([self.db_options_button],
                                        stretch=0)

        
        hbox01 = self.make_hbox_widget([self.canvas])
        hbox02 = self.make_hbox_widget([self.mpl_toolbar],stretch=1)
        vbox_canvas = self.make_vbox_layout([hbox01, hbox02])
        
        vbox_input1 = self.make_vbox_layout([hbox1, hbox2, hbox25], spacing=0)
        #vbox_input15 = self.make_vbox_layout([])
        vbox_input2 = self.make_vbox_layout([hbox3, hbox4])#, hbox5])
        vbox_input = self.make_vbox_layout([vbox_input1, vbox_input2])
        #vbox_input = self.make_vbox_layout([hbox1, hbox2, hbox3, hbox4, hbox5])


        hline_z_input = self.make_hline()
        
        vbox_r_layout = self.make_vbox_layout([vbox_input, hline_z_input, hbox5, 
                                self.vbox_cur, vbox_z_h, self.vbox_ser, vbox_leg, 
                                self.vbox_com, vbox_mask,  
                                hline3, hbox8], stretch=8)
                                
        # Scrollable?
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidgetResizable(True)
        vbox_r_widget = QWidget()
        vbox_r_widget.setLayout(vbox_r_layout)

        right_width = 260
        vbox_r_widget.setMinimumWidth(right_width)
        self.scrollArea.setMinimumWidth(right_width+18)
        
        self.scrollArea.setWidget(vbox_r_widget)
        vbox_r = QVBoxLayout()
        vbox_r.addWidget(self.scrollArea)
        
        
        
        hbox = self.make_hbox_layout([vbox_canvas, vbox_r],
                                    stretch=1)
   
        self.main_frame.setLayout(hbox)
        self.setCentralWidget(self.main_frame)
        
        # Initialize focus to the Mask entry:
        self.maskNameBox.setFocus()
    
    
    ############################################################################
    
    # # Define general drawing methods
    def on_draw(self):
        """ Redraws the figure
        """
        plotObject(self)
    

    ############################################################################
    # Query actions:
    
    def on_all_mask_query(self):
        print('querying all masks')
        
        query_str = None
        query = query_db(query_str)
        
        items = []  
        if query is not None:
                for q in query:
                  primaper_str = self.toPrimAper(str(q['maskname']), str(q['primaryID']), 
                            str(q['aperture_no']), obj_type=q['obj_type'])
                  items.append(str(primaper_str))
        
        self.match_list = items
            
        # Reset combo box:
        self.matches.clear()
        for l in self.match_list:
            self.matches.addItem(l)
    
    def on_mask_query(self):
        self.maskname = str(self.maskNameBox.text())
        
        print('querying mask:', self.maskname)
        
        query_str = "maskname = '{}'".format(self.maskname)
        query = query_db(query_str)
        
        # Update match list to give maskname too:
        items = []  
        if query is not None:
                for q in query:
                  primaper_str = self.toPrimAper(str(q['maskname']), str(q['primaryID']), 
                            str(q['aperture_no']), obj_type=q['obj_type'])
                  items.append(str(primaper_str))
        
        self.match_list = items
            
        # Reset combo box:
        self.matches.clear()
        for l in self.match_list:
            self.matches.addItem(l)
               
        
    def on_mask_id_button(self):
        # When the search button is pressed
        
        self.maskname = str(self.maskNameBox.text())
        if str(self.objIDBox.text()) is not '':
            try:
                 self.obj_id = np.int64(str(self.objIDBox.text()))
            except:
                 # Non-numerical input; star?
                 self.obj_id = np.int64(str(self.objIDBox.text())[1:])
             
            self.on_mask_id_query()
        else:
            print("% mosdef_dataviewer: Please specify maskname and object ID to search on mask+ID")
           
        
    def on_mask_id_query(self):
        ## Actually do the query here, 
        #       whether initiated by a search 
        
        print('querying mask, id:', self.maskname, self.obj_id)
        
        
        # Run the query
        query_str = "maskname = '{}' AND objID = {}".format(self.maskname, self.obj_id)
        query = query_db(query_str)
        
        # +++++++++++++++++++++++++++++++
        # Update object info
        query_good = 0
        if not type(query) == type(None):
            if len(query) == 1:
                query_good = 1
                
        self.query_good = query_good
        
        # +++++++++++++++++++++++++++++++
        # If the query returned items: 
        if query_good:
            # %%%%%%%%%%%%%%%%%%%%%%%
            # Update values
            self.field = query[0]['field']
            self.obj_id = query[0]['objID']
            self.primID = query[0]['primaryID']
            self.primID_v2 = query[0]['primaryIDv2']
            self.primID_v4 = query[0]['primaryIDv4']
            self.aper_no = query[0]['aperture_no']
            self.query_info = query[0]
                
            # Get info from a 2D header:
            spec2d_hdr = self.get_any_2d_hdr()
            if spec2d_hdr is not None:
                self.set_z_values(spec2d_hdr, aper_no=self.aper_no)
                self.z = self.set_initial_z()
            
            spec2d_hdr = None
            
            # Update comments:
            self.comment_info.setText(self.update_comments_list())
        
        # Redraw
        self.on_draw()
        
        # Update current object:
        self.current_info.setText(self.update_current_extract(initprim=self.primID, initaper=self.aper_no, 
                                        initcols=self.obj_id_color))
        
        # Update serendips:
        self.serendip_info.setText(self.update_serendip_list(initlist=self.serendip_ids, 
                        initcols=self.serendip_colors))
        

            

        
    
    def on_mask_prim_aper_query(self):
        ## Actually do the query here, 
        #       whether initiated by a search or one of the 
        #       dropdown menu options

        print('querying maskname, primID, aper_no:', self.maskname, self.primID, self.aper_no)

        # Run the query
        query_str = "maskname = '%s' AND primaryID = '%s' AND aperture_no = %s" % (self.maskname, self.primID, self.aper_no)
        query = query_db(query_str)

        # +++++++++++++++++++++++++++++++
        # Update object info
        query_good = 0
        if not type(query) == type(None):
            if len(query) == 1:
                query_good = 1

        self.query_good = query_good

        # +++++++++++++++++++++++++++++++
        # If the query returned items: 
        if query_good:
            # %%%%%%%%%%%%%%%%%%%%%%%
            # Update values
            self.field = query[0]['field']
            self.obj_id = query[0]['objID']
            self.primID = query[0]['primaryID']
            self.primID_v2 = query[0]['primaryIDv2']
            self.primID_v4 = query[0]['primaryIDv4']
            self.query_info = query[0]
            
            # Get info from a 2D header, if primary:
            spec2d_hdr = self.get_any_2d_hdr()
            if spec2d_hdr is not None:
                self.set_z_values(spec2d_hdr, aper_no=self.aper_no)
                self.z = self.set_initial_z()
        
            spec2d_hdr = None
            
            # Update comments:
            self.comment_info.setText(self.update_comments_list())

        # Redraw
        self.on_draw()
         
        # Update current object:
        self.current_info.setText(self.update_current_extract(initprim=self.primID, initaper=self.aper_no, 
                                        initcols=self.obj_id_color))
                
        # Update serendips:
        self.serendip_info.setText(self.update_serendip_list(initlist=self.serendip_ids, 
                        initcols=self.serendip_colors))

        
    # Method for dealing with changes to redshift on plot.
    def on_z_update(self):
        try:
            self.z = np.float64(str(self.redshiftBox.text()))
            # Update the drawing.
            self.on_draw()
        except:
            # Non-numerical input
            self.z = -1.
                   
    
    ######################################
    # ComboBox setup:
    def initComboBox(self, list):
        combo = QComboBox(self)
        combo.setMinimumWidth(150)
        for l in list:
            combo.addItem(l)

        combo.currentIndexChanged['QString'].connect(self.onSelectMatch)
        return combo
        
    # Helper functions:
    def toPrimAper(self, maskname, primID, aper_no, obj_type='G'):
        if aper_no == '1':
            primaper_str = str(primID)
        else:
            primaper_str = "{}.{}".format(str(primID),str(aper_no))
        
        if obj_type == 'S':
            primaper_str = 'S{}'.format(primaper_str)
        
        return "{}.{}".format(maskname, primaper_str)
        
    def fromPrimAper(self, primaper_str):
        splt = re.split(r'\.', str(primaper_str).strip())
        # UPDATE:
        # Update match list to give maskname too:
        
        ind_mask = 0
        ind_id = 1
        ind_aper = 2
        num_prim = 2
        num_serendip = 3
        
        ##  old:
        # ind_id = 0
        # ind_aper = 1
        # num_prim = 1
        # num_serendip = 2
        
        #print "splt=", splt
        if len(splt) == num_prim:
            if splt[ind_id][0] == 'S':
                splt_tmp = splt[ind_id][1:]
            else:
                splt_tmp = splt[ind_id]
            self.maskname = splt[ind_mask]
            self.primID = splt_tmp
            self.aper_no = 1
        elif len(splt) == num_serendip:
            if splt[ind_id][0] == 'S':
                splt_tmp = splt[ind_id][1:]
            else:
                splt_tmp = splt[ind_id]
            self.maskname = splt[ind_mask]
            self.primID = splt_tmp
            self.aper_no = splt[ind_aper]
        else:
            # Not proper format: reset values
            self.primID = -99
            self.aper_no = -1
            
        return None
    
    def onSelectMatch(self, text):
        # This is where you would hook up to the redraw case.
        self.fromPrimAper(text)
        
        # Redoes the drawing, etc.
        self.on_mask_prim_aper_query()
        
            
    def prev_match(self):
        if self.matches.currentIndex() >= 1:
            ind = self.matches.currentIndex()-1
            self.matches.setCurrentIndex(ind)
            # Execute on select match with the new item.
            #self.onSelectMatch(self.matches.currentText())
        else:
            pass
        
    def next_match(self):
        if self.matches.currentIndex() <= len(self.match_list)-2:
            ind = self.matches.currentIndex()+1
            self.matches.setCurrentIndex(ind)
            # Execute on select match with the new item.
            #self.onSelectMatch(self.matches.currentText())
        else:
            pass

    
    ##########################################################################
    # Open window/dialog to select/add reduction version:
    def on_db_options(self):
    
        dlg = ChangeDBinfo()
        if dlg.exec_():
            dlg.writePaths()
            print('********************************')
            print('Writing new MOSDEF DV database')
            write_cat_db()
            print('Finished writing new DV database')
            print('********************************')
    
    ##########################################################################

    
    # def create_status_bar(self):
    #     self.status_text = QLabel("Reduction v"+self.current_db_version)
    #     self.statusBar().addWidget(self.status_text, 1)
    
    
    ##########################################################################
    # Read-in data methods:
    def set_z_values(self, spec2d_hdr, aper_no=1):
        
        self.z_mosfire_1d = read_bmep_redshift_slim(self.maskname, self.primID, self.aper_no)
        
        if aper_no == 1:
            # Read in a parent cat:
            tdhst_vers = get_tdhst_vers(spec2d_hdr)
            # Get match:
            parent_cat = read_parent_cat(vers=tdhst_vers, field=self.field)
            
            try:
                wh_match = np.where(parent_cat['ID'] == np.int64(self.primID))[0][0]
                # print "wh_match=", wh_match
                # print "parent_cat['Z_SPEC'][wh_match]=", parent_cat['Z_SPEC'][wh_match]
                # print "parent_cat['Z_GRISM'][wh_match]=", parent_cat['Z_GRISM'][wh_match]
            
                # Primary object
                try:
                    zspec = parent_cat['Z_SPEC'][wh_match]
                    if ((zspec == -1.) & (parent_cat['EXT_ZSPEC'][wh_match] > 0.)):
                        zspec = parent_cat['EXT_ZSPEC'][wh_match]
                    self.z_spec = zspec
                    #self.z_spec = spec2d_hdr['z_spec'.upper()]
                except:
                    self.z_spec = -1.
            
                try:
                    self.z_gris = parent_cat['Z_GRISM'][wh_match]
                    #self.z_gris = spec2d_hdr['z_grism'.upper()]
                except:
                    self.z_gris = -1.
            
                try:
                    self.z_phot = parent_cat['Z_PHOT'][wh_match]
                    #self.z_phot = spec2d_hdr['z_phot'.upper()]
                except:
                    self.z_phot = -1.
            except:
                self.z_spec = -1.
                self.z_gris = -1.
                self.z_phot = -1.
        else:
            # Non-primary object -- no 3D-HST redshift from headers
            self.z_spec = -1.
            self.z_gris = -1.
            self.z_phot = -1.
            
        
        # Set z values:
        self.text_z_1d.setText(str(self.z_mosfire_1d))
        self.text_z_spec.setText(str(self.z_spec))
        self.text_z_gris.setText(str(self.z_gris))
        self.text_z_phot.setText(str(self.z_phot))
            
        # Set H mag value:
        try:
            self.h_mag = spec2d_hdr['magnitud'.upper()]
        except:
            self.h_mag = -1.
            
        self.text_h.setText(str(self.h_mag))
            
        return None   
            
    def set_initial_z(self):
        if self.z_mosfire_1d > 0.:
            z = self.z_mosfire_1d
        elif self.z_spec > 0.:
            z = self.z_spec
        elif self.z_gris > 0.:
            z = self.z_gris
        else:
            z = self.z_phot
            
        # Set z value in textbox:
        self.redshiftBox.setText(str(z))
        
        return z
        
    def get_any_2d_hdr(self):
        # Get info from a 2D header -- info that is the same between *any* of the 
        #       2D files, ie 3D-HST redshifts, 3D-HST version...
        flag = 0
        bands = ['K', 'H', 'J', 'Y']
        i = 0
        while flag == 0:
            band = bands[i]
            
            try:
                spec2d, spec2d_hdr = read_spec2d(self.query_info['spec2d_file_'+band.lower()])

                if spec2d is not None:
                    flag = 1
                else:
                    i += 1
            except:
                
                i += 1
                
                if i >= len(bands):
                    # Break the while loop in the case of no match
                    spec2d_hdr = None
                    flag = 1
        
        spec2d = None
    
        return spec2d_hdr

##########################################################################

def launch_DataViewer():
    """
    Launch a MOSDEF DataViewer instance.
    """
    app = QApplication([sys.argv[0]])
    
    screen_rect = app.desktop().screenGeometry()
    width, height = screen_rect.width(), screen_rect.height()
    
            
    
    form = DataViewer(screen_res = [width, height])
    form.show()
    app.exec_()


if __name__ == "__main__":
    launch_DataViewer()

