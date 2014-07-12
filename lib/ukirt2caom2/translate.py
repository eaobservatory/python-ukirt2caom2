from taco import Taco

class TranslationError(Exception):
    pass

class Translator():
    def __init__(self):
        self.taco = Taco(lang='perl')
        self.taco.import_module('Astro::FITS::HdrTrans', 'translate_from_FITS')

    def translate(self, header):
        try:
            header = self.taco.call_function('translate_from_FITS',
                                             header, context='map')

        except Exception as e:
            raise TranslationError(str(e))

        return header
