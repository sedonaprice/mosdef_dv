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
from viewer_io import read_0d_cat, read_path, read_spec1d, read_parent_cat, get_tdhst_vers
import numpy as np

############################################################
# Basic functions: check if things exist, or delete them.
def ensure_dir(f):
    if not os.path.exists(f):
        os.makedirs(f)

def db_exist(dbname):
    exist = os.path.isfile(dbname)
    return exist

def db_delete(dbname):
    sys_cmd = 'rm %s' % dbname
    os.system(sys_cmd)
    return None
    
    
def read_extra1d_filename():
    ## Extra part of 1D filenames
    #extra_1d = 'ell'
    extra_1d = read_path('EXTRA_1D_END')
    if extra_1d is not None:
        extra_1d_list = extra_1d.split()
        if len(extra_1d_list) > 0:
            extra_1d = extra_1d_list[0]
        if extra_1d is not '':
            extra_1d_filename = '.'+extra_1d
        else:
            extra_1d_filename = extra_1d
    else:
        extra_1d = ''
        extra_1d_filename = extra_1d
    return extra_1d_filename
    
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
    #   FFZ_MM  : FF = field code (string), Z = redshift (int), MM = mask (??)


    # if len(maskname) != 6:
    #     print "maskname=", maskname
    #     raise Exception("Maskname has wrong length!")

    # Checked string is proper length
    ff = maskname[0:2]
    z = maskname[2]
    mm = maskname[4:]  #[4:6]

    field = field_short2long(ff)
    redshift = z # keep as a string: for filenames  # int(z) 
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
    files_2d = os.listdir(basedir_2d)
    
    # Returns all files:  including aperture number, bands, masknames, etc.
    
    all_df = pd.DataFrame({})
    for f in files:
        splt = re.split(r'\.', f.strip())
        if splt[-1].lower() != 'fits':
            pass
        else:
            try:
                if splt[-3] == extra_1d:
                    norm_len = 6
                else:
                    norm_len = 5
            except:
                # Only happens for random files.
                norm_len = 5
            if len(splt) == norm_len:
                # Format: mask.band.primID.2d.fits
                mask, band, prim_id = splt[0:3]
                aper_no = 1
                dfNew = pd.DataFrame({'maskname': mask, 
                                    'band': band,
                                    'primID': prim_id,
                                    'aper_no':aper_no},
                                    index=[0])
                all_df = all_df.append(dfNew, ignore_index=True)
            
            elif len(splt) == norm_len+1:
                # Format: mask.band.primID.aper_no.2d.fits
                mask, band, prim_id, aper_no = splt[0:4]
            
                # If it's a star: no serendip objects, aper_no = 1
                if prim_id[0].upper() == 'S':
                    aper_no = 1
            
                dfNew = pd.DataFrame({'maskname': mask, 
                                    'band': band,
                                    'primID': prim_id,
                                    'aper_no':aper_no},
                                    index=[0])
                all_df = all_df.append(dfNew, ignore_index=True)
            
            else:
                pass

    for f in files_2d:
        splt = re.split(r'\.', f.strip())
        if splt[-1].lower() != 'fits':
            pass
        else:
            try:
                if splt[-3] == extra_1d:
                    norm_len = 6
                else:
                    norm_len = 5
            except:
                # Only happens for random files.
                norm_len = 5
            if len(splt) == norm_len:
                # Format: mask.band.primID.2d.fits
                mask, band, prim_id = splt[0:3]
                aper_no = 1
                dfNew = pd.DataFrame({'maskname': mask, 
                                    'band': band,
                                    'primID': prim_id,
                                    'aper_no':aper_no},
                                    index=[0])
                all_df = all_df.append(dfNew, ignore_index=True)
            
            elif len(splt) == norm_len+1:
                # Format: mask.band.primID.aper_no.2d.fits
                mask, band, prim_id, aper_no = splt[0:4]
            
                # If it's a star: no serendip objects, aper_no = 1
                if prim_id[0] == 'S':
                    aper_no = 1
            
                dfNew = pd.DataFrame({'maskname': mask, 
                                    'band': band,
                                    'primID': prim_id,
                                    'aper_no':aper_no},
                                    index=[0])
                all_df = all_df.append(dfNew, ignore_index=True)
	    
            else:
                pass

    # DF containing unique objects:
    obj_df= all_df[['maskname','primID','aper_no']].copy()
    obj_df.drop_duplicates(inplace=True)

    
    filters = ['K','H','J','Y']
    
    
    cat = []
    ### Info that needs to be stored in DB
    keys = [ 'maskname', 'objID', \
            'primaryID', 'aperture_no', \
            'primaryIDv2', 'primaryIDv4', \
            'field', \
            'ra', 'dec', 'obj_type']
            
    # Add tdhst_vers in here???
            
    for i in xrange(len(filters)):
        keys.append('spec1d_file_'+filters[i].lower())
        keys.append('spec2d_file_'+filters[i].lower())
        
    keys.append('hst_file')
    
    field_cur = 'none'

    for ii in xrange(len(obj_df)):
        i = obj_df.index[ii]
        
        # Open MOSDEF parent catalog to try to get objID for objects that are not primary
        #mosdef_0d_cat = read_0d_cat()
        # Get field:
        try:
            field, z, mask = maskname_interp(obj_df.ix[i]['maskname'])
        except:
            print "failed!"
            print obj_df.ix[i]['maskname']
            print obj_df.ix[i]['band']
            print obj_df.ix[i]['primID']
            print obj_df.ix[i]['aper_no']
            raise ValueError
            
        if field != field_cur:
            try:
                mosdef_parent_cat = read_parent_cat(vers='4.1', field=field)
                field_cur = field
            except:
                mosdef_parent_cat = read_parent_cat(vers='2.1', field=field)
                field_cur = field
            
        ###############################
        # Get primary id number in integer:
        try:
            prim_id_name = np.int64(obj_df.ix[i]['primID'])
            obj_type = 'G'
        except:
            if obj_df.ix[i]['primID'][0] == 'S':
                # Has 'S' at the beginning of obj name
                prim_id_name = np.int64(obj_df.ix[i]['primID'][1:])
                obj_type = 'S'
            else:
                prim_id_name = np.int64(obj_df.ix[i]['primID'])[0]
                obj_type = '?'
                
                
        ###########################################
        # Prepare filenames:
        file_1d_base = obj_df.ix[i]['maskname']
        file_2d_base = obj_df.ix[i]['maskname']
        extra_1d_filename = read_extra1d_filename()
        if np.int(obj_df.ix[i]['aper_no']) == 1:
            file_1d_end = obj_df.ix[i]['primID']+extra_1d_filename+'.1d.fits'
            file_2d_end = obj_df.ix[i]['primID']+'.2d.fits'
            
            try:
                objID = np.int64(obj_df.ix[i]['primID'])
            except:
                objID = np.int64(obj_df.ix[i]['primID'][1:])
        else:
            file_1d_end = obj_df.ix[i]['primID']+'.'+obj_df.ix[i]['aper_no']+extra_1d_filename+'.1d.fits'
            file_2d_end = obj_df.ix[i]['primID']+'.2d.fits'
            
            # # Get identified objID if there is an entry in the master cat:
            # if wh is not None:
            #     objID = mosdef_0d_cat['ID'][wh]
            # else:
            objID = -99
        
        files_1d = []
        files_2d = []
        for f in filters:
            #print "file_1d_base, f, file_1d_end, basedir_1d=", file_1d_base, f, file_1d_end, basedir_1d
            file1d = const_filename(file_1d_base, f, file_1d_end, basedir_1d,dim=1)
            
            files_1d.append(file1d)
            
            file2d = const_filename(file_2d_base, f, file_2d_end, basedir_2d,dim=2)
            files_2d.append(file2d)
            
        
        ###############################
        # Get tdhst_version from 2D header:
        #raise ValueError
        tdhst_vers = None
        mm = -1
        while tdhst_vers is None:
            mm += 1
            if mm > len(files_1d)-1:
                break
                
            data, data_err, light_profile, hdr = read_spec1d(files_1d[mm])
            if hdr is not None:
                tdhst_vers = get_tdhst_vers(hdr)
                print "maskname, id=", obj_df.ix[i]['maskname'], prim_id_name
                
        
        # Get match from parent cat for v2, v4 ids:
        if tdhst_vers == '2.1':
            try:
                wh_prim = np.where(mosdef_parent_cat['ID_V21'] == prim_id_name)[0][0]
                prim_idv2 = prim_id_name
                prim_idv4 = mosdef_parent_cat['ID'].iloc[wh_prim]
            except:
                wh_prim = None
                prim_idv2 = prim_id_name
                prim_idv4 = -9999
        else:
            try:
                wh_prim = np.where(mosdef_parent_cat['ID'] == prim_id_name)[0][0]
                prim_idv4 = prim_id_name
                prim_idv2 = mosdef_parent_cat['ID_V21'].iloc[wh_prim]
            except:
                wh_prim = None
                prim_idv4 = prim_id_name
                prim_idv2 = -9999
            
        # Chosen to read in v4.1 catalog, so ref # is v4
        prim_id_ref = prim_idv4
        
        
        # Look for a match in 0D catalog:
        try:
            wh_prim = np.where(mosdef_parent_cat['ID'] == prim_id_ref)[0][0]
            if np.int64(obj_df.ix[i]['aper_no']) == 1:
                wh = wh_prim
            else:
                wh = None
                

        except:
            if obj_df.ix[i]['primID'][0] == 'S':
                # Has 'S' at the beginning of obj name
                try:
                    wh_prim = np.where(mosdef_parent_cat['ID'] == prim_id_ref)[0][0]
                    if np.int64(obj_df.ix[i]['aper_no']) == 1:
                        wh = wh_prim
                    else:
                        wh = None
                except:
                    wh = None
            else:
                wh = None
                
        
        # Temp
        hst_file = '-----'
        

        
        
        # Set ra, dec
        if wh is not None:
            ra, dec = mosdef_parent_cat['RA'].iloc[wh], mosdef_parent_cat['DEC'].iloc[wh]
        else:
            ra, dec = -99., -99.
        
        row = [obj_df.ix[i]['maskname'], objID, \
                prim_id_name, \
                np.int64(obj_df.ix[i]['aper_no']), \
                prim_idv2, prim_idv4, \
                field, \
                ra, dec, obj_type]
        for i in xrange(len(filters)):
                row.append(files_1d[i])
                row.append(files_2d[i])
                
        row.append(hst_file)

        td = dict(zip(keys,row))
        cat.append(td)
    
    return cat


############################


def write_cat_db():
    data_dir = 'mosdef_dv_data'
    ensure_dir(data_dir)

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
                primaryIDv2 INT, primaryIDv4 INT, 
                field TEXT, 
                ra FLOAT, dec FLOAT, 
                obj_type TEXT, 
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
                r['primaryIDv2'], r['primaryIDv4'], \
                r['field'], \
                r['ra'], r['dec'], \
                r['obj_type'], \
                r['spec1d_file_k'].encode('ascii', 'ignore'), r['spec2d_file_k'].encode('ascii', 'ignore'), \
                r['spec1d_file_h'].encode('ascii', 'ignore'), r['spec2d_file_h'].encode('ascii', 'ignore'), \
                r['spec1d_file_j'].encode('ascii', 'ignore'), r['spec2d_file_j'].encode('ascii', 'ignore'), \
                r['spec1d_file_y'].encode('ascii', 'ignore'), r['spec2d_file_y'].encode('ascii', 'ignore'), \
                r['hst_file'].encode('ascii', 'ignore') ]

        dat = tuple(list_dat)
        strdat = str(dat)


        sql_cmd = "INSERT INTO %s" % collname
        sql_cmd = (sql_cmd +  "(maskname, objID, primaryID, aperture_no, " +
                "primaryIDv2, primaryIDv4, " +
                "field, " + 
                "ra, dec, " + 
                "obj_type, "
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
                    'primaryIDv2', 'primaryIDv4', \
                    'field', \
                    'ra', 'dec', \
                    'obj_type', \
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
                td['primaryIDv2'] = np.int64(td['primaryIDv2'])
                td['primaryIDv4'] = np.int64(td['primaryIDv4'])
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



