###
# MOSDEF data viewer--
#           io.py:
#               provide functions to make Data Viewer databse, 
#                   and query it.
###


import sqlite3
import os.path
import os
from numpy import array
import pandas as pd
import numpy as np
import re
from viewer_io import read_0d_cat, read_path
import numpy as np

############################################################
# Basic functions: check if things exist, or delete them.
def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def db_exist(dbname):
    exist = os.path.isfile(dbname)
    return exist

def db_delete(dbname):
    sys_cmd = 'rm %s' % dbname
    os.system(sys_cmd)
    return None
############################################################
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
	#	FFZ_MM	: FF = field code (string), Z = redshift (int), MM = mask (??)


	if len(maskname) != 6:
		raise Exception("Maskname has wrong length!")

	# Checked string is proper length
	ff = maskname[0:2]
	z = maskname[2]
	mm = maskname[4:6]

	field = field_short2long(ff)
	redshift = z # keep as a string: for filenames	# int(z) 
	mask = mm	

	return [field,redshift,mask]

############################################################

def const_filename(filehead,mid,fileend, basedir, dim=2):
    # Construct the filename, if it exists
    filename_dir = basedir+'/'+filehead+'.'+mid+'.'+fileend
    filename = filehead+'.'+mid+'.'+fileend

    exist = os.path.isfile(filename_dir)
    if exist:
        return filename
    else:
        if dim == 1:
            # Try the basic data name:
            splt = re.split(r'\.', filename.strip())
            filename_new = '.'.join(splt[0:len(splt)-3])
            filename_new = filename_new+'.'+'.'.join(splt[-2:])
            
            exist = os.path.isfile(basedir+'/'+filename_new)
            if exist:
    	        return filename_new
            else:
                return '---'
        else:
            # Don't try any trimming if it's a 2D filename
            return '---'

def cat_struct():

    ## Read in catalog info later??? if decided we need it.
    # lines = read_linefits(linefits_file)
    # fast = read_fast(fast_file)
    # colors = read_colors(color_file, version,cat_name=name)

    # Find out what data you have: use 1D spectra directory
    basedir_1d = read_path('MOSDEF_DV_1D')
    basedir_2d = read_path('MOSDEF_DV_2D')
    files = os.listdir(basedir_1d)
    
    # Returns all files:  including aperture number, bands, masknames, etc.
    
    all_df = pd.DataFrame({})
    for f in files:
        splt = re.split(r'\.', f.strip())
        if len(splt) == 5:
            # Format: mask.band.primID.2d.fits
            mask, band, prim_id = splt[0:3]
            aper_no = 1
            dfNew = pd.DataFrame({'maskname': mask, 
                                'band': band,
                                'primID': prim_id,
                                'aper_no':aper_no},
                                index=[0])
            all_df = all_df.append(dfNew, ignore_index=True)
            
        elif len(splt) == 6:
            # Format: mask.band.primID.aper_no.2d.fits
            mask, band, prim_id, aper_no = splt[0:4]
            
            dfNew = pd.DataFrame({'maskname': mask, 
                                'band': band,
                                'primID': prim_id,
                                'aper_no':aper_no},
                                index=[0])
            all_df = all_df.append(dfNew, ignore_index=True)
            
        else:
            raise ValueError(len(splt))

    # DF containing unique objects:
    obj_df= all_df[['maskname','primID','aper_no']].copy()
    obj_df.drop_duplicates(inplace=True)

    
    filters = ['K','H','J','Y']
    
    # Open MOSDEF 0d catalog to get objID for objects that are not primary
    mosdef_0d_cat = read_0d_cat()
    
    cat = []
    ### Info that needs to be stored in DB
    keys = [ 'maskname', 'objID', \
            'primaryID', 'aperture_no', \
            'field', \
            'ra', 'dec']
    for i in xrange(len(filters)):
        keys.append('spec1d_file_'+filters[i].lower())
        keys.append('spec2d_file_'+filters[i].lower())
        
    keys.append('hst_file')

    for ii in xrange(len(obj_df)):
        ## File1d note: might also be named after the identified object number --
        ##  in which case will need to reference master catalog to get 
        ##  objID for use in maskname
        i = obj_df.index[ii]
        
        # Match in 0D catalog
        try:
            wh_prim = np.where(mosdef_0d_cat['SLITOBJNAME'] == np.int64(obj_df.ix[i]['primID']))[0]
            wh_aper = np.where(mosdef_0d_cat['APERTURE_NO'] == np.int64(obj_df.ix[i]['aper_no']))[0]
            wh = np.intersect1d(wh_prim, wh_aper)[0]
            prim_id_name = np.int64(obj_df.ix[i]['primID'])
        except:
            # Has 'S' at the beginning of obj name
            prim_id_name = np.int64(obj_df.ix[i]['primID'][1:])
            wh_prim = np.where(mosdef_0d_cat['SLITOBJNAME'] == np.int64(obj_df.ix[i]['primID'][1:]))[0]
            wh_aper = np.where(mosdef_0d_cat['APERTURE_NO'] == np.int64(obj_df.ix[i]['aper_no']))[0]
            try:
                wh = np.intersect1d(wh_prim, wh_aper)[0]
            except:
                wh = None
        
        file_1d_base = obj_df.ix[i]['maskname']
        file_2d_base = obj_df.ix[i]['maskname']
        if np.int(obj_df.ix[i]['aper_no']) == 1:
            file_1d_end = obj_df.ix[i]['primID']+'.fcscellipse.1d.fits'
            file_2d_end = obj_df.ix[i]['primID']+'.2d.fits'
            
            try:
                objID = np.int64(obj_df.ix[i]['primID'])
            except:
                objID = np.int64(obj_df.ix[i]['primID'][1:])
        else:
            file_1d_end = obj_df.ix[i]['primID']+'.'+obj_df.ix[i]['aper_no']+'.fcscellipse.1d.fits'
            file_2d_end = obj_df.ix[i]['primID']+'.2d.fits'
             
            #objID = -99  # Temp until we get master cat references.
            if wh is not None:
                objID = mosdef_0d_cat['ID'][wh]
            else:
                objID = -99
        
        files_1d = []
        files_2d = []
        for f in filters:
            file1d = const_filename(file_1d_base, f, file_1d_end, basedir_1d,dim=1)
            files_1d.append(file1d)
            
            file2d = const_filename(file_2d_base, f, file_2d_end, basedir_2d,dim=2)
            files_2d.append(file2d)
        
        # Temp
        hst_file = '-----'
        
        # Get field:
        field, z, mask = maskname_interp(obj_df.ix[i]['maskname'])
        
        # Set ra, dec
        if wh is not None:
            ra, dec = mosdef_0d_cat['RA'][wh], mosdef_0d_cat['DEC'][wh]
        else:
            ra, dec = -99., -99.
        
        row = [obj_df.ix[i]['maskname'], objID, \
                prim_id_name, \
                np.int64(obj_df.ix[i]['aper_no']), \
                field, \
                ra, dec]
        for i in xrange(len(filters)):
                row.append(files_1d[i])
                row.append(files_2d[i])
                
        row.append(hst_file)

        td = dict(zip(keys,row))
        cat.append(td)
    
    return cat


############################


    # Tags for the catalog:
    #   'maskname', 'objID', \
    #       'primaryID', 'aperture_no', \
    #       'field', \
    #       'ra', 'dec', \
    #       'spec1d_file_k', 'spec2d_file_k', \
    #       'spec1d_file_h', 'spec2d_file_h', \
    #       'spec1d_file_j', 'spec2d_file_j', \
    #       'spec1d_file_y', 'spec2d_file_y', \
    #       'hst_file'

# def read_current_version(db_dir):
#     # Read in the file to get the current version
#     fileout = db_dir+'/current_version.txt'
#     exist = os.path.isfile(fileout)
#     if exist:
#         f = open(fileout, 'r')
#         version = f.read()
#         f.close()
#     else:
#         version = '--'
# 
#     return version
# 
# def read_current_basedir(db_dir):
#     # Read in the file to get the current basedir
#     fileout = db_dir+'/current_basedir.txt'
#     exist = os.path.isfile(fileout)
#     if exist:
#         f = open(fileout, 'r')
#         basedir = f.read()
#         f.close()
#     else:
#         basedir = '-----'
# 
#     return basedir


def write_cat_db():
        
    data_dir = 'mosdef_dv_data'

    # See if DB exists already. If it does, delete it.
    dbname = data_dir+'/dataviewer_catalog.db'

    # Make a dict containing all the info
    cat = cat_struct()

    # Delete an existing DB of the same name, to avoid appending.
    if db_exist(dbname):
        db_delete(dbname)

    # Connect to DB
    connection, cursor = connect_db(dbname)

    # Create the table, using a random collname
    # tags = [ 'maskname', 'objID', \
    #       'primaryID', 'aperture_no', \
    #       'spec1d_file_k', 'spec2d_file_k', \
    #       'spec1d_file_h', 'spec2d_file_h', \
    #       'spec1d_file_j', 'spec2d_file_j', \
    #       'spec1d_file_y', 'spec2d_file_y', \
    #       'hst_file']
    collname = 'catalog'
    sql_cmd = """CREATE TABLE IF NOT EXISTS %s 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                maskname TEXT, objID INT, primaryID INT, aperture_no INT, 
                field TEXT, 
                ra FLOAT, dec FLOAT, 
                spec1d_file_k TEXT, spec2d_file_k TEXT, 
                spec1d_file_h TEXT, spec2d_file_h TEXT,
                spec1d_file_j TEXT, spec2d_file_j TEXT,
                spec1d_file_y TEXT, spec2d_file_y TEXT,
                hst_file TEXT)""" % collname

    cursor.execute(sql_cmd)

    # cat contains an array of dicts containing this info
    # keys = [gris_id, phot_id, survey, z_grism, mass, sfr, ssfr, age, Av, \
    #       UV, VJ, \
    #       spec1d_file, spec2d_file, sed_file]
    for r in cat:
        # r is the dict in each row

        # Make sure none of the strings are encoded as unicode -- bad for sql
        list_dat = [ r['maskname'].encode('ascii', 'ignore'), \
                r['objID'], r['primaryID'], r['aperture_no'], \
                r['field'], \
                r['ra'], r['dec'], \
                r['spec1d_file_k'].encode('ascii', 'ignore'), r['spec2d_file_k'].encode('ascii', 'ignore'), \
                r['spec1d_file_h'].encode('ascii', 'ignore'), r['spec2d_file_h'].encode('ascii', 'ignore'), \
                r['spec1d_file_j'].encode('ascii', 'ignore'), r['spec2d_file_j'].encode('ascii', 'ignore'), \
                r['spec1d_file_y'].encode('ascii', 'ignore'), r['spec2d_file_y'].encode('ascii', 'ignore'), \
                r['hst_file'].encode('ascii', 'ignore') ]

        dat = tuple(list_dat)
        strdat = str(dat)


        sql_cmd = "INSERT INTO %s" % collname
        sql_cmd = (sql_cmd +  "(maskname, objID, primaryID, aperture_no, field, " + 
                "ra, dec, " + 
                "spec1d_file_k, spec2d_file_k, " + 
                "spec1d_file_h, spec2d_file_h, " + 
                "spec1d_file_j, spec2d_file_j, " +
                "spec1d_file_y, spec2d_file_y, " + 
                "hst_file) VALUES " + strdat)
                
        cursor.execute(sql_cmd)

    connection.commit()
    connection.close()

    return None



def connect_db(dbname):
    connection = sqlite3.connect(dbname)
    cursor = connection.cursor()
    return connection, cursor

def query_db(query_string):
    data_dir = 'mosdef_dv_data'
    dbname = data_dir+'/dataviewer_catalog.db'

    exist = db_exist(dbname)
    # If the DB file exists, do the query....
    if exist: 
        connection, cursor = connect_db(dbname)

        # Get the list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = []
        for t in cursor.fetchall():
            tables.append(t[0])
        # Don't list SQLite's internal table
        tables[:] = (t for t in tables if t != "sqlite_sequence")

        sql_cmd = ""

        if query_string not in ("", " ", None):
            # Actual query string
            for i,t in enumerate(tables):
                if i == 0:
                    sql_cmd = sql_cmd + """SELECT * FROM %s WHERE %s """ %(t, query_string)
                if i>0:
                    sql_cmd = sql_cmd + """UNION SELECT * FROM %s WHERE %s """ %(t, query_string)
        else:
            # Null query string
            for i,t in enumerate(tables):
                if i == 0:
                    sql_cmd = sql_cmd + """SELECT * FROM %s """ % t
                if i>0:
                    sql_cmd = sql_cmd + """UNION SELECT * FROM %s """ % t


        try:
            cursor.execute(sql_cmd)
            db_info = array(cursor.fetchall())

            # Format of output:

            # First is the sql id number
            keys = [ 'id', \
                    'maskname', 'objID', \
                    'primaryID', 'aperture_no', \
                    'field', \
                    'ra', 'dec', \
                    'spec1d_file_k', 'spec2d_file_k', \
                    'spec1d_file_h', 'spec2d_file_h', \
                    'spec1d_file_j', 'spec2d_file_j', \
                    'spec1d_file_y', 'spec2d_file_y', \
                    'hst_file']

            # Store info into an array of dicts
            info = []
            for i in range(len(db_info[:,0])):
                r = db_info[i,:]
                td = dict(zip(keys, r.T))

                # Change the datatypes
                td['id'] = np.int64(td['id'])
                td['objID'] = np.int64(td['objID'])
                td['primaryID'] = np.int64(td['primaryID'])
                td['aperture_no'] = np.int64(td['aperture_no'])
                td['ra'] = np.float64(td['ra'])
                td['dec'] = np.float64(td['dec'])
                
                # Append it to the data structure
                info.append(td)

        except:
            # In case it fails...
            info = None

        connection.close()

    # Case: db doesn't exist:
    else:
        info = None


    return info



