import psycopg2
from api import *
from errors import *

logger = logging.getLogger(__name__)

class Institution(object):
    def __init__(self, uuid, name, country_code):
        self.UUID  = uuid
        self.name  = name
        self.country_code = country_code

    def get_contacts(self):
        options = dict(uuid=self.UUID)
        return db.select('contact', options,
                         what="contact_name", where="institution_uuid = $uuid")

    def get_ip_ranges(self):
        options = dict(uuid=self.UUID)
        return db.select('ip_range', options,
                         what="ip_range_value",
                         where="institution_uuid = $uuid")


    def load_contacts(self):
        data = []
        for e in self.get_contacts():
            data.append(e)
        self.contacts = data


    def load_ip_ranges(self):
        data = []
        for e in self.get_ip_ranges():
            data.append(e)
        self.ip_ranges = data

    @staticmethod
    def get_all():
        try:
            return db.select('institution')
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def get_institution(uuid):
        options = dict(uuid=uuid)
        return db.select('institution',options, where="institution_uuid = $uuid")
