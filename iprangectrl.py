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

        ip_range   = web.input().get('iprange')
        if ip_range:
            results = IPRange.get_from_ip_range(ip_range)
        else:
            results = IPRange.get_all()

        if not results:
            raise Error(NORESULT)
        data = results_to_ip_ranges(results)
        return data


    def POST(self, name):
        data = json.loads(web.data())
        uuid = data.get('institution_uuid')
        ip_range = data.get('ip_range')
        try:
            assert uuid and ip_range
        except AssertionError as error:
            logger.debug(error)
            raise Error(BADPARAMS)
        iprange = IPRange(uuid,ip_range)
        iprange.save()
        return [iprange.__dict__]

    def PUT(self, name):
        raise Error(NOTALLOWED)

    def DELETE(self, name):
        raise Error(NOTALLOWED)
