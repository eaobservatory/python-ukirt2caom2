#!/usr/bin/env python

import palpy as pal

def is_not_none(value):
    return value is not None

class CoordFK5():
    """Class providing coordinate utilities as required
    by ukirt2caom2."""

    def __init__(self, ra_deg=None, ra_rad=None, ra_h=None,
                       dec_deg=None, dec_rad=None):
        if len(filter(is_not_none, (ra_deg, ra_rad, ra_h))) != 1 \
        or len(filter(is_not_none, (dec_deg, dec_rad))) != 1:
            raise Exception('Coordinates not properly specified')

        if ra_deg is not None:
            self.ra = ra_deg * pal.DD2R

        elif ra_h is not None:
            self.ra = ra_h * pal.DD2R * 15

        else:
            self.ra = ra_rad

        if dec_deg is not None:
            self.dec = dec_deg * pal.DD2R

        else:
            self.dec = dec_rad

    def offset(self, dra_deg, ddec_deg):
        (ra, dec) = pal.dtp2s(dra_deg * pal.DD2R, ddec_deg * pal.DD2R, self.ra, self.dec)

        return CoordFK5(ra_rad=ra, dec_rad=dec)

    def rad(self):
        return (self.ra, self.dec)

    def deg(self):
        return (self.ra / pal.DD2R, self.dec / pal.DD2R)
