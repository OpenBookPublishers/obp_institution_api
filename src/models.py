import psycopg2
from api import *
from errors import *

logger = logging.getLogger(__name__)
dateformat = '%Y-%m-%dT%H:%M:%S%z'

class Institution(object):
    def __init__(self, uuid, name, country_code, institution_notes="",
                                                    contacts = [],
                                                    ip_ranges = [],
                                                    parent_of = [],
                                                    child_of = []):
        self.institution_uuid  = uuid
        self.institution_name  = name
        self.country_code = country_code
        self.institution_notes = institution_notes
        self.contacts = contacts
        self.ip_ranges = ip_ranges
        self.parent_of = parent_of
        self.child_of = child_of

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

    def get_parents(self):
        params = dict(uuid=self.institution_uuid)
        try:
            return db.query('''SELECT ir_parent_id FROM institution_relation WHERE
                                            ir_child_id = $uuid''',params)
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    def get_children(self):
        params = dict(uuid=self.institution_uuid)
        try:
            return db.query('''SELECT ir_child_id FROM institution_relation WHERE
                                            ir_parent_id = $uuid''',params)
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    def load_relations(self):
        data = []
        for e in self.get_children():
            data.append(e['ir_child_id'])
        self.set_attribute("parent_of",data)
        data = []
        for e in self.get_parents():
            data.append(e['ir_parent_id'])
        self.set_attribute("child_of",data)

    def load_dates(self):
        options = dict(uuid=self.institution_uuid)
        try:
            results = db.select('institution', options,
                    where="institution_uuid=$uuid",
                    what="institution_created_at,institution_updated_at").first()
            self.set_attribute("institution_created_at",
                                results['institution_created_at'].strftime(dateformat))
            self.set_attribute("institution_updated_at",
                                results['institution_updated_at'].strftime(dateformat))
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    def set_attribute(self,attribute,value):
        self.__dict__.update({attribute:value})

    def load_contacts(self):
        data = []
        for e in self.get_contacts():
            data.append(e['contact_uuid'])
        self.contacts = data

    def load_ip_ranges(self):
        data = []
        for e in self.get_ip_ranges():
            data.append(e['ip_range_value'])
        self.ip_ranges = data

    def save(self):
        with db.transaction():
            db.insert('institution',institution_name=self.institution_name,
                             institution_uuid=self.institution_uuid,
                             institution_country_code=self.country_code,
                             institution_created_at=web.SQLLiteral("NOW()"),
                             institution_updated_at=web.SQLLiteral("NOW()"))
            if self.ip_ranges:
                for ip_range in self.ip_ranges:
                    ipr = IPRange(self.institution_uuid,ip_range)
                    ipr.save()
            if self.contacts:
                for contact in self.contacts:
                    try:
                        assert contact['contact_name']
                    except:
                        raise Error(BADPARAMS, msg="Empty contact provided for %s" % (self.institution_name))
                    try:
                        assert contact['contact_notes']
                    except:
                        contact['contact_notes'] = None
                        pass
                    try:
                        assert contact['contact_email_address']
                    except:
                        contact['contact_email_address'] = None
                        pass

                    c = Contact(generate_uuid(),self.institution_uuid,
                                                contact['contact_name'],
                                                contact['contact_email_address'],
                                                contact['contact_notes'])
                    c.save()
            if self.parent_of:
                for child in self.parent_of:
                    relation = InstRelation(self.institution_uuid,child)
                    relation.save()
            if self.child_of:
                for parent in self.child_of:
                    relation = InstRelation(parent,self.institution_uuid)
                    relation.save()

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
                institution_name = self.institution_name,
                institution_country_code=self.country_code,
                institution_updated_at=web.SQLLiteral("NOW()"),
                institution_notes=self.institution_notes)
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
                    institution_uuid=self.institution_uuid, contact_uuid=self.contact_uuid,
                    contact_created_at=web.SQLLiteral("NOW()"),
                    contact_updated_at=web.SQLLiteral("NOW()"))
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
                 contact_notes=self.notes,institution_uuid=self.institution_uuid,
                 contact_uuid=self.contact_uuid,contact_updated_at=web.SQLLiteral("NOW()"))
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    def load_dates(self):
        options = dict(uuid=self.contact_uuid)
        try:
            results = db.select('contact', options,
                    where="contact_uuid=$uuid",
                    what="contact_created_at,contact_updated_at").first()
            self.set_attribute("contact_created_at",
                                results['contact_created_at'].strftime(dateformat))
            self.set_attribute("contact_updated_at",
                                results['contact_updated_at'].strftime(dateformat))
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    def set_attribute(self,attribute,value):
        self.__dict__.update({attribute:value})

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
        params = dict(ip_range=self.ip_range_value,
                    institution_uuid=self.institution_uuid,
                    ip_range_created_at=web.SQLLiteral("NOW()"))
        q = """INSERT INTO ip_range (ip_range_value, ip_range_created_at, institution_uuid)
        SELECT $ip_range,$ip_range_created_at,$institution_uuid
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

    def load_dates(self):
        options = dict(uuid=self.institution_uuid)
        try:
            results = db.select('ip_range', options,
                    where="institution_uuid=$uuid",
                    what="ip_range_created_at").first()
            self.set_attribute("ip_range_created_at",
                                results['ip_range_created_at'].strftime(dateformat))
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    def set_attribute(self,attribute,value):
        self.__dict__.update({attribute:value})

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

class InstRelation(object):
    def __init__(self, parent_uuid, child_uuid):
        self.parent_inst_uuid = parent_uuid
        self.child_inst_uuid = child_uuid

    def save(self):
        try:
            q = '''INSERT INTO institution_relation (ir_parent_id, ir_child_id) VALUES ($parent_inst_uuid,$child_inst_uuid)'''
            params = dict(parent_inst_uuid=self.parent_inst_uuid,child_inst_uuid=self.child_inst_uuid)
            with db.transaction():
                db.query(q,params)
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    def delete(self):
        try:
            q = '''DELETE FROM institution_relation WHERE
                    ir_parent_id = $parent_inst_uuid
                    AND ir_child_id = $child_inst_uuid'''
            params = dict(parent_inst_uuid=self.parent_inst_uuid,child_inst_uuid=self.child_inst_uuid)
            db.query(q,params)
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)

    @staticmethod
    def get_all():
        try:
            q = """SELECT * FROM institution_relation"""
            return db.query(q)
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    @staticmethod
    def get_from_uuids(institution_uuid_a, institution_uuid_b):
        options = dict(institution_uuid_a=institution_uuid_a ,
                        institution_uuid_b=institution_uuid_b)
        q1 = """SELECT * FROM institution_relation WHERE
                ir_parent_id = $institution_uuid_a AND
                ir_child_id = $institution_uuid_b"""
        q2 = """SELECT * FROM institution_relation WHERE
                ir_parent_id = $institution_uuid_b AND
                ir_child_id = $institution_uuid_a"""
        try:
            results = db.query(q1,options)
            if not results:
                results = db.query(q2,options)
        except Exception as error:
            logger.debug(error)
            raise Error(FATAL)
