#!/usr/bin/env python
import cgi
import os
import ConfigParser
import sqlite3

def check_register(config, username):
    '''Function to check if the user is registered
    '''
    turl = config.get("HTML","not_registered")
    dbfile = config.get("DATABASE", "profile_name")
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    cur.execute('''select dpm_page.url from dpm_page, user_community, 
            user where user.name = ? and user_community.dpm_id =
            dpm_page.dpm_id''',
            (username,))
    qurl = cur.fetchall()
    if (len(qurl) == 1):
        turl = qurl[0][0]
    
    print turl

if __name__ == '__main__':
    print "Content-Type: text/html"
    print ""
    username = 'adil'

    cfgfile = "./config/policy_schema.cfg"
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    check_register(config, username)
