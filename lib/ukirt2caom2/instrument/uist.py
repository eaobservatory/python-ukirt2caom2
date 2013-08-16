from logging import getLogger

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

logger = getLogger(__name__)

uist_imaging_filters = {
        '1.57':      (1.561, 1.583, '1.57(cont)[MK]', 1.573),
        '1.58CH4_s': (1.550, 1.657, 'CH4_s',          1.604),
        '1.644Fe':   (1.630, 1.656, 'FeII[MK]',       1.643),
        '1.69CH4_l': (1.617, 1.730, 'CH4_l',          1.674),
        '2.122MK':   (2.103, 2.134, '2.122 MK',       2.127),
        '2.122S(1)': (2.106, 2.124, '2.122(S1)',      2.121),
        '2.248MK':   (2.235, 2.270, '2.248 MK',       2.263),
        '2.248S(1)': (2.234, 2.269, '2.248(S1)',      2.248),
        '2.27':      (2.257, 2.291, '2.27cont[98]',   2.274),
        '2.42CO':    (2.413, 2.436, '2.42CO',         2.425),
        '3.05ice':   (2.970, 3.125, '3.05ice MK',     3.048),
        '3.30PAH':   (3.264, 3.318, '3.29 PAH MK',    3.286),
        '3.4nbL':    (3.379, 3.451, '3.4nbL',         3.415),
        '3.5mbL':    (3.383, 3.594, '3.5mbL',         3.489),
        '3.6nbLp':   (3.560, 3.625, "3.6nbL'",        3.593),
        '3.99':      (3.964, 4.016, '3.99(cont)',     3.990),
        'BrG':       (2.150, 2.182, 'BrG MK',         2.168),
        'CowieK':    (2.030, 2.370, 'CowieK',         2.20),
        'Dust':      (3.250, 3.305, '3.28"Dust"',     3.278),
        'H98':       (1.490, 1.780, 'H[MK]',          1.64),
        'J98':       (1.170, 1.330, 'J[MK]',          1.25),
        'K98':       (2.030, 2.370, 'K[MK]',          2.20),
        'K_s_MK':    (1.990, 2.310, 'K_s_MK',         2.15),
        'Kp':        (2.030, 2.370, 'Kp',             2.20),
        'Kshort':    (2.028, 2.290, 'Kshort',         2.20),
        'Lp98':      (3.428, 4.108, "L'[MK]",         3.77),
        'Mp98':      (4.572, 4.800, "M'[MK]",         4.69),
        'Y_MK':      (0.966, 1.078, 'Y[MK]',          1.022),
        'ZMK':       (1.008, 1.058, 'Z[MK]',          1.03),
}

class ObservationUIST(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('uist')

        self.caom2.instrument = instrument

        # Camera mode: ifu / imaging / spectroscopy
        camera = headers[0]['INSTMODE']

        if camera == '':
            camera = None
            logger.warning('No camera mode specified')

        self.__camera = camera

        if camera is not None:
            instrument.keywords.append(keywordvalue('mode', camera))

        # Detector mode
        mode = headers[0]['DET_MODE'].lower()
        instrument.keywords.append(keywordvalue('detector_mode', mode))

        # Readout mode
        readout = headers[0].get('READOUT', None)

        if readout is not None:
            instrument.keywords.append(keywordvalue('readout', readout.lower()))

        # Polarizer?
        pol = headers[0]['POLARISE']
        if pol is True:
            instrument.keywords.append(keywordvalue('pol', 'true'))
        elif pol is False:
            instrument.keywords.append(keywordvalue('pol', 'false'))
        else:
            pol = None

        self.__pol = pol

        # Lens
        lens = headers[0]['CAMLENS']

        # Header has a mixture of float and string values
        if type(lens) is not str:
            lens = str(lens)

        if lens != '':
            instrument.keywords.append(keywordvalue('lens', lens.lower()))

        # Filter
        filter = headers[0]['FILTER']
        if filter == '':
            filter = None

        self.__filter = uist_imaging_filters.get(filter,
                (None, None, filter, None))

        # Grism
        grism = headers[0]['GRISM']
        if grism == '':
            grism = None

        if grism is not None:
            if grism.endswith('+pol'):
                grism = grism[:-4]

                if not pol:
                    logger.warning('Grism has +pol suffix but polarise is false')

            elif grism.endswith('+ifu'):
                grism = grism[:-4]

                if camera != 'ifu':
                    logger.warning('Grism has +ifu suffix outside ifu mode')

            instrument.keywords.append(keywordvalue('grism', grism))

        self.__grism = grism

        # Slit
        slit = headers[0]['SLITNAME']
        if slit == '':
            slit = None

        if slit is not None:
            instrument.keywords.append(keywordvalue('slit', slit))

        self.__slit = slit

    def get_spectral_wcs(self, headers):
        (cut_on, cut_off, filter_name, wavelength) = self.__filter

        if self.__camera == 'imaging':
            if None in (cut_on, cut_off):
                logger.warning('Using default filter cut on and off')
                (cut_on, cut_off) = (1.0, 5.0) # From UIST webpage

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

        elif self.__camera == 'ifu':
            return None

        elif self.__camera == 'spectroscopy':
            return None

        else:
            return None

    def get_spatial_wcs(self, headers, translated):
        return None

    def get_polarization_wcs(self, headers):
        return None

instrument_classes['uist'] = ObservationUIST
