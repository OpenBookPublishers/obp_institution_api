import psycopg2
from api import *
from errors import *

logger = logging.getLogger(__name__)

class Institution(object):
    def __init__(self, uuid, name, country_code):
        self.institution_uuid  = uuid
        self.institution_name  = name
        self.country_code = country_code

    def get_contacts(self):
        options = dict(uuid=self.institution_uuid)
        try:
            return db.select('contact', options,
                         what="contact_uuid", where="institution_uuid = $uuid")
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    def get_ip_ranges(self):
        options = dict(uuid=self.institution_uuid)
        try:
            return db.select('ip_range', options,
                         what="ip_range_value",
                         where="institution_uuid = $uuid")
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

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
        try:
            db.insert('institution',institution_name=self.institution_name,
                    institution_uuid=self.institution_uuid, institution_country_code=self.country_code)
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    def delete(self):
        options = dict(uuid=self.institution_uuid)
        try:
            db.delete('institution',vars = options, where='institution_uuid=$uuid')
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    def update(self):
        options = dict(uuid=self.institution_uuid)
        try:
            db.update('institution',vars = options, where='institution_uuid=$uuid',
                institution_name = self.institution_name,institution_country_code=self.country_code)
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

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
        try:
            return db.select('institution',options, where="institution_uuid = $uuid")
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

class Contact(object):
    def __init__(self, contact_uuid, institution_uuid, name, email_address, notes):
        self.institution_uuid  = institution_uuid
        self.contact_uuid = contact_uuid
        self.contact_name  = name
        self.email_address = email_address
        self.notes = notes

    def save(self):
        try:
            db.insert('contact',contact_name=self.contact_name,
                    contact_email_address=self.email_address,contact_notes=self.notes,
                    institution_uuid=self.institution_uuid, contact_uuid=self.contact_uuid)
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    def delete(self):
        options = dict(uuid=self.contact_uuid)
        try:
            db.delete('contact',vars = options, where='contact_uuid=$uuid')
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    def update(self):
        options = dict(uuid=self.contact_uuid)
        try:
            db.update('contact',vars = options, where='contact_uuid=$uuid',
                contact_name = self.contact_name,contact_email_address=self.email_address,
                 contact_notes=self.notes,institution_uuid=self.institution_uuid,contact_uuid=self.contact_uuid)
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    @staticmethod
    def get_all():
        try:
            return db.select('contact')
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def get_from_uuid(uuid):
        options = dict(uuid=uuid)
        try:
            return db.select('contact',options, where="contact_uuid = $uuid")
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

class IPRange(object):
    def __init__(self, uuid, ip_range):
        self.institution_uuid  = uuid
        self.ip_range_value = ip_range

    def save(self):
        params = dict(ip_range=self.ip_range_value,institution_uuid=self.institution_uuid)
        q = """INSERT INTO ip_range (ip_range_value, institution_uuid)
        SELECT $ip_range,$institution_uuid
        WHERE NOT
        ( select inet $ip_range && any ( array(select ip_range_value from ip_range)::inet[] ) )
         OR NOT EXISTS (SELECT ip_range_value FROM ip_range);"""
        try:
            result = db.query(q,params)
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)
        if result == 0:
            p = """SELECT * FROM(
            SELECT ip_range_value, institution_name,
            (select inet $ip_range && ip_range_value)
            AS condition FROM ip_range
            JOIN institution USING (institution_uuid)
            ) table1
            WHERE condition = true
            """
            temp = db.query(p,params)
            result = temp[0]
            raise Error(IPEXISTS,msg="The ip provided (%s) contains or is contained by %s from %s."
            % (self.ip_range_value,result.ip_range_value,result.institution_name))

    def delete(self):
        try:
            options = dict(ip_range_value=self.ip_range_value)
            db.delete('ip_range',vars = options, where='ip_range_value=$ip_range_value')
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    @staticmethod
    def get_all():
        try:
            return db.select('ip_range')
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def get_from_ip_range(ip_range):
        options = dict(ip_range_value=ip_range)
        try:
            return db.select('ip_range',options, where="ip_range_value = $ip_range_value")
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

class Country(object):
    def __init__(self, country_code, country_name=[]):
        self.country_code = country_code
        self.country_name = country_name if country_name else [x['country_name'] for x in self.get_names()]

    def get_names(self):
        options = dict(country_code=self.country_code)
        try:
            return db.select('country_name',options, where="country_code = $country_code")
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    def save(self):
        try:
            q = '''INSERT INTO country VALUES ($country_code) ON CONFLICT DO NOTHING'''
            params = dict(country_code=self.country_code)
            with db.transaction():
                db.query(q,params)
                db.insert('country_name',country_code=self.country_code,country_name=self.country_name)
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    def delete(self):
        options = dict(country_code=self.country_code)
        try:
            with db.transaction():
                db.delete('country_name', vars = options, where='country_code=$country_code')
                db.delete('country',vars = options, where='country_code=$country_code')
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    def delete_name(self,country_name):
        options = dict(country_name = country_name)
        try:
            db.delete('country_name',vars=options,where='country_name=$country_name')
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    @staticmethod
    def get_all():
        try:
            q = """SELECT * FROM country ORDER BY country_code"""
            return db.query(q)
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def get_from_name(name):
        options = dict(name=name)
        q = """SELECT country_code FROM country_name WHERE country_name = $name"""
        try:
            return db.query(q,options)
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)
