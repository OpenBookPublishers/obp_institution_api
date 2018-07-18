import web
from api import *
from errors import *
from models import IPRange

logger = logging.getLogger(__name__)

class IPRangeController(object):
    """Handles IPRange queries"""

    @json_response
    @api_response
    def GET(self, name):
        """ Get IP Range."""
        logger.debug("Query: %s" % (web.input()))

        ip_range   = web.input().get('ip_range_value')
        if ip_range:
            results = IPRange.get_from_ip_range(ip_range)
        else:
            results = IPRange.get_all()

        if not results:
            raise Error(NORESULT)
        data = results_to_ip_ranges(results)
        return data

    @json_response
    @api_response
    def POST(self, name):
        """Inserts new iprange."""
        data = json.loads(web.data())
        institution_uuid = data.get('institution_uuid')
        ip_range_value = data.get('ip_range_value')
        try:
            assert institution_uuid and ip_range_value
        except AssertionError as error:
            logger.debug(error)
            raise Error(BADPARAMS)
        iprange = IPRange(institution_uuid,ip_range_value)
        iprange.save()
        return [iprange.__dict__]

    def PUT(self, name):
        raise Error(NOTALLOWED,msg="Try deleting or inserting instead.")

    @json_response
    @api_response
    def DELETE(self, name):
        """Deletes ip-range using ip-range."""
        ip_range_value = web.input().get('ip_range_value')
        try:
            assert ip_range_value
        except AssertionError as error:
            logger.debug(error)
            raise Error(BADPARAMS)
        try:
            r = IPRange.get_from_ip_range(ip_range_value)[0]
            iprange = IPRange(r['institution_uuid'],r['ip_range_value'])
            iprange.delete()
        except:
            raise Error(NOTFOUND,msg="The ip-range does not exist.")
        return [iprange.__dict__]
