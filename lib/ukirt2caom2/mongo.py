from pymongo import MongoClient

class HeaderDBError(Exception):
    pass

class HeaderDB:
    def __init__(self):
        mongo = MongoClient()
        self.db = mongo.ukirt

    def find(self, instrument, date, obs):
        cursor = self.db[instrument].find({'utdate': date, 'obs': obs})

        if cursor.count() == 0:
            raise HeaderDBError('No headers found')

        elif cursor.count() > 1:
            raise HeaderDBError('Multiple headers found')

        return cursor[0]
