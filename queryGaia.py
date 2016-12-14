"""
Script to query the GAIA catalogue for parallaxes

TODO: Take the IRFM theta values from Barry and
      calculate the stellar radii of any matches found
"""
import os
import re
import argparse as ap
from collections import OrderedDict
import astropy.units as u
from astropy.coordinates import SkyCoord, Angle
from astroquery.vizier import Vizier

# pylint: disable = invalid-name

GAIA_CATALOGUE_ID = 'I/337/tgasptyc'

def argParse():
    """
    Parse the command line arguments
    """
    parser = ap.ArgumentParser()
    parser.add_argument('swasp_id',
                        help='swasp_id to cross match with GAIA. This '
                             'can also be a path to a text file containing 1 '
                             'swasp_id per line')
    parser.add_argument('--radius',
                        help='search radius in arcsec',
                        type=int,
                        default=5)
    return parser.parse_args()

def swaspIdToSkyCoord(swasp_id):
    """
    Convert a swasp_id to SkyCoord object

    Parameters
    ----------
    swasp_id : str
        ID of the swasp object

    Returns
    -------
    coords : astropy.coordinates.SkyCoord
        SkyCoord object for the given swasp_id

    Raises
    ------
    None
    """
    # set up a regex string for the swasp_id format
    p = re.compile(r'1SWASPJ(?P<ra1>\d\d)(?P<ra2>\d\d)(?P<ra3>\d\d.\d\d)(?P<dec1>.\d\d)(?P<dec2>\d\d)(?P<dec3>\d\d.\d)')
    match = re.findall(p, swasp_id)[0]
    if len(match) == 6:
        ra = ":".join(match[:3])
        dec = ":".join(match[3:])
        coords = SkyCoord(ra=ra, dec=dec, unit=(u.hourangle, u.degree), frame='icrs')
    else:
        coords = None
    return coords

def queryGaiaAroundSwaspId(swasp_id, radius):
    """
    Query GAIA around the coordinates of a given
    SuperWASP object

    Parameters
    ----------
    swasp_id : str
        SuperWASP object ID, e.g. 1SWASPJ102030.65+222839.0
    radius : int
        Search radius in arcsec

    Returns
    -------
    objects : array-like
        Dictionary of matching objects. Returns empty OrderedDict
        if nothing is found

    Raises
    ------
    None
    """
    coordinates = swaspIdToSkyCoord(swasp_id)
    objects = OrderedDict()
    if coordinates:
        vizier = Vizier(columns = ['TYC', 'HIP', '_RAJ2000', '_DEJ2000', 'Plx', 'e_Plx',
                                   'pmRA', 'pmDE', 'Source'],
                       keywords=['optical'])
        vizier.ROW_LIMIT = -1
        results = vizier.query_region(coordinates,
                                      radius=Angle(radius*u.arcsec),
                                      catalog=GAIA_CATALOGUE_ID)
        for result in results[0]:
            print(result)
            objects[result['Source']] = {'tyc': result['TYC'],
                                         'hip': result['HIP'],
                                         'ra': result['_RAJ2000'],
                                         'dec': result['_DEJ2000'],
                                         'plx': result['Plx'],
                                         'eplx': result['e_Plx'],
                                         'pmra': result['pmRA'],
                                         'pmdec': result['pmDE']}
    return objects

if __name__ == "__main__":
    args = argParse()
    swasp_ids = []
    matches = OrderedDict()
    if os.path.exists(args.swasp_id):
        f = open(args.swasp_id, 'r').readlines()
        for obj in f:
            swasp_ids.append(obj.rstrip())
    else:
        swasp_ids = [args.swasp_id]
    for swasp_id in swasp_ids:
        print('\nQuerying GAIA for {}:'.format(swasp_id))
        matches[swasp_id] = queryGaiaAroundSwaspId(swasp_id, args.radius)


