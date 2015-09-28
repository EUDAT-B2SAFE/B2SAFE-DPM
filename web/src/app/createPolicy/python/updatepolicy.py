#!/usr/bin/env python

import getopt
import sys
import cgi
import ConfigParser
import sqlite3
import hashlib
import re

def usage():
    '''Function describing the script usage
    '''
    print "Script to upload log messages to the database"
    print "Usage: updatepolicy.py?id=<id>&state=<state>&center=<center>&timestamp=<timestamp>&community=<community>"
    print "Options:"
    print "help=help               Prints this help"
    print "state=state             The log message. Allowed states are: QUEUED, RUNNING, FINISHED, FAILED" 
    print "community=<community>   The community identifier"
    print "timestamp=<timestamp>   The timestamp for the message"
    print "center=<center>         The data center origin of the log message"
    print "id=<id>                 The uuid for the policy"
    print ""

class FilterPolicy(kyotocabinet.Visitor):
    '''Class implementing the visitor pattern to filter the database
    '''
    def __init__(self, config, uid, md5sum):
        self.uid = uid
        self.md5 = md5sum
        self.uid_index = -1
        self.duplicate = False
        self.md5_key = config.get("LOG_SCHEMA", "log_hash")
        self.uid_key = config.get("POLICY_SCHEMA", "uniqueid")
        super(FilterPolicy, self).__init__()

    def visit_full(self, key, val):
        '''Method to filter the results according to the uid
        '''
        if (val == self.uid and self.uid_key in key):
            # we want to just have the index number not the whole key
            self.uid_index = key.split("_")[-1]
        # Check to see if the hash exists if so set the index
        if (val == self.md5 and self.md5_key in key):
            self.duplicate = True
        return self.NOP

    def visit_empty(self, key):
        '''Method to return nothing of the key doesn't exist
        '''
        return self.NOP

def loadData(config):
    '''Function to load the log info into the database
    '''
    store_vals = {}
    next_entry = 0

    allowed_states = [x.strip() for x in config.get("LOG_KEYS", "allowed_states").split(",")]
    valid_keys = set([config.get("LOG_KEYS", "id"),
        config.get("LOG_KEYS", "state"), 
        config.get("LOG_KEYS", "timestamp"),
        config.get("LOG_KEYS", "center"), 
        config.get("LOG_KEYS", "community")])

    print "Content-Type: application-json; charset=utf-8"
    print ""

    formData = cgi.FieldStorage()

    # check the keys are valid
    keys = formData.keys()

    if (formData.has_key(config.get("LOG_KEYS", "help"))):
        usage()
        sys.exit(0)

    if (len(keys) == 0 or (set(keys) != valid_keys)):
        print "Error: no recognised parameters supplied"
        print "run with the help option ('?help=help') to see the help"
        sys.exit(1)

    # Check that the log message is acceptable
    if (formData.getvalue(config.get("LOG_KEYS", "state")) not in
            allowed_states):
        print "Error: unrecognised state. Allowed values are: RUNNING, FINISHED, FAILED"
        sys.exit(40)
    
    # Check the timestamp is a unix timestamp
    alph_str = re.compile("[a-zA-Z]+")
    if (alph_str.search(formData.getvalue(config.get("LOG_KEYS",
        "timestamp")))):
        print "Error: the timestamp should be the number of seconds since the unix epoch"
        sys.exit(50)

    # Compute the hash for the message
    hash_string = "%s%s%s%s%s" % \
            (formData.getvalue(config.get("LOG_KEYS", "id"), ""),
                    formData.getvalue(config.get("LOG_KEYS", "state"), ""),
                    formData.getvalue(config.get("LOG_KEYS", "timestamp"),
                        ""),
                    formData.getvalue(config.get("LOG_KEYS", "center"), ""),
                    formData.getvalue(config.get("LOG_KEYS", "community"),
                        ""))
    md5 = hashlib.md5()
    md5.update(hash_string)
    md5sum = md5.hexdigest()

    # Open the database
    dbfile = config.get("DATABASE", "name").strip()
    if (not os.path.isfile(dbfile)):
        sys.stderr.write("Database %s does not exist" % dbfile)
        sys.exit(-100)
    conn = sqlite3.connect(dbfile)
    
    # Get the key corresponding to the id and make sure that the
    # message doesn't already exist in the store
    filter_obj = FilterPolicy(config, 
            formData.getvalue(config.get("LOG_KEYS", "id"), ""), md5sum)
    db.iterate(filter_obj, False)
    
    # How many log entries are there for this id (we need to add one
    # for the new log entry)
    if (filter_obj.uid_index >= 0 and not filter_obj.duplicate):
        log_key = "%s_%s" % (config.get("LOG_SCHEMA", "log_entries"), 
                filter_obj.uid_index)
        # Check if the log entry exists
        if db.check(log_key) > 0:
            next_entry = int(db.get(log_key)) + 1
    elif (filter_obj.duplicate):
        print "Message already exists in database"
        sys.exit(0)
    else:
        print "Error: cannot find database entry for UID: %s" %\
                formData.getvalue(config.get("LOG_KEYS", "id"), "")
        sys.exit(40)

    store_vals[log_key] = next_entry
    
    log_hash_key = "%s_%s_%d" % (config.get("LOG_SCHEMA", "log_hash"),
            filter_obj.uid_index, next_entry)
    store_vals[log_hash_key] = md5sum

    # increase the index and append the indices to the keys
    log_state_key = "%s_%s_%d" % (config.get("LOG_SCHEMA", 
        "log_state"), filter_obj.uid_index, next_entry)
    store_vals[log_state_key] = \
            formData.getvalue(config.get("LOG_KEYS", "state"), "")

    log_timestamp_key = "%s_%s_%d" % (config.get("LOG_SCHEMA", 
        "log_timestamp"), filter_obj.uid_index, next_entry)
    store_vals[log_timestamp_key] = \
            formData.getvalue(config.get("LOG_KEYS", 
        "timestamp"), "")

    log_center_key = "%s_%s_%d" % (config.get("LOG_SCHEMA", 
        "log_center"), filter_obj.uid_index, next_entry)
    store_vals[log_center_key] = \
            formData.getvalue(config.get("LOG_KEYS",
        "center"), "")

    # Store the key-value pairs in the database
    for key, val in store_vals.items():
        if not db.set(key, val):
            print "Error: unable to store %s %s\n" % (key, val)
            print str(db.error())
            sys.exit(20)

    if not db.close():
        print "Error: unable to close the database ", str(db.error())
        sys.exit(30)

if __name__ == '__main__':
    # The config file
    cfgfile = './config/policy.cfg'
    
    # Read the configs
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)

    loadData(config)
