from logging import getLogger

from caom2 import Instrument
from jcmt2caom2.raw import keywordvalue

from ukirt2caom2 import IngestionError
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT
from ukirt2caom2.util import clean_header, normalize_detector_name

logger = getLogger(__name__)

class ObservationIRCAM(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('ircam')

        self.caom2.instrument = instrument

        if self.obstype is not None:
            instrument.keywords.append(keywordvalue('observation_type', self.obstype))

        # Filter

        filter = clean_header(headers[0]['FILTER'])

        if filter.endswith('+pol'):
            pol = True
            filter = filter[:-4]
        else:
            pol = False

        if filter == 'Unknown':
            filter = None

        elif filter == 'Blanks':
            filter = 'Blank'

        self.__filter = filter

        instrument.keywords.append(keywordvalue('pol',
                                   'true' if pol else 'false'))

        # Magnifier

        if 'MAGNIFIE' in headers[0]:
            magnifier = clean_header(headers[0]['MAGNIFIE']).lower()

            instrument.keywords.append(keywordvalue('magnifier', magnifier))

        # Mode

        mode = headers[0]['MODE'].lower()

        instrument.keywords.append(keywordvalue('detector_mode', mode))

        # Speed

        if 'SPD_GAIN' in headers[0]:
            speed = headers[0]['SPD_GAIN'].lower()

            instrument.keywords.append(keywordvalue('speed_gain', speed))

        # Detector

        detector = normalize_detector_name(headers[0]['DETECTOR'])

        if detector is not None:
            instrument.keywords.append(keywordvalue('detector', detector))


    def get_spectral_wcs(self, headers):
        return None

    def get_spatial_wcs(self, headers, translated):
        return None

    def get_polarization_wcs(self, headers):
            return None

instrument_classes['ircam'] = ObservationIRCAM
