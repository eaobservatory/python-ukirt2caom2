from datetime import datetime

from taco import Taco

class ReleaseCalculator():
    def __init__(self):
        self.taco = Taco(lang='perl')
        self.taco.import_module('lib', '../omp-perl')
        self.taco.import_module('OMP::DateTools')

    def calculate(self, date):
        semester = self.taco.call_function(
            'OMP::DateTools::determine_semester', None,
            date=date.strftime('%Y%m%d'), tel='UKIRT')
        (sem_begin, sem_end) = self.taco.call_function(
            'OMP::DateTools::semester_boundary', None,
            semester=semester, tel='UKIRT', context='list')

        end_date = datetime.utcfromtimestamp(sem_end.call_method('epoch'))

        return end_date.replace(year=end_date.year + 1,
                                hour=23, minute=59, second=59)
