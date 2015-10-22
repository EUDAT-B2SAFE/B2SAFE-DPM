#!/usr/bin/env python

import sys
import cgi
import json
import os
import csv
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


def getAdmins(config):
    '''Function to load the DPM admin username
    '''
    dpm_admins = []
    fh = file(config.get("DPM_ADMIN", "admin_file"), "r")
    csv_obj = csv.reader(fh)
    for dpm_admin in csv_obj:
        dpm_obj = {}
        dpm_obj['username'] = dpm_admin[1].strip()
        dpm_obj['email'] = dpm_admin[2].strip()
        dpm_admins.append(dpm_obj)
    fh.close()
    return dpm_admins


def openDatabase(dbfile):
    '''Open the database file
    '''
    conn = None
    if (not os.path.isfile(dbfile)):
        print "Error: database does not exist ", dbfile
        sys.exit(10)
    else:
        conn = sqlite3.connect(dbfile)
    return conn


def queryProfile(conn, username):
    '''Function to return the user profile if it exists
    '''
    user_profile = {}
    u_comm = []
    u_comm_d = {}
    u_user = {}

    cur = conn.cursor()
    cur.execute('''select email from user where name = ?''',
                (username,))
    u_email = cur.fetchone()[0]

    cur.execute('''select community.name from community, user,
        user_community where user.name = ? and
        user.user_id = user_community.user_id and
        user_community.community_id = community.community_id''', (username,))
    communities = cur.fetchall()
    conn.commit()
    u_comm = []
    u_comm_d = {}
    for acommunity in communities:
        u_comm.append(acommunity[0])
    u_comm_d["communities"] = u_comm

    u_user["username"] = username.strip()
    u_user["email"] = u_email
    user_profile["profile"] = [u_user]
    user_profile["profile"].append(u_comm_d)
    return user_profile


def getProfile(config):
    '''Function to return the username
    '''
    print "Content-Type: application/json charset=utf-8"
    print ""

    username = ''
    user_profile = {}
    dpmAdmin = False

    # Check the auth type and act accordingly
    if (config.getopt("AUTHENTICATION", "type") == "AAI"):
        username = ""
    elif (config.getopt("AUTHENTICATION", "type") == "STANDALONE"):
        username = config.option("HTMLENV", "user")

    admins = getAdmins(config)
    for admin in admins:
        if (admin['username'] == username.strip()):
            dpmAdmin = True
            user_profile['profile'] = [admin]
            user_profile['profile'].append({'communites': 'all'})
            break

    dbfile = config.get("DATABASE", "profile_name")

    conn = openDatabase(dbfile)
    if (conn):
        if (not dpmAdmin):
            user_profile = queryProfile(conn, username)

    print json.dumps(user_profile)

if __name__ == '__main__':
    cfgfile = "./config/policy.cfg"

    fields = cgi.FieldStorage()
    if ("help" in fields):
        usage()
        sys.exit()

    # Read the config file
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    getProfile(config)
