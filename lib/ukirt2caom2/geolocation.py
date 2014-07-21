from math import degrees

import palpy

from tools4caom2.geolocation import geolocation

def ukirt_geolocation():
    """Location of UKIRT as an (X, Y, Z) tuple.

    Takes the coordinates of UKIRT from PAL and converts
    them to X, Y, Z using jcmt2caom2.geolocation.

    Note: this routine swaps the sign of the longitude
    returned by PAL because PAL uses a west-positive
    convention whereas tools4caom2 appears to use
    east-positive."""

    ukirt = palpy.obs()['UKIRT']
    geo = geolocation(- degrees(ukirt['long']),
                       degrees(ukirt['lat']),
                       ukirt['height'])

    # Check sign convention!
    assert(geo[0] < 0.0)
    assert(geo[1] < 0.0)
    assert(geo[2] > 0.0)

    return geo

if __name__ == '__main__':
    print(repr(ukirt_geolocation()))
