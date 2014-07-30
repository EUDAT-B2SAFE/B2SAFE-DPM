#!/usr/bin/env python

import getopt
import sys
import cgi
import kyotocabinet
import re
import ConfigParser

def usage():
    '''Function describing the script usage
    '''
    print "Script to query database for log information"
    print "Usage: querylogs.py?id=<id>"
    print "Options:"
    print "help=help         Prints this help."
    print "id=<id>           The UUID for the policy. Specify 'all' to"
    print "                  get log information for all policies"
    print ""

class FilterPolicyForID(kyotocabinet.Visitor):
    '''Class implementing the visitor patterm to filter the database
    for ids
    '''
    def __init__(self, state_key, uid):
        self.state_key = state_key
        self.uid = uid
        self.uuid_indexes = []
        super(FilterPolicyForID, self).__init__()

    def visit_full(self, key, val):
        '''Method to filter the results according to uid
        '''
        # For the log entries we need the state, community, timestamp,
        # centre
        if (self.uid == 'all'):
            if (self.state_key in key):
                self.uuid_indexes.append((key.split("_")[-1], val))
        else:
            if (self.state_key in key and self.uid == val):
                self.uuid_indexes.append((key.split("_")[-1], val))
        return self.NOP
    
    def visit_empty(self, key):
        '''Method to return nothing if the key doesn't exist
        '''
        return self.NOP

def runQuery(config):
    '''Function to execute the query
    '''
    print "Content-Type: application-json; charset=utf-8"
    print ""

    formData = cgi.FieldStorage()
    if (formData.has_key("help")):
        usage()
        sys.exit(0)

    if (not formData.has_key("id")):
        print "Error: unrecognised parameters"
        print "Run with the help option ('?help=help') to see the help"
        sys.exit(5)

    # Open the database
    db = kyotocabinet.DB()
    if (not db.open(config.get("DATABASE", "name").strip(),
        kyotocabinet.DB.OREADER)):
        print "Unable to open the database " + str(db.error())
        sys.exit(10)
    
    idval = formData.getvalue("id", "")

    # Get the index from the key with the matching UUID
    filter_obj_id = FilterPolicyForID(config.get("POLICY_SCHEMA", 
        "uniqueid"), idval)
    db.iterate(filter_obj_id, False)
    
    # Loop over the uuid indexes
    for idx, idv in filter_obj_id.uuid_indexes:
        # Get the state keys for this index
        state_keys = db.match_prefix("%s_%s_" % \
                (config.get("POLICY_SCHEMA", "log_state"), idx))

        comm_str = config.get("POLICY_SCHEMA", "community")
        timestamp_str = config.get("POLICY_SCHEMA", "log_timestamp")
        center_str = config.get("POLICY_SCHEMA", "log_center")

        community_keys = ["%s_%s" % (comm_str, x.split('_')[-2]) \
                for x in state_keys]
        timestamp_keys = ["%s_%s_%s" % (timestamp_str, x.split('_')[-2], \
                x.split('_')[-1]) for x in state_keys]
        center_keys = ["%s_%s_%s" % (center_str, x.split('_')[-2], \
                x.split('_')[-1]) for x in state_keys]

        states = db.get_bulk(state_keys)
        communities = db.get_bulk(community_keys)
        centers = db.get_bulk(center_keys)
        timestamps = db.get_bulk(timestamp_keys)

        # Print out the log results
        if (len(state_keys) > 0):
            print "-"*80
            print "Identifier: %s" % idv
            print "Log Entries:"
            print "{}{}{}{}".format("Community".rjust(20), 
                    "Center".rjust(20), "State".rjust(10), 
                    "Timestamp".rjust(15))
            for i in range(0, len(state_keys)):
                print "{}{}{}{}".format(
                    communities[community_keys[i]].rjust(20),
                    centers[center_keys[i]].rjust(20),
                    states[state_keys[i]].rjust(10),
                    timestamps[timestamp_keys[i]].rjust(15))
        else:
            print "-"*80
            print "Identifier: %s" % idv
            print "No Log Entries"

if __name__ == '__main__':
    cfgfile = './config/policy_schema.cfg'

    # Read the configurations
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)

    runQuery(config)
