from logging import getLogger

from jcmt2caom2.raw import keywordvalue

from ukirt2caom2 import IngestionError
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT
from ukirt2caom2.instrument.rutstartend import rut_start_end
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
        '1.57c':      (1.560, 1.580, '1.57(cont)[MK]',  None), #1.57),
        '2.122S1':    (2.109, 2.129, '2.122(S1)',       2.122),
        '2.1c':       (2.092, 2.112, '2.1(cont)',       None), #2.100),
        '2.248S1':    (2.23,  2.27,  '2.248(S1)',       2.248),
        '2.2c':       (None,  None,  '2.2(cont)',       None), #2.200),
        '3.4nbL':     (None,  None,  '3.4nbL',          None), #3.4),
        '3.5mbL':     (None,  None,  '3.5mbL',          None), #3.5),
        '3.6nbLp':    (None,  None,  "3.6nbL'",         None), #3.6),
        '4.0c':       (None,  None,  '4.0(cont)',       None), #4.000),
        'BrA':        (None,  None,  'BrA',             4.0),
        'BrG':        (None,  None,  'BrG',             2.0),
        'BrGz':       (None,  None,  '2.181(BrGz)',     2.181),
        'CO1%':       (None,  None,  'CO(1%)',          None), # Same as 2.32(CO-1%) ?
        'CO4%':       (None,  None,  'CO(4%)',          None), # Same as 2.42(CO) ?
        'Dust':       (3.250, 3.305, '3.28(dust)',      3.28),
        'FeII':       (1.636, 1.652, '1.644(FeII)[MK]', 1.644),
        'H':          (1.538, 1.805, 'H',               None), #1.671),
        'H98':        (1.487, 1.780, 'H[MK]',           None), #1.635),
        'Ice':        (3.085, 3.115, '3.10(ice)',       3.1),
        'J':          (1.137, 1.354, 'J',               None), #1.245),
        'J98':        (1.165, 1.329, 'J[MK]',           None), #1.250),
        'K':          (2.018, 2.409, 'K',               None), #2.213),
        'K98':        (2.028, 2.362, 'K[MK]',           None), #2.150),
        'Longmore':   (None,  None,  'Longmore',        None),
        'Lp':         (None,  None,  "L'",              None),
        'Lp98':       (3.428, 4.108, "L'[MK]",          None), #3.6),
        'Mp98':       (4.572, 4.800, "M'[MK]",          None), #4.800),
        'S(1)':       (None,  None,  'S(1)',            None), # Same as 2.122(S1) ?
        'S(1)2-1':    (None,  None,  'S(1)2-1',         None), # Same as 2.122(S1) ?
        'S(1)z':      (None,  None,  'S(1)z',           2.136), # Same as 2.122(S1) ?
        'nbM':        (None,  None,  'nbM',             None),
}

# Assumed filter aliases:
for (alias, filter) in (
                           ('nbL', '3.4nbL'),
                           ('S1z', 'S(1)z'),
                       ):
    ircam_filters[alias] = ircam_filters[filter]

class ObservationIRCAM(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('IRCAM3')

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

    def get_temporal_wcs(self, headers):
        return rut_start_end(self.date, headers)

instrument_classes['ircam'] = ObservationIRCAM
