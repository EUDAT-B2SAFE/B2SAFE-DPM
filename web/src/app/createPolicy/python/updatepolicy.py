#!/usr/bin/env python

import sys
import cgi
import ConfigParser
import sqlite3
import hashlib
import re
import os


def usage():
    '''Function describing the script usage
    '''
    print "Script to upload log messages to the database"
    print "Usage: updatepolicy.py?id=<id>&state=<state>&center=<center>&" \
        + "timestamp=<timestamp>&community=<community>"
    print "Options:"
    print "help=help               Prints this help"
    print "state=state             The log message. Allowed states are: " \
        " QUEUED, RUNNING, FINISHED, FAILED"
    print "community=<community>   The community identifier"
    print "timestamp=<timestamp>   The timestamp for the message"
    print "center=<center>         The data center origin of the log message"
    print "id=<id>                 The uuid for the policy"
    print ""


def policy_exists(policy_id, conn):
    '''Check if the policy exists'''
    policy_found = False
    cur = conn.cursor()
    cur.execute('''select value from policies where
        key like 'policy_uniqueid_%' and value = ?''', (policy_id,))
    results = cur.fetchall()
    if (len(results) == 1):
        policy_found = True
    return policy_found


def get_log(policy_id, conn):
    '''Get the index for the log for this policy'''
    index = -1
    cur = conn.cursor()
    cur.execute('''select key from policies where key like
        'log_policy_uuid_%' and value = ?''', (policy_id,))
    keys = cur.fetchall()
    if (len(keys) > 0):
        indices = []
        for akey in keys:
            indices.append(int(akey[0].split("_")[-1]))
        indices.sort()
        index = indices[-1]

    return index


def log_exists(conn, md5key, md5val):
    '''Check if the log message already exists
    '''
    exists = True
    key = "%s_%%" % (md5key)
    cur = conn.cursor()
    cur.execute('''select key from policies where key like ? and value = ?''',
                (key, md5val))
    keys = cur.fetchall()
    if (len(keys) == 0):
        exists = False
    return exists


def loadData(config):
    '''Function to load the log info into the database
    '''

    allowed_states = [x.strip() for x in
                      config.get("LOG_KEYS", "allowed_states").split(",")]
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

    if (config.get("LOG_KEYS", "help") in formData):
        usage()
        sys.exit(0)

    if (len(keys) == 0 or (set(keys) != valid_keys)):
        print "Error: no recognised parameters supplied"
        print "run with the help option ('?help=help') to see the help"
        sys.exit(1)

    # Check that the log message is acceptable
    if (formData.getvalue(config.get("LOG_KEYS", "state")) not in
            allowed_states):
        print "Error: unrecognised state. Allowed values are: RUNNING, " \
            + "FINISHED, FAILED"
        sys.exit(40)

    # Check the timestamp is a unix timestamp
    alph_str = re.compile("[a-zA-Z]+")
    if (alph_str.search(formData.getvalue(config.get("LOG_KEYS",
                                          "timestamp")))):
        print "Error: the timestamp should be the number of seconds " \
            + "since the unix epoch"
        sys.exit(50)

    log = {"id": formData.getvalue(config.get("LOG_KEYS", "id"), ""),
           "state": formData.getvalue(config.get("LOG_KEYS", "state"), ""),
           "timestamp":
           formData.getvalue(config.get("LOG_KEYS", "timestamp"), ""),
           "center": formData.getvalue(config.get("LOG_KEYS", "center"), ""),
           "community":
           formData.getvalue(config.get("LOG_KEYS", "community"), "")}

    # Compute the hash for the message
    hash_string = "%s%s%s%s%s" % \
        (log["id"], log["state"], log["timestamp"], log["center"],
         log["community"])
    md5 = hashlib.md5()
    md5.update(hash_string)
    log["hash"] = md5.hexdigest()

    # Open the database
    dbfile = config.get("DATABASE", "name").strip()
    if (not os.path.isfile(dbfile)):
        sys.stderr.write("Database %s does not exist" % dbfile)
        sys.exit(-100)
    conn = sqlite3.connect(dbfile)

    # Check that a policy exists with this uuid
    if (not policy_exists(log["id"], conn)):
        print "Error: policy with id %s does not exist" % \
            formData.getvalue(config.get("LOG_KEYS", "id"), "")
        sys.exit(2)

    # Check if the policy has existing log entries
    log_id = get_log(log["id"], conn)

    if (log_id >= 0):
        if (log_exists(conn, config.get("LOG_SCHEMA", "hash"), log["hash"])):
            print "Error: log message already recorded"
            sys.exit(3)

    cur = conn.cursor()
    log_id = log_id + 1
    for key in log.keys():
        tkey = "%s_%s" % (config.get("LOG_SCHEMA", key), log_id)
        cur.execute('''insert into policies (key, value) values (?, ?)''',
                    (tkey, log[key]))
    conn.commit()


if __name__ == '__main__':
    # The config file
    cfgfile = './config/policy.cfg'

    # Read the configs
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)

    loadData(config)
