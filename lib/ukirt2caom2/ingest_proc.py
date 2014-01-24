from datetime import datetime
from io import BytesIO
from pprint import pprint
from logging import getLogger
import re

from caom2 import Algorithm, Artifact, CompositeObservation, Instrument, Plane, Telescope
from caom2.caom2_enums import CalibrationLevel, ObservationIntentType, ProductType
from caom2.xml.caom2_observation_writer import ObservationWriter
from caom2repoClient.caom2repoClient import CAOM2RepoClient

from ukirt2caom2.geolocation import ukirt_geolocation
from ukirt2caom2.release_date import ReleaseCalculator

logger = getLogger(__name__)

pattern_fits = re.compile('UKIRT_([A-Z]+)_([0-9]+)_([0-9]+)_([A-Za-z0-9]+)\.fits')
pattern_png = re.compile('UKIRT_([A-Z]+)_([0-9]+)_([0-9]+)_([A-Za-z0-9]+)_preview_([0-9]+)\.png')

class IngestProc:
    def __init__(self):
        self.geolocation = ukirt_geolocation()
        self.release_calculator = ReleaseCalculator()
        self.writer = ObservationWriter(True)
        self.client = CAOM2RepoClient()

    def __call__(self, files):
        observations = {}
        previews = {}

        for file in files:
            match = pattern_fits.match(file)

            if match:
                (instrument, date, obsnum, product) = match.groups()

                key = (instrument, date, obsnum)

                if key in observations:
                    observations[key].append(product)
                else:
                    observations[key] = [product]

                continue

            match = pattern_png.match(file)

            if match:
                (instrument, date, obsnum, product, size) = match.groups()

                key = (instrument, date, obsnum, product)

                if key in previews:
                    previews[key].append(int(size))
                else:
                    previews[key] = [int(size)]

                continue

            logger.warning('Unrecognised file name: {}'.format(file))

        for (key, products) in observations.items():
            (instrument, date, obsnum) = key

            dateobj = datetime.strptime(date, '%Y%m%d')
            release = self.release_calculator.calculate(dateobj)

            observation = CompositeObservation(
                collection='UKIRT',
                observation_id='{}_{}_{}'.format(instrument, date, obsnum),
                algorithm=Algorithm('group'),
                sequence_number=int(obsnum),
                intent=ObservationIntentType.SCIENCE,
                telescope=Telescope('UKIRT', *self.geolocation),
                instrument=Instrument(instrument),
                meta_release=release,
            )

            for product in products:
                plane = Plane(
                    product_id=product,
                    meta_release=release,
                    data_release=release
                )

                observation.planes[product] = plane

                uri = 'ad:UKIRT/UKIRT_{}_{}_{}_{}.fits'.format(instrument, date, obsnum, product)

                artifact = Artifact(uri, product_type=ProductType.SCIENCE)

                plane.artifacts[uri] = artifact

                key = (instrument, date, obsnum, product)

                if key in previews:
                    for size in sorted(previews[key]):
                        uri = 'ad:UKIRT/UKIRT_{}_{}_{}_{}_preview_{}.png'.format(instrument, date, obsnum, product, size)

                        artifact = Artifact(uri, product_type=ProductType.PREVIEW)

                        plane.artifacts[uri] = artifact

            with BytesIO() as f:
                self.writer.write(observation, f)
                xml = f.getvalue()


            caom2_uri = 'caom2:UKIRT/{}_{}_{}'.format(instrument, date, obsnum)

            logger.info('Updating record: {}'.format(caom2_uri))
            self.client.remove(caom2_uri)
            status = self.client.put_xml(caom2_uri, xml)
            if not status:
                raise Exception('Failed to send to CAOM-2 repository')
