import web
from api import *
from errors import *
from models import Institution
import json

logger = logging.getLogger(__name__)

class InstitutionController(object):
    """Handles institution queries"""

    @json_response
    @api_response
    def GET(self, name):
        """ Get institutions."""
        logger.debug("Query: %s" % (web.input()))

        uuid   = web.input().get('uuid')
        if uuid:
            results = Institution.get_institution(uuid)
        else:
            results = Institution.get_all()

        if not results:
            raise Error(NORESULT)
        data = results_to_institutions(results)
        return data

    @json_response
    @api_response
    def POST(self, name):
        """Inserts new institution."""
        data = json.loads(web.data())
        institution_name = data.get('institution_name')
        country_code = data.get('country_code')
        try:
            assert institution_name and country_code
        except AssertionError as error:
            logger.debug(error)
            raise Error(BADPARAMS)
        uuid = generate_uuid_from_name(institution_name)
        institution = Institution(uuid,institution_name,country_code)
        institution.save()
        return [institution.__dict__]

    def PUT(self, name):
        raise Error(NOTALLOWED)

    @json_response
    @api_response
    def DELETE(self, name):
        raise Error(NOTALLOWED)
