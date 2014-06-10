###

"""
MOSDEF data viewer:
	Module to contain all plotting routines.
	
Written:
	2014-05-31, SHP

"""

import sys
import matplotlib
import matplotlib.pyplot as plt
import re
#matplotlib.use('Qt4Agg')
#import pylab

import numpy as np
from scipy.stats import norm

#from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.figure import Figure

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from matplotlib.pyplot import cm
from matplotlib.font_manager import FontProperties
#from matplotlib.pyplot import figure as Figure
from matplotlib.axes import Axes

import matplotlib.gridspec as gridspec

from database import write_cat_db, query_db
from viewer_io import read_spec1d, read_spec2d, read_pstamp
#from viewer_io import read_thumbnail

from position_angles import angle_offset


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
    
    # Plot bands
    bands = ['K', 'H', 'J', 'Y']
    cutoffs = [2., 3., 3., 3.]

    if self.query_good == 1:
        # Initialize overall figure:
        # Set overall figure title
        font_main_header = FontProperties()
        font_main_header.set_size(10.)
        title =  'Mask: '+self.maskname+', ID:'+str(self.obj_id)+\
                    ", PrimID:"+str(self.primID)+", Aper:"+str(self.aper_no)#+\
                    #", "+self.query_info['spec2d_file_h']
                
        self.fig.suptitle(title,fontproperties=font_main_header,
                            x=0.5, y=1.)
                

        has_bands = []
        for b in bands:
            #if self.aper_no == 1:
            if self.query_info['spec2d_file_'+b.lower()] != '---':
                # If it isn't the default, 'band not observed' option put in DB:
                has_bands.append(b)
            # else:
            #                 # Only display the ones with an extraction?
            #                 if self.query_info['spec1d_file_'+b.lower()] != '---':
            #                     # If it isn't the default, 'band not observed' option put in DB:
            #                     has_bands.append(b)
        
        #if message:        
        #    print has_bands
                            
        # setup the overall gridspec:
        gs_main = gridspec.GridSpec(len(has_bands),1, 
                  left=0.03, right=.99,
                  top=0.96, bottom=0.0,
                  hspace=0., wspace=0.)
        # Laptop monitor:
        # gs_main = gridspec.GridSpec(len(has_bands),1, 
        #         left=0.05, right=.985,
        #         top=0.96, bottom=0.0,
        #         hspace=0., wspace=0.)
                  # hspace=.25, 
                            
        for i,b in enumerate(has_bands):
            plotBand(self, gs_main, pos=i, band=b, cutoff=cutoffs[i])
    
    # And draw the figure!    
    self.canvas.draw()

def plotBand(self, gs_main, pos=0, band='H', cutoff=3.):
    # Intialized grids for 1 band plots
    # gs_outer = 
    
    gs = gridspec.GridSpecFromSubplotSpec(2,2, 
              subplot_spec = gs_main[pos],
              width_ratios = [7,1], 
              height_ratios = [0.6,1], 
              wspace=0.01,
              hspace=0.01)
    

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
    ax2 = self.fig.add_subplot(gs[1,0]) # Not the leftmost
    #ax2.set_title('2d spectrum',fontproperties=font_header)
    ax2.set_axis_off()
    
    #print self.query_info['spec2d_file_h'], self.current_db_basedir
    
    # Read in data from files
    spec2d, spec2d_hdr = read_spec2d(self.query_info['spec2d_file_'+band.lower()])
    
    lam0 = spec2d_hdr['crval1']
    lamdelt = spec2d_hdr['cdelt1']/spec2d_hdr['crpix1']
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
        if (np.any(np.isfinite(spec2d[:,li])) == False) or \
            (spec2d[:,li].min() == 0 and spec2d[:,li].max() == 0):
            li += 1
        else:
            left_inds[1] = li
            l_flag = 1
            
    while r_flag == 0:
        # Check finite:
        if (np.any(np.isfinite(spec2d[:,ri])) == False) or \
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
              vmin = range_spec[.05*len(range_spec)], \
              vmax = range_spec[.95*len(range_spec)], \
              interpolation='None', origin='lower')
      
        xlim = ax2.get_xlim()
        ylim = ax2.get_ylim()

        plot_lines(ax2, self.z, 
                np.array(range(np.shape(spec2d)[1])), spec2d_x, 
                ls='-', flag_2d=True)

                
        if spec1d_hdr is not None:        
            plot_spatial_pos(ax2, spec1d_hdr, ls='-')

        ax2.set_xlim(xlim)
        ax2.set_ylim(ylim)

        range_spec = None

    ## spec2d_hdr contains PA, position offset, pix_scale, etc etc!!!


    # &&&&&&&&&&&&&&&&&&&&
    # Thumbnail + slit plot:
    ax3 = self.fig.add_subplot(gs[0,1])
    ax3.set_axis_off()
    
    splt = re.split('v', spec2d_hdr['version'])
    tdhst_vers = splt[-1]
    

    ## This is waaaaay too small. Will have to read in the full image.... boo.
    ## Use the pstamp of the primary if it's pepper:
    pstamp, pstamp_hdr = read_pstamp(spec2d_hdr['field'], self.primID)

    # WFC3 pixel scale is ~0.06"/pix
    
    if pstamp is not None:
        range_spec = pstamp[np.isfinite(pstamp)].copy()
        range_spec.sort()
        ax3.imshow(pstamp, cmap=cm.gray, \
                vmin = range_spec[.02*len(range_spec)], \
                vmax = range_spec[.98*len(range_spec)], \
                interpolation='None', origin='lower')
        

            
        # Angle btween 3DHST and MOSFIRE slit PA- 
        angle = angle_offset(self.maskname, self.obj_id, 
                    field=spec2d_hdr['field'], 
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
        #slit_len = 0.7     # Artificially short, for testing
        slit_wid = 0.7      # arcsec -- can you get this from the headers?
    
        pscale_3dhst = 0.06  # arcsec -- taken from Brammer+11
        
        
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
                
        ax3.plot(rect_sci_x, rect_sci_y, lw=1, ls='-', c='cyan')        
        ############
                

                
        ####
        
        ax3.set_xlim(xlim)
        ax3.set_ylim(ylim)
        
 
    


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
            
        scale = ax_ratio/ax2_ratio*1.15  #*1.65
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
        
        #ax4.yaxis.set_ticks_position('right')
        
        #for tick in ax4.xaxis.get_major_ticks():
        #     tick.label.set_fontsize(tick_fontsize) 
        #for tick in ax4.get_yticklabels():
        #    tick.set_fontsize(tick_fontsize)
        
    
    return None
    
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
    
def plot_lines(ax, z, xarr, wavearr, ls='-', flag_2d=False, lw=2.):
    lines_lam0 = [6563., 4861., 6584., 4959., 5007., 3727., 6717., 6731.]
    # Ha, Hb, NII, OIII, OIII, OII, SII, SII
    cs = ['red', 'red', 'orange', 'yellow', 'yellow', 'yellow', 'magenta', 'magenta']

    wav_del = np.average(wavearr[1:]-wavearr[:-1])
    x_del = np.average(xarr[1:]-xarr[:-1])
    x0 = xarr.min()
    wav0 = wavearr.min()

    for i,l in enumerate(lines_lam0):
        wav = l*(1.+z)/1.e4
        wav_t = (wav-wav0)/wav_del
        wav_x = wav_t*x_del+x0
        if flag_2d == False:
            ax.axvline(x=wav_x, color=cs[i], ls=ls, lw=lw)
        else:
            ax.axvline(x=wav_x, ymin=0, ymax=0.15, color=cs[i], ls=ls, lw=lw)
            ax.axvline(x=wav_x, ymin=0.85, ymax=1., color=cs[i], ls=ls, lw=lw)

    return None
    
    
def plot_spatial_pos(ax, spec1d_hdr, ls='-'):
    #ax.axhline(y=spec1d_hdr['ypos'], ls='-', color='white')
    ax.axhline(y=spec1d_hdr['ypos'], xmin=0., xmax=0.1, ls='-', color='white')
    ax.axhline(y=spec1d_hdr['ypos'], xmin=0.9, xmax=1., ls='-', color='white')
    
    return None
    
    
def plot_1d(self, gs, band, font_header, font_axes, labelpad, 
                tick_fontsize, left_inds, right_inds, cutoff=3.):
    ##############################
    ax = self.fig.add_subplot(gs[0,0])
    
    ax.set_title(band+' band',fontproperties=font_header,
                  x=0.5, y=0.96)
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

        lam0 = spec1d_hdr['crval1']
        lamdelt = spec1d_hdr['cdelt1']/spec1d_hdr['crpix1']
        lamend = lam0+lamdelt*(len(spec1d_flux)-1)
        spec1d_x = np.linspace(lam0, lamend, num=len(spec1d_flux))
        spec1d_y = spec1d_flux


        # Trim everything similar to how spec2d was trimmed:
        spec1d_x = spec1d_x[left_inds[1]:right_inds[0]]/1.e4   # plotting um
        spec1d_y = spec1d_y[left_inds[1]:right_inds[0]]
        spec1d_err = spec1d_err[left_inds[1]:right_inds[0]]

        xlim = [spec1d_x.min(), spec1d_x.max()]

        
        # Check if we're going to mask skylines:
        if self.masksky_cb.isChecked():
            wh_cont, wh_cont_sky = wh_skylines(spec1d_err, cutoff=cutoff)   
        else:
            wh_cont = None
            wh_cont_sky = None


        spec1d_errlo = spec1d_y-spec1d_err
        spec1d_errhi = spec1d_y+spec1d_err
        
        plot_lines(ax,self.z, spec1d_x, spec1d_x, ls='-')
        
        if wh_cont is not None:
            # Masking skylines
            for wh in wh_cont:
                xx = spec1d_x[wh]
                yy_lo = spec1d_errlo[wh]
                yy_hi = spec1d_errhi[wh]
                yy = spec1d_y[wh]
                
                ############
                # If you're smoothing:
                if self.smooth_cb.isChecked():
                    yy_lo = smooth_arr(yy_lo, npix=np.int(self.smooth_num.text()))
                    yy_hi = smooth_arr(yy_hi, npix=np.int(self.smooth_num.text()))
                    yy = smooth_arr(yy, npix=np.int(self.smooth_num.text()))
                ############
                
                # plot the flux errors
                ax.fill_between(xx, yy_lo, yy_hi, \
                      color='b', \
                      facecolor='b', alpha=.25)

                # plot the flux vs wave (observed)
                ax.plot(xx, yy, 'b-', lw=1)
        else:
            # Not masking skylines
            
            ############
            # If you're smoothing:
            if self.smooth_cb.isChecked():
                spec1d_errlo = smooth_arr(spec1d_errlo, npix=np.int(self.smooth_num.text()))
                spec1d_errhi = smooth_arr(spec1d_errhi, npix=np.int(self.smooth_num.text()))
                spec1d_y = smooth_arr(spec1d_y, npix=np.int(self.smooth_num.text()))
            ############
            
            ax.fill_between(spec1d_x, spec1d_errlo, spec1d_errhi, \
                  color='b', \
                  facecolor='b', alpha=.25)
        
            # plot the flux vs wave (observed)
            ax.plot(spec1d_x,spec1d_y, 'b-', lw=1)
        
        
        
        range_spec = spec1d_y[np.isfinite(spec1d_y)].copy()
        range_spec.sort()
        
        
        ax.set_ylim([min(range_spec[.02*len(range_spec)]*.25,0.), 
                    range_spec[.99*len(range_spec)]])

        ax.set_xlim(xlim)
        
            
        if wh_cont_sky is not None:
            # Plot grey boxes where skylines are:
            # based on wh_cont_sky:
            ylim = ax.get_ylim()
            
            for wh in wh_cont_sky:
                ax.fill_between([spec1d_x[wh].min(), spec1d_x[wh].max()], \
                                [ylim[0], ylim[0]], [ylim[1],ylim[1]], \
                                color='grey', \
                                facecolor='grey', alpha=0.25)
                                
                                # darkgrey
        

        spec1d_y = None
        spec1d_err = None
        range_spec = None



    # If there isn't data: Turn the frame off:
    if spec1d_flux is None:
          ax.set_axis_off()
          
          
    return ax, spec1d_flux, spec1d_hdr, spec1d_light_profile
    
    
def wh_skylines(err_spec, cutoff=3.):
    median = np.median(err_spec)
    
    wh_sky = np.where(err_spec >= cutoff*median)[0]
    wh_nosky = np.where(err_spec < cutoff*median)[0]
    
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
    
    