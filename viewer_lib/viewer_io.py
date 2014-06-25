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

# from mosdef_io import read_data
# try:   
#     from tdhst_io import read_data as tdhst_read_data
#     from tdhst_io import paths as _tdhst_paths
# except:
#     pass
    
from astropy import wcs

import socket
hostname = socket.gethostname()
mbp = 'shp-mbp'
pepper = 'pepper.astro.berkeley.edu'


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


    if len(maskname) != 6:
        raise Exception("Maskname has wrong length!")

    # Checked string is proper length
    ff = maskname[0:2]
    z = maskname[2]
    mm = maskname[4:6]

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
    if path[-1] == '/':
        path = path[0:-1]

    if ((field.upper() == 'GOODS-N') and (vers == '4.0')):
        field_name = 'GOODSN'
    elif ((field.upper() == 'GOODS-S') and (vers == '4.0')):
        field_name = 'GOODSS'
    else:
        field_name = field

    filename = path+'/'+field.upper()+'/'+field_name.lower()+'_3dhst.v'+vers+'.cat.FITS'

    exist = os.path.isfile(filename)
    if exist:
        hdulist = fits.open(filename)
        data = hdulist[1].data
    
        hdulist.close()

        return data
    else:
        filename = path+'/'+field.upper()+'/'+field.upper()+'_3dhst.v'+vers+'.cat.FITS'
        
        exist = os.path.isfile(filename)
        if exist:
            hdulist = fits.open(filename)
            data = hdulist[1].data

            hdulist.close()

            return data
        
        else:
            return None



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
        data = hdulist[ext_start].data
        data_err = hdulist[ext_start+1].data
        light_profile = hdulist[5].data
        hdr = hdulist[0].header
        hdulist.close()
    else:
        # Try the basic data name:
        splt = re.split(r'\.', filename.strip())
        filename_new = '.'.join(splt[0:len(splt)-3])
        filename_new = filename_new+'.'+'.'.join(splt[-2:])
        
        exist = os.path.isfile(basedir+'/'+filename)
        if exist:
            hdulist = fits.open(basedir+'/'+filename)
            data = hdulist[ext_start].data
            data_err = hdulist[ext_start+1].data
            light_profile = hdulist[5].data
            hdr = hdulist[0].header
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
        data = hdulist[1].data
        hdr = hdulist[1].header
        
        hdulist.close()
    else:
        data = None
        hdr = None

    return data, hdr


def read_pstamp(field, ID):

    path = read_path('MOSDEF_DV_PSTAMP')
    path = path+'/'+field.upper()+'/'
    
    filename = path+field.upper()+'_'+str(ID)+'.fits'
    
    try:
        hdulist = fits.open(filename)
        pstamp = hdulist[0].data
        hdr = hdulist[0].header
        hdulist.close()

        return pstamp, hdr
    except:
        path = read_path('MOSDEF_DV_PSTAMP')
        path = path+'/'+field.upper()+'/ALL/'

        filename = path+field.upper()+'_'+str(ID)+'.fits'

        try:
            hdulist = fits.open(filename)
            pstamp = hdulist[0].data
            hdr = hdulist[0].header
            hdulist.close()

            return pstamp, hdr
        except:
            return None, None




def read_0d_cat(vers='2.1'):
    """
        Read in the MOSDEF 0d catalog (fits format)
    """
    if vers == '4.0':
        raise Exception("MOSDEF catalogs not made with v4.0 yet!")

    path = read_path('MOSDEF_DV_MEAS')
    filename = path+'/mosdef_0d.fits'
    
    hdu = fits.open(filename)
    data = hdu[1].data
    data_df = fits_to_df(data)
    hdu.close()
    
    return data_df






def read_paths():
    data_dir = 'mosdef_dv_data'
            
    filename = data_dir+'/mosdef_dv_paths.txt'
    if os.path.exists(filename):
 
        path_info = np.genfromtxt(filename, dtype=None,
                    names=['label', 'path'])
        
        return pd.DataFrame(path_info)
        
    else:
        return None


def read_path(key):
    path_info = read_paths()
    
    if path_info is not None:
        try:
            path = path_info['path'][path_info['label']==key].values[0]
        except:
            path = None
        return path
    else:
        return None

def write_paths(path_info):
    data_dir = 'mosdef_dv_data'
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
    
    
def read_bmep_redshift_slim(primID, aper_no):
    path = read_path('MOSDEF_DV_BMEP_Z')
    filename = path+'/00_redshift_catalog_slim_bmep.txt'
    
    if os.path.exists(filename):
 
        redshift_info_fits = np.genfromtxt(filename, dtype=None,
                    names=['maskname', 'primID', 'aper_no', 'z1', 'n_lines1',
                            'z2', 'n_lines2'])
                            
        redshift_info = pd.DataFrame(redshift_info_fits)
        
        try:
        # Has a match
            wh_prim = np.where(redshift_info['primID'] == np.int64(primID))[0]
            wh_aper = np.where(redshift_info['aper_no'] == np.int64(aper_no))[0]
            wh = np.intersect1d(wh_prim, wh_aper)[0]
    
            return redshift_info['z1'][wh]
        except:
            # No match in file
            return -1.
    else:
        return -1.
    
