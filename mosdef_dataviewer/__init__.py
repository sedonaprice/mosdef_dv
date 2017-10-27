# Licensed under the MIT license. See LICENSE
"""
MOSDEF DataViewer
-----------------
The MOSDEF DataViewer is for use examining reduction and extraction data 
prodcuts from the MOSDEF survey (http://mosdef.astro.berkeley.edu/) 
This includes 2D and 1D spectra for each of the spectroscopic bands examined, and 
HST image postage stamps showing the slit position and the primary target, as well 
as any other objects near the slit. 
The DataViewer also reports redshifts from MOSDEF (if available) and 3DHST and 
the F160W/H band magnitude. 
The `best' redshift is used to overplot the wavelengths of a 
number of emission and absorption features, 
though the user has the option to adjust the plotted redshift.

Developed by Sedona Price, 2013-2017.
"""

from .data_viewer import (launch_DataViewer, DataViewer)