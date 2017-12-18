#!/usr/bin/env python

import sys
import os
import cgi
import json
import ConfigParser
import sqlite3
import csv


def usage():
    '''Function describing the script usage
    '''
    print "Script to return the policy log information"
    print "Usage:"
    print " ?help=help      Prints this help"
    print ""


def get_uuids(conn, uuid_key_str):
    '''Return the list of keys corresponding to the policy uuids'''
    uuid_keys = []
    uuid_key_str = "%s_%%" % uuid_key_str
    cur = conn.cursor()
    cur.execute('''select key from policies where key like ?''',
                (uuid_key_str,))
    results = cur.fetchall()
    if (len(results) > 0):
        for res in results:
            uuid_keys.append(res[0])
    return uuid_keys


def getUserCommunities(config, username, admin):
    '''Function to get the communities a user belongs to
    '''
    conn = sqlite3.connect(config.get("DATABASE", "profile_name"))
    cur = conn.cursor()

    res = []
    if (admin):
        cur.execute('''select community.name from community''')
        res = cur.fetchall()
    else:
        cur.execute('''select community.name from community, user_community,
                    user where user.name = ? and
                    user.user_id = user_community.user_id and
                    community.community_id = user_community.community_id''',
                    (username.lower(),))
        res = cur.fetchall()
    conn.commit()
    communities = []

    for ares in res:
        communities.append(ares[0])

    return communities


def get_admins(config):
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


def get_value(conn, key):
    '''Return the value from the database for the corresponding key'''
    value = ""
    cur = conn.cursor()
    cur.execute('''select value from policies where key = ?''',
                (key,))
    result = cur.fetchone()
    if (type(result) is not type(None)):
        if (len(result) > 0):
            value = result[0]
    return value


def get_log_entries(conn, log_uuid, uuid):
    '''Return the number of log entries for a policy'''
    log_entries = -1
    log_uuid = "%s_%%" % log_uuid
    cur = conn.cursor()
    cur.execute('''select count(value) from policies where key like ?
                and value = ?''', (log_uuid, uuid))
    result = cur.fetchone()
    if (len(result) > 0):
        log_entries = result[0]
    return log_entries


def getLogs(config, username, admin):
    '''Function to get the log information for all policies
    '''
    print "Content-Type: application-json; charset=utf-8"
    print ""

    # Open the database
    dbfile = config.get("DATABASE", "name").strip()
    if (not os.path.isfile(dbfile)):
        sys.stderr.write("Database %s does not exist" % dbfile)
        sys.exit(-100)
    conn = sqlite3.connect(dbfile)

    # Find out which communities the user belongs to
    communities = getUserCommunities(config, username, admin)

    # Get the keys for the uuid
    uuid_keys = get_uuids(conn, config.get("POLICY_SCHEMA", "uniqueid"))
    policy_logs = {}
    policy_log_data = []
    for auuid in uuid_keys:
        uuid_num = auuid.split(config.get("POLICY_SCHEMA", "uniqueid"))[1]

        # We need to skip the log entries if they don't correspond to the
        # logged in users community
        community_key = "policy_community%s" % (uuid_num)
        if (get_value(conn, community_key) not in communities):
            continue

        # Get the policy name from the database
        pol_name_key = "%s%s" % (config.get("POLICY_SCHEMA", "name"),
                                 uuid_num)
        pol_name = get_value(conn, pol_name_key)

        uuid_val = get_value(conn, auuid)
        log_entries = get_log_entries(conn, config.get("LOG_SCHEMA",
                                                       "identifier"),
                                      uuid_val)

        if (log_entries >= 0):
            for log_num in range(0, int(log_entries)):
                log_state = get_value(conn, "%s_%s%s" %
                                      (config.get("LOG_SCHEMA", "state"),
                                       log_num,
                                       uuid_num))
                log_timestamp = get_value(conn, "%s_%s%s" %
                                          (config.get("LOG_SCHEMA",
                                                      "timestamp"),
                                           log_num,
                                           uuid_num))
                log_center = get_value(conn, "%s_%s%s" %
                                       (config.get("LOG_SCHEMA", "hostname"),
                                        log_num,
                                        uuid_num))
                policy_log_data.append((pol_name, uuid_val, log_state,
                                        log_center, float(log_timestamp)*1000))
    policy_logs["columns"] = [config.get("POLICY_SCHEMA", "name"),
                              config.get("POLICY_SCHEMA", "uniqueid"),
                              config.get("LOG_SCHEMA", "state"),
                              config.get("LOG_SCHEMA", "hostname"),
                              config.get("LOG_SCHEMA", "timestamp")]
    # Reverse the order of the log data so the most recent timestamps are
    # first
    policy_log_data.sort(key=lambda x: x[-1], reverse=True)
    policy_logs["data"] = policy_log_data
    print json.dumps(policy_logs)

if __name__ == '__main__':
    cfgfile = './config/policy.cfg'
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)

    fields = cgi.FieldStorage()
    if ("help" in fields):
        usage()
        sys.exit()

    username = ''
    if (config.get("AUTHENTICATION", "type") == "AAI"):
        username = os.environ["persistentid"]
    elif (config.get("AUTHENTICATION", "type") == "STANDALONE"):
        if (config.has_option("HTMLENV", "user")):
            username = config.get("HTMLENV", "user")

    dpm_admins = get_admins(config)
    admin = False
    for admin in dpm_admins:
        if (admin['username'] == username.strip()):
            admin = True
            break

    getLogs(config, username, admin)
