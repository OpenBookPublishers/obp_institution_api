#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Institutional IP ranges API. Simple web.py based API to a PostgreSQL database.

usage: python api.py

(c) Tan Chuan, Open Book Publishers, March 2018
Use of this software is governed by the terms of the MIT license

Dependencies:
  pbkdf2==1.3
  PyJWT==1.6.1
  psycopg2==2.6.1
  uri==2.0.0
  urllib3==1.20
  web.py==0.38
"""

import os
import web
import sys
import json
import logging
from errors import *
import uuid
import re

# Determine logging level
debug = os.environ['API_DEBUG'] == 'True'
level = logging.NOTSET if debug else logging.ERROR
logging.basicConfig(level=level)
logger = logging.getLogger(__name__)


# Define routes
urls = (
    "/institutions(/?)", "instctrl.InstitutionController",
    "/contacts(/?)", "contactctrl.ContactController",
    "/countries(/?)", "countryctrl.CountryController",
    "/ipranges(/?)", "iprangectrl.IPRangeController",
)

try:
    db = web.database(dbn='postgres',
                      host=os.environ['INSTITUTIONDB_HOST'],
                      user=os.environ['INSTITUTIONDB_USER'],
                      pw=os.environ['INSTITUTIONDB_PASS'],
                      db=os.environ['INSTITUTIONDB_DB'])
except Exception as error:
    logger.error(error)
    raise Error(FATAL)

def api_response(fn):
    """Decorator to provided consistency in all responses"""
    def response(self, *args, **kw):
        data  = fn(self, *args, **kw)
        count = len(data)
        if count > 0:
            return {'status': 'ok', 'count': count, 'data': data}
        else:
            raise Error(NORESULT)
    return response

def json_response(fn):
    """JSON decorator"""
    def response(self, *args, **kw):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        return json.dumps(fn(self, *args, **kw), ensure_ascii=False)
    return response

def results_to_institutions(results):
    data = []
    for e in results:
        data.append(result_to_institution(e).__dict__)
    return data

def result_to_institution(r):
    inst = Institution(r["institution_uuid"], r["institution_name"], r["institution_country_code"])
    inst.load_contacts()
    inst.load_ip_ranges()
    return inst

def results_to_contacts(results):
    data = []
    for e in results:
        data.append(result_to_contact(e).__dict__)
    return data

def result_to_contact(r):
    return Contact(r["contact_uuid"], r["institution_uuid"], r["contact_name"],
                r["contact_email_address"], r["contact_notes"])

def results_to_countries(results):
    data = []
    for e in results:
        data.append(result_to_country(e).__dict__)
    return data

def result_to_country(r):
    return Country(r["country_code"])

def results_to_ip_ranges(results):
    data = []
    for e in results:
        data.append(result_to_ip_range(e).__dict__)
    return data

def result_to_ip_range(r):
    return IPRange(r["institution_uuid"],r["ip_range_value"])

def generate_uuid():
    return str(uuid.uuid4())

import instctrl, contactctrl, countryctrl, iprangectrl
from models import Institution, Contact, Country, IPRange

if __name__ == "__main__":
    logger.info("Starting API...")
    app = web.application(urls, globals())
    web.config.debug = debug
    app.internalerror = internal_error
    app.notfound = not_found
    app.run()
