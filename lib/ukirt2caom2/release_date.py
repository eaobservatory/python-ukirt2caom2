from __future__ import print_function

from datetime import datetime
import subprocess

class ReleaseCalculator():
    def __init__(self):
        self.p = subprocess.Popen(['perl', 'scripts/release_date.pl'],
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE)

    def calculate(self, date):
        print(date.strftime('%Y%m%d'), file=self.p.stdin)
        line = self.p.stdout.readline().strip()

        return datetime.strptime(line, '%Y%m%d %H:%M:%S')
