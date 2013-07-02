from logging import getLogger

from caom2 import Instrument
from jcmt2caom2.raw import keywordvalue

from ukirt2caom2 import IngestionError
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT
from ukirt2caom2.util import clean_header

logger = getLogger(__name__)

class ObservationUIST(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('uist')

        self.caom2.instrument = instrument

        if self.obstype is not None:
            instrument.keywords.append(keywordvalue('observation_type', self.obstype))

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
        if lens != '':
            instrument.keywords.append(keywordvalue('lens', lens.lower()))

        # Filter
        filter = headers[0]['FILTER']
        if filter == '':
            filter = None

        self.__filter = filter

        # Grism
        grism = headers[0]['GRISM']
        if grism == '':
            grism = None

        if grism.endswith('+pol'):
            grism = grism[:-4]

            if not pol:
                logger.warning('Grism has +pol suffix but polarise is false')

        elif grism.endswith('+ifu'):
            grism = grism[:-4]

            if camera != 'ifu':
                logger.warning('Grism has +ifu suffix outside ifu mode')

        if grism is not None:
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
        return None

    def get_spatial_wcs(self, headers, translated):
        return None

    def get_polarization_wcs(self, headers):
            return None

instrument_classes['uist'] = ObservationUIST
