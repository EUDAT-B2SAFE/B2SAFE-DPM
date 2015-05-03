#!/usr/bin/env python
import json
import sys
import ConfigParser
import StringIO
import hashlib
import time
import os

import kyotocabinet

class VisitUUID(kyotocabinet.Visitor):
    def __init__(self, config, uuid):
        self.uuid_idx = ''
        self.uuid = uuid
        self.config = config

    def visit_full(self, key, value):
        if (self.uuid.strip() == value.strip()):
            self.uuid_idx = key.split(self.config.get("POLICY_SCHEMA",
                "uniqueid"))[-1]
        return self.NOP
    
    def visit_empty(self, key):
        return self.NOP

def reactivatePol(config):
    '''Function to reactivate the policy
    '''
    
    # Read the input
    data = {}
    data = json.load(sys.stdin)
    # Open the database
    dbfile = config.get("DATABASE", "name").strip()
    db = kyotocabinet.DB()
    if (not db.open(dbfile, 
        kyotocabinet.DB.OWRITER | kyotocabinet.DB.OCREATE)):
        sys.stderr.write("open error: " + str(db.error()))
    
    # Find the key for the uuid
    uuid_keys = db.match_prefix(config.get("POLICY_SCHEMA", "uniqueid"))
    visit_uuid = VisitUUID(config, data['uuid'])
    db.accept_bulk(uuid_keys, visit_uuid, False)

    # Construct the remove key
    pol_rm = "%s%s" % (config.get("POLICY_SCHEMA", "removed"),
            visit_uuid.uuid_idx)

    # Set the removed key to false - this means the policy is reactivated
    db.set(pol_rm, 'false')

    # Close the database
    db.close()

if __name__ == '__main__':
    cfgfile = 'config/policy_schema.cfg'
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    print "Content-Type: html/text"
    print ""
    reactivatePol(config)
