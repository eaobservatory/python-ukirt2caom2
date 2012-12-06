#!/usr/bin/env python

import sys
from codecs import latin_1_decode
from re import sub
from subprocess import Popen, PIPE

from astropy.io.fits import Header

class UkirtHeader(Header):
    """Class for handling FITS headers from UKIRT data."""

    def get_object(self):
        """Fetch the source name.

        Various characters are replaced by underscores."""

        return sub('[^-_+,.A-Za-z0-9]', '_', self['OBJECT'])

def read_header(filename):
    """Uses the KAPPA fitslist command to fetch the FITS header.

    Returns a UkirtHeader (subclass for astropy.io.fits.Header)."""

    try:
        p = Popen('${KAPPA_DIR}/fitslist ' + filename, shell=True, stdout=PIPE)

        (stdout, stderr) = p.communicate()

        if p.returncode == 0:
            header = latin_1_decode(stdout, 'replace')[0]

            return UkirtHeader.fromstring(header, sep='\n')

        else:
            print(sys.argv[0] + ': failed to read headers')
            exit(1)

    except OSError:
        print(sys.argv[0] + ': failed to execute command')
        exit(1)

if __name__ == '__main__':
    filename = sys.argv[1]
    hdr = read_header(filename)
    print(repr(hdr))
