from logging import getLogger

from jcmt2caom2.raw import keywordvalue

from ukirt2caom2 import IngestionError
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT
from ukirt2caom2.util import clean_header, normalize_detector_name
from caom2 import Instrument
from caom2.caom2_enums import ObservationIntentType
from caom2.wcs.caom2_axis import Axis
from caom2.wcs.caom2_coord_axis1d import CoordAxis1D
from caom2.wcs.caom2_coord_range1d import CoordRange1D
from caom2.wcs.caom2_ref_coord import RefCoord
from caom2.wcs.caom2_spectral_wcs import SpectralWCS


logger = getLogger(__name__)

# Filter details (cut-on, cut-off, name, centre)
ircam_filters = {
        '1.57c':      (1.560, 1.580, '1.57cont98(MK)',  1.57),
        '2.122S1':    (2.109, 2.129, '2.122(S1)',       2.122),
        '2.1c':       (2.092, 2.112, '2.1cont',         2.100),
        '2.248S1':    (2.23, 2.27,   '2.248S1',         2.248),
        '2.2c':       (None,  None,  '2.2c',            2.200),
        '3.4nbL':     (None,  None,  '3.4nbL',          3.4),
        '3.5mbL':     (None,  None,  '3.5mbL',          3.5),
        '3.6nbLp':    (None,  None,  '3.6nbLp',         3.6),
        '4.0c':       (None,  None,  '4.0c',            4.000),
        'BrA':        (None,  None,  'BrA',             4.0),
        'BrG':        (None,  None,  'BrG',             2.0),
        'BrGz':       (None,  None,  '2.181(BrGz)',     2.181),
#       'CO1%':       (),
#       'CO4%':       (),
        'Dust':       (3.250, 3.305, '3.28"dust"',      3.28),
        'FeII':       (1.636, 1.652, '1.644FeII98(MK)', 1.644),
#       'H':          (),
        'H98':        (1.487, 1.780, 'H98(MK)',         1.635),
        'Ice':        (3.085, 3.115, '3.10"ice"',       3.1),
#       'J':          (),
        'J98':        (1.165, 1.329, 'J98(MK)',         1.250),
#       'K':          (),
        'K98':        (2.028,2.362,  'K98(MK)',         2.150),
#       'Longmore':   (),
#       'Lp':         (),
        'Lp98':       (3.428, 4.108, "L'98(MK)",        3.6),
        'Mp98':       (4.572, 4.800, "M'98(MK)",        4.800),
#       'S(1)':       (),
#       'S(1)2-1':    (),
        'S(1)z':      (None,  None,  'S(1)z',           2.136),
#       'S1z':        (),
#       'nbM':        (),
}

# Assumed filter aliases:
for (alias, filter) in (
                           ('nbL', '3.4nbL'),
                       ):
    ircam_filters[alias] = ircam_filters[filter]

class ObservationIRCAM(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('ircam')

        self.caom2.instrument = instrument

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

        if filter in ircam_filters:
            self.__filter = ircam_filters[filter]
        else:
            self.__filter = (None, None, filter, None)

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

    def ingest_type_intent(self, headers):
        super(ObservationIRCAM, self).ingest_type_intent(headers)
        if 'OBJECT' in headers[0]:
            if headers[0]['OBJECT'] == 'Array Tests':
                self.caom2.intent = ObservationIntentType.CALIBRATION

    def get_spectral_wcs(self, headers):
        (cut_on, cut_off, filter_name, wavelength) = self.__filter

        if cut_on is None or cut_off is None:
            logger.warning('Using default filter cut on and off for "{}"'.format(filter_name))
            (cut_on, cut_off) = (1.0, 5.0) # From IRCAM website

        axis = CoordAxis1D(Axis('WAVE', 'm'))
        axis.range = CoordRange1D(RefCoord(0.5, 1.0e-6 * cut_on),
                                  RefCoord(1.5, 1.0e-6 * cut_off))

        wcs = SpectralWCS(axis, 'TOPOCENT')
        wcs.ssysobs = 'TOPOCENT'

        if filter_name is not None:
            wcs.bandpass_name = filter_name

        if wavelength is not None:
            wcs.restwav = 1.0e-6 * wavelength

        return wcs

    def get_spatial_wcs(self, headers, translated):
        return None

    def get_polarization_wcs(self, headers):
        return None

instrument_classes['ircam'] = ObservationIRCAM
