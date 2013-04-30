#!/usr/bin/env python

from contextlib import closing
import sys

from ukirt2caom2 import ProjectInfo

class Proposals():
    """Class for reading project information from the proposals file."""

    def __init__(self, file='data/projects.csv'):

        self.projects = {}

        with open(file) as f:
            for line in f:
                (projectid, name, title) = line.rstrip().split('\t', 3)
                self.projects[projectid] = ProjectInfo(title, name)

    def project_info(self, projectid):
        """Looks up relevant information about a project.
        
        This will be a ProjectInfo object (a namedtuple)."""

        return self.projects.get(projectid)

if __name__ == '__main__':
    prop = Proposals()
    print(repr(prop.project_info(sys.argv[1])))
