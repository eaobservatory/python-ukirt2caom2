from logging import getLogger

from caom2 import Instrument
from jcmt2caom2.raw import keywordvalue

from ukirt2caom2 import IngestionError
from ukirt2caom2.coord import CoordFK5
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT
from ukirt2caom2.util import clean_header
from caom2.wcs.caom2_axis import Axis
from caom2.wcs.caom2_coord2d import Coord2D
from caom2.wcs.caom2_coord_axis1d import CoordAxis1D
from caom2.wcs.caom2_coord_axis2d import CoordAxis2D
from caom2.wcs.caom2_coord_polygon2d import CoordPolygon2D
from caom2.wcs.caom2_coord_range1d import CoordRange1D
from caom2.wcs.caom2_polarization_wcs import PolarizationWCS
from caom2.wcs.caom2_ref_coord import RefCoord
from caom2.wcs.caom2_spatial_wcs import SpatialWCS
from caom2.wcs.caom2_spectral_wcs import SpectralWCS

logger = getLogger(__name__)

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
        'Kprime':    (1.99,  2.25,  "K'",              None), # TODO check (from OT config)
        'Y_MK':      (0.966, 1.078, 'Y_MK',            1.022),
        'Z':         (0.850, 1.055, 'Z',               None),

        'Mask':      (None,  None,  'Mask',            None),
        'Blank':     (None,  None,  'Blank',           None),
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
        logger.warning('Filter ' + value + ' is not recognised')
        return (None, pol)

def to_coord2D(coord, xpix=0.5, ypix=1.5):
    (ra, dec) = coord.deg()

    return Coord2D(RefCoord(float(xpix), ra),
                   RefCoord(float(ypix), dec))

class ObservationUFTI(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('ufti')

        self.caom2.instrument = instrument

        if 'MODE' in headers[0]:
            mode = clean_header(headers[0]['MODE']).lower()

            instrument.keywords.append(keywordvalue('detector_mode', mode))

        if 'FILTER' in headers[0]:
            (filter, pol) = parse_filter(clean_header(headers[0]['FILTER']))
            self.__filter = filter
            self.__pol = pol

            if pol:
                instrument.keywords.append(keywordvalue('pol', 'true'))
            else:
                instrument.keywords.append(keywordvalue('pol', 'false'))

        else:
            self.__filter = None
            self.__pol = None

        if 'SPD_GAIN' in headers[0]:
            speed = clean_header(headers[0]['SPD_GAIN']).lower()

            instrument.keywords.append(keywordvalue('speed_gain', speed))

        if self.obstype is not None:
            instrument.keywords.append(keywordvalue('observation_type', self.obstype))

    def get_spectral_wcs(self, headers):
        # TODO deal with Fabry Perot thing.

        filter = self.__filter

        if filter is None:
            (cut_on, cut_off, filter_name, wavelength) = (None,) * 4
        else:
            (cut_on, cut_off, filter_name, wavelength) = filter

        if cut_on is None or cut_off is None:
            logger.warning('Using default filter cut on and off')
            (cut_on, cut_off) = (0.8, 2.5) # From Roche P.F. et al. 2002

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
        if self.obstype not in ('object', 'sky'):
            return None

        # Fetch data
        rabase = translated.get('RA_BASE', None)
        decbase = translated.get('DEC_BASE', None)
        xref = translated.get('X_REFERENCE_PIXEL', None)
        yref = translated.get('Y_REFERENCE_PIXEL', None)
        rascale = translated.get('RA_SCALE', None)
        decscale = translated.get('DEC_SCALE', None)
        x1 = translated.get('X_LOWER_BOUND', None)
        x2 = translated.get('X_UPPER_BOUND', None)
        y1 = translated.get('Y_LOWER_BOUND', None)
        y2 = translated.get('Y_UPPER_BOUND', None)
        xoff = translated.get('RA_TELESCOPE_OFFSET', None)
        yoff = translated.get('DEC_TELESCOPE_OFFSET', None)

        if None in (rabase, decbase, xref, yref, rascale, decscale,
                x1, x2, y1, y2):
            logger.error('Insufficient information for WCS')
            return None

        if type(rabase) is int:
            rabase = float(rabase)
        if type(decbase) is int:
            decbase = float(decbase)

        if any(map(lambda x: type(x) is not float, (rabase, decbase))):
            logger.error('Non-float in WCS information: ' +
                         str(rabase) + ', ' + str(decbase))
            return None

        # Convert to degrees
        rascale = float(rascale) / 3600.0
        decscale = float(decscale) / 3600.0

        # Create coordinates
        base = CoordFK5(ra_deg=rabase, dec_deg=decbase)

        if xoff is not None and yoff is not None:
            base = base.offset(float(xoff) / 3600.0, float(yoff) / 3600.0)

        box = CoordPolygon2D()
        box.vertices.append(to_coord2D(base.offset(rascale * (x1 - xref), decscale * (y2 - yref)), x1, y2)) #TL
        box.vertices.append(to_coord2D(base.offset(rascale * (x2 - xref), decscale * (y2 - yref)), x2, y2)) #TR
        box.vertices.append(to_coord2D(base.offset(rascale * (x2 - xref), decscale * (y1 - yref)), x2, y1)) #BR
        box.vertices.append(to_coord2D(base.offset(rascale * (x1 - xref), decscale * (y1 - yref)), x1, y1)) #BL

        spatial_axes = CoordAxis2D(Axis('RA', 'deg'),
                                   Axis('DEC', 'deg'))
        spatial_axes.bounds = box

        wcs = SpatialWCS(spatial_axes,
                         coordsys='ICRS',
                         equinox=2000.0)
                  # TODO resolution=(arseconds, seeing/beam)

        return wcs

    def get_polarization_wcs(self, headers):
        pol = self.__pol

        if not pol:
            return None

        if 'WPLANGLE' not in headers[0]:
            logger.warning('Pol filter present without WPLANGLE')
            return None

        angle = headers[0]['WPLANGLE']

        # The Wells 1981 FITS paper defines CTYPE ANGLE as an
        # angle on the sky in degrees.

        # TODO: is WPLANGLE actually angle on sky ?

        # TODO: check IRPOLARM == 'Extended' ?

        axis = CoordAxis1D(Axis('ANGLE', 'deg'))
        axis.range = CoordRange1D(RefCoord(0.5, angle),
                                  RefCoord(1.5, angle))

        return PolarizationWCS(axis)

instrument_classes['ufti'] = ObservationUFTI
