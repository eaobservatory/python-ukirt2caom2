import json
import subprocess

class TranslationError(Exception):
    pass

class Translator():
    def __init__(self):
        self.p = subprocess.Popen(['perl', 'scripts/header_translator.pl'],
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE)

    def translate(self, header):
        self.p.stdin.write(json.dumps(header))
        self.p.stdin.write("\n###\n")

        buff = ''

        while True:
            line = self.p.stdout.readline()

            if line.startswith('###'):
                break

            buff = buff + line

        header = json.loads(buff)

        if '__ERROR__' in header:
            raise TranslationError(header['__ERROR__'])

        else:
            return header

