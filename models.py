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

    def save(self):
        db.insert('institution',institution_name=self.name,
                institution_uuid=self.UUID, institution_country_code=self.country_code)

    def delete(self):
        options = dict(uuid=self.UUID)
        db.delete('institution',vars = options, where='institution_uuid=$uuid')

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

class Contact(object):
    def __init__(self, uuid, name, email_address, notes):
        self.institution_id  = uuid
        self.name  = name
        self.email_address = email_address
        self.notes = notes

    def save(self):
        db.insert('contact',contact_name=self.name,
                contact_email_address=self.email_address,contact_notes=self.notes,
                institution_uuid=self.institution_id)

    @staticmethod
    def get_all():
        try:
            return db.select('contact')
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def get_from_name(name):
        options = dict(name=name)
        return db.select('contact',options, where="contact_name = $name")

class IPRange(object):
    def __init__(self, uuid, ip_range):
        self.institution_id  = uuid
        self.ip_range = ip_range

    def save(self):
        db.insert('ip_range',institution_uuid=self.institution_id,
                ip_range_value=self.ip_range)

    @staticmethod
    def get_all():
        try:
            return db.select('ip_range')
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def get_from_ip_range(ip_range):
        options = dict(ip_range=ip_range)
        return db.select('ip_range',options, where="ip_range_value = $ip_range")

class Country(object):
    def __init__(self, country_code):
        self.country_code = country_code
        self.name = [x['country_name'] for x in self.get_names()]

    def get_names(self):
        options = dict(country_code=self.country_code)
        return db.select('country_name',options, where="country_code = $country_code")

    def save(self):
        db.insert('country_name',country_code=self.country_code,country_name=self.name) # TODO What happens if country_name is an array

    @staticmethod
    def get_all():
        try:
            q = """SELECT * FROM country_name ORDER BY country_code"""
            return db.query(q)
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def get_from_name(name):
        options = dict(name=name)
        q = """SELECT country_code FROM country_name WHERE country_name = $name"""
        return db.query(q,options)
