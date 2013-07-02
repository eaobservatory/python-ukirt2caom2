from logging import getLogger

from caom2 import Instrument
from jcmt2caom2.raw import keywordvalue

from ukirt2caom2 import IngestionError
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT
from ukirt2caom2.util import clean_header, normalize_detector_name

logger = getLogger(__name__)

class ObservationCGS4(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('cgs4')

        self.caom2.instrument = instrument

        if self.obstype is not None:
            instrument.keywords.append(keywordvalue('observation_type', self.obstype))

        # CVF

        cvf = headers[0]['CVF']

        if cvf.endswith('__'):
            cvf = cvf[:-2].rstrip()

        instrument.keywords.append(keywordvalue('cvf', cvf))

        # Filter

        filter = headers[0]['FILTERS']

        if filter == '?:?':
            filter = None

        self.__pol = False
        self.__prism = False

        if filter is None:
            pass

        elif filter.endswith('+ND'):
            filter = filter[:-3]

        elif filter.endswith('+prism'):
            filter = filter[:-6]
            self.__prism = True

        elif filter.endswith('+pol'):
            # Note 'POLARISE' header is useless, it only contains false or junk.
            filter = filter[:-4]
            self.__pol = True

        if filter == 'open':
            filter = None

        self.__filter = filter

        instrument.keywords.append(keywordvalue('pol',
                'true' if self.__pol else 'false'))
        instrument.keywords.append(keywordvalue('prism',
                'true' if self.__prism else 'false'))

        # Grating

        grating = headers[0]['GRATING']

        if grating in ('', 'Undefined'):
            grating = None

        if grating is not None:
            instrument.keywords.append(keywordvalue('grating', grating))

        self.__grating = grating

        self.__grating_order = headers[0]['GORDER']

        instrument.keywords.append(keywordvalue('grating_order',
                                                str(self.__grating_order)))

        # Detector mode

        if 'DET_MODE' in headers[0]:
            mode = headers[0]['DET_MODE']
        elif 'MODE' in headers[0]:
            mode = headers[0]['MODE']
        else:
            mode = None

        if mode is not None:
            # We see some modes with and without underscore
            mode = mode.replace('_', '').lower()

            instrument.keywords.append(keywordvalue('detector_mode', mode))

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

instrument_classes['cgs4'] = ObservationCGS4
