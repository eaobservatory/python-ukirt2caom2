from logging import getLogger
from os import makedirs
from os.path import exists, join, splitext
from sys import stdout

from caom2 import Proposal, SimpleObservation, Telescope
from caom2.xml.caom2_observation_writer import ObservationWriter

from ukirt2caom2 import IngestionError
from ukirt2caom2.fixup_headers import fixup_headers
from ukirt2caom2.geolocation import ukirt_geolocation
from ukirt2caom2.instrument import instrument_classes
from ukirt2caom2.mongo import HeaderDB
from ukirt2caom2.omp import OMP
from ukirt2caom2.proposals import Proposals
from ukirt2caom2.translate import TranslationError, Translator
from ukirt2caom2.util import document_to_ascii
from ukirt2caom2.valid_project_code import valid_project_code

from SECRET import staff_password

logger = getLogger(__name__)

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
        num_errors = 0

        for doc in self.db.find(instrument, date, obs_num):
            document_to_ascii(doc)
            fixup_headers(doc)
            filename = doc['filename']
            logger.info('Ingesting observation ' + filename)

            try:
                translated = self.translator.translate(doc['headers'][0])
            except TranslationError as e:
                logger.warning('Failed to translate headers: ' + e.message)
                translated = {}

            obs_date = doc['utdate'] if date is None else date

            # Construct CAOM2 object with basic identifying information.

            id_ = splitext(filename)[0]
            fits_format = filename.endswith('.fits')

            uri = 'ad:UKIRT/' + id_ + ('.fits' if fits_format else '.sdf')

            caom2_obs = SimpleObservation('UKIRT', id_)
            caom2_obs.telescope = Telescope('UKIRT', *self.geo)
            caom2_obs.sequence_number = doc['obs'] if obs_num is None else obs_num

            # Ingest the data into the CAOM2 object

            try:
                observation = self.ingest_observation(instrument,
                    caom2_obs, obs_date,
                    uri, fits_format, doc['headers'], translated)

                if dump:
                    observation.write(self.writer, stdout)

                if out_dir is not None:
                    obs_dir = join(out_dir, instrument, obs_date)
                    if not exists(obs_dir):
                        makedirs(obs_dir)
                    with open(join(obs_dir, id_ + '.xml'),
                              'w') as f:
                        observation.write(self.writer, f)

            except IngestionError as e:
                logger.error('Ingestion error: ' + e.message)
                num_errors += 1

        return num_errors

    def ingest_observation(self, instrument, caom2_obs, date,
                           uri, fits_format, headers, translated):
        # Collect project information.

        project_id = valid_project_code(headers[0].get('PROJECT', None))

        if project_id is None:
            project_info = None

        else:
            project_id = project_id
            project_info = self.omp.project_info(project_id)

            if project_info is None:
                project_info = self.prop.project_info(project_id)

        # Add general information to the CAOM2 object

        if project_id is not None:
            proposal = Proposal(project_id)

            if project_info is not None:
                if project_info.title is not None:
                    proposal.title = project_info.title
                if project_info.pi is not None:
                    proposal.pi  = project_info.pi

            caom2_obs.proposal = proposal

        # Construct instrument-specific observation object.

        observation = instrument_classes[instrument](
                caom2_obs, date,
                uri, fits_format)

        observation.ingest(headers, translated)

        return observation

