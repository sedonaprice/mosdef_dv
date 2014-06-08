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

# import socket
# hostname = socket.gethostname()
# mbp = 'shp-mbp'
# pepper = 'pepper.astro.berkeley.edu'

#from tdhst_io import read_data as tdhst_read_data
# Will need to change this to work on pepper for everyone... 
#       or bundle this in the viewer_lib...

def read_spec1d(filename, optimal=True):
    if optimal:
        ext_start = 1
    else:
        ext_start = 3
        
    basedir = os.getenv('MOSDEF_DV_1D', '/Users/mosdef/Data/Reduced/v0.2/1D')
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
    basedir = os.getenv('MOSDEF_DV_2D', '/Users/mosdef/Data/Reduced/v0.2/2D')
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

    path = os.getenv('MOSDEF_DV_PSTAMP', 
                '/Users/mosdef/Mask_Design/postage_stamps/30_by_30/')
    path = path+'/'+field.upper()+'/'
    
    filename = path+field.upper()+'_'+str(ID)+'.fits'
    
    try:
        hdulist = fits.open(filename)
        pstamp = hdulist[0].data
        hdr = hdulist[0].header
        hdulist.close()

        return pstamp, hdr
    except:
        path = os.getenv('MOSDEF_DV_PSTAMP', 
                '/Users/mosdef/Mask_Design/postage_stamps/30_by_30/')
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


 

# def read_thumbnail():
#     """
#     return a trimmed part of the detection image for plotting, with an 
#     accompanying WCS.
#     """
#     
#     return None


def read_0d_cat(vers='2.1'):
	"""
		Read in the MOSDEF 0d catalog (fits format)
	"""
	if vers == '4.0':
		raise Exception("MOSDEF catalogs not made with v4.0 yet!")

	path = os.getenv('MOSDEF_DV_MEAS', '/Users/mosdef/Measurements')
	filename = path+'/mosdef_0d.fits'
	
	hdu = fits.open(filename)
	data = hdu[1].data
	data_df = fits_to_df(data)
	hdu.close()
	
	return data_df



# 
# def read_linefits(filename, basedir):
#     print 'still using separate program to read lines -- need to incorporate into this module!'
#     lines = read_data.lines()
#     
#     return lines


# 
# 
# def read_versions():
#     db_dir = os.getenv('MOSDEF_DV_DB', '~')
#     filename = db_dir+'/versions.txt'
#     exist = os.path.isfile(filename)
#     if exist:
#         dt = 'S6'
#         versions = np.loadtxt(filename, dtype=dt)
#         if versions.size <= 1:
#             versions = [str(versions)]
#         else:
#             versions = list(versions)
# 
#     else:
#         versions = ['--------']
# 
# 
#     return versions
# 
# def read_basedirs():
#     """ Basedirs structure """
#     db_dir = os.getenv('MOSDEF_DV_DB', '~')
#     filename = db_dir+'/basedirs.txt'
#     exist = os.path.isfile(filename)
#     if exist:
#         dt = {'names': ('vers', 'dir'), 
#             'formats': ('S6', 'S40')}
# 
#         basedirs = np.loadtxt(filename, dtype=dt)
#     else:
#         basedirs = None
# 
#     return basedirs
# 
# def read_basedir(vers):
#     db_dir = os.getenv('MOSDEF_DV_DB', '~')
#     filename = db_dir+'/basedirs.txt'
#     exist = os.path.isfile(filename)
#     if exist:
#         dt = {'names': ('vers', 'dir'), 
#             'formats': ('S6', 'S40')}
# 
#         dirs = np.loadtxt(filename, dtype=dt)
#         
#         if len(np.shape(dirs)) >= 1:
#             basedir = dirs['dir'][dirs['vers']==str(vers)][0]
#         else:
#             basedir = dirs['dir'][dirs['vers']==str(vers)]
#     else:
#         basedir = None
# 
#     return basedir
# 
# def write_basedir(vers):
#     db_dir = os.getenv('MOSDEF_DV_DB', '~')
#     filename = db_dir+'/basedirs.txt'
#     f = open(filename, 'a')
#     if basedir[-1] == '/':
#         basedir = basedir[0:-1]
#     
#     f.write(vers+' '+basedir+'\n')
#     f.close()
# 
#     return None
# 
# def write_version(vers, db_dir):
#     filename = db_dir+'/versions.txt'
#     f = open(filename, 'a')
#     f.write(vers+'\n')
#     f.close()
# 
#     return None
# 
# def write_current_basedir(basedir, db_dir):
#     filename = db_dir+'/current_basedir.txt'
#     exist = os.path.isfile(filename)
#     if exist:
#         sys_cmd = 'rm %s' % filename
#         os.system(sys_cmd)
#         
#     if basedir[-1] == '/': 
#         basedir = basedir[0:-1]
#             
#     f = open(filename, 'w')
#     f.write(basedir)
#     f.close()
# 
#     return None
# 
# def write_current_version(vers, db_dir):
#     filename = db_dir+'/current_version.txt'
#     exist = os.path.isfile(filename)
#     if exist:
#         sys_cmd = 'rm %s' % filename
#         os.system(sys_cmd)
# 
#     f = open(filename, 'w')
#     f.write(vers)
#     f.close()
# 
#     return None
#     


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
