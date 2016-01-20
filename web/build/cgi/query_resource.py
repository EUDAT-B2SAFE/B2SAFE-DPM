#!/usr/bin/env python
# CGI script to query the database containing storage resources
#
# Adil Hasan

import cgi
import sqlite3
import os
import json
import ConfigParser


def querydb(dbase):
    '''Function to query the database
    '''
    conn = None
    results = None
    system = None
    site = None

    # The database must exist otherwise we have a little problem
    if (os.path.exists(dbase)):
        conn = sqlite3.connect(dbase)
    else:
        return "error"

    fields = cgi.FieldStorage()

    # Get the type of parameter to query
    qtype = fields["qtype"].value

    if ("system" in fields):
        system = fields["system"].value

    if ("site" in fields):
        site = fields["site"].value

    # Query the database and get the results
    cur = conn.cursor()
    if (qtype == "systems"):
        cur.execute("select system from systems")
        results = cur.fetchall()
    elif (qtype == "sites"):
        cur.execute('''select distinct site from sites, resources, systems
        where systems.system = ? and systems.id = resources.system_id and
        resources.site_id = sites.id''', (system,))
        results = cur.fetchall()
    elif (qtype == "resources"):
        cur.execute('''select storage.store, storage.path from storage,
        resources, systems, sites where systems.system = ? and
        systems.id = resources.system_id and
        sites.site = ? and sites.id = resources.site_id and
        resources.store_id = storage.id''', (system, site))
        results = cur.fetchall()
    elif (qtype == "sitePath"):
        cur.execute('''select sites.site, storage.path from resources, sites,
                    storage where storage.id = resources.id and
                    sites.id = resources.id and storage.id = resources.id''')
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
    dbase = config.get("DATABASE", "resource_name").strip()
    results = querydb(dbase)
    returnResults(results)
