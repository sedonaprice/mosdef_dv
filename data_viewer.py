###

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

import sys, os
import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import numpy as np

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

from viewer_lib.database import write_cat_db, query_db
from viewer_lib.viewer_io import read_spec2d, read_bmep_redshift_slim
from viewer_lib.database_options import ChangeDBinfo

from viewer_lib.plot_object import *
#   Properly input all the functions when you have them written.

from astropy import wcs

class NavigationToolbar(NavigationToolbar):
    
    # only display the buttons we need
    #spacer = NavigationToolbar.toolitems[3]
    toolitems = [t for t in NavigationToolbar.toolitems if
                 t[0] in ('Home', 'Pan', 'Zoom', 'Save')]
    #toolitems = []
    #toolitems.append(toolitems_init[0])
    #toolitems.append(spacer)
    #for i in xrange(1,3):
    #    toolitems.append(toolitems_init[i])
    #toolitems.append(spacer)
    #toolitems.append(toolitems_init[3])
    #toolitems = tuple(toolitems)


class DataViewer(QMainWindow):
    def __init__(self, parent=None, screen_res=None):
        QMainWindow.__init__(self, parent)
        
        # Set default size of the window:
        if screen_res is not None:
            mult = 1.3
            if screen_res[1]*mult < screen_res[0]:
                screen_res[0] = screen_res[1]*mult
            elif screen_res[0]/mult < screen_res[1]:
                screen_res[1] = screen_res[0]/mult
                
            self.setGeometry(screen_res[0], screen_res[1], 
                    screen_res[0], screen_res[1])
        
        self.setWindowTitle('MOSDEF Data Viewer')
        
        # Working directory: where you are running it from
        #self.run_dir = os.getcwd()

        # Initial values:
        self.maskname = '-----'
        self.obj_id = -99
        self.primID = -99
        self.aper_no = -1
        self.z = -1.  # Which value should this be set as?
        
        
        self.z_mosfire_1d = None
        self.z_spec = None
        self.z_gris = None
        self.z_phot = None
        self.h_mag = None
        
        # self.z_mosfire_1d = -42.
        # self.z_spec = -42.
        # self.z_gris = -42.
        # self.z_phot = -42.
        # self.h_mag = -28.
        
        
        # No initial query
        self.query_good = 0
        
        # Create things:
        self.create_main_frame(screen_res=screen_res)

        # Initialize plot
        self.on_draw()
    
    
    ############################################################################
    
    def create_main_frame(self, screen_res=None):
        self.main_frame = QWidget()
        
        # Create the mpl Figure and FigCanvas objects. 
        self.dpi = 100.
        
        # Set it larger than it ever should be:
        self.fig = Figure((20.0, 20.0), dpi=self.dpi)
        
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        # Create the navigation toolbar, tied to the canvas
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        ## Add a button for line centroiding here??
        
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
                    self.objIDBox, 
                    self.query_maskid_button],
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
        
        vbox_z = self.make_vbox_layout([hbox_z_1d,hbox_z_spec, hbox_z_gris, hbox_z_phot])
        
        vbox_hmag = self.make_vbox_layout([hbox_hmag])
                                
        hbox_z_h = self.make_hbox_layout([vbox_z, vbox_hmag], stretch=1)
        vbox_z_h = self.make_vbox_layout([hline_z, hbox_z_h])
        
        #####################################
        # Smoothing, masking options
        hline1 = self.make_hline()
        
        
        self.masksky_cb = QCheckBox("&Mask skylines")
        self.masksky_cb.setChecked(True)   # Temp; default: False
        self.connect(self.masksky_cb, SIGNAL('stateChanged(int)'), self.on_draw)
        
        h_masksky = self.make_hbox_widget([self.masksky_cb], stretch=1)
        
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
        
        
        vbox_mask = self.make_vbox_layout([hline1, h_masksky, h_smooth])
        
        
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
        
        vbox_ll = self.make_vbox_layout([h_red, h_ora, h_mag])
        vbox_rl = self.make_vbox_layout([h_tea, h_yel, h_gre])
        hbox_l = self.make_hbox_layout([vbox_ll, vbox_rl],stretch=2)
        
        vbox_leg = self.make_vbox_layout([hline2, h_leg, hbox_l]) 
        
        
        ######################################      
        hline3 = self.make_hline()
        hline4 = self.make_hline()
        hbox8 = self.make_hbox_widget([self.db_options_button],
                                        stretch=0)

        
        hbox01 = self.make_hbox_widget([self.canvas])
        hbox02 = self.make_hbox_widget([self.mpl_toolbar],stretch=1)
        vbox_canvas = self.make_vbox_layout([hbox01, hbox02])
        
        vbox_input = self.make_vbox_layout([hbox1, hbox2, hbox3, hbox4, hbox5])

        vbox_r = self.make_vbox_layout([vbox_input, vbox_z_h, vbox_leg, 
                                vbox_mask, hline3, hline4, hbox8], stretch=5)
        
        hbox = self.make_hbox_layout([vbox_canvas, vbox_r],
                                    stretch=1)
   
        self.main_frame.setLayout(hbox)
        self.setCentralWidget(self.main_frame)
    
    
    ############################################################################
    
    # # Define general drawing methods
    def on_draw(self):
        """ Redraws the figure
        """
        plotObject(self)
        #self.plotObject()
        
        
    # def plotObject(self):
    #     return plotObject(self)
    
    #def plotBand(self,band='H'):
    #    return plotBand(self,band=band)
    

        
    
    ############################################################################
    # Query actions:
    
    def on_mask_query(self):
        self.maskname = str(self.maskNameBox.text())
        
        print 'querying mask:', self.maskname
        
        query_str = "maskname = '%s'" % (self.maskname)
        query = query_db(query_str)
        
        items = []  
        if query is not None:
                for q in query:
                  primaper_str = self.toPrimAper(str(q['primaryID']), str(q['aperture_no']))
                  items.append(str(primaper_str))
        
        self.match_list = items
            
        # Reset combo box:
        self.matches.clear()
        for l in self.match_list:
            self.matches.addItem(l)

        
        
    def on_mask_id_button(self):
        # When the search button is pressed
        
        self.maskname = str(self.maskNameBox.text())
        try:
             self.obj_id = np.int64(str(self.objIDBox.text()))
        except:
             # Non-numerical input
             self.obj_id = str(self.objIDBox.text())
             
        self.on_mask_id_query()

        
        
    def on_mask_id_query(self):
        ## Actually do the query here, 
        #       whether initiated by a search or one of the 
        #       dropdown menu options
        
        print 'querying mask, id:', self.maskname, self.obj_id
        
        # Run the query
        query_str = "maskname = '%s' AND objID = %s" % (self.maskname, self.obj_id)
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
            self.primID = query[0]['primaryID']
            self.aper_no = query[0]['aperture_no']
            
            self.query_info = query[0]
                
            # Get info from a 2D header:
            spec2d_hdr = self.get_any_2d_hdr()
            if spec2d_hdr is not None:
                self.set_z_values(spec2d_hdr, aper_no=self.aper_no)
                
                self.z = self.set_initial_z()
            
            spec2d_hdr = None
        
        # Redraw
        self.on_draw()
        
    
    def on_mask_prim_aper_query(self):
        ## Actually do the query here, 
        #       whether initiated by a search or one of the 
        #       dropdown menu options

        print 'querying maskname, primID, aper_no:', self.maskname, self.primID, self.aper_no

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
            self.obj_id = query[0]['objID']

            self.query_info = query[0]
            
            # Get info from a 2D header, if primary:
            spec2d_hdr = self.get_any_2d_hdr()
            if spec2d_hdr is not None:
                self.set_z_values(spec2d_hdr, aper_no=self.aper_no)
                
                self.z = self.set_initial_z()
        
            spec2d_hdr = None



        # Redraw
        self.on_draw()
        
        
        
        
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
        for l in list:
            combo.addItem(l)

        combo.currentIndexChanged['QString'].connect(self.onSelectMatch)
        return combo
        
    # Helper functions:
    def toPrimAper(self, primID, aper_no):
        if aper_no == '1':
            primaper_str = str(primID)
        else:
            primaper_str = str(primID)+'.'+str(aper_no)
        
        return primaper_str
        
    def fromPrimAper(self, primaper_str):
        splt = re.split(r'\.', str(primaper_str).strip())
        if len(splt) == 1:
            self.primID = splt[0]
            self.aper_no = 1
        elif len(splt) == 2:
            self.primID = splt[0]
            self.aper_no = splt[1]
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
            print '********************************'
            print 'Writing new MOSDEF DV database'
            write_cat_db()
            print 'Finished writing new DV database'
            print '********************************'
    
    ##########################################################################
    # Layout setup:
    def make_hbox_widget(self, items, stretch=-1):
        hbox0 = QHBoxLayout()
        for i,w in enumerate(items):
            if stretch == i:
                hbox0.addStretch(1)
            hbox0.addWidget(w)
            hbox0.setAlignment(w, Qt.AlignVCenter)
        # Stretch at end?
        if stretch == i+1:
            hbox0.addStretch(1)
        return hbox0
    
    def make_hbox_layout(self, layouts, stretch=-1):
        hbox0 = QHBoxLayout()
        if stretch == 0:
            hbox0.addStretch(1)
        for i,l in enumerate(layouts):
            if i == stretch:
                hbox0.addStretch(1)
            hbox0.addLayout(l)
        # Stretch at end?
        if stretch == i+1:
            hbox0.addStretch(1)
        return hbox0
        
    def make_vbox_widget(self, items, stretch=-1):
         vbox0 = QVBoxLayout()
         for i, w in enumerate(items):
             if stretch == i:
                 vbox0.addStretch(1)
             vbox0.addWidget(w)
             vbox0.setAlignment(w, Qt.AlignHCenter)
         # Stretch at end?
         if stretch == i+1:
             vbox0.addStretch(1)
         return vbox0

    def make_vbox_layout(self, layouts, stretch=-1):
        vbox0 = QVBoxLayout()
        if stretch == 0:
            vbox0.addStretch(1)
        for i,l in enumerate(layouts):
            if i == stretch:
                    vbox0.addStretch(1)
            vbox0.addLayout(l)
        # Stretch at end?
        if stretch == i+1:
            vbox0.addStretch(1)
        return vbox0
    
    
    def make_line_leg(self, line_name, color, line_lbl_wid=25):
        line = QFrame()
        line.setFrameStyle(QFrame.HLine)
        line.setFixedWidth(20)
        line.setLineWidth(2)
        line.setStyleSheet('color: '+color)
        
        lbl = QLabel()
        lbl.setTextFormat(Qt.RichText)
        lbl.setText(line_name)
        lbl.setFixedWidth(line_lbl_wid)
        h = self.make_hbox_widget([line, lbl], stretch=2)
        
        return h
    
    def make_hline(self):
        line = QFrame()
        line.setFrameStyle(QFrame.HLine | QFrame.Sunken)
        line.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        hline = self.make_hbox_widget([line])
        
        return hline
    
    def make_redshift_info(self, subscript, initval=None):   
        lbl = QLabel("z<sub>"+subscript+"</sub> =")
        lbl.setTextFormat(Qt.RichText)
        
        text = QLabel()
        if initval is not None:
            text.setText(str(initval))
        
        return lbl, text
        
    def make_hmag_info(self, initval=None):   
        lbl = QLabel("H =")
        lbl.setTextFormat(Qt.RichText)

        text = QLabel()
        if initval is not None:
            text.setText(str(initval))

        return lbl, text
    
    # def create_status_bar(self):
    #     self.status_text = QLabel("Reduction v"+self.current_db_version)
    #     self.statusBar().addWidget(self.status_text, 1)
    
    
    ##########################################################################
    # Read-in data methods:
    def set_z_values(self, spec2d_hdr, aper_no=1):
        # How to set z_mosfire_1d:
        #self.z_mosfire_1d = -42.
        self.z_mosfire_1d = read_bmep_redshift_slim(self.primID, self.aper_no)
        
        if aper_no == 1:
            # Primary object
            try:
                self.z_spec = spec2d_hdr['z_spec'.upper()]
            except:
                self.z_spec = -1.
            
            try:
                self.z_gris = spec2d_hdr['z_grism'.upper()]
            except:
                self.z_gris = -1.
            
            try:
                self.z_phot = spec2d_hdr['z_phot'.upper()]
            except:
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
        if self.z_mosfire_1d >= 0.:
            z = self.z_mosfire_1d
        elif self.z_spec >= 0.:
            z = self.z_spec
        elif self.z_gris >= 0.:
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

def main():
    app = QApplication(sys.argv)
    
    screen_rect = app.desktop().screenGeometry()
    width, height = screen_rect.width(), screen_rect.height()
    
    form = DataViewer(screen_res = [width, height])
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()

