from logging import getLogger
import re

from caom2 import Instrument
from jcmt2caom2.raw import keywordvalue

from ukirt2caom2 import IngestionError
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT
from ukirt2caom2.util import clean_header

logger = getLogger(__name__)

def parse_filter(value):
    """Attempt to interpret name of Michelle filter."""

    m = re.match('^([EIF])(P?)(\d+)B(\d+)$', value)

    if m is None:
        return (None, None)

    (prefix, pol, centre, bandpass) = m.groups()

    name = 'F{}B{}'.format(centre, bandpass)

    pol = pol == 'P'

    centre = float(centre) / 10.0 # um
    bandpass = float(bandpass) / 100.0 # %

    cut_on = centre - 0.5 * centre * bandpass
    cut_off = centre + 0.5 * centre * bandpass

    return ((cut_on, cut_off, name), pol)

class ObservationMichelle(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('michelle')

        self.caom2.instrument = instrument

        # Detector mode

        if 'DETMODE' in headers[0]:
            instrument.keywords.append(keywordvalue('detector_mode',
                                       headers[0]['DETMODE'].lower()))
        elif 'DET_MODE' in headers[0]:
            instrument.keywords.append(keywordvalue('detector_mode',
                                       headers[0]['DET_MODE'].lower()))

        # Camera mode: imaging / spectroscopy / targetAcq
        # also stored in the object as self.__camera

        if 'INSTMODE' in headers[0]:
            camera = headers[0]['INSTMODE'].lower()
        elif 'CAMERA' in headers[0]:
            camera = headers[0]['CAMERA'].lower()
        else:
            logger.warning('Instrument mode not found')
            camera = None

        if camera == '':
            camera = None

        if camera is not None:
            instrument.keywords.append(keywordvalue('mode', camera))

        self.__camera = camera

        # Filter Wheel

        (filter, pol) = parse_filter(headers[0]['FILTER'])

        self.__filter = filter
        self.__pol = pol

        instrument.keywords.append(keywordvalue('pol',
                                   'true' if pol else 'false'))

        # Grating Drum

        grating = headers[0]['GRATNAME']

        if grating in ('', 'undefined'):
            grating = None

        if grating is not None:
            instrument.keywords.append(keywordvalue('grating', grating))

        self.__grating = grating

        # Slit Wheel

        slit = headers[0]['SLITNAME']

        if slit == '':
            slit = None

        if slit is not None:
            instrument.keywords.append(keywordvalue('slit', slit))

        self.__slit = slit

        # Cal / Pol unit

        calpol = headers[0].get('CALSELN', None)

        if calpol is not None:
            instrument.keywords.append(keywordvalue('cal_pol', calpol))

        self.__calpol = calpol

    def get_spectral_wcs(self, headers):
        return None

    def get_spatial_wcs(self, headers, translated):
        return None

    def get_polarization_wcs(self, headers):
        return None

instrument_classes['michelle'] = ObservationMichelle
