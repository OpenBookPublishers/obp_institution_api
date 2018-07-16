#!/usr/bin/env python2

# json_reader.py
# json_reader, by Chuan Tan <ct538@cam.ac.uk>
#
# Copyright (C) Chuan Tan 2018
#
# This programme is free software; you may redistribute and/or modify
# it under the terms of the Apache Licence, version 2.0.

# Usage: json_reader.py

# Reads from json files and adds stuff into database.

import psycopg2
import json
import uuid

def append_uuid(data):
    for JSONObject in data:
        institution_name = JSONObject["Institution"]
        JSONObject["Institution-uuid"] = str(uuid.uuid3(uuid.NAMESPACE_DNS,institution_name.encode("utf-8")))
        
    return data
        
def get_inst_country_code(country):
    # Returns country code of country where institution is located. 
    cursor.execute("SELECT country_code , country_name FROM country WHERE country_name = %s",[country])
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        # TODO: Case where there is missing country code
        return "00" # will return Key(institution_country_code) = (00) is not present in table "country".

def insert_into_institution(data):
    processed_data = [ ( data[x]["Institution-uuid"] , data[x]["Institution"] , get_inst_country_code(data[x]["Country"]) ) for x in range(len(data)) ]
    query = """INSERT INTO institution (institution_uuid,institution_name, institution_country_code)
                VALUES ( %s , %s , %s ); """
    cursor.executemany(query,processed_data)
    conn.commit()

def insert_into_contact(data):
    processed_data = [ ( "some guy", data[x]["Contact"] , "Hello world" , data[x]["Institution-uuid"] ) for x in range(len(data)) ]
    query = """INSERT INTO contact (contact_name,contact_email_address, contact_notes, institution_uuid)
                VALUES (%s , %s , %s , %s);"""
    cursor.executemany(query,processed_data)
    conn.commit()

def insert_into_ip_range(data):
    processed_data = []
    for i in range(len(data)):
        for j in range(len(data[i]["IP-Range"])):
            processed_data.append( ( data[i]["IP-Range"][j] , data[i]["Institution-uuid"] ) )
    query = """INSERT INTO ip_range (ip_range_value , institution_uuid)
                VALUES (%s , %s);"""
    cursor.executemany(query,processed_data)
    conn.commit()

conn = psycopg2.connect(database='obp_institutions',
                        user = 'obp',
                        password = 'some_secret_password',
                        host = '192.168.99.100',
                        port = '5432')
cursor = conn.cursor()

with open("data.json") as f:
    print "Loading JSON file."
    data = json.load(f)
    data = append_uuid(data)
    insert_into_institution(data)
    insert_into_contact(data)
    insert_into_ip_range(data)
    cursor.close()
    conn.close()
    






