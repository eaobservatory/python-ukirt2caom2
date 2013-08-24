#!/usr/bin/env python

from __future__ import print_function

import logging
import os.path

from caom2.caom2_enums import ObservationIntentType
from ukirt2caom2.ingest import IngestRaw

instruments = ('cgs3', 'cgs4', 'ircam', 'michelle', 'ufti', 'uist')

def main():
    from argparse import ArgumentParser
    import re

    parser = ArgumentParser()

    parser.add_argument('--instrument', '-i', required=True,
                        choices=instruments)
    parser.add_argument('--date', '-d', required=False,
                        default=None)
    parser.add_argument('--verbose', '-v', required=False,
                        default=False, action='store_true')

    args = parser.parse_args()

    if args.date is not None and not re.match('^[0-9]{8}$', args.date):
        raise Exception('Invalid date ' + args.date)

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    logger = logging.getLogger()

    logger.info('Initializing preparation')
    raw = IngestRaw()

    logger.info('Staring preparation')
    observations = raw(args.instrument, args.date, return_observations=True)

    logger.info('Finished preparation')


    calibrations = []
    science = []

    prep = DR_Prep()

    for key in sorted(observations.keys()):
        (date, obs) = key
        (filename, observation, doc) = observations[key]

        if observation.caom2.intent == ObservationIntentType.CALIBRATION:
            calibrations.append((obs, observation, doc, filename))
        else:
            science.append((obs, observation, doc, filename))

    for obs in calibrations + science:
        (obsnum, obs, doc, filename) = obs
        (filename, extension) = os.path.splitext(filename)
        prep(obsnum, obs, doc, filename)

    print(prep.get_list())
    prep.write_headers()

class DR_Prep(object):
    def __init__(self):
        # Observation sequences for reduction lists.
        self.blocks = []
        self.pending = []

        # Header override information.
        self.filename = {}
        self.headers = {}

        # Observation grouping.
        self.group = []
        self.groupkey = None

    def __call__(self, obsnum, obs, doc, filename):
        recipe = self._determine_recipe(obs, doc)
        self.headers[obsnum] = {'DRRECIPE': recipe}
        self.filename[obsnum] = filename

        if self.pending and (self.pending[-1] != obsnum - 1):
            self._flush_pending()

        self.pending.append(obsnum)

        groupkey = self._group_key(obs, doc)
        if self.group and (self.groupkey != groupkey):
            self._flush_group()

        if groupkey is not None:
            self.group.append(obsnum)
            self.groupkey = groupkey

    def _determine_recipe(self, obs, doc):
        if obs.caom2.intent == ObservationIntentType.CALIBRATION:
            if doc['headers'][0]['OBJECT'] == 'Array Tests':
                return 'ARRAY_TESTS'
            else:
                return 'REDUCE_DARK'
        else:
            return 'JITTER_SELF_FLAT'

    def _flush_pending(self):
        if len(self.pending) == 1:
            self.blocks.append(str(self.pending[0]))
        else:
            self.blocks.append('{}:{}'.format(self.pending[0], self.pending[-1]))

        self.pending = []

    def _flush_group(self):
        if not self.group:
            return

        grpnum = self.group[0]
        noffsets = len(self.group) + 1

        if len(self.group) > 1:
            for num in self.group:
                self.headers[num]['GRPNUM'] = grpnum
                self.headers[num]['GRPMEM'] = 'T'
                self.headers[num]['NOFFSETS'] = noffsets

        self.group = []

    def _group_key(self, obs, doc):
        return doc['headers'][0]['OBJECT']

    def get_list(self):
        self._flush_pending()
        return(','.join(self.blocks))

    def write_headers(self):
        self._flush_group()

        with open('header_override.ini', 'w') as f:
            for obsnum in sorted(self.filename.keys()):
                print('[{}]'.format(self.filename[obsnum]), file=f)

                for (header, value) in self.headers[obsnum].items():
                    print('{}={}'.format(header, value), file=f)

                print('', file=f)

if __name__ == '__main__':
    main()

