from caom2 import Environment, Proposal, SimpleObservation, Target, Telescope

from ukirt2caom2.util import airmass_to_elevation, valid_object

class ObservationUKIRT():
    def __init__(self, date, obs, id_, project_id, project_info, geolocation):
        self.date = date
        self.obs = obs

        # Construct CAOM2 object with basic identifying information.

        self.caom2 = SimpleObservation('UKIRT', id_.encode('ascii'))

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

    def ingest_target(self, headers):
        if 'OBJECT' in headers[0]:
            object = valid_object(headers[0]['OBJECT'])
            target = Target(object.encode('ascii'))

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

        self.caom2.environment = environment
