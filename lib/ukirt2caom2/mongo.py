from pymongo import MongoClient

class HeaderDBError(Exception):
    pass

class HeaderDB:
    def __init__(self):
        mongo = MongoClient()
        self.db = mongo.ukirt

    def find(self, instrument, date, obs_num):
        prototype = {}

        if date is not None:
            prototype['utdate'] = date

        if obs_num is not None:
            prototype['obs'] = obs_num

        cursor = self.db[instrument].find(prototype, timeout=False)

        if cursor.count() == 0:
            raise HeaderDBError('No headers found')

        elif date is not None and obs_num is not None and cursor.count() > 1:
            raise HeaderDBError('Multiple headers found')

        for doc in cursor:
            yield doc
