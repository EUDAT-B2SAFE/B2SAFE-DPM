#!/usr/bin/env python
import cgi
import sqlite3
import json
import ConfigParser

def getCommunity(config):
    '''Function to get the list of communities
    '''
    communities = []
    data = {}
    roles = []
    dbfile = config.get("DATABASE", "profile_name")
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    cur.execute('''select name from community''')
    results = cur.fetchall()
    for res in results:
        communities.append(res[0])
    
    cur.execute('''select name from roles''')
    results = cur.fetchall()
    for res in results:
        roles.append(res[0])

    data["communities"] = communities
    data["roles"] = roles

    print json.dumps(data)

if __name__ == '__main__':
    print 'Content-Type: application/json; charset=utf-8'
    print ''
    cfgfile = './config/policy_schema.cfg'
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    getCommunity(config)
