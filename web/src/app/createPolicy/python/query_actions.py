#!/usr/bin/env python
# CGI script to query the database containing acceptable actions
#
# Adil Hasan

import cgi
import sqlite3
import os
import sys
import json
import ConfigParser

def querydb(dbase):
    '''Function to query the database
    '''
    conn = None
    results = None
    operation = None
    atype = None
    atrigger = None

    # The database must exist otherwise we have a little problem
    if (os.path.exists(dbase)):
        conn = sqlite3.connect(dbase)
    else:
        return "error"
    
    fields = cgi.FieldStorage()

    # Get the type of parameter to query
    qtype = fields["qtype"].value

    if (fields.has_key("operation")):
        operation = fields["operation"].value
    if (fields.has_key("type")):
        atype = fields["type"].value
    if (fields.has_key("trigger")):
        atrigger = fields["trigger"].value

    # Query the database and get the results
    cur = conn.cursor()
    if (qtype == "operations"):
        cur.execute("select name from operation")
        results = cur.fetchall()
    elif (qtype == "types"):
        cur.execute('''select distinct type.name from type, action,
        operation 
        where operation.name = ? and operation.id = action.operation_id and
        action.type_id = type.id''', (operation,))
        results = cur.fetchall()
    elif (qtype == "triggers"):
        cur.execute('''select distinct trigger.name from trigger, operation,
        type, action where operation.name = ? and type.name = ? and
        operation.id = action.operation_id and type.id = action.type_id
        and trigger.id = action.trigger_id''',
                (operation, atype))
        results = cur.fetchall()
    elif (qtype == "identifiers"):
        cur.execute('''select distinct name from persistentID''')
        results = cur.fetchall()
    elif (qtype == "locations"):
        cur.execute('''select distinct locationtype.name from locationtype, action,
                type, trigger, operation where 
                locationtype.id = action.location_id and type.name = ? 
                and type.id = action.type_id and trigger.name = ? and
                trigger.id = action.trigger_id and operation.name = ?
                and operation.id = action.operation_id''',
                (atype, atrigger, operation))
        results = cur.fetchall()
    elif (qtype == "organisations"):
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
    results = querydb(dbase)
    returnResults(results)

