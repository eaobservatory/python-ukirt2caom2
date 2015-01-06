from logging import getLogger

from caom2 import Instrument
from ukirt2caom2.keywordvalue import keywordvalue

from ukirt2caom2 import IngestionError
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT
from ukirt2caom2.instrument.rutstartend import rut_start_end
from ukirt2caom2.util import clean_header, normalize_detector_name

logger = getLogger(__name__)

# List of CGS4 filters with the 50% cut-on and cut-off points, full name
# and line wavelength for narrow filters.
cgs4_filters = {
        'IJ':        (0.84,  1.04,  'IJ',              None), #0.94),

        'B1':        (0.99,  1.59,  'B1',              None), #1.29),
        'B2':        (1.43,  2.60,  'B2',              None), #2.02),
        'B3':        (2.14,  4.16,  'B3',              None), #3.15),
        'B4':        (2.75,  4.24,  'B4',              None), #3.50),
        'B5':        (4.35,  5.5,   'B5',              None), #4.92),
        'B6':        (2.00,  2.41,  'B6',              None), #2.21),
        'B7':        (None,  None,  'B7',              None), #None),

        'N1':        (1.078, 1.099, 'N1',              None), #1.089),
        'N2':        (1.218, 1.240, 'N2',              None), #1.229),
        'N3':        (1.247, 1.272, 'N3',              None), #1.259),
        'N4':        (1.264, 1.286, 'N4',              None), #1.275),
        'N5':        (1.283, 1.305, 'N5',              None), #1.293),

        'blank':     (None,  None,  'Blank',           None),
        'open':      (None,  None,  'Open',            None),
        'lens':      (None,  None,  'Lens',            None),
        'Blanks':    (None,  None,  'Blank',           None),
}

class ObservationCGS4(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('CGS4')

        self.caom2.instrument = instrument

        # CVF
        if 'CVF' in headers[0]:
            cvf = headers[0]['CVF']

            if cvf.endswith('__'):
                cvf = cvf[:-2].rstrip()

            instrument.keywords.append(keywordvalue('cvf', cvf))

        # Filter

        if 'FILTERS' in headers[0]:
            filter = headers[0]['FILTERS']
        else:
            filter = None

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

        if 'GRATING' in headers[0]:
            grating = headers[0]['GRATING']
        else:
            grating = None

        if grating in ('', 'Undefined'):
            grating = None

        if grating is not None:
            instrument.keywords.append(keywordvalue('grating', grating))

        self.__grating = grating

        if 'GORDER' in headers[0]:
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

        if 'DETECTOR' in headers[0]:
            detector = normalize_detector_name(headers[0]['DETECTOR'])
        else:
            detector = None

        if detector is not None:
            instrument.keywords.append(keywordvalue('detector', detector))

    def get_spectral_wcs(self, headers):
        return None

    def get_spatial_wcs(self, headers, translated):
        return None

    def get_polarization_wcs(self, headers):
        return None

    def get_temporal_wcs(self, headers):
        # First try the regular method, via the DATE-OBS/END headers:
        wcs = ObservationUKIRT.get_temporal_wcs(self, headers)
        if wcs is not None:
            return wcs

        # Otherwise try RUTSTART/RUTEND:
        return rut_start_end(self.date, headers)

instrument_classes['cgs4'] = ObservationCGS4
