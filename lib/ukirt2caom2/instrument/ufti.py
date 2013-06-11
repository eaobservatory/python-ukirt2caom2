from caom2 import Instrument
from jcmt2caom2.raw import keywordvalue

from ukirt2caom2 import IngestionError
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT
from ukirt2caom2.util import clean_header

class ObservationUFTI(ObservationUKIRT):
    def ingest_instrument(self, headers):
        instrument = Instrument('ufti')

        self.caom2.instrument = instrument

        if 'MODE' in headers[0]:
            mode = clean_header(headers[0]['MODE']).lower()

            instrument.keywords.append(keywordvalue('mode', mode))

        if 'FILTER' in headers[0]:
            filter = clean_header(headers[0]['FILTER']).lower()

            instrument.keywords.append(keywordvalue('filter', filter))

instrument_classes['ufti'] = ObservationUFTI
