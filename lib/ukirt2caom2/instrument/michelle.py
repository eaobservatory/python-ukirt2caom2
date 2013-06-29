from logging import getLogger

from caom2 import Instrument
from jcmt2caom2.raw import keywordvalue

from ukirt2caom2 import IngestionError
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT
from ukirt2caom2.util import clean_header

logger = getLogger(__name__)

class ObservationMichelle(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('michelle')

        self.caom2.instrument = instrument

        # Detector mode

        if 'DETMODE' in headers[0]:
            instrument.keywords.append(keywordvalue('mode',
                                       headers[0]['DETMODE'].lower()))
        elif 'DET_MODE' in headers[0]:
            instrument.keywords.append(keywordvalue('mode',
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
            instrument.keywords.append(keywordvalue('camera', camera))

        self.__camera = camera

    def get_spectral_wcs(self, headers):
        return None

    def get_spatial_wcs(self, headers, translated):
        return None

    def get_polarization_wcs(self, headers):
            return None

instrument_classes['michelle'] = ObservationMichelle
