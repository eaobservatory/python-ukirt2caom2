from datetime import datetime, timedelta

from caom2 import Artifact, Chunk, \
        Environment, Part, Plane, Target
from caom2.caom2_enums import CalibrationLevel, ObservationIntentType
from caom2.util.caom2_util import TypedList
from caom2.wcs.caom2_axis import Axis
from caom2.wcs.caom2_coord_axis1d import CoordAxis1D
from caom2.wcs.caom2_coord_range1d import CoordRange1D
from caom2.wcs.caom2_ref_coord import RefCoord
from caom2.wcs.caom2_temporal_wcs import TemporalWCS

from jcmt2caom2.mjd import utc2mjd

from ukirt2caom2 import IngestionError
from ukirt2caom2.util import airmass_to_elevation, clean_header, valid_object

c = 299792458.0

calibration_types = ('dark', 'flat', 'arc', 'sky',
                     'targetacq', 'bias', 'calibration')

class ObservationUKIRT():
    def __init__(self, caom2_obs, date, uri, fits_format):
        self.caom2 = caom2_obs
        self.date = datetime.strptime(date, '%Y%m%d')
        self.uri = uri
        self.fits_format = fits_format

        # Useful data to cache during the ingestion process

        self.obstype = None

    def ingest(self, headers, translated):
        # Go through each ingestion step, allowing each to be
        # over-ridden by sub-classes.  Note that the order
        # is important because instrument classes may
        # add data to the object.

        self.ingest_type_intent(headers)
        self.ingest_target(headers)
        self.ingest_environment(headers)
        self.ingest_instrument(headers)
        self.ingest_plane(headers, translated)

    def ingest_target(self, headers):
        # Must ingest type/intent before this to determine whether
        # we should be reading STANDARD or not.

        if 'OBJECT' in headers[0]:
            object = valid_object(headers[0]['OBJECT'])

            # If the target name is the empty string then the CAOM-2 observation
            # writer writes <caom2:name></caom2:name> and the reader fails
            # to read it as it gets None as the child text and rejects
            # it for not being a string.
            if object == '':
                return

            target = Target(object)

            if (self.caom2.intent == ObservationIntentType.SCIENCE and
                    'STANDARD' in headers[0]):
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

            self.obstype = type

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

    def ingest_plane(self, headers, translated):
        plane = self.caom2.planes.get('raw', None)
        if plane is None:
            plane = Plane('raw')
            self.caom2.planes.clear()
            self.caom2.planes['raw'] = plane

        plane.calibration_level = CalibrationLevel.RAW_STANDARD \
            if self.fits_format else CalibrationLevel.RAW_INSTRUMENT

        if self.date.month == 2 and self.date.day == 29:
            release = self.date.replace(day=28, year=self.date.year + 1)

        else:
            release = self.date.replace(year=self.date.year + 1)

        plane.meta_release = release
        plane.data_release = release

        artifact = self.ingest_artifact(plane, headers, translated)

    def ingest_artifact(self, plane, headers, translated):
        artifact = plane.artifacts.get(self.uri, None)
        if artifact is None:
            artifact = Artifact(self.uri)
            plane.artifacts.clear()
            plane.artifacts[self.uri] = artifact

        self.ingest_parts(artifact, headers, translated)

    def ingest_parts(self, artifact, headers, translated):
        # We only have FITS files for UFTI and we don't appear to
        # have any with multiple extensions.
        part_name = 'fits' if self.fits_format else 'ndf'
        part = artifact.parts.get(part_name, None)
        if part is None:
            part = Part(part_name)
            artifact.parts.clear()
            artifact.parts[part_name] = part

        if len(part.chunks) == 1:
            chunk = part.chunks[0]

        else:
            chunk = Chunk()
            part.chunks = TypedList((Chunk,), chunk)

        if 'DATE-OBS' in headers[0] and 'DATE-END' in headers[0]:
            date_start = self.parse_date(headers[0]['DATE-OBS'])
            date_end = self.parse_date(headers[0]['DATE-END'])

            if date_start is not None and date_end is not None:
                time = CoordAxis1D(Axis('TIME', 'd'))
                time.range = CoordRange1D(
                        RefCoord(0.5, date_start),
                        RefCoord(1.5, date_end))

                chunk.time = TemporalWCS(time, 'UTC')

        energy = self.get_spectral_wcs(headers)
        if energy is not None:
            chunk.energy = energy

        position = self.get_spatial_wcs(headers, translated)
        if position is not None:
            chunk.position = position

        polarization = self.get_polarization_wcs(headers)
        if polarization is not None:
            chunk.polarization = polarization

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
