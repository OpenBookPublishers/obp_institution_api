import web
from api import *
from errors import *
from models import Contact

logger = logging.getLogger(__name__)

class ContactController(object):
    """Handles contact queries"""

    @json_response
    @api_response
    def GET(self, name):
        """ Get contacts."""
        logger.debug("Query: %s" % (web.input()))

        contact_name = web.input().get('contact_name')
        if contact_name:
            results = Contact.get_from_name(contact_name)
        else:
            results = Contact.get_all()

        if not results:
            raise Error(NORESULT)
        data = results_to_contacts(results)
        return data

    def POST(self, name):
        data = json.loads(web.data())
        uuid = data.get('institution_uuid')
        name = data.get('contact_name')
        email_address = data.get('contact_email_address')
        notes = data.get('contact_notes')
        try:
            assert uuid and name and email_address and notes
        except AssertionError as error:
            logger.debug(error)
            raise Error(BADPARAMS)
        contact = Contact(uuid,name,email_address,notes)
        contact.save()
        return [contact.__dict__]

    def PUT(self, name):
        raise Error(NOTALLOWED)

    def DELETE(self, name):
        raise Error(NOTALLOWED)
