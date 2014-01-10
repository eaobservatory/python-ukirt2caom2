class ObsList(object):
    def __init__(self):
        self.blocks = []
        self.pending = []

    def __call__(self, obsnum):
        if self.pending and (self.pending[-1] != obsnum - 1):
            self._flush_pending()

        self.pending.append(obsnum)

    def _flush_pending(self):
        if not self.pending:
            return
        elif len(self.pending) == 1:
            self.blocks.append(str(self.pending[0]))
        else:
            self.blocks.append('{}:{}'.format(self.pending[0], self.pending[-1]))

        self.pending = []

    def get_list(self):
        self._flush_pending()
        return(','.join(self.blocks))
