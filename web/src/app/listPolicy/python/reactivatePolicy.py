#!/usr/bin/env python
import json
import sys
import ConfigParser
import StringIO
import hashlib
import time
import os
import sqlite3

def reactivatePol(config):
    '''Function to reactivate the policy
    '''
    
    # Read the input
    data = {}
    data = json.load(sys.stdin)
    # Open the database
    dbfile = config.get("DATABASE", "name").strip()
    if (not os.path.isfile(dbfile)):
        sys.stderr.write("Unable to open the database: %s" % dbfile)
        sys.exit(-100)
    
    # Find the key for the uuid
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    uuid_key = "%s%%" % config.get("POLICY_SCHEMA", "uniqueid")
    cur.execute("select key from policies where key like ? and value=?",
            (uuid_key, data['uuid']))
    result = cur.fetchone()
    uuid_idx = -1
    if (len(result) > 0):
        uuid_idx = result[0].split("_")[-1]

    # Construct the remove key
    pol_rm = "%s_%s" % (config.get("POLICY_SCHEMA", "removed"), uuid_idx)

    # Set the removed key to false - this means the policy is reactivated
    cur.execute("update policies set value=? where key=?",
            ('false', pol_rm))
    conn.commit()

if __name__ == '__main__':
    cfgfile = 'config/policy.cfg'
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    print "Content-Type: html/text"
    print ""
    reactivatePol(config)
