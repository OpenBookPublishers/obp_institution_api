import web
from api import *
from errors import *
from models import Country

logger = logging.getLogger(__name__)

class CountryController(object):
    """Handles country queries"""

    @json_response
    @api_response
    def GET(self, name):
        """ Get countries."""
        logger.debug("Query: %s" % (web.input()))

        country_name   = web.input().get('country_name')
        if country_name:
            results = Country.get_from_name(country_name)
        else:
            results = Country.get_all()

        if not results:
            raise Error(NORESULT)
        data = results_to_countries(results)
        return data

    @json_response
    @api_response
    def POST(self, name):
        """Inserts new country."""
        data = json.loads(web.data())
        country_code = data.get('country_code')
        try:
            assert country_code
        except AssertionError as error:
            logger.debug(error)
            raise Error(BADPARAMS)
        country = Country(country_code)
        country.save()
        return [country.__dict__]

    def PUT(self, name):
        raise Error(NOTALLOWED)

    def DELETE(self, name):
        raise Error(NOTALLOWED)
