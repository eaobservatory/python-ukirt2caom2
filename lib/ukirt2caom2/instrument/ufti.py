from caom2 import Instrument

from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT

class ObservationUFTI(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('ufti')

        self.caom2.instrument = instrument

instrument_classes['ufti'] = ObservationUFTI
