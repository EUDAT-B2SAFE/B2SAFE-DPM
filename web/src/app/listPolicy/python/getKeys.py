#!/usr/bin/env python

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

def get_keys(config):
    '''Function to extract the policy schema keys
    '''

    # Get the list of keys that are visible by default
    visible_keys = [x.strip() for x in config.get("DATABASE", "default_visible").split(',')]

    # Keys to skip
    skip_keys = [x.strip() for x in config.get("DATABASE", "skip_keys").split(',')]
    sections = ["POLICY_SCHEMA", "ACTIONS_SCHEMA", "SOURCES_SCHEMA",
                "TARGETS_SCHEMA"]
    keys = []
    for section in sections:
        for option in config.options(section):
            val = config.get(section, option)
            if val in skip_keys:
                continue
            if val in visible_keys:
                keys.append((val, "true"))
            else:
                keys.append((val, "false"))
    return keys

def return_results(keys):
    '''Function to return the results'''
    print "Content-Type: application/json charset=utf-8"
    print ""
    print json.dumps(keys)

if __name__ == '__main__':
    CFG_FILE = './config/policy.cfg'

    FIELDS = cgi.FieldStorage()
    if "help" in FIELDS:
        usage()
        sys.exit()

    # Read the configs
    POLICY_CONFIG = ConfigParser.ConfigParser()
    POLICY_CONFIG.read(CFG_FILE)
    POLICY_KEYS = get_keys(POLICY_CONFIG)
    return_results(POLICY_KEYS)
