from logging import getLogger

from caom2 import Instrument
from jcmt2caom2.raw import keywordvalue

from ukirt2caom2 import IngestionError
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT
from ukirt2caom2.util import clean_header

logger = getLogger(__name__)

class ObservationCGS4(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('cgs4')

        self.caom2.instrument = instrument

        # CVF

        cvf = headers[0]['CVF']

        if cvf.endswith('__'):
            cvf = cvf[:-2].rstrip()

        instrument.keywords.append(keywordvalue('cvf', cvf))

        # Filter

        filter = headers[0]['FILTERS']

        if filter == '?:?':
            filter = None

        # TODO split off ND / prism / pol suffix ?

        self.__filter = filter

        # Grating

        grating = headers[0]['GRATING']

        if grating == '' or grating == 'Undefined':
            grating = None

        if grating is not None:
            instrument.keywords.append(keywordvalue('grating', grating))

        self.__grating = grating

    def get_spectral_wcs(self, headers):
        return None

    def get_spatial_wcs(self, headers, translated):
        return None

    def get_polarization_wcs(self, headers):
            return None

instrument_classes['cgs4'] = ObservationCGS4
