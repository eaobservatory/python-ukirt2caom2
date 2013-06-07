from datetime import datetime, timedelta

from caom2 import Artifact, Chunk, \
        Environment, Part, Plane, Proposal, \
        SimpleObservation, Target, Telescope
from caom2.caom2_enums import CalibrationLevel
from caom2.util.caom2_util import TypedList
from caom2.wcs.caom2_axis import Axis
from caom2.wcs.caom2_coord_axis1d import CoordAxis1D
from caom2.wcs.caom2_coord_range1d import CoordRange1D
from caom2.wcs.caom2_ref_coord import RefCoord
from caom2.wcs.caom2_temporal_wcs import TemporalWCS

from jcmt2caom2.mjd import utc2mjd

from ukirt2caom2.util import airmass_to_elevation, valid_object

class ObservationUKIRT():
    def __init__(self, date, obs_num, id_, project_id, project_info,
                 geolocation, fits_format):
        self.date = datetime.strptime(date, '%Y%m%d')
        self.fits_format = fits_format
        id_ = id_.encode('ascii')

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
        self.ingest_environment(headers)
        self.ingest_instrument(headers)
        self.ingest_plane(headers)

    def ingest_target(self, headers):
        if 'OBJECT' in headers[0]:
            object = valid_object(headers[0]['OBJECT'])
            target = Target(object.encode('ascii'))

            if 'STANDARD' in headers[0]:
                target.standard = True if headers[0]['STANDARD'] else False

            target.target_type = None

            self.caom2.target = target

    def ingest_environment(self, headers):
        environment = Environment()

        # Elevation.

        airmasses = []

        for hdr in headers:
            if 'AMSTART' in hdr:
                airmasses.append(hdr['AMSTART'])
            if 'AMEND' in hdr:
                airmasses.append(hdr['AMEND'])

        environment.elevation = airmass_to_elevation(max(airmasses))

        if 'HUMIDITY' in headers[0]:
            humidity = headers[0]['HUMIDITY'] / 100

            # We seem to have some humidity values over 100% which
            # the Environment class will reject.
            if humidity > 1.0:
                humidity = 1.0
            elif humidity < 0.0:
                humidity = 0.0

            environment.humidity = humidity

        if 'AIRTEMP' in headers[0]:
            environment.ambient_temp = headers[0]['AIRTEMP']

        self.caom2.environment = environment

    def ingest_plane(self, headers):
        plane = Plane('raw')

        plane.calibration_level = CalibrationLevel.RAW_STANDARD \
            if self.fits_format else CalibrationLevel.RAW_INSTRUMENT

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
            time = CoordAxis1D(Axis('TIME', 'd'))
            time.range = CoordRange1D(
                    RefCoord(0.5, self.parse_date(headers[0]['DATE-OBS'])),
                    RefCoord(1.5, self.parse_date(headers[0]['DATE-END'])))

            chunk.time = TemporalWCS(time, 'UTC')

        part.chunks = TypedList((Chunk,), chunk)

        return [part]

    def parse_date(self, date_str):
        if date_str[-1] == 'Z':
            date_str = date_str[:-1]

        date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')

        return utc2mjd(date)
