from logging import getLogger

from caom2 import Instrument
from caom2.caom2_enums import ObservationIntentType
from jcmt2caom2.raw import keywordvalue

from ukirt2caom2 import IngestionError
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT
from ukirt2caom2.util import clean_header

logger = getLogger(__name__)

class ObservationCGS3(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('cgs3')

        self.caom2.instrument = instrument

        # Mode just distinguishes spectroscopy / spectropolarimetry.
        # Note that 'C3POL' header always agrees with this so we need
        # only read one.

        mode = headers[0]['MODE']

        if mode == 'LPCGS3':
            pol = True

        elif mode == 'ICGS3':
            pol = False

        else:
            logger.warning('Unknown mode ' + mode)
            pol = None

        if pol is not None:
            instrument.keywords.append(keywordvalue('pol',
                                       'true' if pol else 'false'))

        # Grating

        grating = headers[0]['C3GRAT']

        instrument.keywords.append(keywordvalue('grating', grating))

        self.__grating = grating

    def ingest_type_intent(self, headers):
        # CGS3 will need a custom version of this method as it
        # does not have an OBSTYPE header.
        pass

    def get_spectral_wcs(self, headers):
        filter = headers[0]['C3FILT']
        wavelength = headers[0]['C3WAVE']

        return None

    def get_spatial_wcs(self, headers, translated):
        return None

    def get_polarization_wcs(self, headers):
        return None

instrument_classes['cgs3'] = ObservationCGS3
