#!/usr/bin/env python

import getopt
import sys
import cgi
import json
import ConfigParser
import kyotocabinet

def usage():
    '''Function describing the script usage
    '''
    print "Script to get the database info for the policies"
    print "Usage: getPolicyData.py"
    print "Options:"
    print "help=help                 Prints this help"
    print ""

def getData(config):
    '''Function to return the policies from the database
    '''

    # Read the configs and get database keys
    visible_keys = [x.strip() for x in config.get("DATABASE", "default_visible").split(',')]

    # Keys to skip
    skip_keys = [x.strip() for x in config.get("DATABASE", "skip_keys").split(',')]
    sections = ["POLICY_SCHEMA", "DATASETS_SCHEMA", "ACTIONS_SCHEMA",
            "TARGETS_SCHEMA"]
    columns = []
    for section in sections:
        for option in config.options(section):
            val = config.get(section, option)
            if (val in skip_keys):
                continue
            if (val in visible_keys):
                columns.append((val, "true"))
            else:
                columns.append((val, "false"))

    # Open the database
    db = kyotocabinet.DB()
    dbfile = config.get("DATABASE", "name").strip()
    if (not db.open(dbfile, 
        kyotocabinet.DB.OWRITER | kyotocabinet.DB.OCREATE)):
        sys.stderr.write("open error: " + str(db.error()))

    data = []
    last_index = int(db.get(config.get("DATABASE", "last_index")))
    for idx in range(0, last_index+1):
        col_names = []
        dvals = []
        for acol in columns:
            col_names.append("%s_%s" % (acol[0], idx))
        vals = db.get_bulk(col_names)
        for aid in range(0, len(vals)):
            if (vals.has_key(col_names[aid])):
                dvals.append((vals[col_names[aid]], columns[aid][1]))
            else:
                dvals.append(("", columns[aid][1]))
        data.append(dvals)

    print "Content-Type: application/json charset=utf-8"
    print ""
    print json.dumps(data)

if __name__ == '__main__':
    cfgfile = "./config/policy_schema.cfg"
    
    fields = cgi.FieldStorage()

    if (fields.has_key("help")):
        usage()
        sys.exit()

    # Read the configs
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)

    getData(config)

