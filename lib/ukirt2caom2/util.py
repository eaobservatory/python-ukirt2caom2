#!/usr/bin/env python

from math import asin, degrees
from re import sub

def airmass_to_elevation(airmass):
    """Converts an airmass to elevation in degrees."""

    if airmass == 0:
        return None

    return degrees(asin(1.0 / airmass))

def valid_object(object):
    """Various characters are replaced by underscores."""

    return sub('[^-_+,.A-Za-z0-9]', '_', object)

def clean_header(header):
    """Sometimes headers have trailing junk."""

    return header.partition(' ')[0]
