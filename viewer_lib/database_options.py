from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys, os


class DB_Options_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowTitle('Database Options')
        #Dialog.resize(508, 300)
        
        self.layout = QVBoxLayout()

        lbl_1d = QLabel(self)
        lbl_1d.setText('1D spec dir:')
        dir_1d = QLabel(self)
        dir_1d.setText(os.getenv('MOSDEF_DV_1D'))
        hbox1 = self.make_hbox_widget([lbl_1d, dir_1d])
        
        lbl_2d = QLabel(self)
        lbl_2d.setText('2D spec dir:')
        dir_2d = QLabel(self)
        dir_2d.setText(os.getenv('MOSDEF_DV_2D'))
        hbox2 = self.make_hbox_widget([lbl_2d, dir_2d])
        
        lbl_meas = QLabel(self)
        lbl_meas.setText('Measurements dir:')
        dir_meas = QLabel(self)
        dir_meas.setText(os.getenv('MOSDEF_DV_MEAS'))
        hbox3 = self.make_hbox_widget([lbl_meas, dir_meas])
        
        lbl_db = QLabel(self)
        lbl_db.setText('Database dir:')
        dir_db = QLabel(self)
        dir_db.setText(os.getenv('MOSDEF_DV_DB'))
        hbox4 = self.make_hbox_widget([lbl_db, dir_db])
        
        
        self.layout.addLayout(hbox1)
        self.layout.addLayout(hbox2)
        self.layout.addLayout(hbox3)
        self.layout.addLayout(hbox4)
        
        
        
        # Add stretch to separate the current selection from the "add new DB"
        self.layout.addStretch(1)
        
        # Add spacer:
        self.spacer = QLabel(self)
        self.spacer.setText('****************')
        hbox5 = self.make_hbox_widget([self.spacer],stretch=0)
        self.layout.addLayout(hbox5)
        
        # Add info:
        self.write = QLabel(self)
        self.write.setText('Write/rewrite DB?')
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

    

if __name__ == "__main__":
    app = QApplication(sys.argv)


    dlg = ChangeDBinfo()
    if dlg.exec_():
        pass