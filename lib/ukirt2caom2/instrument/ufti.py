from caom2 import Instrument
from caom2.caom2_enums import ObservationIntentType
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

    def ingest_type_intent(self, headers):
        type = clean_header(headers[0]['OBSTYPE']).lower()

        if type != '':
            self.caom2.obs_type = type

            if type == 'object':
                self.caom2.intent =  ObservationIntentType.SCIENCE

            elif type in ('sky', 'dark'):
                self.caom2.intent =  ObservationIntentType.CALIBRATION

            else:
                raise IngestionError('Unknown OBSTYPE: ' + type)


instrument_classes['ufti'] = ObservationUFTI
