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
	
	alias mosdef_dv='python /Users/sedona/software/mosdef_dataviewer/data_viewer.py'


######Launch program:
Navigate to directory where you would like to create the DV dir containing the DB. 
__You must always run MOSDEF DV from this directory to keep using the current DB and 
previously set paths.__

Within this directory, run:

	mosdef_dv

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




