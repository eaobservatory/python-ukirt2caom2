#!/usr/bin/env python

def fixup_headers(doc):
    """Attempt to fix mangled FITS headers.

    Tries to fix the following:

    * Long strings including the comment.

    Alters the supplied document in place and
    doesn't return anything."""

    for hdr in doc['headers']:
        cards = hdr.keys()

        for card in cards:
            val = hdr[card]
            modified = False

            if type(val) is str:
                if len(val) > 23:
                    pos = val.find('/', 23)
                    if pos != -1:
                        val = val[:pos].rstrip()
                        modified = True

                        if val.startswith('='):
                            val = val[1:]

            if modified:
                try:
                    hdr[card] = int(val)
                except ValueError:
                    try:
                        hdr[card] = float(val)
                    except ValueError:
                        hdr[card] = val

