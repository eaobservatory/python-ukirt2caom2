from datetime import datetime
from logging import getLogger

from caom2 import Instrument
from caom2.caom2_enums import ObservationIntentType
from caom2.wcs.caom2_axis import Axis
from caom2.wcs.caom2_coord_axis1d import CoordAxis1D
from caom2.wcs.caom2_coord_range1d import CoordRange1D
from caom2.wcs.caom2_ref_coord import RefCoord
from caom2.wcs.caom2_temporal_wcs import TemporalWCS

from ukirt2caom2.keywordvalue import keywordvalue
from tools4caom2.mjd import utc2mjd

from ukirt2caom2 import IngestionError
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT
from ukirt2caom2.util import clean_header

logger = getLogger(__name__)

# List of CGS3 filters.
cgs3_filters = {
        '7-14UM':     (7.0,   14.0,  '7-14um',          None),
        '7-22FKS':    (7.0,   22.0,  '7-22um[FKS]',     None),
        '7-22NEI':    (7.0,   22.0,  '7-22um[NEI]',     None),
        '8-12UM':     (8.0,   12.0,  '8-12um',          None),
        '15-24UM':    (15.0,  24.0,  '15-24um',         None),
        'K':          (None,  None,  'K[CGS3]',         None), # Not to be confused with the normal K

        'BLANK':      (None,  None,  'Blank',           None),
}

class ObservationCGS3(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('CGS3')

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

        grating = headers[0]['C3GRAT'].lower()

        instrument.keywords.append(keywordvalue('grating', grating))

        self.__grating = grating

        # Chopper

        instrument.keywords.append(keywordvalue('chopper', self.__chopper))

    def ingest_type_intent(self, headers):
        # CGS3 needs a custom version of this method as it
        # does not have an OBSTYPE header.  It looks like
        # we need to guess from the object name, but all
        # entries with chopper == 'sector' are probably calibrations.

        self.__chopper = headers[0]['C3CHOPPR'].lower()

        krypton = ('arc', 'kr', 'krypton', 'krpton', 'kr_lamp', 'lamp')

        object = headers[0]['OBJECT']

        if object.lower() in krypton:
            type = 'arc'

        elif object.startswith('SKY for'):
            type = 'sky'

            if self.__chopper == 'secondary':
                logger.warning('SKY in non-secondary chopping')

        else:
            type = 'object'

            if self.__chopper != 'secondary':
                logger.warning('Unknown object ' + object + ' in non-secondary chopping')

        # Add the data to the CAOM-2 object

        self.caom2.obs_type = type

        if type == 'object':
            self.caom2.intent = ObservationIntentType.SCIENCE

        else:
            self.caom2.intent = ObservationIntentType.CALIBRATION

        self.obstype = type

    def get_spectral_wcs(self, headers):
        filter = headers[0]['C3FILT']
        wavelength = headers[0]['C3WAVE']

        return None

    def get_spatial_wcs(self, headers, translated):
        return None

    def get_polarization_wcs(self, headers):
        return None

    def get_temporal_wcs(self, headers):
        if 'UTSTART' in headers[0] and 'UTEND' in headers[0]:
            time_start = self.parse_time(headers[0]['UTSTART'])
            time_end = self.parse_time(headers[0]['UTEND'])

            if time_start is not None and time_end is not None:
                date_start = datetime.combine(self.date.date(), time_start)
                date_end = datetime.combine(self.date.date(), time_end)

                time = CoordAxis1D(Axis('TIME', 'd'))
                time.range = CoordRange1D(
                        RefCoord(0.5, utc2mjd(date_start)),
                        RefCoord(1.5, utc2mjd(date_end)))

                return TemporalWCS(time, 'UTC')

        return None

    def parse_time(self, time_str):
        try:
            return datetime.strptime(time_str, '%H:%M:%S').time()

        except ValueError:
            return None

instrument_classes['cgs3'] = ObservationCGS3
