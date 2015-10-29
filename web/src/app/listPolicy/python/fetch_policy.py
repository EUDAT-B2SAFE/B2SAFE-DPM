#!/usr/bin/env python
import cgi
import os
import sys
import ConfigParser
import sqlite3


def usage():
    '''Function describing the script usage
    '''
    print "Script to fetch the policy for a given id"
    print "Usage: fetch_policy.py?policy_id=<id>"
    print "Options"
    print "policy_id=<id>          The identifier for the policy object"
    print ""


def fetchPolicy():
    '''Function to fetch the policy from the database
    '''
    policy_object_key = "policy_id"
    help_key = "help"

    # Read the configurations
    config = ConfigParser.ConfigParser()
    config.read("config/policy.cfg")

    print "Content-Type: application/json charset=utf-8"
    print ""

    # Get the arguments
    formData = cgi.FieldStorage()

    keys = formData.keys()

    if (help_key in formData):
        usage()
        sys.exit(0)

    # Check we have the correct key
    if (policy_object_key not in keys):
        print "Error: no recognised parameter supplied"
        print "Recognised parameter is: policy_id"
        print "Run with the help option (add '?help=help') to see the help"
        sys.exit(1)

    policy_object_id = formData.getvalue(policy_object_key, "")

    # Open the database
    dbfile = config.get("DATABASE", "name").strip()
    if (not os.path.isfile(dbfile)):
        sys.stderr.write("Unable to open the database %s" % dbfile)
        sys.exit(-100)

    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    # Extract the policy from the database and return as a string
    cur.execute("select value from policies where key = ?",
                (policy_object_id,))
    policy = cur.fetchone()
    if (policy):
        sys.stdout.write(policy[0])
    else:
        print "Error: cannot find a policy with id: ", policy_object_id
        sys.exit(20)

if __name__ == '__main__':
    fetchPolicy()
