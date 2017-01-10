# mosdef/
#   kinematics/line_2d_model/extra_progs.py
# Module to hold extra programs for 2d line modeling,
#   before you have a better organization method.
# Written 2014 April 29, SHP
#

# Hidden modules prepended with '_'
import numpy as _np
import pandas as _pd
#import re as _re

def pos_angle(cd2_1, cd2_2):
    # Returns angle in dec deg
    return _np.arccos(cd2_2/_np.sqrt(cd2_1**2 + cd2_2**2))*180./_np.pi*_np.sign(cd2_1)

    
    
def read_tdhst_PAs(vers='4.0'):
    path = os.getenv('MOSDEF_DV_DB', '~')
    filename = path+'tdhst_PAs_v'+vers+'.dat'
    
    # Get the header names
    data = _pd.read_csv(filename, sep=' ', skipinitialspace=True)
    num = len(data.columns)
    names = data.columns[1:num]

    data = _pd.read_csv(filename, sep=' ', skiprows=1, names=names, skipinitialspace=True)

    return data
    
    
def angle_offset(maskname, ID, field=None, mask_PA=0., 
        pstamp_hdr=None, vers='4.0'):
    
    ## Return the "phi angle" between 3D-HST and dispersion direction:
    #       0. is parallel (best), 90. is perp (worst, no rot curve)
    ## For postage stamps: want to subtract (4-0.22deg) to instead use PA of science detector.
    
    
    pa_mosdef = mask_PA
    
    ### Seems to be wrong for AEGIS, though DS9 does it right -- try the calculation!
    #pa_tdhst = pstamp_hdr['ORIENTAT']
    
    # Directly calculate, so you're using the same thing DS9 is.
    try:
        cd21 = pstamp_hdr['CD2_1']
    except:
        cd21 = 0.
    try:
        cd22 = pstamp_hdr['CD2_2']
    except:
        cd22 = 0.
        
    pa_tdhst = pos_angle(cd21, cd22)
    

    
    #except:
    #tdhst_PAs = read_tdhst_PAs(vers=vers)
    #pa_tdhst = tdhst_PAs[tdhst_PAs['field']==field]['PA']
    
    #print pa_tdhst
    
    d2r = _np.pi/180.    # Degrees to radians
    
    # PA of MOSFIRE longslit = PA_mosdef + 4 deg 
    phi = ((pa_mosdef)- pa_tdhst)
    
    
    return phi   # Decimal degrees