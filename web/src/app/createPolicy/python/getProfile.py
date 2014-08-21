#!/usr/bin/env python

import sys
import cgi
import json
import os
import sqlite3
import ConfigParser

def usage():
    '''Function describing the script usage
    '''
    print "Script to return the user information"
    print "Usage: getProfile.py"
    print "Options:"
    print "?help=help              Prints this help"
    print ""

def openDatabase(dbfile):
    '''Open the database file
    '''
    conn = sqlite3.connect(dbfile)
    return conn

def queryProfile(conn, username):
    '''Function to return the user profile if it exists
    '''
    dpmAdmin = False
    user_profile = {}
    u_comm = []
    u_comm_d = {}
    u_user = {}
    communities = []

    cur = conn.cursor()
    cur.execute('''select email from user where name = ?''',
            (username,))
    u_email = cur.fetchone()[0]
    # Check if the user is a dpm admin
    cur.execute('''select roles.role_id from user_community, user, roles,
        status  where user.name = ? and 
        user.user_id = user_community.user_id and
        roles.name = 'dpm admin' and status.status = 'approved' and
        status.status_id = user_community.status_id and 
        roles.role_id = user_community.role_id''',
        (username,))
    roles = cur.fetchall()
    if (len(roles) > 0):
        dpmAdmin = True

    # If the dpm admin we fetch all the communities
    if (dpmAdmin):
        cur.execute('''select community.name from community 
                where community.name <> 'all' ''')
        communities = cur.fetchall()
    else:
        cur.execute('''select community.name from community, user, status, 
            user_community where user.name = ? and 
            user.user_id = user_community.user_id and
            user_community.status_id = status.status_id and
            status.status = 'approved' and
            user_community.community_id = community.community_id''',
            (username,))
        communities = cur.fetchall()
    conn.commit()
    u_comm = []
    u_comm_d = {}
    for acommunity in communities:
        u_comm.append(acommunity[0])
    u_comm_d["communities"] = u_comm

    u_user["username"] = username
    u_user["email"] = u_email
    user_profile["profile"] = [u_user]
    user_profile["profile"].append(u_comm_d)
    return user_profile

def getProfile(config):
    '''Function to return the username
    '''
    print "Content-Type: application/json charset=utf-8"
    print ""
    
    if (config.has_option("HTMLENV", "user")):
        username = config.get("HTMLENV", "user")
    else:
        username = os.environ["REMOTE_USER"]

    dbfile = config.get("DATABASE", "profile_name")

    conn = openDatabase(dbfile)
    if (conn):
        user_profile = queryProfile(conn, username)

    print json.dumps(user_profile)

if __name__ == '__main__':
    cfgfile = "./config/policy_schema.cfg"

    fields = cgi.FieldStorage();
    if (fields.has_key("help")):
        usage()
        sys.exit()
    
    # Read the config file
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    getProfile(config)

