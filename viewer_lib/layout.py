import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class DV_Layout(object):
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
        lbl.setMargin(0)
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

    