#!/usr/bin/env python

import sys
import cgi
import json
import ConfigParser
import kyotocabinet

def usage():
    '''Function describing the script usage
    '''
    print "Script to return the policy log information"
    print "Usage:"
    print " ?help=help      Prints this help"
    print ""

def getLogs(config, username):
    '''Function to get the log information for all policies
    '''
    print "Content-Type: application-json; charset=utf-8"
    print ""

    # Open the database
    db = kyotocabinet.DB()
    if (not db.open(config.get("DATABASE", "name").strip(),
        kyotocabinet.DB.OREADER)):
        print "Unable to open the database " + str(db.error())
        sys.exit(10)
    
    # Get the keys for the uuid
    uuid_keys = db.match_prefix(config.get("POLICY_SCHEMA", "uniqueid"))
    policy_logs = {}
    policy_log_data = []
    for auuid in uuid_keys:
        uuid_num = auuid.split(config.get("POLICY_SCHEMA", "uniqueid"))[1]
        
        # We need to skip the log entries if they don't correspond to the
        # logged in users community
        community_key = "policy_community_%s" % (uuid_num)
        if (db.get(community_key) != username):
            continue

        log_entries = db.get("%s%s" % \
                (config.get("LOG_SCHEMA", "log_entries"), uuid_num))
        uuid_val = db.get(auuid)
        if (type(log_entries) != type(None)):
            for log_num in range(0, int(log_entries)+1):
                log_state = db.get("%s%s_%s" % \
                        (config.get("LOG_SCHEMA", "log_state"), 
                        uuid_num, log_num))
                log_timestamp = db.get("%s%s_%s" % \
                        (config.get("LOG_SCHEMA", "log_timestamp"), 
                        uuid_num, log_num))
                log_center = db.get("%s%s_%s" % \
                        (config.get("LOG_SCHEMA", "log_center"), 
                        uuid_num, log_num))
                policy_log_data.append((uuid_val, log_state, log_center, 
                        log_timestamp))
    policy_logs["columns"] = [config.get("POLICY_SCHEMA", "uniqueid"),
            config.get("LOG_SCHEMA", "log_state"),
            config.get("LOG_SCHEMA", "log_center"),
            config.get("LOG_SCHEMA", "log_timestamp")]
    policy_logs["data"] = policy_log_data
    print json.dumps(policy_logs)

if __name__ == '__main__':
    cfgfile = './config/policy_schema.cfg'
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    
    fields = cgi.FieldStorage()
    if (fields.has_key("help")):
        usage()
        sys.exit()
    
    username = fields.getvalue("username", "")

    getLogs(config, username)

