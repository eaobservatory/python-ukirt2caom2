from math import degrees

import palpy

from tools4caom2.geolocation import geolocation

def ukirt_geolocation():
    """Location of UKIRT as an (X, Y, Z) tuple.

    Takes the coordinates of UKIRT from PAL and converts
    them to X, Y, Z using jcmt2caom2.geolocation."""

    ukirt = palpy.obs()['UKIRT']
    return geolocation(degrees(ukirt['long']),
                       degrees(ukirt['lat']),
                       ukirt['height'])

if __name__ == '__main__':
    print(repr(ukirt_geolocation()))
