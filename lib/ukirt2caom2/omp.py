#!/usr/bin/env python

from contextlib import closing
from collections import namedtuple
from getpass import getpass
import sys

import Sybase

ProjectInfo = namedtuple('ProjectInfo', ['title', 'pi'])

class OMP():
    """Class for extracting information from the OMP database."""

    def __init__(self, username='staff', password=None,
                       server='SYB_JAC', database='omp'):
        if password is None:
            password = getpass('Database password for ' + username + ': ')

        self.db = Sybase.connect(server, username, password, database=database)

    def project_info(self, projectid):
        """Looks up relevant information about a project.
        
        This will be a ProjectInfo object (a namedtuple)."""

        with closing(self.db.cursor()) as c:
            c.execute('SELECT title, uname '
                      'FROM ompproj '
                          'LEFT JOIN ompuser '
                              'ON pi=userid '
                      'WHERE projectid=@projectid',
                      {'@projectid': projectid})

            cols = c.fetchone()

            if cols is None:
                return None
            else:
                return ProjectInfo(*cols)

if __name__ == '__main__':
    omp = OMP()
    print(repr(omp.project_info(sys.argv[1])))
