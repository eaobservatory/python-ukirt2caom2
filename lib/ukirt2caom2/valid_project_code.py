import re

training = re.compile('^[A-Z]{2,3}[0-9]{2}$')
service = re.compile('^U/SERV/([0-9]{4})$')
standard = re.compile('^U?/?([0-9]{2}[AB]|EC)/([HJD]?)([0-9]+)([AB]?)$')

def valid_project_code(code):
    '''Determine whether a string represents a valid UKIRT project.
    
    A validated project code will be returned if successful, otherwise
    None.'''

    if code is None:
        return None

    code = code.upper()

    if code == 'CAL':
        return code

    elif training.match(code):
        return code

    elif service.match(code):
        return code

    if code.startswith('PATT') and len(code) > 4:
        code = code[4:]

    m = standard.match(code)

    if m:
        return 'U/{}/{}{}{}'.format(m.group(1), m.group(2),
                                    int(m.group(3)), m.group(4))

    return None


if __name__ == '__main__':
    from pymongo import MongoClient

    mongo = MongoClient()

    for instrument in 'cgs3 cgs4 ircam michelle ufti uist'.split():
        collection = mongo.ukirt[instrument]
        codes = map(lambda x: x.encode('ascii'),
                    collection.distinct('headers.0.PROJECT'))

        for code in codes:
            vcode = valid_project_code(code)

            if vcode is None:
                print('Invalid code: ' + code)

            else:
                pass
                #print('  Valid code: ' + vcode)
