from ukirt2caom2.geolocation import ukirt_geolocation
from ukirt2caom2.mongo import HeaderDB
from ukirt2caom2.omp import OMP
from ukirt2caom2.proposals import Proposals
from ukirt2caom2.util import airmass_to_elevation, valid_object
from ukirt2caom2.valid_project_code import valid_project_code

from SECRET import staff_password

class IngestionError(Exception):
    pass

class IngestRaw:
    def __init__(self):
        self.geo = ukirt_geolocation()
        self.omp = OMP(password=staff_password)
        self.prop = Proposals()
        self.db = HeaderDB()

    def ingest_observation(self, instrument, date, obs):
        doc = self.db.find(instrument, date, obs)
        headers = doc['headers']

        project_id = valid_project_code(headers[0]['PROJECT'])

        if project_id is None:
            project_info = None

        else:
            project_info = self.omp.project_info(project_id)

            if project_info is None:
                project_info = self.prop.project_info(project_id)

        if 'OBJECT' in headers[0]:
            object = valid_object(headers[0]['OBJECT'])
        else:
            object = None

        airmasses = []

        for hdr in headers:
            if 'AMSTART' in hdr:
                airmasses.append(hdr['AMSTART'])
            if 'AMEND' in hdr:
                airmasses.append(hdr['AMEND'])

        elevation = airmass_to_elevation(max(airmasses))
