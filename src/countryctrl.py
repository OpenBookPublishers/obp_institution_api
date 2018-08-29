import web
from api import *
from errors import *
from models import Country

logger = logging.getLogger(__name__)

class CountryController(object):
    """Handles country queries"""

    @json_response
    def OPTIONS(self,name):
        return

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
        country_name = data.get('country_name')
        try:
            assert country_code and country_name
        except AssertionError as error:
            logger.debug(error)
            raise Error(BADPARAMS)
        country = Country(country_code,country_name)
        country.save()
        return [country.__dict__]

    @json_response
    @api_response
    def PUT(self, name):
        raise Error(NOTALLOWED,msg="Try deleting or inserting instead.")

    @json_response
    @api_response
    def DELETE(self, name):
        """Deletes country using either country name or country code."""
        country_name = web.input().get('country_name')
        country_code = web.input().get('country_code')
        try:
            if country_name:
                assert country_name and not country_code
            elif country_code:
                assert country_code and not country_name
        except AssertionError as error:
            logger.debug(error)
            raise Error(BADPARAMS)
        try:
            if country_name:
                r = Country.get_from_name(country_name)[0]
                country = Country(r['country_code'])
                country.delete_name(country_name)
            elif country_code:
                country = Country(country_code)
                country.delete()
        except:
            raise Error(NOTFOUND,msg="The country does not exist.")
        return [country.__dict__]
