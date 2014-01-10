class HeaderOverride(object):
    def __init__(self):
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

    def write_headers(self):
        self._flush_group()

        with open('header_override.ini', 'w') as f:
            for obsnum in sorted(self.filename.keys()):
                print('[{}]'.format(self.filename[obsnum]), file=f)

                for (header, value) in self.headers[obsnum].items():
                    print('{}={}'.format(header, value), file=f)

                print('', file=f)


