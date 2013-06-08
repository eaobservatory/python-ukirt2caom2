from collections import namedtuple

ProjectInfo = namedtuple('ProjectInfo', ['title', 'pi'])

class IngestionError(Exception):
    pass
