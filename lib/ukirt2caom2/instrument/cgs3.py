from caom2 import Instrument
from caom2.caom2_enums import ObservationIntentType
from jcmt2caom2.raw import keywordvalue

from ukirt2caom2 import IngestionError
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT
from ukirt2caom2.util import clean_header

class ObservationCGS3(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('cgs3')

        self.caom2.instrument = instrument

    def ingest_type_intent(self, headers):
        # CGS3 will need a custom version of this method as it
        # does not have an OBSTYPE header.
        pass

    def get_spectral_wcs(self, headers):
        return None

    def get_spatial_wcs(self, headers, translated):
        return None

instrument_classes['cgs3'] = ObservationCGS3
