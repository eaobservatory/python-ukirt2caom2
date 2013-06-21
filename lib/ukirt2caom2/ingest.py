from os import makedirs
from os.path import exists, join, splitext
from sys import stdout

from caom2.xml.caom2_observation_writer import ObservationWriter

from ukirt2caom2.geolocation import ukirt_geolocation
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.mongo import HeaderDB
from ukirt2caom2.omp import OMP
from ukirt2caom2.proposals import Proposals
from ukirt2caom2.translate import TranslationError, Translator
from ukirt2caom2.util import document_to_ascii
from ukirt2caom2.valid_project_code import valid_project_code

from SECRET import staff_password

class IngestRaw:
    def __init__(self):
        self.geo = ukirt_geolocation()
        self.omp = OMP(password=staff_password)
        self.prop = Proposals()
        self.db = HeaderDB()
        self.writer = ObservationWriter()
        self.translator = Translator()

    def __call__(self, instrument, date=None, obs_num=None, out_dir=None,
                 dump=False):
        for doc in self.db.find(instrument, date, obs_num):
            document_to_ascii(doc)
            filename = doc['filename']

            try:
                translated = self.translator.translate(doc['headers'][0])
            except TranslationError as e:
                print(filename + ': ' + e.message)
                translated = {}

            obs_date = doc['utdate'] if date is None else date
            print(doc['filename'])
            observation = self.ingest_observation(instrument,
                obs_date,
                doc['obs'] if obs_num is None else obs_num,
                doc['headers'], filename, translated)

            if dump:
                observation.write(self.writer, stdout)

            if out_dir is not None:
                obs_dir = join(out_dir, instrument, obs_date)
                if not exists(obs_dir):
                    makedirs(obs_dir)
                with open(join(obs_dir, splitext(filename)[0] + '.xml'),
                          'w') as f:
                    observation.write(self.writer, f)

    def ingest_observation(self, instrument, date, obs_num, headers,
                           filename, translated):
        # Collect project information.

        project_id = valid_project_code(headers[0].get('PROJECT', None))

        if project_id is None:
            project_info = None

        else:
            project_id = project_id
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

        observation.ingest(headers, translated)

        return observation

