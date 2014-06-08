## MOSDEF Data viewer
#### History: Written 2014-05-29, SHP

#### PyQt4 GUI data-viewer for internal MOSDEF data products




---

	
##### Instructions:
######Install:
Navigate to the directory where you'd like to install the MOSDEF data viewer.

Download code from git repo using the following:

``` git clone https://github.com/sedonaprice/mosdef_dv.git```

######Setup:
Include the following in your system environment variables (ie in ~/.bashrc)

	export MOSDEF_DV_2D=/Users/mosdef/Data/Reduced/v0.2/2D
	export MOSDEF_DV_1D=/Users/mosdef/Data/Reduced/v0.2/1D
	export MOSDEF_DV_MEAS=/Users/mosdef/Measurements
	export MOSDEF_DV_DB=/Users/sedona/software/mosdef_dataviewer/viewer_data
	export MOSDEF_DV_PSTAMP=/Users/mosdef/Mask_Design/postage_stamps/30_by_30

######Launch program:
``` python data_viewer.py ```


---

##### Dependencies:
PyQt4

*Generally, Anaconda python (conda) or Continuum (Enthought)
have a nice bundle of all the extra packages you need.
There are academic licences for both of these.*




