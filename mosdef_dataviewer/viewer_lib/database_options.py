# ###################
# Licensed under the MIT license. See LICENSE
# ###################

from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from PyQt5.QtWidgets import *
import sys, os

import pandas as pd
from viewer_io import read_paths, write_paths

class DB_Options_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowTitle('Set paths')
        #Dialog.resize(508, 300)
        
        self.layout = QVBoxLayout()

        lbl_1d = QLabel(self)
        lbl_1d.setText('1D spec dir:')
        self.dir_1d = QLineEdit(self)  # MOSDEF_DV_1D
        hbox1 = self.make_hbox_widget([lbl_1d, self.dir_1d])
        
        lbl_2d = QLabel(self)
        lbl_2d.setText('2D spec dir:')
        self.dir_2d = QLineEdit(self) # MOSDEF_DV_2D
        hbox2 = self.make_hbox_widget([lbl_2d, self.dir_2d])
        
        lbl_meas = QLabel(self)
        lbl_meas.setText('Measurements dir:')
        self.dir_meas = QLineEdit(self) # MOSDEF_DV_MEAS
        hbox3 = self.make_hbox_widget([lbl_meas, self.dir_meas])
        
        lbl_parent = QLabel(self)
        lbl_parent.setText('Parent cat dir:')
        self.dir_parent = QLineEdit(self) # MOSDEF_DV_PARENT
        hbox35 = self.make_hbox_widget([lbl_parent, self.dir_parent])
        
        
        lbl_pstamp = QLabel(self)
        lbl_pstamp.setText('Pstamp dir:')
        self.dir_pstamp = QLineEdit(self) # MOSDEF_DV_PSTAMP
        hbox4 = self.make_hbox_widget([lbl_pstamp, self.dir_pstamp])
        
        lbl_bmep_z = QLabel(self)
        lbl_bmep_z.setText('BMEP redshift dir:')
        self.dir_bmep_z = QLineEdit(self)
        hbox5 = self.make_hbox_widget([lbl_bmep_z, self.dir_bmep_z])
        
        lbl_tdhst_cat = QLabel(self)
        lbl_tdhst_cat.setText('3D-HST cat dir:')
        self.dir_tdhst_cat = QLineEdit(self)
        hbox6 = self.make_hbox_widget([lbl_tdhst_cat, self.dir_tdhst_cat])
        
        lbl_EXTRA_1D_END = QLabel(self)
        lbl_EXTRA_1D_END.setText('Extra end for 1D spectrum (blank for raw extraction):')
        self.EXTRA_1D_END = QLineEdit(self)
        hbox7 = self.make_hbox_widget([lbl_EXTRA_1D_END, self.EXTRA_1D_END])
        
        
        # Set min widths:
        lbl_wid = 120
        lbl_1d.setMinimumWidth(lbl_wid)
        lbl_2d.setMinimumWidth(lbl_wid)
        lbl_meas.setMinimumWidth(lbl_wid)
        lbl_parent.setMinimumWidth(lbl_wid)
        lbl_pstamp.setMinimumWidth(lbl_wid)
        lbl_bmep_z.setMinimumWidth(lbl_wid)
        lbl_tdhst_cat.setMinimumWidth(lbl_wid)
        lbl_EXTRA_1D_END.setMinimumWidth(lbl_wid)
        
        lbl_1d.setAlignment(Qt.AlignRight)
        lbl_2d.setAlignment(Qt.AlignRight)
        lbl_meas.setAlignment(Qt.AlignRight)
        lbl_parent.setAlignment(Qt.AlignRight)
        lbl_pstamp.setAlignment(Qt.AlignRight)
        lbl_bmep_z.setAlignment(Qt.AlignRight)
        lbl_tdhst_cat.setAlignment(Qt.AlignRight)
        lbl_EXTRA_1D_END.setAlignment(Qt.AlignRight)
        
        # Set min widths:
        min_wid = 500
        self.dir_1d.setMinimumWidth(min_wid)
        self.dir_2d.setMinimumWidth(min_wid)
        self.dir_meas.setMinimumWidth(min_wid)
        self.dir_parent.setMinimumWidth(min_wid)
        self.dir_pstamp.setMinimumWidth(min_wid)
        self.dir_bmep_z.setMinimumWidth(min_wid)
        self.dir_tdhst_cat.setMinimumWidth(min_wid)
        self.EXTRA_1D_END.setMinimumWidth(min_wid)
        
        # Set initial text values, if there is already a paths file.
        path_info = read_paths()
        labels = ['MOSDEF_DV_1D', 'MOSDEF_DV_2D', 
                'MOSDEF_DV_MEAS', 'MOSDEF_DV_PARENT', 'MOSDEF_DV_PSTAMP',
                'MOSDEF_DV_BMEP_Z','TDHST_CAT', 'EXTRA_1D_END']
        boxes = [self.dir_1d, self.dir_2d, 
                self.dir_meas, self.dir_parent, self.dir_pstamp,
                self.dir_bmep_z, self.dir_tdhst_cat, self.EXTRA_1D_END]
        if path_info is not None:
            for i in xrange(len(labels)):
                try:
                    path = path_info['path'][path_info['label']==labels[i]].values[0]
                    boxes[i].setText(str(path))
                except:
                    pass
                
        
        self.layout.addLayout(hbox1)
        self.layout.addLayout(hbox2)
        self.layout.addLayout(hbox3)
        self.layout.addLayout(hbox35)
        self.layout.addLayout(hbox4)
        self.layout.addLayout(hbox5)
        self.layout.addLayout(hbox6)
        self.layout.addLayout(hbox7)
        
        
        
        # Add stretch to separate the current selection from the "add new DB"
        self.layout.addStretch(1)
        
        # Add spacer:
        self.spacer = QLabel(self)
        self.spacer.setText('****************')
        hbox5 = self.make_hbox_widget([self.spacer],stretch=0)
        self.layout.addLayout(hbox5)
        
        # Add info:
        self.write = QLabel(self)
        self.write.setText('Update paths, write DB')
        hbox6 = self.make_hbox_widget([self.write], stretch=0)
        self.layout.addLayout(hbox6)
        
        # Buttons
        self.button_box = QHBoxLayout()
        self.button_box.addStretch(1)
        
        self.buttons = QDialogButtonBox(Dialog)
        self.buttons.setOrientation(Qt.Horizontal)
        self.buttons.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        
        self.button_box.addWidget(self.buttons)
        
        self.layout.addLayout(self.button_box)
        
        self.setLayout(self.layout)
        
        QObject.connect(self.buttons, SIGNAL("accepted()"), Dialog.accept)
        QObject.connect(self.buttons, SIGNAL("rejected()"), Dialog.reject)
        QMetaObject.connectSlotsByName(Dialog)


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

class ChangeDBinfo(QDialog, DB_Options_Dialog):
    def __init__(self, parent=None):
        QDialog.__init__(self,parent)
        self.setupUi(self)

    def writePaths(self):
        # Write the paths out to the file.
        MOSDEF_DV_1D = str(self.dir_1d.text())
        MOSDEF_DV_2D = str(self.dir_2d.text())
        MOSDEF_DV_MEAS = str(self.dir_meas.text())
        MOSDEF_DV_PARENT = str(self.dir_parent.text())
        MOSDEF_DV_PSTAMP = str(self.dir_pstamp.text())
        MOSDEF_DV_BMEP_Z = str(self.dir_bmep_z.text())
        TDHST_CAT = str(self.dir_tdhst_cat.text())
        EXTRA_1D_END = str(self.EXTRA_1D_END.text())
        
        labels = ['MOSDEF_DV_1D', 'MOSDEF_DV_2D', 
                'MOSDEF_DV_MEAS', 'MOSDEF_DV_PARENT', 'MOSDEF_DV_PSTAMP',
                'MOSDEF_DV_BMEP_Z', 'TDHST_CAT', 'EXTRA_1D_END']
                
        paths = [MOSDEF_DV_1D, MOSDEF_DV_2D, 
                MOSDEF_DV_MEAS, MOSDEF_DV_PARENT, 
                MOSDEF_DV_PSTAMP,
                MOSDEF_DV_BMEP_Z, TDHST_CAT, EXTRA_1D_END]
                
        for i,p in enumerate(paths):
            if p == '':
                paths[i] = 'not_set'
                
        df = pd.DataFrame({'label': labels,
                            'path': paths})
                            
        write_paths(df)
        
        return None
    

if __name__ == "__main__":
    app = QApplication(sys.argv)

    dlg = ChangeDBinfo()
    if dlg.exec_():
        dlg.writePaths()
        #pass
