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

    






