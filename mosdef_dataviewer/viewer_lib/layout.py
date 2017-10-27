# ###################
# Licensed under the MIT license. See LICENSE.rst
# ###################

import sys, os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from viewer_io import read_spec1d_comments

default_spacing = 8

class DV_Layout(object):
    # Layout setup:
    def make_hbox_widget(self, items, stretch=-1, spacing=default_spacing):
        hbox0 = QHBoxLayout()
        hbox0.setSpacing(spacing)
        for i,w in enumerate(items):
            if stretch == i:
                hbox0.addStretch(1)
            hbox0.addWidget(w)
            hbox0.setAlignment(w, Qt.AlignVCenter)
        # Stretch at end?
        if stretch == i+1:
            hbox0.addStretch(1)
        return hbox0
    
    def make_hbox_layout(self, layouts, stretch=-1, spacing=default_spacing):
        hbox0 = QHBoxLayout()
        hbox0.setSpacing(spacing)
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
        
    def make_vbox_widget(self, items, stretch=-1, spacing=default_spacing):
         vbox0 = QVBoxLayout()
         vbox0.setSpacing(spacing)
         for i, w in enumerate(items):
             if stretch == i:
                 vbox0.addStretch(1)
             vbox0.addWidget(w)
             vbox0.setAlignment(w, Qt.AlignHCenter)
         # Stretch at end?
         if stretch == i+1:
             vbox0.addStretch(1)
         return vbox0

    def make_vbox_layout(self, layouts, stretch=-1, spacing=default_spacing):
        vbox0 = QVBoxLayout()
        vbox0.setSpacing(spacing)
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
    
    
    def make_line_leg(self, line_name, color, line_lbl_wid=25, spacing=default_spacing):
        line = QFrame()
        line.setFrameStyle(QFrame.HLine)
        line.setFixedWidth(20)
        line.setLineWidth(2)
        line.setStyleSheet('color: '+color)
        
        lbl = QLabel()
        lbl.setTextFormat(Qt.RichText)
        lbl.setText(line_name)
        lbl.setFixedWidth(line_lbl_wid)
        h = self.make_hbox_widget([line, lbl], stretch=2, spacing=spacing)
        
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

    def make_comments_list(self):
        hline_comments = self.make_hline()
        
        vbox_com = QVBoxLayout()
        vbox_com.setSpacing(default_spacing)
        
        vbox_com.addLayout(hline_comments)

        str_long = self.update_comments_list()
        
        com_lbl = QLabel(self)
        com_lbl.setWordWrap(True)
        com_lbl.setText(str_long)
        h_com = self.make_hbox_widget([com_lbl], stretch=1)
        vbox_com.addLayout(h_com)
        vbox_com.setAlignment(h_com, Qt.AlignHCenter)
        
        
        hline_com = self.make_hline()
        vbox_com.addLayout(hline_com)
                
        vbox_com.addStretch(1)
        vbox_com.addSpacing(5)
        
        return vbox_com, com_lbl
        
    def update_comments_list(self):
        if self.query_good == 1:
            bands = ['K', 'H', 'J', 'Y']

            comments_list = []
            for band in bands:
                try:
                    spec1d_comments = \
                        read_spec1d_comments(self.query_info['spec1d_file_'+band.lower()], band)
                    if len(spec1d_comments) > 0:
                        comments_list.extend(spec1d_comments)
                except:
                    pass

            if len(comments_list) > 0:
                # Convert this to one string, with carriage returns between lines.
                str_long = ''
                for ii, com in enumerate(comments_list):
                    str_long = str_long+com
                    if ii < len(comments_list)-1:
                        str_long = str_long+'\n'
                    
                return str_long
            else:
                return ''
        else:
            return ''
            
    def make_current_extract(self, initprim=None, initaper=None, initcols=None):
        hline_current_extract = self.make_hline()
        
        lbl = QLabel("Extracted object:")
        lbl.setTextFormat(Qt.RichText)
        
        text = QLabel()
        text.setTextFormat(Qt.RichText)
        text.setWordWrap(True)
        
        str_long = self.update_current_extract(initprim=initprim, initaper=initaper, initcols=initcols)
        text.setText(str_long)
        
        hbox_cur = self.make_hbox_widget([text], stretch=1)
        h_lbl = self.make_hbox_widget([lbl], stretch=1)
        vbox_cur = self.make_vbox_layout([hline_current_extract, h_lbl, hbox_cur])
        
        return vbox_cur, text
            
    def make_serendip_list(self, initlist=None, initcols=None):
        hline_serendip = self.make_hline()
        
        lbl = QLabel("Objects in/near slit:")
        lbl.setTextFormat(Qt.RichText)
        
        text = QLabel()
        text.setTextFormat(Qt.RichText)
        text.setWordWrap(True)
        
        str_long = self.update_serendip_list(initlist=initlist, initcols=initcols)
        text.setText(str_long)
        
        hbox_ser = self.make_hbox_widget([text], stretch=1)
        h_lbl = self.make_hbox_widget([lbl], stretch=1)
        vbox_ser = self.make_vbox_layout([hline_serendip, h_lbl, hbox_ser])
        
        return vbox_ser, text
        
    def make_serendip_markup(self, text=None, color=None):
        #<span style="color:#aa0000;">TextLabel</span>
        if (color == 'yellow') or (color == 'cyan'):
            markup = '<span style="color:'+color
            #markup = markup+'; background-color:DimGray">'+text+'</span>'
            markup = '<span style="color:'+color+'">'+text+'</span>'
        else:
            markup = '<span style="color:'+color+'">'+text+'</span>'
        #markup = '<color='+color+'>'+text+'</color>'
        return markup
        
        
        
    def update_current_extract(self, initprim=None, initaper=None,initcols=None):
        if ((initprim is not None) & (initprim != -99)):
            if initaper > 1:
                initlist = str(initprim)+'.'+str(initaper)
            else:
                initlist = str(initprim)
            markup_str = self.make_serendip_markup(text=initlist, 
                                            color=initcols)
        
            str_long = markup_str#+'<p>'
        
            return str_long
        else:
            return ''
        
        
    def update_serendip_list(self, initlist=None, initcols=None):
        
        bands = ['K', 'H', 'J', 'Y']
        vals_num = []
        if initlist is not None:
            serendip_text = []      
            obj_list = []
            

            ## ALWAYS plot serendips for each band separately -- avoids any weird 
            ##      problems for different obj identified in different bands.
            flag = 1
            
                
            for band in bands:
                j = -99
                for jj in xrange(len(initlist)):
                    if initlist[jj][0] == band:
                        j = jj
                if j >= 0:
                    if flag == 0:
                        text_tmp = ''
                    else:
                        # Printing info for each band
                        text_tmp = band+': '
                
                    # Rich text formatting:
                    for i in xrange(len(initlist[j][1])):
                        if flag == 0:
                            if initlist[j][1][i] not in obj_list:
                                obj_list.append(initlist[j][1][i])
                            
                                markup_str = self.make_serendip_markup(text=initlist[j][1][i], 
                                                                color=initcols[j][1][i])
                                text_tmp = text_tmp+markup_str
                    
                                if i < len(initlist[j][1])-1:
                                    text_tmp = text_tmp+', '
                        else:
                            # Printing info for each band:
                            obj_list.append(initlist[j][1][i])

                            markup_str = self.make_serendip_markup(text=initlist[j][1][i], 
                                                            color=initcols[j][1][i])
                            text_tmp = text_tmp+markup_str

                            if i < len(initlist[j][1])-1:
                                text_tmp = text_tmp+', '
                    
                    if text_tmp == '':
                        pass
                    else:
                        serendip_text.append(text_tmp)
            
                
            if len(serendip_text) > 0:
                # Convert this to one string, with carriage returns between lines.
                str_long = ''
                for ii, com in enumerate(serendip_text):
                    if ii < len(serendip_text)-1:
                        str_long = str_long+com+'<p>'
                    else:
                        str_long = str_long+com

                return str_long
            else:
                return ''
        else:
            return ''

        
        