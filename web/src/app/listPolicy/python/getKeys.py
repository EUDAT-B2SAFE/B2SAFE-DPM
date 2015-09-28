#!/usr/bin/env python

import getopt
import sys
import json
import cgi
import ConfigParser

def usage():
    '''Function describing the script usage
    '''
    print "Script to get the database key for the policy schema"
    print "Usage: getKeys.py"
    print "Options:"
    print "help=help                Prints this help"
    print ""

def getKeys(config):
    '''Function to extract the policy schema keys
    '''
    
    # Get the list of keys that are visible by default
    visible_keys = [x.strip() for x in config.get("DATABASE", "default_visible").split(',')]

    # Keys to skip
    skip_keys = [x.strip() for x in config.get("DATABASE", "skip_keys").split(',')]
    sections = ["POLICY_SCHEMA", "DATASETS_SCHEMA", "ACTIONS_SCHEMA",
            "TARGETS_SCHEMA"]
    keys = []
    for section in sections:
        for option in config.options(section):
            val = config.get(section, option)
            if (val in skip_keys):
                continue
            if (val in visible_keys):
                keys.append((val, "true"))
            else:
                keys.append((val, "false"))
    return keys

def returnResults(keys):
    '''Function to return the results'''
    print "Content-Type: application/json charset=utf-8"
    print ""
    print json.dumps(keys)

if __name__ == '__main__':
    cfgfile = './config/policy.cfg'

    fields = cgi.FieldStorage()
    if (fields.has_key("help")):
        usage()
        sys.exit()

    # Read the configs
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    keys = getKeys(config)
    returnResults(keys)
