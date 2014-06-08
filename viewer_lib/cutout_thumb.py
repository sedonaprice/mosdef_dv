"""
======
Cutout
======

Modified from file from A Ginsburg:
https://code.google.com/p/agpy/source/browse/trunk/agpy/cutout.py

Generate a cutout image from a .fits file
"""
import astropy.io.fits as pyfits
import astropy.wcs as pywcs
import numpy


class DimensionError(ValueError):
    pass

def cutout(data, hdr, xc, yc, xw=25, yw=25, units='pixels', outfile=None,
        clobber=True, useMontage=False, coordsys='celestial', verbose=False):
    """
    Inputs:
        file  - .fits filename or pyfits HDUList (must be 2D)
        xc,yc - x and y coordinates in the fits files' coordinate system (CTYPE)
        xw,yw - x and y width (pixels or wcs)
        units - specify units to use: either pixels or wcs
        outfile - optional output file
    """

    # if isinstance(filename,str):
    #     file = pyfits.open(filename)
    #     opened=True
    # elif isinstance(filename,pyfits.HDUList):
    #     file = filename
    #     opened=False
    # else:
    #     raise Exception("cutout: Input file is wrong type (string or HDUList are acceptable).")
    # 
    # head = file[0].header.copy()
    hdr = head.copy()

    if head['NAXIS'] > 2:
        raise DimensionError("Too many (%i) dimensions!" % head['NAXIS'])
    cd1 = head.get('CDELT1') if head.get('CDELT1') else head.get('CD1_1')
    cd2 = head.get('CDELT2') if head.get('CDELT2') else head.get('CD2_2')
    if cd1 is None or cd2 is None:
        raise Exception("Missing CD or CDELT keywords in header")
    wcs = pywcs.WCS(head)




    xx,yy = wcs.wcs_sky2pix(xc,yc,0)

    if units=='pixels':
        xmin,xmax = numpy.max([0,xx-xw]),numpy.min([head['NAXIS1'],xx+xw])
        ymin,ymax = numpy.max([0,yy-yw]),numpy.min([head['NAXIS2'],yy+yw])
    elif units=='wcs':
        xmin,xmax = numpy.max([0,xx-xw/numpy.abs(cd1)]),numpy.min([head['NAXIS1'],xx+xw/numpy.abs(cd1)])
        ymin,ymax = numpy.max([0,yy-yw/numpy.abs(cd2)]),numpy.min([head['NAXIS2'],yy+yw/numpy.abs(cd2)])
    else:
        raise Exception("Can't use units %s." % units)

    if xmax < 0 or ymax < 0:
        raise ValueError("Max Coordinate is outside of map: %f,%f." % (xmax,ymax))
    if ymin >= head.get('NAXIS2') or xmin >= head.get('NAXIS1'):
        raise ValueError("Min Coordinate is outside of map: %f,%f." % (xmin,ymin))

    head['CRPIX1']-=xmin
    head['CRPIX2']-=ymin
    head['NAXIS1']=int(xmax-xmin)
    head['NAXIS2']=int(ymax-ymin)

    if head.get('NAXIS1') == 0 or head.get('NAXIS2') == 0:
        raise ValueError("Map has a 0 dimension: %i,%i." % (head.get('NAXIS1'),head.get('NAXIS2')))

    img = data[ymin:ymax,xmin:xmax]
    #img = file[0].data[ymin:ymax,xmin:xmax]
    #newfile = pyfits.PrimaryHDU(data=img,header=head)
    if verbose: print "Cut image %s with dims %s to %s.  xrange: %f:%f, yrange: %f:%f" % (filename, file[0].data.shape,img.shape,xmin,xmax,ymin,ymax)

    #if isinstance(outfile,str):
    #    newfile.writeto(outfile,clobber=clobber)

    #if opened:
    #    file.close()

    #return newfile
    return img, head