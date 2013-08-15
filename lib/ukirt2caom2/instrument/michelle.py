from logging import getLogger
import re

from caom2 import Instrument
from jcmt2caom2.raw import keywordvalue

from ukirt2caom2 import IngestionError
from ukirt2caom2.coord import CoordFK5
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT
from ukirt2caom2.util import clean_header
from ukirt2caom2.wcs_util import to_coord2D
from caom2.wcs.caom2_axis import Axis
from caom2.wcs.caom2_coord_axis1d import CoordAxis1D
from caom2.wcs.caom2_coord_axis2d import CoordAxis2D
from caom2.wcs.caom2_coord_polygon2d import CoordPolygon2D
from caom2.wcs.caom2_coord_range1d import CoordRange1D
from caom2.wcs.caom2_ref_coord import RefCoord
from caom2.wcs.caom2_spatial_wcs import SpatialWCS
from caom2.wcs.caom2_spectral_wcs import SpectralWCS

logger = getLogger(__name__)

def parse_filter(value):
    """Attempt to interpret name of Michelle filter."""

    m = re.match('^([EIF])(P?)(\d+)B(\d+)$', value)

    if m is None:
        return (None, None)

    (prefix, pol, centre, bandpass) = m.groups()

    name = 'F{}B{}'.format(centre, bandpass)

    pol = pol == 'P'

    centre = float(centre) / 10.0 # um
    bandpass = float(bandpass) / 100.0 # %

    cut_on = centre - 0.5 * centre * bandpass
    cut_off = centre + 0.5 * centre * bandpass

    return ((cut_on, cut_off, name), pol)

class ObservationMichelle(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('michelle')

        self.caom2.instrument = instrument

        # Detector mode

        if 'DETMODE' in headers[0]:
            instrument.keywords.append(keywordvalue('detector_mode',
                                       headers[0]['DETMODE'].lower()))
        elif 'DET_MODE' in headers[0]:
            instrument.keywords.append(keywordvalue('detector_mode',
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
            instrument.keywords.append(keywordvalue('mode', camera))

        self.__camera = camera

        # Filter Wheel

        (filter, pol) = parse_filter(headers[0]['FILTER'])

        self.__filter = filter
        self.__pol = pol

        instrument.keywords.append(keywordvalue('pol',
                                   'true' if pol else 'false'))

        # Grating Drum

        grating = headers[0]['GRATNAME']

        if grating in ('', 'undefined'):
            grating = None

        if grating is not None:
            instrument.keywords.append(keywordvalue('grating', grating))

        self.__grating = grating

        # Slit Wheel

        slit = headers[0]['SLITNAME']

        if slit == '':
            slit = None

        if slit is not None:
            instrument.keywords.append(keywordvalue('slit', slit))

        self.__slit = slit

        # Cal / Pol unit

        calpol = headers[0].get('CALSELN', None)

        if calpol is not None:
            instrument.keywords.append(keywordvalue('cal_pol', calpol))

        self.__calpol = calpol

    def get_spectral_wcs(self, headers):
        if self.__camera == 'imaging':
            if self.__filter is None:
                logger.warning('Using default filter cut on and off')
                (cut_on, cut_off, filter_name) = (8, 25, None) # From Michelle webpage
            else:
                (cut_on, cut_off, filter_name) = self.__filter

            axis = CoordAxis1D(Axis('WAVE', 'm'))
            axis.range = CoordRange1D(RefCoord(0.5, 1.0e-6 * cut_on),
                                      RefCoord(1.5, 1.0e-6 * cut_off))

            wcs = SpectralWCS(axis, 'TOPOCENT')
            wcs.ssysobs = 'TOPOCENT'

            if filter_name is not None:
                wcs.bandpass_name = filter_name

            return wcs

        else:
            return None

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

        # Convert to degrees, using checks taken from MICHELLE/_GET_PLATE_SCALE_
        if rascale is None or decscale is None:
            rascale = -0.2134 / 3600.0
            decscale = 0.2134 / 3600.0
        else:
            if rascale > 0.0:
                rascale *= -1.0
            if not (headers[0]['CTYPE1'] == 'RA---TAN' and rascale < 1.0e-3):
                rascale = float(rascale) / 3600.0
                decscale = float(decscale) / 3600.0

        if self.__camera == 'imaging':
            # Create coordinates
            base = CoordFK5(ra_deg=rabase, dec_deg=decbase)

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

        else:
            return None

    def get_polarization_wcs(self, headers):
        return None

instrument_classes['michelle'] = ObservationMichelle
