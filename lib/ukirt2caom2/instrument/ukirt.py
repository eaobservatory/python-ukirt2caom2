from datetime import datetime, timedelta

from caom2 import Artifact, Chunk, \
        Environment, Part, Plane, Proposal, \
        SimpleObservation, Target, Telescope
from caom2.caom2_enums import CalibrationLevel, ObservationIntentType
from caom2.util.caom2_util import TypedList
from caom2.wcs.caom2_axis import Axis
from caom2.wcs.caom2_coord_axis1d import CoordAxis1D
from caom2.wcs.caom2_coord_range1d import CoordRange1D
from caom2.wcs.caom2_ref_coord import RefCoord
from caom2.wcs.caom2_temporal_wcs import TemporalWCS

from jcmt2caom2.mjd import utc2mjd

from ukirt2caom2.util import airmass_to_elevation, clean_header, valid_object

c = 299792458.0

calibration_types = ('dark', 'flat', 'arc', 'sky',
                     'targetacq', 'bias', 'calibration')

class ObservationUKIRT():
    def __init__(self, date, obs_num, id_, project_id, project_info,
                 geolocation, fits_format):
        self.date = datetime.strptime(date, '%Y%m%d')
        self.fits_format = fits_format

        self.uri = 'ad:UKIRT/' + id_ + ('.fits' if fits_format else '.sdf')

        # Construct CAOM2 object with basic identifying information.

        self.caom2 = SimpleObservation('UKIRT', id_)

        self.caom2.sequence_number = obs_num
        self.caom2.telescope = Telescope('UKIRT', *geolocation)

        if project_id is not None:
            proposal = Proposal(project_id)

            if project_info is not None:
                if project_info.title is not None:
                    proposal.title = project_info.title
                if project_info.pi is not None:
                    proposal.pi  = project_info.pi

            self.caom2.proposal = proposal

    def write(self, writer, out):
        writer.write(self.caom2, out)

    def ingest(self, headers):
        # Go through each ingestion step, allowing each to be
        # over-ridden by sub-classes.

        self.ingest_target(headers)
        self.ingest_type_intent(headers)
        self.ingest_environment(headers)
        self.ingest_instrument(headers)
        self.ingest_plane(headers)

    def ingest_target(self, headers):
        if 'OBJECT' in headers[0]:
            object = valid_object(headers[0]['OBJECT'])
            target = Target(object)

            if 'STANDARD' in headers[0]:
                target.standard = True if headers[0]['STANDARD'] else False

            target.target_type = None

            self.caom2.target = target

    def ingest_type_intent(self, headers):
        if 'OBSTYPE' in headers[0]:
            type = clean_header(headers[0]['OBSTYPE']).lower()

            if type != '':
                self.caom2.obs_type = type

                if type == 'object':
                    self.caom2.intent = ObservationIntentType.SCIENCE

                elif type in calibration_types:
                    self.caom2.intent = ObservationIntentType.CALIBRATION

                else:
                    raise IngestionError('Unknown OBSTYPE: ' + type)

    def ingest_environment(self, headers):
        environment = Environment()

        # Elevation.

        airmasses = []

        for hdr in headers:
            if ('AMSTART' in hdr and hdr['AMSTART'] is not None and
                    type(hdr['AMSTART']) != str):
                airmasses.append(hdr['AMSTART'])
            if ('AMEND' in hdr and hdr['AMEND'] is not None and
                    type(hdr['AMEND']) != str):
                airmasses.append(hdr['AMEND'])

        if airmasses:
            environment.elevation = airmass_to_elevation(max(airmasses))

        if ('HUMIDITY' in headers[0] and headers[0]['HUMIDITY'] is not None and
                type(headers[0]['HUMIDITY']) != str):
            humidity = headers[0]['HUMIDITY'] / 100

            # We seem to have some humidity values over 100% which
            # the Environment class will reject.
            if humidity > 1.0:
                humidity = 1.0
            elif humidity < 0.0:
                humidity = 0.0

            environment.humidity = humidity

        if ('AIRTEMP' in headers[0] and headers[0]['AIRTEMP'] is not None and
                type(headers[0]['AIRTEMP']) != str):
            environment.ambient_temp = headers[0]['AIRTEMP']

        if ('CSOTAU' in headers[0] and headers[0]['CSOTAU'] is not None and
                type(headers[0]['CSOTAU']) != str):
            tau = headers[0]['CSOTAU']

            # Ignore invalid tau values
            if 0.0 <= tau <= 1.0:
                environment.tau = tau
                environment.wavelength_tau = c / 225.0e9

        self.caom2.environment = environment

    def ingest_plane(self, headers):
        plane = Plane('raw')

        plane.calibration_level = CalibrationLevel.RAW_STANDARD \
            if self.fits_format else CalibrationLevel.RAW_INSTRUMENT

        if self.date.month == 2 and self.date.day == 29:
            release = self.date.replace(day=28, year=self.date.year + 1)

        else:
            release = self.date.replace(year=self.date.year + 1)

        plane.meta_release = release
        plane.data_release = release

        artifact = self.ingest_artifact(headers)

        plane.artifacts[self.uri] = artifact

        self.caom2.planes['raw'] = plane

    def ingest_artifact(self, headers):
        artifact = Artifact(self.uri)

        for part in self.ingest_parts(headers):
            artifact.parts[part.name] = part

        return artifact

    def ingest_parts(self, headers):
        # We only have FITS files for UFTI and we don't appear to
        # have any with multiple extensions.
        part = Part('fits' if self.fits_format else 'ndf')

        chunk = Chunk()

        if 'DATE-OBS' in headers[0] and 'DATE-END' in headers[0]:
            date_start = self.parse_date(headers[0]['DATE-OBS'])
            date_end = self.parse_date(headers[0]['DATE-END'])

            if date_start is not None and date_end is not None:
                time = CoordAxis1D(Axis('TIME', 'd'))
                time.range = CoordRange1D(
                        RefCoord(0.5, date_start),
                        RefCoord(1.5, date_end))

                chunk.time = TemporalWCS(time, 'UTC')

        part.chunks = TypedList((Chunk,), chunk)

        return [part]

    def parse_date(self, date_str):
        if date_str == '':
            return None

        if date_str[-1] == 'Z':
            date_str = date_str[:-1]

        try:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')

            return utc2mjd(date)

        except ValueError:
            return None
