#!/usr/bin/env python
import cgi
import os
import ConfigParser
import sqlite3

def check_register(config, username):
    '''Function to check if the user is registered
    '''
    comAdmin = False
    dpmAdmin = False

    turl = config.get("HTML","not_registered")
    dbfile = config.get("DATABASE", "profile_name")
    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()
    
    # Check if user is a dpm admin or a community admin
    cur.execute('''select dpm_page.url from dpm_page, roles, status, 
        user_community, user where roles.name = 'dpm admin' and 
        roles.role_id = user_community.role_id and user.name = ? and
        dpm_page.dpm_id = user_community.dpm_id and 
        user.user_id = user_community.user_id and 
        status.status = 'approved' and 
        status.status_id = user_community.status_id''',
        (username,))
    res = cur.fetchall()
    if (len(res) > 0):
        turl = res[0][0]
        dpmAdmin = True
    else:
        cur.execute('''select dpm_page.url from dpm_page, roles, status, 
            user_community, user where roles.name = 'community admin' and 
            roles.role_id = user_community.role_id and user.name = ? and
            dpm_page.dpm_id = user_community.dpm_id and
            status.status = 'approved' and 
            status.status_id = user_community.status_id and
            user.user_id = user_community.user_id''',
            (username,))
        res = cur.fetchall()
        if (len(res) > 0):
            turl = res[0][0]
            comAdmin = True
    
    if (not comAdmin and not dpmAdmin):
        cur.execute('''select dpm_page.url from dpm_page, user_community, 
                user, status where user.name = ? and 
                user.user_id = user_community.user_id and
                user_community.dpm_id = dpm_page.dpm_id and 
                status.status = 'approved' and 
                user_community.status_id = status.status_id''',
                (username,))
        qurl = cur.fetchall()
        # We only need to take the first URL since for approved accounts
        # the approved pages should be the same
        if (len(qurl) >= 1):
            turl = qurl[0][0]
    
    print turl

if __name__ == '__main__':
    print "Content-Type: text/html"
    print ""

    username = ''
    cfgfile = "./config/policy_schema.cfg"
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    
    if (config.has_option("HTMLENV", "user")):
        username = config.get("HTMLENV", "user")
    else:
        username = os.environ["REMOTE_USER"]

    check_register(config, username)
