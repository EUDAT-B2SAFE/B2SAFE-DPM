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
    print "Script to get the policy from the database"
    print "Usage: getPolicy.py"
    print "Options:"
    print "help=help                 Prints this help"
    print ""

class VisitPolicy(kyotocabinet.Visitor):
    '''Visitor class to get the index for the key
    '''
    def __init__(self, uuid, uuid_key):
        self.uuid = uuid
        self.uuid_key = uuid_key
        self.index = 0
        super(VisitPolicy, self).__init__()

    def visit_full(self, key, value):
        if (self.uuid == value and self.uuid_key in key):
            self.index = key.split("_")[-1]
        return self.NOP

    def visit_empty(self, key):
        return self.NOP

def getData(config, uuid):
    '''Function to get the policy from the database
    '''
    
    # get the uuid key and the policy key
    uuid_key = config.get("POLICY_SCHEMA", "uniqueid")
    policy_key = config.get("POLICY_SCHEMA", "object")

    # Open the database
    db = kyotocabinet.DB()
    dbfile = config.get("DATABASE", "name").strip()
    if (not db.open(dbfile, 
        kyotocabinet.DB.OWRITER | kyotocabinet.DB.OCREATE)):
        sys.stderr.write("open error: " + str(db.error()))
    
    # Get the uuid key corresponding to the uuid and construct
    # the policy key
    visit_obj = VisitPolicy(uuid, uuid_key)
    db.iterate(visit_obj, False)
    
    policy_key = "%s_%s" % (policy_key, visit_obj.index)
    policy = db.get(policy_key)
    # policy = policy.replace("\n", "<br/>")
    print "Content-Type: application/json charset=utf-8"
    print ""
    print json.dumps(policy)

if __name__ == '__main__':
    cfgfile = "./config/policy_schema.cfg"
    
    fields = cgi.FieldStorage()

    if (fields.has_key("help")):
        usage()
        sys.exit()

    # Get the uuid
    uuid = fields["uuid"].value

    # Read the configs
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)

    getData(config, uuid)

