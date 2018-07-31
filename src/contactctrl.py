import web
from api import *
from errors import *
from models import Contact, Institution

logger = logging.getLogger(__name__)

class ContactController(object):
    """Handles contact queries"""

    @json_response
    @api_response
    def GET(self, name):
        """ Get contacts."""
        logger.debug("Query: %s" % (web.input()))

        contact_uuid = web.input().get('contact_uuid')
        if contact_uuid:
            results = Contact.get_from_uuid(contact_uuid)
        else:
            results = Contact.get_all()

        if not results:
            raise Error(NORESULT)
        data = results_to_contacts(results)
        return data

    @json_response
    @api_response
    def POST(self, name):
        """Inserts new contact."""
        data = json.loads(web.data())
        institution_uuid = data.get('institution_uuid')
        name = data.get('contact_name')
        email_address = data.get('email_address')
        notes = data.get('contact_notes')
        try:
            assert institution_uuid and name
        except AssertionError as error:
            logger.debug(error)
            raise Error(BADPARAMS)
        try:
            assert Institution.get_institution(institution_uuid)[0]
        except:
            raise Error(NOTFOUND,msg="The institution provided does not exist.")
        contact_uuid = generate_uuid()
        contact = Contact(contact_uuid,institution_uuid,name,email_address,notes)
        contact.save()
        return [contact.__dict__]

    @json_response
    @api_response
    def PUT(self, name):
        """Checks if entry exists using contact_uuid, then modifies it."""
        data = json.loads(web.data())
        institution_uuid = data.get('institution_uuid')
        contact_uuid = data.get('contact_uuid')
        name = data.get('contact_name')
        email_address = data.get('contact_email_address')
        notes = data.get('contact_notes')
        try:
            assert institution_uuid and contact_uuid and name
        except AssertionError as error:
            logger.debug(error)
            raise Error(BADPARAMS)
        try:
            assert Contact.get_from_uuid(contact_uuid)[0]
        except:
            raise Error(NOTFOUND,msg="The contact uuid provided does not exist.")
        contact = Contact(contact_uuid,institution_uuid,name,email_address,notes)
        contact.update()
        return [contact.__dict__]

    @json_response
    @api_response
    def DELETE(self, name):
        """Deletes contact using contact name."""
        contact_uuid = web.input().get('contact_uuid')
        try:
            assert contact_uuid
        except AssertionError as error:
            logger.debug(error)
            raise Error(BADPARAMS)
        try:
            result = Contact.get_from_uuid(contact_uuid)[0]
        except:
            raise Error(NOTFOUND,msg="The contact uuid provided does not exist.")
        contact = Contact(result['contact_uuid'],result['institution_uuid'],
                    result['contact_name'],result['contact_email_address'],
                    result['contact_notes'])
        contact.delete()
        return [contact.__dict__]
