import web
import json

NOTFOUND     = 10
NOTALLOWED   = 20
BADPARAMS    = 30
BADFILTERS   = 40
NORESULT     = 50
FATAL        = 80
UNAUTHORIZED = 90
FORBIDDEN    = 100
BADAUTH      = 110
NOTVALIDIP   = 120
IPEXISTS     = 130
SAMEINST     = 140
DEFAULT      = NOTFOUND

_level_messages = {
    NOTFOUND:     'Not Found.',
    NOTALLOWED:   'Not Allowed.',
    BADPARAMS:    'Invalid parameters provided.',
    BADFILTERS:   'Invalid filters supplied.',
    NORESULT:     'No records have matched your search criteria.',
    FATAL:        'Something terrible has happened.',
    UNAUTHORIZED: 'Authentication is needed.',
    FORBIDDEN:    'You do not have permissions to access this resource.',
    BADAUTH:      'Wrong credentials provided.',
    NOTVALIDIP:   'Invalid IP range. Cannot be cidrized.',
    IPEXISTS:     'IP already exists.',
    SAMEINST:     'The two uuids provided are the same.'
}

_level_codes = {
    NOTFOUND:     404,
    NOTALLOWED:   405,
    BADPARAMS:    400,
    BADFILTERS:   400,
    NORESULT:     404,
    FATAL:        500,
    UNAUTHORIZED: 401,
    FORBIDDEN:    403,
    BADAUTH:      401,
    NOTVALIDIP:   400,
    IPEXISTS:     400,
    SAMEINST:     400
}

_level_statuses = {
    NOTFOUND:     '404 Not Found',
    NOTALLOWED:   '405 Method Not Allowed',
    BADPARAMS:    '400 Bad Request',
    BADFILTERS:   '400 Bad Request',
    NORESULT:     '404 Not Found',
    FATAL:        '500 Internal Server Error',
    UNAUTHORIZED: '401 Unauthorized',
    FORBIDDEN:    '403 Forbidden',
    BADAUTH:      '401 Unauthorized',
    NOTVALIDIP:   '400 Bad Request',
    IPEXISTS:     '400 Bad Request',
    SAMEINST:     '400 Bad Request'

}

class Error(web.HTTPError):
    """Exception handler in the form of http errors"""

    def __init__(self, level=DEFAULT, msg = '', data = []):
        httpstatus = self.get_status(level)
        httpcode   = self.get_code(level)
        headers    = {'Content-Type': 'application/json'}
        message    = self.get_message(level)
        params     = web.input() if web.input() else web.data()
        output     = json.dumps(
                        self.make_output(httpcode, message, msg,  params, data))

        web.HTTPError.__init__(self, httpstatus, headers, output)

    def get_code(self, level):
        return _level_codes.get(level)

    def get_status(self, level):
        return _level_statuses.get(level)

    def get_message(self, level):
        return _level_messages.get(level)

    def make_output(self, httpcode, status_msg, description,  parameters, data):
        return {
            'status': 'error',
            'code': httpcode,
            'message': status_msg,
            'description': description,
            'parameters': parameters,
            'count': len(data),
            'data': data
        }

def not_found():
    raise Error(NOTFOUND)

def internal_error():
    raise Error(FATAL)
