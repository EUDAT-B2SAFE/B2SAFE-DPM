#!/usr/bin/env python
# CGI script to query the database containing acceptable actions
#
# Adil Hasan

import cgi
import sqlite3
import os
import json
import ConfigParser


def querydb(d_base):
    '''Function to query the database
    '''
    conn = None
    results = None

    # The database must exist otherwise we have a little problem
    if (os.path.exists(d_base)):
        conn = sqlite3.connect(d_base)
    else:
        return "error"

    fields = cgi.FieldStorage()

    # Get the type of parameter to query
    qtype = fields["qtype"].value

    # Query the database and get the results
    cur = conn.cursor()
    if qtype == "types":
        cur.execute('''select type.name from type''')
        results = cur.fetchall()
    elif qtype == "triggers":
        cur.execute('''select trigger.name from trigger''')
        results = cur.fetchall()
    elif qtype == 'trigger_date':
        cur.execute('select trigger_date.name, trigger_date.value from trigger_date')
        results = cur.fetchall()
    elif qtype == "identifiers":
        cur.execute('''select distinct name from persistentID''')
        results = cur.fetchall()
    elif qtype == "organisations":
        cur.execute('''select distinct name from organisation''')
        results = cur.fetchall()

    return results


def returnResults(results):
    '''Function to return the results'''
    print "Content-Type: application/json; charset=utf-8"
    print ""
    print json.dumps(results)

if __name__ == '__main__':
    # The database containing the resources
    config = ConfigParser.ConfigParser()
    config.read('./config/policy.cfg')
    dbase = config.get("DATABASE", "action_name").strip()
    data = querydb(dbase)
    returnResults(data)
