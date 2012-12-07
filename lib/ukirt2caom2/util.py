#!/usr/bin/env python

from math import asin, degrees

def airmass_to_elevation(airmass):
    """Converts an airmass to elevation in degrees."""

    return degrees(asin(1.0 / airmass))
