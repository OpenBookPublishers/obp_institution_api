import web
from api import *
from errors import *
from models import Institution, Country
import json

logger = logging.getLogger(__name__)

class InstitutionController(object):
    """Handles institution queries"""

    @json_response
    def OPTIONS(self,name):
        return

    @json_response
    @api_response
    @check_token
    def GET(self, name):
        """ Get institutions."""
        logger.debug("Query: %s" % (web.input()))

        institution_uuid   = web.input().get('institution_uuid')
        if institution_uuid:
            results = Institution.get_institution(institution_uuid)
        else:
            results = Institution.get_all()

        if not results:
            raise Error(NORESULT)
        data = results_to_institutions(results)
        return data

    @json_response
    @api_response
    @check_token
    def POST(self, name):
        """Inserts new institution."""
        logger.debug(web.data())
        data = json.loads(web.data())
        institution_name = data.get('institution_name')
        country_code = data.get('country_code')
        country_name = data.get('country_name')
        institution_notes = data.get('institution_notes')
        contacts = data.get('contacts')
        ip_ranges = data.get('ip_ranges')
        parent_of = data.get('parent_of')
        child_of = data.get('child_of')
        try:
            assert institution_name and ip_ranges
        except AssertionError as error:
            logger.debug(error)
            raise Error(BADPARAMS,msg="Both institution name and ip range are required.")
        try:
            country = ""
            if country_name and not country_code:
                logger.debug(country_name)
                country = country_name
                country_code = Country.get_from_name(country_name).first()['country_code']
                logger.debug(country_code)
            elif country_code and not country_name:
                country = country_code
                country_name = Country(country_code).get_names().first()['country_name']
            else:
                raise Error(BADPARAMS,msg="No country provided.")
        except:
            raise Error(BADPARAMS,msg="Country '%s' does not exist." %(country))
        institution_uuid = generate_uuid()
        institution = Institution(institution_uuid,institution_name,
                                                    country_code,
                                                    institution_notes,
                                                    contacts,
                                                    ip_ranges,
                                                    parent_of,
                                                    child_of)
        institution.save()
        return [institution.__dict__]

    @json_response
    @api_response
    @check_token
    def PUT(self, name):
        """Checks if entry exists using uuid, then modifies it."""
        data = json.loads(web.data())
        institution_uuid = data.get('institution_uuid')
        name = data.get('institution_name')
        country_code = data.get('country_code')
        try:
            assert institution_uuid and name and country_code
        except AssertionError as error:
            logger.debug(error)
            raise Error(BADPARAMS)
        try:
            assert Institution.get_institution(institution_uuid)[0]
        except:
            raise Error(NOTFOUND,msg="The institution provided does not exist.")
        institution = Institution(institution_uuid,name,country_code)
        institution.update()
        return [institution.__dict__]

    @json_response
    @api_response
    @check_token
    def DELETE(self, name):
        """Deletes institution using institution uuid."""
        institution_uuid = web.input().get('institution_uuid')
        try:
            assert institution_uuid
        except AssertionError as error:
            logger.debug(error)
            raise Error(BADPARAMS)
        try:
            result = Institution.get_institution(institution_uuid)[0]
        except:
            raise Error(NOTFOUND,msg="The institution provided does not exist.")
        institution = Institution(result['institution_uuid'],
                    result['institution_name'],result['institution_country_code'])
        institution.delete()
        return [institution.__dict__]
