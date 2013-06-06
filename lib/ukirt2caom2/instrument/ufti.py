from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.instrument.ukirt import ObservationUKIRT

class ObservationUFTI(ObservationUKIRT):
    pass

instrument_classes['ufti'] = ObservationUFTI
