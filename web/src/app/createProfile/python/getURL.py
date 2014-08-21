#!/usr/bin/env python
import ConfigParser
import sqlite3
import os
import cgi

def geturl(config):
    '''Function to get the url from the database
    '''
    print 'Content-Type: text/html'
    print ''

    conn = sqlite3.connect(config.get("DATABASE", "profile_name"))
    cur = conn.cursor()
    
    form = cgi.FieldStorage()
    print form
    cur.execute('''select dpm_page.url from dpm_page where
            dpm_page.name = 'dpm' ''')
    res = cur.fetchall()
    if (len(res) > 0):
        turl = res[0][0]

if __name__ == '__main__':
    cfgfile = './config/policy_schema.cfg'
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    geturl(config)
