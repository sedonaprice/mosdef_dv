###

"""
MOSDEF data viewer:
	Module to contain all plotting routines.
	
Written:
	2014-05-31, SHP

"""

import matplotlib.pyplot as plt
import re

import numpy as np
from scipy.stats import norm

from matplotlib.pyplot import cm
from matplotlib.font_manager import FontProperties
from matplotlib.axes import Axes

import matplotlib.gridspec as gridspec

from database import query_db
from viewer_io import read_spec1d, read_spec2d, read_pstamp, read_3dhst_cat, read_pstamp_from_detect
from viewer_io import maskname_interp, get_tdhst_vers

from position_angles import angle_offset

from astropy.wcs import WCS
try:
    from shapely.geometry import Polygon, Point
    shapely_installed = True
except:
    print "*******************************************"
    print "* Python package 'shapely' not installed. *"
    print "*******************************************"
    shapely_installed = False
    
frac_pstamp = 0.05
frac_spec = 0.05

############
# For testing:
import socket
hostname = socket.gethostname()
mbp = 'shp-mbp'
if hostname == mbp:
    message = True
else:
    message = False
############

# Change some settings
plt.rc('font', **{'size':'6.'})

def plotObject(self):
    # Clear the existing figure.
    self.fig.clf()
    
    # Reset the current info about serendips:
    self.serendip_ids = None
    self.serendip_colors = None
    
    # Plot bands
    bands = ['K', 'H', 'J', 'Y']
    cutoffs = [2., 3., 3., 3.]

    if self.query_good == 1:
        # Initialize overall figure:
        # Set overall figure title
        title =  'Mask: '+self.maskname+', ID:'+str(self.obj_id)+\
                    ", PrimID:"+str(self.primID)+", Aper:"+str(self.aper_no)
                
        self.fig.suptitle(title, fontsize=10.,  #backgroundcolor='cyan', 
                            x=0.5, y=0.99)
                

        has_bands = []
        for b in bands:
            if self.query_info['spec2d_file_'+b.lower()] != '---':
                has_bands.append(b)
                            
        # setup the overall gridspec:
        # gs_main = gridspec.GridSpec(len(has_bands),1, 
        #           left=0.03, right=.99,
        #           top=0.96, bottom=0.0,
        #           hspace=0.05,
        #           wspace=0.)
        
        gs_main = gridspec.GridSpec(len(has_bands),1, 
                  left=0.05, right=0.99,
                  top=0.95, bottom=0.0,
                  hspace=0.05,
                  wspace=0.)
                  
                  
        # Read in any 2d hdr:
        spec2d_hdr = self.get_any_2d_hdr()

        # Get 3DHST version number:
        tdhst_vers = get_tdhst_vers(spec2d_hdr)
                  
        # Read in the pstamp: same for all objects:
        #field = maskname_interp(self.maskname)[0]
        tdhst_cat = read_3dhst_cat(self.field, vers=tdhst_vers)

        if self.field.upper() != 'AEGIS':
            pstamp, pstamp_hdr = read_pstamp(self.field, self.primID_v2)
        else:
            pstamp, pstamp_hdr = read_pstamp(self.field, self.primID_v4)
        if (pstamp is None):
            # Match object

            wh = np.where(tdhst_cat['ID'] == np.int64(self.primID))[0]
            # print "wh = ", wh
            # 
            # print "tdhst_vers=", tdhst_vers
            # print "self.primID, self.primID_v2, self.primID_v4 =", self.primID, self.primID_v2, self.primID_v4
            # print "tdhst_cat['RA'][wh]=", tdhst_cat['RA'][wh]
            # print "tdhst_cat['DEC'][wh]=", tdhst_cat['DEC'][wh]

            if len(wh)> 0:
                wh = wh[0]
                ra = tdhst_cat['RA'][wh]
                dec = tdhst_cat['DEC'][wh]

                pstamp, pstamp_hdr = read_pstamp_from_detect(self.field, 
                    np.int64(self.primID_v4), ra, dec, img_vers='4.0')
        
                            
        for i,b in enumerate(has_bands):
            plotBand(self, gs_main, pos=i, band=b, cutoff=cutoffs[i],
                    pstamp=pstamp, pstamp_hdr=pstamp_hdr, tdhst_cat=tdhst_cat,
                    tdhst_vers=tdhst_vers)
    
    # And draw the figure!    
    self.canvas.draw()

def plotBand(self, gs_main, pos=0, band='K', cutoff=3., 
            pstamp=None, pstamp_hdr=None, tdhst_cat=None, tdhst_vers=None):
            
            
    gs = gridspec.GridSpecFromSubplotSpec(2,2, 
              subplot_spec = gs_main[pos],
              width_ratios = [7,1], 
              height_ratios = [1,1],
              hspace=0.2,
              wspace=0.01)
    

    # Set Default Font properties
    font_header = FontProperties()
    font_header.set_size(8.)
    font_axes = FontProperties()
    font_axes.set_size(6.5)
    tick_fontsize = 6.5
    labelpad = -1
    

    # &&&&&&&&&&&&&&&&&&&&
    # SPEC2D plot prep:
    
            
    # Add 2D spectrum axis:
    ax2 = self.fig.add_subplot(gs[1,0])
    ax2.set_axis_off()
    
    # Read in data from files
    spec2d, spec2d_hdr = read_spec2d(self.query_info['spec2d_file_'+band.lower()])
    
    
    lamdelt = spec2d_hdr['cdelt1']
    lam0 = spec2d_hdr['crval1'] - ((spec2d_hdr['crpix1']-1)*spec2d_hdr['cdelt1'])
    lamend = lam0+lamdelt*(np.shape(spec2d)[1]-1)
    spec2d_x = np.linspace(lam0, lamend, num=np.shape(spec2d)[1])/1.e4   # plotting um
              
    # In the interest of plotting, trim all ranges where the columns are full 
    #   of nans, or are all zero.
    # Need to check left and right
    left_inds = np.array([0,0])
    right_inds = np.array([np.shape(spec2d)[1]-1, np.shape(spec2d)[1]-1])
    
    # Keep columns left_inds[1] to right_inds[0]-1, 
    #   ie index as [left_inds[1], right_inds[0]]
    
    l_flag, r_flag = 0, 0
    li, ri = 0, np.shape(spec2d)[1]-1
    
    while l_flag == 0:
        # Check finite:
        if (np.all(np.isfinite(spec2d[:,li])) == False) or \
            (spec2d[:,li].min() == 0 and spec2d[:,li].max() == 0):
            li += 1
        else:
            left_inds[1] = li
            l_flag = 1
            
    while r_flag == 0:
        # Check finite:
        if (np.all(np.isfinite(spec2d[:,ri])) == False) or \
            (spec2d[:,ri].min() == 0 and spec2d[:,ri].max() == 0):
            ri -= 1
        else:
            right_inds[0] = ri+1
            r_flag = 1
            
    spec2d = spec2d[:,left_inds[1]:right_inds[0]]
    spec2d_x = spec2d_x[left_inds[1]:right_inds[0]]
    
    
    # &&&&&&&&&&&&&&&&&&&&
    # SPEC1D plot:
  
    # Add 1D spectrum axis:
    ax, spec1d_flux, spec1d_hdr, spec1d_light_profile = plot_1d(self, gs, band, 
                    font_header, font_axes, 
                    labelpad, tick_fontsize,
                    left_inds, right_inds,
                    cutoff=cutoff)
    


    # &&&&&&&&&&&&&&&&&&&&
    # SPEC2D plot:
    
    if spec2d is not None:
        range_spec = spec2d[np.isfinite(spec2d)].copy()
        range_spec.sort()
        ax2.imshow(spec2d, cmap=cm.gray, \
              vmin = range_spec[np.int(np.round(frac_spec*len(range_spec)))], \
              vmax = range_spec[np.int(np.round((1.-frac_spec)*len(range_spec)))], \
              interpolation='None', origin='lower')
              
        ax2.format_coord = make_format_ax2(ax2, spec2d_hdr, left_inds[1])
      
        xlim = ax2.get_xlim()
        ylim = ax2.get_ylim()

        plot_lines(ax2, self.z, 
                np.array(range(np.shape(spec2d)[1])), spec2d_x, 
                ls='-', flag_2d=True, quiescent_lines=self.quilines_cb.isChecked())

                
        if spec1d_hdr is not None:        
            plot_spatial_pos(ax2, spec1d_hdr['ypos'], ls='-', length=0.08)

        ax2.set_xlim(xlim)
        ax2.set_ylim(ylim)

        range_spec = None

    ## spec2d_hdr contains PA, position offset, pix_scale, etc etc!!!


    # &&&&&&&&&&&&&&&&&&&&
    # Thumbnail + slit plot:
    ax3 = self.fig.add_subplot(gs[0,1])
    ax3.set_axis_off()
    
    
    # WFC3 pixel scale is ~0.06"/pix
    
    if pstamp is not None:
        range_spec = pstamp[np.isfinite(pstamp)].copy()
        range_spec.sort()
        ax3.imshow(pstamp, cmap=cm.gray, \
                vmin = range_spec[np.int(np.round(frac_pstamp*len(range_spec)))], \
                vmax = range_spec[np.int(np.round((1.-frac_pstamp)*len(range_spec)))], \
                interpolation='None', origin='lower')
            
        # Angle btween 3DHST and MOSFIRE slit PA- 
        angle = angle_offset(self.maskname, self.obj_id, 
                    field=self.field, 
                    mask_PA=spec2d_hdr['PA'], 
                    pstamp_hdr=pstamp_hdr, vers=tdhst_vers)   # Decimal_degrees
        
        if message:        
            print 'Mask PA=', spec2d_hdr['PA']            
            print angle
          
        # Setup values     
        # Assume angle already is slit angle 
        slit_angle = angle    # PA for MOSFIRE slits
        sci_angle = angle -4. + 0.22   # PA for MOSFIRE science detector, not to slit.
        d2r = np.pi/180.            
        slit_len = np.shape(spec2d)[0]*spec2d_hdr['pscale']   # arcsec
        slit_wid = 0.7      # arcsec -- can you get this from the headers?
    
        pscale_3dhst = 0.06  # arcsec -- taken from Brammer+11
        pscale_mosfire = spec2d_hdr['pscale']
        
        xlim = ax3.get_xlim()
        ylim = ax3.get_ylim()
        x0 = np.average(xlim)
        y0 = np.average(ylim)
        
        
        # Offset in slit coords
        try:
            y0_off = spec2d_hdr['c_offset']/pscale_3dhst
        except:
            # Someone doesn't have the updated header version of 2D: fall back to 
            #   raw data offset.
            y0_off = spec2d_hdr['offset']/pscale_3dhst
        
        y0 -= y0_off
        
        
        ##############
        # Corner coords: slit rectangle
        off_angle = 4.-0.22   # exaggerate for test. really: 4.-0.22
        y_shear = slit_wid/pscale_3dhst*np.tan(off_angle*d2r)
        
        pos_11 = np.array([x0-0.5*slit_wid/pscale_3dhst, y0-0.5*slit_len/pscale_3dhst])
        pos_12 = np.array([x0-0.5*slit_wid/pscale_3dhst, y0+0.5*slit_len/pscale_3dhst])
        pos_21 = np.array([x0+0.5*slit_wid/pscale_3dhst, y0-0.5*slit_len/pscale_3dhst])
        pos_22 = np.array([x0+0.5*slit_wid/pscale_3dhst, y0+0.5*slit_len/pscale_3dhst])
        
        # Modify BL, TR corner y coords: shear
        pos_11[1] += y_shear
        pos_22[1] -= y_shear
        
        rect_sci_x, rect_sci_y = rot_corner_coords([pos_11,pos_21,pos_22,pos_12,pos_11], 
                slit_angle*d2r, x0=x0, y0=y0+y0_off)
                
        ax3.plot(rect_sci_x, rect_sci_y, lw=1, ls='-', c='lime')        
        ############
                
        ###################################################################
        # Overplot circles for objects within the field of view:
        
        # If the tdhst_cat is found:
        if tdhst_cat is not None:
            pad_arcsec = 1. # 2.
            # Define region with 1" padding around slit area, for plotting object IDs.
            rect_padded_x, rect_padded_y = padded_region([pos_11,pos_21,pos_22,pos_12,pos_11], 
                    slit_angle*d2r, x0=x0, y0=y0+y0_off, pad=pad_arcsec, pscale_3dhst=pscale_3dhst)
        
            # Get info for primary object, if the 1D spectra exist:
            try:
                prim_y_pos = get_primary_y_pos(self, band)
                main_y_pos = spec1d_hdr['ypos']
            except:
                prim_y_pos = -1
                main_y_pos = -1
        
            w = WCS(pstamp_hdr)
            
            
            main_id = self.obj_id
        
            plot_detections_in_stamp(self, ax3, ax2, tdhst_cat, w, 
                         main_id, main_y_pos, prim_y_pos, slit_angle, 
                        pscale_ratio=pscale_mosfire/pscale_3dhst, 
                        x0=x0, y0=y0+y0_off, 
                        rect_pad_x=rect_padded_x, rect_pad_y=rect_padded_y,
                        band=band)
        ###################################################################
        
        ax3.set_xlim(xlim)
        ax3.set_ylim(ylim)
        ##########
    

    # &&&&&&&&&&&&&&&&&&&&
    # Spatial profile plot:
    if spec1d_flux is not None:
        ax4 = self.fig.add_subplot(gs[1,1])
    
        # Light profile in spec1d_light_profile
        #Get spec2d aspect ratio:
        h_2d, w_2d = np.shape(spec2d)
        ax_ratio = np.float(h_2d)/np.float(w_2d)
            
        ax2_pos = ax2.get_position()
        ax3_pos = ax3.get_position()
        ax2_ratio = np.float(ax2_pos.bounds[3])/np.float(ax2_pos.bounds[2])
            
        scale = ax_ratio/ax2_ratio*1.35 #*1.15  #*1.65
        diff = (ax2_pos.bounds[3]*(1-scale))
            
        rect = [ax3_pos.bounds[0], ax2_pos.bounds[1]+diff/2., 
                ax3_pos.bounds[2], ax2_pos.bounds[3]*scale]
            
            
        ax4.set_position(rect)
        
        spatial_y = np.array(range(len(spec1d_light_profile)))  
        profile = spec1d_light_profile.copy()
        ax4.plot(profile, spatial_y, 'b-')
        ax4.set_ylim([spatial_y.min(), spatial_y.max()])
    
        ax4.get_xaxis().set_ticks([])
        ax4.get_yaxis().set_ticks([])
        
    
    return None
    
def plot_detections_in_stamp(self, ax3, ax2d, tdhst_cat, w,  main_id, main_y_pos, prim_y_pos, 
        slit_angle, pscale_ratio=1., x0=0., y0=0., rect_pad_x=None, rect_pad_y=None,
        band='K'):
    
    ## Define the "near the slit" polygon, to determine if we should plot.
    if (rect_pad_x is not None) and (rect_pad_y is not None):
        rect = np.array([rect_pad_x, rect_pad_y])
        corners = rect.T
        # convert to FITS origin convention
        w_x0, w_y0 = w.wcs_pix2world(min(rect_pad_x)+1, min(rect_pad_y)+1, 1)
        w_x1, w_y1 = w.wcs_pix2world(max(rect_pad_x)+1, max(rect_pad_y)+1, 1)
    else:
        w_x0, w_y0 = w.wcs_pix2world(1, 1, 1)
        w_x1, w_y1 = w.wcs_pix2world(hdr['naxis1']+1, hdr['naxis2']+1, 1)
        corners = None
                
    w_x = np.array([min(w_x0, w_x1), max(w_x0, w_x1)])
    w_y = np.array([min(w_y0, w_y1), max(w_y0, w_y1)])
    
    wh_ra_0 = np.where(tdhst_cat['ra'] >= w_x[0])[0]
    wh_ra_1 = np.where(tdhst_cat['ra'] <= w_x[1])[0]
    wh_ra = np.intersect1d(wh_ra_0, wh_ra_1)
    
    wh_dec_0 = np.where(tdhst_cat['dec'] >= w_y[0])[0]
    wh_dec_1 = np.where(tdhst_cat['dec'] <= w_y[1])[0]
    wh_dec = np.intersect1d(wh_dec_0, wh_dec_1)
    
    wh_in_stamp = np.intersect1d(wh_ra, wh_dec)
    
    
    #colors = ['cyan', 'orange', 'magenta', 'yellow', 'red', 'MediumSlateBlue']
    colors = ['darkturquoise', 'orange', 'magenta', 'yellowgreen', 'red', 'MediumSlateBlue']
    
    # Find the y_pos in un-rot coord of the primary object:
    ind_prim = np.where(tdhst_cat['id'] == np.float64(self.primID))[0][0]
    d2r = np.pi/180. 
    px, py = w.wcs_world2pix(tdhst_cat['ra'][ind_prim], tdhst_cat['dec'][ind_prim], 1)
    # Convert to np convention
    px -= 1.
    px -= 1.
    x_prim_HST, y_prim_HST = rot_corner_coords([[px, py]], -1.*slit_angle*d2r, x0=x0, y0=y0) 
    
    
    if len(wh_in_stamp) > 0:
        ser_cols = []
        ser_ids = []
        slit_ys = []
        color_ind = 0
        for ind in wh_in_stamp:
            color_ind, ser_ids, ser_cols, slit_ys = plot_detection(self, ax3, ax2d, tdhst_cat, w, 
                 main_id, main_y_pos, prim_y_pos, y_prim_HST, 
                slit_angle, pscale_ratio, x0, y0, 
                ind, corners=corners, 
                colors=colors, color_ind=color_ind, 
                ser_ids=ser_ids, ser_cols=ser_cols, slit_ys=slit_ys)
                
        
        
        # Sort on slit_ys:
        inds_slit_sort = np.argsort(slit_ys)[::-1]
        ser_ids = np.array(ser_ids)
        ser_cols = np.array(ser_cols)
        ser_ids_sort = list(ser_ids[inds_slit_sort])
        ser_cols_sort = list(ser_cols[inds_slit_sort])
        
        if self.serendip_ids is not None:
            ser_all = self.serendip_ids
            col_all = self.serendip_colors
        else:
            ser_all = []
            col_all = []
        ser_all.append([band, ser_ids_sort])
        col_all.append([band, ser_cols_sort])
        self.serendip_ids = ser_all
        self.serendip_colors = col_all
        
        ser_ids_int = np.array(ser_ids_sort,dtype=np.int64)
        wh_tmp = np.where(ser_ids_int == self.obj_id)[0]
        if len(wh_tmp)>0:
            self.obj_id_color = ser_cols_sort[wh_tmp[0]]
        else:
            self.obj_id_color='black'
            
    
    return None
    
def plot_detection(self, ax, ax2d, tdhst_cat, w, main_id, main_y_pos, prim_y_pos, 
            y_prim_HST, slit_angle, pscale_ratio, 
            x0, y0, ind, corners=None, colors=['cyan'], color_ind=0,
            ser_ids=None, ser_cols=None, slit_ys=None):
        
    px, py = w.wcs_world2pix(tdhst_cat['ra'][ind], tdhst_cat['dec'][ind], 1)
    # Convert to np convention
    px -= 1.
    px -= 1.
    
    if corners is not None:
        # Check if it's in region:
        if is_in_region(corners, px, py):
            plot_ind = True
        else:
            plot_ind = False
            
    else:
        plot_ind = True
        
    if plot_ind:
        ser_cols.append(colors[color_ind])
        ser_ids.append(str(np.int64(tdhst_cat['id'][ind])))
        
        # Plot a circle, ID for objects within region:
        circle = plt.Circle((px, py), 10, color=colors[color_ind], fill=False)
        ax.add_artist(circle)
        ang = slit_angle
        xoff = 25
        yoff = -7
        if np.abs(ang) > 90:
            xoff = -35
            yoff = 10
            ang = ang - np.sign(ang)*180.
            if np.abs(ang) > 90:
                ang = ang - np.sign(ang)*180.
                xoff = 35
                yoff = 15
            
        d2r = np.pi/180. 

        slit_x, slit_y = rot_corner_coords([[px, py]], -1.*slit_angle*d2r, x0=x0, y0=y0)
        
        slit_ys.append(slit_y)
        
        # Plot text relative to slit positions:
        text_x, text_y = rot_corner_coords([[slit_x+xoff, slit_y+yoff]], 
                    slit_angle*d2r, x0=x0, y0=y0)
        ax.text(text_x, text_y, str(np.int64(tdhst_cat['id'][ind])), 
                color=colors[color_ind], fontsize=8., rotation=ang, 
                clip_on=True, fontweight='bold')
                
        # Convert to slit pixels
        slit_y = slit_y/pscale_ratio
        # Relative to primary object:
        y_prim_HST = y_prim_HST/pscale_ratio
        y_pos = prim_y_pos - (y_prim_HST - slit_y)
        
        #if np.abs(y_pos - main_y_pos) <= 0.5:
        if tdhst_cat['id'][ind] == main_id:
            length = 0.08
        else:
            length = 0.05
            
        
        plot_spatial_pos(ax2d, y_pos, 
                    ls='-', color=colors[color_ind], length=length)
        
        color_ind += 1
        if color_ind == len(colors):
            color_ind = 0
    
    # Only appended stuff if plot_ind = True
    return color_ind, ser_ids, ser_cols, slit_ys

    
def rot_coord_angle(arr, th, x0=0., y0=0.):
    """
    Input angle in radians.
    x0,y0 are center of rot.
    x1_off, y1_off are arbitrary offset to apply after transform.
    """
    # Rotate around zp if given:
    pos_arr = np.array([arr[0]-x0, arr[1]-y0])
    
    x1 = pos_arr[0]*np.cos(th) - pos_arr[1]*np.sin(th)
    y1 = pos_arr[0]*np.sin(th) + pos_arr[1]*np.cos(th)
    
    return x1 + x0 , y1 + y0
    
def rot_corner_coords(coords, th, x0=0., y0=0.):
    """
    Rotate a rectangle, and return two arrs: xcorr, ycorr.
    Input: [[x1,y1],[x2,y2], [x3,y3], [x4,y4]]
    
    x0,y0 are center of rot.
    x1_off, y1_off are arbitrary *additative* offset to apply after transform.
    """
    corners = np.array([])
    for c in coords:
        cx, cy = rot_coord_angle(c, th, x0=x0, y0=y0)
        if np.shape(corners)[0] == 0:
            corners = np.array([cx, cy]).flatten()
        else:
            corners = np.vstack((corners, np.array([cx, cy]).flatten()))
        
    corners = np.array(corners)
    
    return corners.T[0], corners.T[1]
    
    
def padded_region(pos_arr, angle_rad, x0=0., y0=0., pad=2, pscale_3dhst=0.06):
    # Unpack values       
    pos_11,pos_21,pos_22,pos_12,pos_11 = pos_arr
    
    p_pad = pad/pscale_3dhst
    pos_11[0] -= p_pad
    pos_11[1] -= p_pad
    
    pos_12[0] -= p_pad
    pos_12[1] += p_pad
    
    pos_21[0] += p_pad
    pos_21[1] -= p_pad
    
    pos_22[0] += p_pad
    pos_22[1] += p_pad
    
    rect_padded_x, rect_padded_y = rot_corner_coords([pos_11,pos_21,pos_22,pos_12,pos_11], 
            angle_rad, x0=x0, y0=y0)
    
    return  rect_padded_x, rect_padded_y
    
    
def is_in_region(corners, px, py):
    if shapely_installed:
        poly = Polygon(corners)
        point = Point(px, py)
        if point.within(poly):
            return True
        else:
            return False
    else:
        # If shapely or GEOS isn't installed, just use min, max of x/y pos:
        corn_x, corn_y = corners.T
        if (py >= min(corn_y)) and (py <= max(corn_y)):
            if (px >= min(corn_x)) and (px <= max(corn_x)):
                return True
            else:
                return False
        else:
            return False
      
def get_primary_y_pos(self, band):
    query_str = "maskname = '%s' AND primaryID = '%s' AND aperture_no = %s" % (self.maskname, self.primID, 1)
    query = query_db(query_str)
    
    if not type(query) == type(None):
        if len(query) == 1:
            query_info = query[0]
            spec1d_flux, spec1d_err, spec1d_light_profile, spec1d_hdr = \
                    read_spec1d(query_info['spec1d_file_'+band.lower()])
                    
            prim_y_pos = spec1d_hdr['ypos']
            
        else:
            prim_y_pos = -1.
    else:
        prim_y_pos = -1.
    
    return prim_y_pos
    
    
def plot_lines(ax, z, xarr, wavearr, ls='-', flag_2d=False, lw=2., quiescent_lines=False):
    lines_lam0 = [6564.60, 4862.71, 
                6585.27, 
                4960.295, 5008.240, 
                3727.10, 3729.86, 
                6718.294, 6732.673]
    # Ha, Hb, NII, OIII, OIII, OII, SII, SII
    cs = ['red', 'darkturquoise', 'orange', 'yellow', 'yellow', 
            'green', 'green', 'magenta', 'magenta']
            
            
    #
    if quiescent_lines:
        lines_q = [5170.1, 4000., 4341.692, 4102.892]
        # MgB, D4000, Hg, Hd
        cs_q = ['mediumseagreen', 'lightcoral', 'slateblue', 'darkorchid']
        
        lines_lam0.extend(lines_q)
        cs.extend(cs_q)

    wav_del = np.average(wavearr[1:]-wavearr[:-1])
    x_del = np.average(xarr[1:]-xarr[:-1])
    x0 = xarr.min()
    wav0 = wavearr.min()

    for i,l in enumerate(lines_lam0):
        wav = l*(1.+z)/1.e4
        wav_t = (wav-wav0)/wav_del
        wav_x = wav_t*x_del+x0
        if flag_2d == False:
            # 1D case
            ax.axvline(x=wav_x, color=cs[i], ls=ls, lw=lw)
        else:
            # 2D case
            ax.axvline(x=wav_x, ymin=0, ymax=0.15, color=cs[i], ls=ls, lw=lw)
            ax.axvline(x=wav_x, ymin=0.85, ymax=1., color=cs[i], ls=ls, lw=lw)

    return None
    
    
def plot_spatial_pos(ax, ypos, ls='-', color='white', length=0.1):
    pix_center_off = 0.5
    ax.axhline(y=ypos+pix_center_off, xmin=0., xmax=length, ls='-', color=color)
    ax.axhline(y=ypos+pix_center_off, xmin=1.-length, xmax=1., ls='-', color=color)
    
    return None
    
    
def plot_1d(self, gs, band, font_header, font_axes, labelpad, 
                tick_fontsize, left_inds, right_inds, cutoff=3.):
    ##############################
    ax = self.fig.add_subplot(gs[0,0])
    
    ax.set_title(band+' band',fontproperties=font_header,
                  x=0.5, y=0.97)
    ax.set_xlabel('$\lambda$ (Obs. frame, $\mu \mathrm{m}$)',fontproperties=font_axes)
    #ax.set_xlabel('$\lambda$ (Observed frame, $\AA$)',fontproperties=font_axes)
    ax.set_ylabel('F$_{\lambda}$ (erg/s/cm$^2$/$\AA$)',fontproperties=font_axes)
    for tick in ax.xaxis.get_major_ticks():
           tick.label.set_fontsize(tick_fontsize) 
    for tick in ax.yaxis.get_major_ticks():
           tick.label.set_fontsize(tick_fontsize) 

    ax.xaxis.labelpad = labelpad
    ax.yaxis.labelpad = labelpad

    spec1d_flux, spec1d_err, spec1d_light_profile, spec1d_hdr = read_spec1d(self.query_info['spec1d_file_'+band.lower()])

    if spec1d_flux is not None:     
        # Need to construct wavelength from header information, just like in kinematics work

        lamdelt = spec1d_hdr['cdelt1']
        lam0 = spec1d_hdr['crval1'] - ((spec1d_hdr['crpix1']-1)*spec1d_hdr['cdelt1'])
        lamend = lam0+lamdelt*(len(spec1d_flux)-1)
        spec1d_x = np.linspace(lam0, lamend, num=len(spec1d_flux))
        spec1d_y = spec1d_flux

        # Trim everything similar to how spec2d was trimmed:
        spec1d_x = spec1d_x[left_inds[1]:right_inds[0]]/1.e4   # plotting um
        spec1d_y = spec1d_y[left_inds[1]:right_inds[0]]
        spec1d_err = spec1d_err[left_inds[1]:right_inds[0]]

        xlim = [spec1d_x.min(), spec1d_x.max()]
        

        spec1d_errlo = spec1d_y-spec1d_err
        spec1d_errhi = spec1d_y+spec1d_err
        
        plot_lines(ax,self.z, spec1d_x, spec1d_x, ls='-', quiescent_lines=self.quilines_cb.isChecked())
        
        if self.masksky_cb.isChecked():
            wh_cont, wh_cont_sky = wh_skylines(spec1d_err, cutoff=cutoff)
        else:
            wh_cont, wh_cont_sky = None, None
        
        # Check if we're going to mask skylines:
        if wh_cont is not None:
            spec1d_x_concat = np.array([])
            spec1d_y_concat = np.array([])
            spec1d_y_err_concat = np.array([])
            for wh in wh_cont:
                xx = spec1d_x[wh]
                yy_lo = spec1d_errlo[wh]
                yy_hi = spec1d_errhi[wh]
                yy = spec1d_y[wh]
                yerr = spec1d_err[wh]
                
                ############
                # If you're smoothing:
                if self.smooth_cb.isChecked():
                    try:
                        if np.int(self.smooth_num.text()) > 0:
                            yy_lo = smooth_arr(yy_lo, npix=np.int(self.smooth_num.text()))
                            yy_hi = smooth_arr(yy_hi, npix=np.int(self.smooth_num.text()))
                            yy = smooth_arr(yy, npix=np.int(self.smooth_num.text()))
                            yerr = smooth_arr(yerr, npix=np.int(self.smooth_num.text()))
                    except:
                        # Invalid smooth input: no smoothing
                        pass
                ############
                
                # Concatenate onto spec1d_y_concat:
                spec1d_x_concat = np.append(spec1d_x_concat, xx)
                spec1d_y_concat = np.append(spec1d_y_concat, yy)
                spec1d_y_err_concat = np.append(spec1d_y_err_concat, yerr)
                
                # plot the flux errors
                ax.fill_between(xx, yy_lo, yy_hi, \
                      color='b', \
                      facecolor='b', \
                      lw = 0., \
                      alpha=.25)

                # plot the flux vs wave (observed)
                ax.plot(xx, yy, 'b-', lw=1)
        else:
            # Not masking skylines
            
            ############
            # If you're smoothing:
            if self.smooth_cb.isChecked():
                try:
                    if np.int(self.smooth_num.text()) > 0:
                        spec1d_errlo = smooth_arr(spec1d_errlo, npix=np.int(self.smooth_num.text()))
                        spec1d_errhi = smooth_arr(spec1d_errhi, npix=np.int(self.smooth_num.text()))
                        spec1d_y = smooth_arr(spec1d_y, npix=np.int(self.smooth_num.text()))
                        spec1d_err = smooth_arr(spec1d_err, npix=np.int(self.smooth_num.text()))
                except:
                    # Invalid smooth input: no smoothing
                    pass
            ############
            
            # Concatenate for fitting array:
            spec1d_x_concat = spec1d_x
            spec1d_y_concat = spec1d_y
            spec1d_y_err_concat = spec1d_err
            
            #ymax = spec1d_errhi[20:-20].max()
            
            ax.fill_between(spec1d_x, spec1d_errlo, spec1d_errhi, \
                  color='b', \
                  facecolor='b', alpha=.25)
        
            # plot the flux vs wave (observed)
            ax.plot(spec1d_x,spec1d_y, 'b-', lw=1)
        
        
        # Get range_spec for using all points that aren't skylines

        # Skip very edge of spectra:
        spec1d_y_trim = spec1d_y_concat[20:len(spec1d_y_concat)-20]
        spec1d_err_trim = spec1d_y_err_concat[20:len(spec1d_y_err_concat)-20]
        wh_finite = np.where(np.isfinite(spec1d_err_trim))[0]
        spec1d_y_trim = spec1d_y_trim[wh_finite]
        spec1d_err_trim = spec1d_err_trim[wh_finite]
        wh_no_sky, wh_sky = wh_skylines(spec1d_err_trim, cutoff=cutoff, full=True)  
        spec1d_y_nosky = spec1d_y_trim[wh_no_sky]
        spec1d_err_nosky = spec1d_err_trim[wh_no_sky]

        finite = np.isfinite(spec1d_y_nosky)
        y_finite = spec1d_y_nosky[finite].copy()
        y_err_finite = spec1d_err_nosky[finite].copy()
        

        # Find median, std of range_spec:
        median = np.median(y_finite)
        std = np.std(y_finite)
        ax.set_ylim([median-3*std, max(y_finite+y_err_finite)])

        ax.set_xlim(xlim)

        if wh_cont_sky is not None:
            # Plot grey boxes where skylines are, based on wh_cont_sky:
            ylim = ax.get_ylim()

            for wh in wh_cont_sky:
                ax.fill_between([spec1d_x[wh].min(), spec1d_x[wh].max()], \
                                [ylim[0], ylim[0]], [ylim[1],ylim[1]], \
                                color='grey', \
                                facecolor='grey', alpha=0.25)


        spec1d_y = None
        spec1d_err = None
        range_spec = None

    # If there isn't data: Turn the frame off:
    if spec1d_flux is None:
          ax.set_axis_off()
          
    return ax, spec1d_flux, spec1d_hdr, spec1d_light_profile
    
    
def wh_skylines(err_spec, cutoff=3., full=False):
    median = np.median(err_spec)
    
    wh_sky = np.where(err_spec >= cutoff*median)[0]
    wh_nosky = np.where(err_spec < cutoff*median)[0]
    
    if full:
        return wh_nosky, wh_sky
        
    else:
        wh_cont = wh_continuous(wh_nosky)
        wh_cont_sky = wh_continuous(wh_sky)
        
        return wh_cont, wh_cont_sky
    
def wh_continuous(wh_arr):
    wh_arrs = []
    arr = []
    for i in xrange(len(wh_arr)):
        if i < len(wh_arr)-1:
            if wh_arr[i+1] - wh_arr[i] == 1:
                arr.append(wh_arr[i])
            else:
                arr.append(wh_arr[i])
                wh_arrs.append(arr)
                arr = []
        else:
            arr.append(wh_arr[i])
            wh_arrs.append(arr)
    
    return wh_arrs
            
    
def smooth_arr(arr, npix=3.):
    # Call this within a continuous check, to only smooth a little bit at a time.
    if len(arr) < 2*npix+1:
        # If the truncated section is too short, reset the npix just for that part
        npix = np.floor((len(arr)-1)/2.)
    
    xx = np.linspace(-1*npix, npix, num=2*npix+1)
    yy = norm.pdf(xx,0,npix)
    
    # Do convolution:
    yy_out = np.convolve(arr, yy, mode='same')
    
    return yy_out
    
def make_format_ax2(ax, hdr, start_ind):
    # Change axis format so that it shows wavelength, as well as x pixel pos
    # wavearr: in um
    def format_coord(x, y):
        lamdelt = hdr['cdelt1']
        lam0 = hdr['crval1'] - ((hdr['crpix1']-1)*hdr['cdelt1']) + (start_ind)*hdr['cdelt1']
        wave = (lam0 + lamdelt*x)/1.e4
        return 'wave=%1.5f [um]    x=%1.5f   x_orig=%1.5f   y=%1.5f' % (wave, x, x+start_ind, y)
    return format_coord
