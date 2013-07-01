#!/usr/bin/env python

from codecs import ascii_encode
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

    if header.endswith('_'):
        header = header[:-1]

    return header.partition(' ')[0]

def document_to_ascii(doc):
    """Convert unicode in the headers to ASCII.

    Because we can't use an up to date version of Python with
    Sybase we need to convert unicode documents back to
    ASCII.  However it only seems necessary to alter the
    values, not the card names.

    Alters the supplied document in place and
    doesn't return anything."""

    for hdr in doc['headers']:
        cards = hdr.keys()

        for card in cards:
            val = hdr[card]

            if type(val) == unicode:
                hdr[card] = ascii_encode(val)[0]

    for key in doc:
        if key != 'headers':
            val = doc[key]
            if type(val) == unicode:
                doc[key] = ascii_encode(val)[0]

def normalize_detector_name(detector):
    if detector in (None, 'Detectorname', 'undefined', ''):
        return None

    # Assuming the 0 is not signficant.
    if detector == 'fpa046':
        return 'FPA46'

    return detector.replace(' ', '').replace('_', '').upper()
