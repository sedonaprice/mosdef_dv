###
# MOSDEF data viewer--
#           viewer_io.py:
#               provide functions to read in data.
###

from astropy.io import fits
import os
import numpy as np
import pandas as pd
import re
import gc
#from astropy.io import ascii as _ascii

# from mosdef_io import read_data
# try:   
#     from tdhst_io import read_data as tdhst_read_data
#     from tdhst_io import paths as _tdhst_paths
# except:
#     pass
    
from astropy.wcs import WCS

import socket
hostname = socket.gethostname()
mbp = 'shp-mbp'
pepper = 'pepper.astro.berkeley.edu'

# Should set this from OS path
#data_dir = '../mosdef_dv_data'
data_dir = 'mosdef_dv_data'


def get_tdhst_vers(hdr):
    catfile = hdr['CATALOG']
    
    splt = re.split('\.',catfile)
    
    
    tdhst_vers_raw = ".".join(splt[-2:])
    
    
    splt = re.split('v', tdhst_vers_raw)
    tdhst_vers = splt[-1]
    
    
    return tdhst_vers


def field_short2long(field):
    return {
            'ae' : 'AEGIS',
            'co' : 'COSMOS', 
            'gn' : 'GOODS-N',
            'gs' : 'GOODS-S',
            'ud' : 'UDS'
            }.get(field.lower(), 'NOT_FOUND')

def maskname_interp(maskname):
    """ Input maskname, ie 'ae2_03', which gives field (ae = AEGIS), 
        redshift (2 = redshift 2), and mask (?) (03 = mask 3???)
        Output: [FIELD (full name, str), Z (str), MASK (str)]
    """
    
    # Input string format:
    #   FFZ_MM  : FF = field code (string), Z = redshift (int), MM = mask (??)
    
    
    # Checked string is proper length
    ff = maskname[0:2]
    z = maskname[2]
    mm = maskname[4:]

    field = field_short2long(ff)
    redshift = z # keep as a string: for filenames  # int(z) 
    mask_no = mm    

    return [field,redshift,mask_no]

def read_3dhst_cat(field, vers='2.1'):
    """
        Read in the 3DHST photometry catalog
    """

    path = read_path('TDHST_CAT')
    # clean up any trailing slash
    if path is not None:
        if path[-1] == '/':
            path = path[0:-1]

        if ((field.upper() == 'GOODS-N') and (vers == '4.0')):
            field_name = 'GOODSN'
        elif ((field.upper() == 'GOODS-S') and (vers == '4.0')):
            field_name = 'GOODSS'
        else:
            field_name = field

        filename = path+'/v'+vers+'/'+field.upper()+'/'+field_name.lower()+'_3dhst.v'+vers+'.cat.FITS'
        

        exist = os.path.isfile(filename)
        if exist:
            hdulist = fits.open(filename)
            data = hdulist[1].data.copy()
    
            hdulist.close()

            return data
        else:
            filename = path+'/v'+vers+'/'+field.upper()+'/'+field.upper()+'_3dhst.v'+vers+'.cat.FITS'
        
            exist = os.path.isfile(filename)
            if exist:
                hdulist = fits.open(filename)
                data = hdulist[1].data.copy()

                hdulist.close()

                return data
        
            else:
                return None

def read_spec1d_comments(filename, band, optimal=True):
    data, data_err, light_profile, hdr = read_spec1d(filename, optimal=optimal)
    
    # UCOMMENT
    # UCMEAN
    comments = []
    try:
        str_ucomment = band+' band comment: '+hdr['UCOMMENT']
        ## Testing:
        #str_ucomment = band+' band comment: '+hdr['FIELD']
        comments.append(str_ucomment)
    except:
        pass
    try:
        str_ucmean = band+' band user code: '+hdr['UCMEAN']\
        ## Testing:
        #str_ucmean = band+' band user code: '+hdr['VERSION']+' and more text, wheeee'
        comments.append(str_ucmean)
    except:
        pass
        
    return comments

def read_spec1d(filename, optimal=True):
    if optimal:
        ext_start = 1
    else:
        ext_start = 3
        
    basedir = read_path('MOSDEF_DV_1D')
    # clean up any trailing slash
    if basedir[-1] == '/':
        basedir = basedir[0:-1]
        

    exist = os.path.isfile(basedir+'/'+filename)
    if exist:
        hdulist = fits.open(basedir+'/'+filename)
        data = hdulist[ext_start].data.copy()
        data_err = hdulist[ext_start+1].data.copy()
        light_profile = hdulist[5].data.copy()
        hdr = hdulist[0].header.copy()
        hdulist.close()
    else:
        # Try the basic data name:
        splt = re.split(r'\.', filename.strip())
        filename_new = '.'.join(splt[0:len(splt)-3])
        filename_new = filename_new+'.'+'.'.join(splt[-2:])
        
        exist = os.path.isfile(basedir+'/'+filename)
        if exist:
            hdulist = fits.open(basedir+'/'+filename)
            data = hdulist[ext_start].data.copy()
            data_err = hdulist[ext_start+1].data.copy()
            light_profile = hdulist[5].data.copy()
            hdr = hdulist[0].header.copy()
            hdulist.close()
        else:
            data = None
            data_err = None
            light_profile = None
            hdr = None
            

    return data, data_err, light_profile, hdr


def read_spec2d(filename):
    basedir = read_path('MOSDEF_DV_2D')
    # clean up any trailing slash
    if basedir[-1] == '/':
        basedir = basedir[0:-1]
    
    exist = os.path.isfile(basedir+'/'+filename)
    #print exist
    if exist:
        hdulist = fits.open(basedir+'/'+filename)
        data = hdulist[1].data.copy()
        hdr = hdulist[1].header.copy()
        
        hdulist.close()
    else:
        data = None
        hdr = None

    return data, hdr


def read_pstamp(field, ID, RA=None,DEC=None):

    path = read_path('MOSDEF_DV_PSTAMP')
    path = path+'/'+field.upper()+'/'
    
    filename = path+field.upper()+'_'+str(ID)+'.fits'
    
    try:
        hdulist = fits.open(filename)
        pstamp = hdulist[0].data.copy()
        hdr = hdulist[0].header.copy()
        hdulist.close()

        return pstamp, hdr
    except:
        path = read_path('MOSDEF_DV_PSTAMP')
        path = path+'/'+field.upper()+'/ALL/'

        filename = path+field.upper()+'_'+str(ID)+'.fits'

        try:
            hdulist = fits.open(filename)
            pstamp = hdulist[0].data.copy()
            hdr = hdulist[0].header.copy()
            hdulist.close()

            return pstamp, hdr
        except:
            return None, None
            


def read_parent_cat(vers='2.1', field=None):
    path = read_path('MOSDEF_DV_PARENT')
    filename = path+'/'+field+'_v'+vers+'.zall.parent.fits'
    
    
    hdu = fits.open(filename)
    data = hdu[1].data.copy()
    data_df = fits_to_df(data)
    hdu.close()
    
    return data_df

def read_0d_cat(vers='2.1'):
    """
        Read in the MOSDEF 0d catalog (fits format)
    """
    if vers == '4.0':
        raise Exception("MOSDEF catalogs not made with v4.0 yet!")

    path = read_path('MOSDEF_DV_MEAS')
    filename = path+'/mosdef_0d_latest.fits'
    
    hdu = fits.open(filename)
    data = hdu[1].data.copy()
    data_df = fits_to_df(data)
    hdu.close()
    
    return data_df






def read_paths():
            
    filename = data_dir+'/mosdef_dv_paths.txt'
    if os.path.exists(filename):
 
        path_info = np.genfromtxt(filename, dtype=None, 
                    names=['label', 'path'])
        
        df = pd.DataFrame(path_info)
        for i in xrange(len(df)):
            if df['path'][i] == 'not_set':
                df['path'][i] = ''
                
            else:
                # Drop trailing / if it's there:
                if df['path'][i][-1] == '/':
                    df['path'][i] = df['path'][i][0:-1]
                
        return df
        
    else:
        return None


def read_path(key):
    path_info = read_paths()
    
    if path_info is not None:
        try:
            path = path_info['path'][path_info['label']==key].values[0]
        except:
            path = None
        if path == 'not_set':
            path = None
        return path
    else:
        return None

def write_paths(path_info):
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir)
        except:
            print 'Cannot create directory '+data_dir+' under current working directory.'
            raise

    filename = data_dir+'/mosdef_dv_paths.txt'

    if os.path.exists(filename):
        sys_cmd = 'rm %s' % filename
        os.system(sys_cmd)
        
    f = open(filename, 'w')
    for i in xrange(len(path_info.index)):
        f.write(path_info['label'][i]+' '+path_info['path'][i]+'\n')
        
    f.close()
    
    return None




def fits_to_df(fitsrec):
    """
        Addresses the big endian vs little endian 
        problem with just creating a DF by
        pd.DataFrame(fitsrec)
    """
    names = fitsrec.names

    for i, name in enumerate(names):
        if (i == 0):
            df = pd.DataFrame({name: fitsrec[name]})
        else:
            df[name] = fitsrec[name]

    return df
    
    
def read_bmep_redshift_slim(mask, primID, aper_no):
    #print "mask, primID, aper_no=", mask, primID, aper_no
    
    path = read_path('MOSDEF_DV_BMEP_Z')
    filename = path+'/00_redshift_catalog_slim_bmep.txt'
    
    if os.path.exists(filename):
        
        names = ['maskname', 'primID', 'aper_no', 'z1', 'n_lines1', 'z2', 'n_lines2']
        redshift_info = pd.read_csv(filename, sep=' ', 
                            names=names, dtype=str, 
                            skipinitialspace=True)
        
        
        # Has a match
        wh = np.where((redshift_info['maskname'].str.strip() == mask) & \
                    (redshift_info['primID'].str.strip() == str(primID)) & \
                    (redshift_info['aper_no'].str.strip() == str(aper_no)))[0]
        
        if len(wh)>0:
            wh = wh[0]
            
            return np.float(redshift_info['z1'][wh])
        else:
            return -1.
        
        
        # except:
        #     # No match in file
        #     return -1.
    else:
        return -1.
        
        
#
def read_pstamp_from_detect(field,ID,ra,dec, img_vers='4.0', filt='F160W', pad = 7.):
    # pad: [arcsec]  # 7.
    
    if (ra is None) | (dec is None):
        return None, None
    else:

        
        
        # Need to find out the limits of the number of pix you can trim
        hdr = read_detection(field, vers=img_vers, hdr_only=True)
        
        w = WCS(hdr)
        wcs_origin = 1 #1
        
        
        x, y = w.wcs_world2pix(ra, dec, wcs_origin)
        x = np.int(np.round(x))
        y = np.int(np.round(y))
        
        pad = pad/0.06 #np.int(np.round(pad/0.06))    # 2 arcsec / (0.06 arcsec/pix)
    
        xmin = max([0, x-pad])
        xmax = min([x+pad+1, hdr['NAXIS1']])
        ymin = max([0, y-pad])
        ymax = min([y+pad+1, hdr['NAXIS2']])
        
        
        xmin = np.int(np.round(xmin))
        xmax = np.int(np.round(xmax))
        ymin = np.int(np.round(ymin))
        ymax = np.int(np.round(ymax))
        
        
    
        pstamp = read_detection(field, filt=filt, vers=img_vers,
                              sect_x=[xmin, xmax],
                              sect_y=[ymin, ymax],
                              no_hdr=True)
        
        
        # Update header values: NAXIS1, NAXIS2, CRPIX1, CRPIX2, 
        #               CRVAL1, CRVAL2
        CRPIX1 = xmin # Numpy coordinates -- starts at 0
        CRPIX2 = ymin # Numpy coordinates -- starts at 0
        
    
        CRVAL1, CRVAL2 = w.wcs_pix2world(CRPIX1+1, CRPIX2+1, wcs_origin)
        #print w.wcs_world2pix(hdr['CRVAL1'], hdr['CRVAL1'], wcs_origin)
    
        hdr['NAXIS1'] = np.shape(pstamp)[0]
        hdr['NAXIS2'] = np.shape(pstamp)[1]
        hdr['CRPIX1'] = 1.#1.#0. # 0.5 #CRPIX1  # 
        hdr['CRPIX2'] = 1. #1. #0. #CRPIX2
        hdr['CRVAL1'] = CRVAL1*1.  # make a float
        hdr['CRVAL2'] = CRVAL2*1.  # make a float
        
        
        
        return pstamp, hdr
        
        
def read_detection(field, vers='4.0', filt='F160W', sect_x=None, sect_y=None, hdr_only=False, no_hdr=False):
    
    return detection_general(field, filt=filt, vers=vers, hdr_only=hdr_only,
            no_hdr=no_hdr, sect_x=sect_x, sect_y=sect_y, alt=True)
            
#
def detection_general(field, filt='F160W', vers='4.0', hdr_only=False,
                        no_hdr=False, sect_x=None, sect_y=None, alt=False):
                        
                        
    field_lower = "".join(field.split('-')).lower()
    #path_tmp = '/Volumes/Surveys/3DHST/
    path_tmp = read_path('TDHST_CAT')
    # clean up any trailing slash
    if path_tmp is not None:
        if path_tmp[-1] == '/':
            path_tmp = path_tmp[0:-1]
    path_tmp = path_tmp+'/v'+vers+'/'+field.upper()+'/Detection/'
    filename = path_tmp + field_lower+'_3dhst.v'+vers+'.'+filt+'_orig_sci.fits'
    filename2 = filename+'.gz'
    
    ext = 0
    
    return get_data_fromfits_img(filename, filename2, hdr_only=hdr_only, 
                                    no_hdr=no_hdr, sect_x=sect_x, sect_y=sect_y, ext=ext)
                                    
                                    
#
def get_data_fromfits_img(filename, filename2, hdr_only=False, 
                                no_hdr=False, sect_x=None, sect_y=None, ext=None):
    
    if ext is None:
        ext = 0

    if hdr_only:
        try:
            hdr = fits.getheader(filename, ext).copy()
        except:
            hdr = fits.getheader(filename2, ext).copy()

        return hdr
    else:
        try:    
            if (sect_x is None) and (sect_y is None):
                if no_hdr:
                    data = fits.getdata(filename, ext=ext).copy()
                
                else:
                    data= fits.getdata(filename, ext=ext, header=False).copy()
                    hdr = fits.getheader(filename, ext).copy()
            else:
                if sect_x is None:
                    sect_x = [0, -1]
                if sect_y is None:
                    sect_y = [0, -1]

                fits_file = fits.open(filename)


                data = fits_file[ext].section[sect_y[0]:sect_y[1],
                                        sect_x[0]:sect_x[1]].copy()

                if not no_hdr:
                    hdr = fits.getheader(filename, ext).copy()
                    
        except:
            try:
                if (sect_x is None) and (sect_y is None):
                    if no_hdr:
                        data = fits.getdata(filename2, ext=ext)
                    else:
                        data = fits.getdata(filename2, ext=ext)
                        hdr = fits.getheader(filename2, ext)
                else:
                    if sect_x is None:
                        sect_x = [0, -1]
                    if sect_y is None:
                        sect_y = [0, -1]
        
                    fits_file = fits.open(filename2)
        
                    # 
                    data = fits_file[ext].section[sect_y[0]:sect_y[1],
                                    sect_x[0]:sect_x[1]].copy()
        
                    if not no_hdr:
                        hdr = fits.getheader(filename2, ext)
            except:
                if no_hdr:
                    return None
                else:
                    return None, None

        fits_file.close()
        #fits_file = None

        if no_hdr:
            return data
        else:
            return data, hdr


    
    
