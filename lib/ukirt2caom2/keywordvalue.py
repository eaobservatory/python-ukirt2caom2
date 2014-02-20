def keywordvalue(keyword, value):
    """Replacement for the old jcmt2caom2.raw.keywordvalue function

    Joins the given strings to form a keyword=value string
    without spaces.
    """

    kv = keyword + '=' + value

    return kv.replace(' ', '')
