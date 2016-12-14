"""
Script to query the GAIA catalogue for parallaxes
"""
import os
import re
import argparse as ap
from collections import OrderedDict
import astropy.units as u
from astropy.coordinates import SkyCoord, Angle
from astroquery.vizier import Vizier

# pylint: disable = invalid-name
# pylint: disable = redefined-outer-name
# pylint: disable = no-member
# pylint: disable = undefined-loop-variable

GAIA_CATALOGUE_ID = 'I/337/tgasptyc'

def argParse():
    """
    Parse the command line arguments

    Parameters
    ----------
    None

    Returns
    -------
    args : array-like
        Parsed ArgumentParser object containing the
        command line arguments

    Raises
    ------
    None
    """
    parser = ap.ArgumentParser()
    parser.add_argument('swasp_id',
                        help='swasp_id to cross match with GAIA. This '
                             'can also be a path to a text file containing a '
                             'swasp_id and IRFM theta pair per line. If theta is '
                             'unknown, insert a minus number instead')
    parser.add_argument('--theta',
                        help='IRFM theta value (mas). If supplying swasp_ids in a text '
                             'file put the corresponding theta value on the same '
                             'line as the swasp_id separated by a space. Insert a '
                             'minus number if theta is unknown')
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
    p = re.compile(r'1SWASPJ(?P<ra1>\d\d)(?P<ra2>\d\d)(?P<ra3>\d\d.\d\d)'
                   r'(?P<dec1>.\d\d)(?P<dec2>\d\d)(?P<dec3>\d\d.\d)')
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
        vizier = Vizier(columns=['TYC', 'HIP', '_RAJ2000', '_DEJ2000', 'Plx', 'e_Plx',
                                 'pmRA', 'pmDE', 'Source'],
                        keywords=['optical'])
        vizier.ROW_LIMIT = -1
        results = vizier.query_region(coordinates,
                                      radius=Angle(radius*u.arcsec),
                                      catalog=GAIA_CATALOGUE_ID)
        for result in results[0]:
            objects[result['Source']] = {'tyc': result['TYC'],
                                         'hip': result['HIP'],
                                         'ra': round(float(result['_RAJ2000']), 8),
                                         'dec': round(float(result['_DEJ2000']), 8),
                                         'plx': round(float(result['Plx']), 4),
                                         'eplx': round(float(result['e_Plx']), 4),
                                         'pmra': round(float(result['pmRA']), 4),
                                         'pmdec': round(float(result['pmDE']), 4)}
    return objects

def rStar(theta, parallax):
    """
    Calculate r_star from IRFM theta and parallax

    Parameters
    ----------
    theta : float
        IRFM theta value from SWASP paramfit (mas, from Barry Smalley)
    parallax : float
        GAIA parallax (mas)

    Returns
    -------
    r_star : float
        Stellar radius in R_sun

    Raises
    ------
    None
    """
    r_star = 214.9*(theta/2.)/parallax
    return r_star

if __name__ == "__main__":
    args = argParse()
    swasp_ids, thetas = [], []
    matches = OrderedDict()
    if os.path.exists(args.swasp_id):
        f = open(args.swasp_id, 'r').readlines()
        for line in f:
            obj, theta = line.split()
            swasp_ids.append(obj)
            if float(theta) > 0:
                thetas.append(float(theta))
            else:
                thetas.append(None)
    else:
        swasp_ids = [args.swasp_id]
        if args.theta:
            thetas = [args.theta]
        else:
            thetas = [None]

    # loop over the objects and get the matches
    # and r_stars for any matches
    for swasp_id, theta in zip(swasp_ids, thetas):
        print('\nQuerying GAIA for {}:'.format(swasp_id))
        print('ID                   TYC        RA           DEC          '
              'PMRA      PMDEC  PLX    ePLX   RSTAR')
        matches[swasp_id] = queryGaiaAroundSwaspId(swasp_id, args.radius)
        for match in matches[swasp_id]:
            parallax = matches[swasp_id][match]['plx']
            if theta:
                r_star = rStar(theta, parallax)
                matches[swasp_id][match]['rstar'] = round(float(r_star), 4)
            else:
                matches[swasp_id][match]['rstar'] = -1
        print("{:<20} {:<10} {:<12} {:<12} {:<9} \
              {:<6} {:<6} {:<6} {:<6}".format(match,
                                              matches[swasp_id][match]['tyc'].decode('ascii'),
                                              matches[swasp_id][match]['ra'],
                                              matches[swasp_id][match]['dec'],
                                              matches[swasp_id][match]['pmra'],
                                              matches[swasp_id][match]['pmdec'],
                                              matches[swasp_id][match]['plx'],
                                              matches[swasp_id][match]['eplx'],
                                              matches[swasp_id][match]['rstar']))


