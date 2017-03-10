## MOSDEF Data viewer
#### History: Written 2014-05-29, SHP

#### PyQt4 GUI data-viewer for internal MOSDEF data products




---

	
##### Instructions:
######Install:
Navigate to the directory where you'd like to install the MOSDEF data viewer.

Download code from git repo using the following:

``` git clone https://github.com/sedonaprice/mosdef_dv.git```

(Already installed on pepper.)

######Setup:
Include the following in your system environment variables (ie in ~/.bashrc)

	alias mosdef_dv='python /path/to/MOSDEF_DV/data_viewer.py'

On pepper, this should be 
	
	alias mosdef_dv='python /Users/sedona/software/mosdef_dataviewer/mosdef_dataviewer/data_viewer.py'


######Launch program:
Navigate to the directory where you would like to run the DV. The program will automatically create the folder "mosdef_dv_data" (if it doesn't already exist), which holds the necessary DB and path information.
__You must always run MOSDEF DV from this directory to keep using the current DB and 
previously set paths.__

Within this directory, run:

	mosdef_dv

######Path setup:
For the first run, or if the paths are updated, you will need to set up the dataviewer paths ("Set paths" button on lower right) to point to correct directories.

On pepper, these are similar to:
- MOSDEF 1D spectra: /Users/mosdef/Data/Reduced/v0.4/2D/1D_staging
- MOSDEF 2D spectra: /Users/mosdef/Data/Reduced/v0.4/2D
- MOSDEF measurements: /Users/mosdef/Measurements
- MOSDEF parent catalogs: /Users/mosdef/External_catalogs
- Postage stamps: /Users/mosdef/Mask_Design/postage_stamps/30_by_30
- MOSDEF BMEP redshift file location: /Users/mosdef/Data/Reduced/v0.4/2D/1D_staging
- 3DHST catalog parent dir: /Volumes/Surveys/3DHST

The final box allows you to enter any extra ending that should appear on the 1D filenames (ie, if they are corrected and have "*.ell*" in the names). This should be left blank for the initial 1D extracted spectra

---

##### Shortcuts:
- Cmd/Ctrl+Left: Previous object in mask
- Cmd/Ctrl+Right: Next object in mask
- Cmd/Ctrl+O: Zoom
- Cmd/Ctrl+P: Pan
- Esc: Return to original plot view
- Cmd/Ctrl+Q: Quit


---

##### Dependencies:
- PyQt4
- pyregions (standalone)
- shapely (standalone)
- GEOS (Geometry Engine Open Source; system install: http://trac.osgeo.org/geos/)

*Generally, Anaconda python (conda) or Continuum (Enthought)
have a nice bundle of most of the extra packages you need.
There are academic licences for both of these.*

Easy way to install the dependencies (using Homebrew, alternates also exist for MacPorts and Fink):
- brew install pyqt
- brew install GEOS
- pip install pyregion
- pip install Shapley

