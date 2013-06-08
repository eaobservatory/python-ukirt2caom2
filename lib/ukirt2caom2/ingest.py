from os.path import splitext

from caom2.xml.caom2_observation_writer import ObservationWriter

from ukirt2caom2.geolocation import ukirt_geolocation
from ukirt2caom2.mongo import HeaderDB
from ukirt2caom2.omp import OMP
from ukirt2caom2.proposals import Proposals
from ukirt2caom2.valid_project_code import valid_project_code
from ukirt2caom2.instrument import instrument_classes

from SECRET import staff_password

class IngestRaw:
    def __init__(self):
        self.geo = ukirt_geolocation()
        self.omp = OMP(password=staff_password)
        self.prop = Proposals()
        self.db = HeaderDB()
        self.writer = ObservationWriter()

    def __call__(self, instrument, date=None, obs_num=None):
        for doc in self.db.find(instrument, date, obs_num):
            self.ingest_observation(instrument,
                doc['utdate'] if date is None else date,
                doc['obs'] if obs_num is None else obs_num,
                doc['headers'], doc['filename'])

    def ingest_observation(self, instrument, date, obs_num, headers, filename):
        # Collect project information.

        project_id = valid_project_code(headers[0].get('PROJECT', None))

        if project_id is None:
            project_info = None

        else:
            project_id = project_id.encode('ascii')
            project_info = self.omp.project_info(project_id)

            if project_info is None:
                project_info = self.prop.project_info(project_id)

        # Construct instrument-specific observation object.

        observation = instrument_classes[instrument](
                date, obs_num,
                splitext(filename)[0],
                project_id, project_info,
                self.geo,
                filename.endswith('.fits'))

        observation.ingest(headers)


