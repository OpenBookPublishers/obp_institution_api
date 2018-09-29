import web
import sys
import json_outputter

from api import *
from errors import *
from io import BytesIO
from StringIO import StringIO

pysrc = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                     'cidrize_wacky_ranges')
sys.path.append(pysrc)
logger = logging.getLogger(__name__)

class CidrizeController(object):
    """Handles cidrize ip  queries"""

    @json_response
    def OPTIONS(self,name):
        return

    @json_response
    @api_response
    @check_token
    def GET(self, name):
        raise Error(NOTALLOWED,msg="Try inserting instead.")

    @json_response
    @api_response
    @check_token
    def POST(self, name):
        """Post xlsx file and cidrize the ip addresses within."""
        data = web.data()
        filename = BytesIO(data)
        stdout_ = sys.stdout
        stderr_ = sys.stderr
        result = StringIO()
        result_err = StringIO()
        sys.stdout = result
        sys.stderr = result_err
        json_outputter.process_file(filename,"Sheet1",1,3,5,7,9)
        sys.stdout = stdout_
        sys.stderr = stderr_
        return result.getvalue(), result_err.getvalue()

    @json_response
    @api_response
    @check_token
    def PUT(self, name):
        raise Error(NOTALLOWED,msg="Try inserting instead.")

    @json_response
    @api_response
    @check_token
    def DELETE(self, name):
        raise Error(NOTALLOWED,msg="Try inserting instead.")

