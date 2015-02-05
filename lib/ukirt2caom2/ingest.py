from io import BytesIO
from logging import getLogger
from os import makedirs
from os.path import exists, join, splitext
import re
from sys import stdout

from caom2 import Proposal, SimpleObservation, Telescope
from caom2.xml.caom2_observation_reader import ObservationReader
from caom2.xml.caom2_observation_writer import ObservationWriter

from caom2repoClient.caom2repoClient \
    import CAOM2RepoClient, CAOM2RepoError, CAOM2RepoNotFound

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

valid_date = re.compile('^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ?$')

class IngestRaw:
    def __init__(self):
        self.geo = ukirt_geolocation()
        self.omp = OMP(password=staff_password)
        self.prop = Proposals()
        self.db = HeaderDB()
        self.reader = ObservationReader(True)
        self.writer = ObservationWriter(True)
        self.translator = Translator()
        self.client = CAOM2RepoClient()
        self.project_cache = {}

    def __call__(self, instrument, date=None, obs_num=None,
                 use_repo=False, out_dir=None, dump=False,
                 return_observations=False, control_file=None):
        num_errors = 0
        num_success = 0
        all_obs = {}

        if control_file is None:
            control = None
        else:
            control = read_control_file(control_file)
            control_file = open(control_file, 'a')

        for doc in self.db.find(instrument, date, obs_num):
            document_to_ascii(doc)
            fixup_headers(doc)
            filename = doc['filename']

            if control is not None and filename in control:
                logger.debug('Skipping (already ingested) ' + filename)
                continue

            logger.info('Ingesting observation ' + filename)

            obs_date = doc['utdate'] if date is None else date

            translated = {}
            if instrument not in ('cgs3',):
                try:
                    # Take a copy of the headers and insert fake values for those
                    # headers which we don't need but which cause HdrTrans to
                    # abort its translation.
                    header_copy = doc['headers'][0].copy()
                    obs_date_fake = '{}-{}-{}T00:00:00'.format(obs_date[0:4],
                                                obs_date[4:6], obs_date[6:8])
                    for date_field in ('DATE-OBS', 'DATE-END'):
                        if date_field not in header_copy or not valid_date.match(header_copy[date_field]):
                            logger.warning('For translation, replacing {} "{}" with "{}"'.format(
                                           date_field, header_copy.get(date_field, 'NONE'), obs_date_fake))
                            header_copy[date_field] = obs_date_fake

                    translated = self.translator.translate(header_copy)

                except TranslationError as e:
                    logger.warning('Failed to translate headers: ' + e.message)

            id_ = splitext(filename)[0]
            fits_format = filename.endswith('.fits')

            uri = 'ad:UKIRT/' + filename
            caom2_uri = 'caom2:UKIRT/' + id_
            in_repo = False
            caom2_obs = None

            # Attempt to fetch observation from the CAOM-2 repository.

            if use_repo:
                logger.debug('Getting from CAOM-2: ' + caom2_uri)
                try:
                    xml = self.client.get_xml(caom2_uri)

                    with BytesIO(xml) as f:
                        caom2_obs = self.reader.read(f)

                    in_repo = True

                except TypeError as e:
                    logger.error('Failed to read CAOM-2 XML from repository: ' +
                                 e.message)
                    logger.debug('Attempting to delete unreadable entry.')
                    self.client.remove(caom2_uri)

                except CAOM2RepoNotFound:
                    # Do nothing as in_repo already initialized to False.
                    pass

                except CAOM2RepoError:
                    raise IngestionError('Failed to get/remove CAOM-2 document')


            # Check the file directory exists, and if we didn't already find
            # the observation, attempt to read the previous version from a
            # file.

            if out_dir is not None:
                obs_dir = join(out_dir, instrument, obs_date)
                obs_file = join(obs_dir, id_ + '.xml')
                if not exists(obs_dir):
                    makedirs(obs_dir)

                if caom2_obs is None and exists(obs_file):
                    logger.debug('Reading file: ' + obs_file)
                    try:
                        caom2_obs = self.reader.read(obs_file)
                    except TypeError as e:
                        logger.error('Failed to read CAOM-2 XML from disk: ' +
                                     e.message)

            # Otherwise construct CAOM-2 object with basic information.

            if caom2_obs is None:
                logger.debug('Constructing new CAOM-2 object')
                caom2_obs = SimpleObservation('UKIRT', id_)

                caom2_obs.sequence_number = doc['obs'] if obs_num is None \
                                                       else obs_num

            # Ingest the data into the CAOM2 object

            try:
                observation = self.ingest_observation(instrument,
                    caom2_obs, obs_date,
                    uri, fits_format, doc['headers'], translated)

                if return_observations:
                        all_obs[(obs_date, caom2_obs.sequence_number)] = \
                        (filename, uri, observation, doc)

                if dump:
                    self.writer.write(observation.caom2, stdout)

                if out_dir is not None:
                    logger.debug('Writing file: ' + obs_file)
                    with open(obs_file, 'w') as f:
                        self.writer.write(observation.caom2, f)

                # Try to send to CAOM-2 last in case we need to
                # raise an exception.

                if use_repo:
                    with BytesIO() as f:
                        self.writer.write(observation.caom2, f)
                        xml = f.getvalue()

                    try:
                        if not in_repo:
                            logger.debug('Putting to CAOM-2: ' + caom2_uri)
                            self.client.put_xml(caom2_uri, xml)
                        else:
                            logger.debug('Updating in CAOM-2: ' + caom2_uri)
                            self.client.update_xml(caom2_uri, xml)

                    except CAOM2RepoError:
                        raise IngestionError('Failed to send to CAOM-2 repository')

            except IngestionError as e:
                logger.error('Ingestion error: ' + e.message)
                num_errors += 1

            else:
                num_success += 1
                if control_file is not None:
                    write_control_file(control_file, filename)

        if control_file is not None:
            control_file.close()

        logger.info('Ingestion run finished, number ingested: ' + str(num_success))

        if return_observations:
            return all_obs
        else:
            return num_errors

    def ingest_observation(self, instrument, caom2_obs, date,
                           uri, fits_format, headers, translated):
        # Set telescope.

        caom2_obs.telescope = Telescope('UKIRT', *self.geo)

        # Collect project information.

        project_id = valid_project_code(headers[0].get('PROJECT', None))

        if project_id is None:
            project_info = None

        else:
            if project_id in self.project_cache:
                project_info = self.project_cache[project_id]

            else:
                logger.debug('Fetching project {} information from OMP'.format(project_id))
                project_info = self.omp.project_info(project_id)

                if project_info is None:
                    logger.debug('Fetching project {} information from file'.format(project_id))
                    project_info = self.prop.project_info(project_id)

                self.project_cache[project_id] = project_info

        # Add general information to the CAOM2 object

        if project_id is not None:
            proposal = Proposal(project_id)

            if project_info is not None:
                if project_info.title is not None:
                    title = project_info.title
                    if title.find('\n') != -1:
                        title = title.replace('\n', ' ')
                    proposal.title = title
                if project_info.pi is not None:
                    proposal.pi_name  = project_info.pi

            caom2_obs.proposal = proposal

        # Construct instrument-specific observation object.

        observation = instrument_classes[instrument](
                caom2_obs, date,
                uri, fits_format)

        observation.ingest(headers, translated)

        return observation

def read_control_file(filename):
    ingested = set()

    if exists(filename):
        with open(filename) as file:
            for text in file:
                ingested.add(text.strip())

    return ingested

def write_control_file(file, text):
    file.write(text + '\n')
