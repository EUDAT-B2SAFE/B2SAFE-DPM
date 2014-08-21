#!/usr/bin/env python
import ConfigParser
import sqlite3
import os
import sys
import json

def geturl(config):
    '''Function to get the url from the database
    '''
    print 'Content-Type: application/json charset=utf-8'
    print ''
    
    turl = ''
    conn = sqlite3.connect(config.get("DATABASE", "profile_name"))
    cur = conn.cursor()
    
    data = json.load(sys.stdin)

    cur.execute('''select dpm_page.url from dpm_page where
                dpm_page.name = ?''',
                (data["name"],))
    
    res = cur.fetchall()
    if (len(res) > 0):
        turl = res[0][0]
    
    print turl

if __name__ == '__main__':
    cfgfile = './config/policy_schema.cfg'
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    geturl(config)
