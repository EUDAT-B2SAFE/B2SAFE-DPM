#!/usr/bin/env python

import sys
import os
import cgi
import json
import ConfigParser
import sqlite3
import kyotocabinet

def usage():
    '''Function describing the script usage
    '''
    print "Script to return the policy log information"
    print "Usage:"
    print " ?help=help      Prints this help"
    print ""

def getUserCommunities(config, username):
    '''Function to get the communities a user belongs to
    '''
    dpmAdmin = False
    conn = sqlite3.connect(config.get("DATABASE", "profile_name"))
    cur = conn.cursor()
    cur.execute('''select roles.role_id from user_community, user,
    roles where user.name = ? and user.user_id = user_community.user_id
    and roles.name = 'dpm admin' and 
    roles.role_id = user_community.role_id''', (username,))

    roles = cur.fetchall()
    if (len(roles) > 0):
        dpmAdmin = True

    res = []
    if (dpmAdmin):
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
        communities.append(res[0][0])

    return communities


def getLogs(config, username):
    '''Function to get the log information for all policies
    '''
    print "Content-Type: application-json; charset=utf-8"
    print ""

    # Open the database
    db = kyotocabinet.DB()
    if (not db.open(config.get("DATABASE", "name").strip(),
        kyotocabinet.DB.OREADER)):
        print "Unable to open the database " + str(db.error())
        sys.exit(10)
   
    # Find out which communities the user belongs to
    communities = getUserCommunities(config, username)

    # Get the keys for the uuid
    uuid_keys = db.match_prefix(config.get("POLICY_SCHEMA", "uniqueid"))
    policy_logs = {}
    policy_log_data = []
    for auuid in uuid_keys:
        uuid_num = auuid.split(config.get("POLICY_SCHEMA", "uniqueid"))[1]
        
        # We need to skip the log entries if they don't correspond to the
        # logged in users community
        community_key = "policy_community%s" % (uuid_num)
        if (db.get(community_key) not in communities):
            continue

        # Get the policy name from the database
        pol_name_key = "%s%s" % (config.get("POLICY_SCHEMA", "name"),
                uuid_num)
        pol_name = db.get(pol_name_key)

        log_entries = db.get("%s%s" % \
                (config.get("LOG_SCHEMA", "log_entries"), uuid_num))
        uuid_val = db.get(auuid)
        if (type(log_entries) != type(None)):
            for log_num in range(0, int(log_entries)+1):
                log_state = db.get("%s%s_%s" % \
                        (config.get("LOG_SCHEMA", "log_state"), 
                        uuid_num, log_num))
                log_timestamp = db.get("%s%s_%s" % \
                        (config.get("LOG_SCHEMA", "log_timestamp"), 
                        uuid_num, log_num))
                log_center = db.get("%s%s_%s" % \
                        (config.get("LOG_SCHEMA", "log_center"), 
                        uuid_num, log_num))
                policy_log_data.append((pol_name, uuid_val, log_state, 
                    log_center, float(log_timestamp)*1000))
    policy_logs["columns"] = [config.get("POLICY_SCHEMA", "name"),
            config.get("POLICY_SCHEMA", "uniqueid"),
            config.get("LOG_SCHEMA", "log_state"),
            config.get("LOG_SCHEMA", "log_center"),
            config.get("LOG_SCHEMA", "log_timestamp")]
    # Reverse the order of the log data so the most recent timestamps are
    # first
    policy_log_data.sort(key=lambda x: x[-1], reverse=True)
    policy_logs["data"] = policy_log_data
    print json.dumps(policy_logs)

if __name__ == '__main__':
    cfgfile = './config/policy_schema.cfg'
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    
    fields = cgi.FieldStorage()
    if (fields.has_key("help")):
        usage()
        sys.exit()
   
    username = ''
    if (config.has_option("HTMLENV", "user")):
        username = config.get("HTMLENV", "user")
    else:
        username = os.environ["REMOTE_USER"]

    getLogs(config, username)

