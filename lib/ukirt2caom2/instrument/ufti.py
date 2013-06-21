from caom2 import Instrument
from jcmt2caom2.raw import keywordvalue

from ukirt2caom2 import IngestionError
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT
from ukirt2caom2.util import clean_header
from caom2.wcs.caom2_axis import Axis
from caom2.wcs.caom2_coord_axis1d import CoordAxis1D
from caom2.wcs.caom2_coord_range1d import CoordRange1D
from caom2.wcs.caom2_ref_coord import RefCoord
from caom2.wcs.caom2_spectral_wcs import SpectralWCS

# List of UFTI filters with the 50% cut-on and cut-off points, full name
# and line wavelength for narrow filters.
ufti_filters = {
        '1.57':      (1.560, 1.580, '1.57(cont)[98]',  1.57),
        '1.644':     (1.636, 1.652, '1.644(FeII)[98]', 1.644),
        '1.69CH4_l': (1.617, 1.730, '1.69CH4_l',       1.69),
        '2.10':      (None,  None,  '2.1cont',         None), # 1998-2000
        '2.122':     (2.109, 2.129, '2.122(S1)',       2.122),
        '2.122MK':   (2.103, 2.134, '2.122MK',         2.122),
        '2.248MK':   (2.235, 2.270, '2.248MK',         2.248),
        '2.248S(1)': (None,  None,  '2.248(S1)',       2.248),
        '2.27':      (2.260, 2.280, '2.27cont[98]',    2.27),
        '2.32':      (2.310, 2.331, '2.32(CO-1%)',     2.32),
        '2.424':     (None,  None,  'Qbranch', None), # Not useable 1998-2000
        'BrG':       (2.155, 2.177, '2.166(BrG)[98]',  2.166),
        'BrGz':      (2.147, 2.199, '2.173(BrGz)',     2.173),
        'H98':       (1.49,  1.78,  'H[98]',           None),
        'I':         (0.785, 0.925, 'I',               None),
        'J98':       (1.17,  1.33,  'J[98]',           None),
        'JBarr':     (None,  None,  'J(Barr)',         None), # 1998-1999
        'K98':       (2.03,  2.37,  'K[98]',           None),
        'Kprime':    (None,  None,  "K'",              None), # TODO narrow?
        'Y_MK':      (0.966, 1.078, 'Y_MK',            None),
        'Z':         (0.850, 1.055, 'Z',               None),

        'Mask':      None,
        'Blank':     None,
}

# Copy filter specifications for aliases.
for (alias, filter) in (
                           ('2.166', 'BrG'),
                           ('2.181', 'BrGz'),
                           ('2.248', '2.248S(1)'), # Must be this one as it
                                                   # only appears on 20000303
                                                   # and 20000401.
                       ):
    ufti_filters[alias] = ufti_filters[filter]

def parse_filter(value):
    """Checks for +pol suffix and looks up the filter in ufti_filters."""

    if value.endswith('+pol'):
        pol = True
        value = value[:-4]
    else:
        pol = False

    if value in ufti_filters:
        return (ufti_filters[value], pol)

    else:
        # TODO issue warning if not found.
        return (None, pol)

class ObservationUFTI(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('ufti')

        self.caom2.instrument = instrument

        if 'MODE' in headers[0]:
            mode = clean_header(headers[0]['MODE']).lower()

            instrument.keywords.append(keywordvalue('mode', mode))

        if 'FILTER' in headers[0]:
            (filter, pol) = parse_filter(clean_header(headers[0]['FILTER']))

            if filter is not None:
                instrument.keywords.append(keywordvalue('filter', filter[2]))

            if pol:
                instrument.keywords.append(keywordvalue('pol', 'true'))
            else:
                instrument.keywords.append(keywordvalue('pol', 'false'))

        if 'SPD_GAIN' in headers[0]:
            speed = clean_header(headers[0]['SPD_GAIN']).lower()

            instrument.keywords.append(keywordvalue('speed', speed))

    def get_spectral_wcs(self, headers):
        if 'FILTER' not in headers[0]:
            return None

        (filter, pol) = parse_filter(clean_header(headers[0]['FILTER']))

        if filter is None:
            return None

        (cut_on, cut_off, filter_name, wavelength) = filter

        if cut_on is None or cut_off is None:
            return None

        axis = CoordAxis1D(Axis('WAVE', 'm'))
        axis.range = CoordRange1D(RefCoord(0.5, 1.0e-6 * cut_on),
                                  RefCoord(1.5, 1.0e-6 * cut_off))

        wcs = SpectralWCS(axis, 'TOPOCENT')
        wcs.ssysobs = 'TOPOCENT'
        wcs.bandpass_name = filter_name

        if wavelength is not None:
            wcs.restwav = 1.0e-6 * wavelength

        return wcs

    def get_spatial_wcs(self, headers):
        return None

instrument_classes['ufti'] = ObservationUFTI
