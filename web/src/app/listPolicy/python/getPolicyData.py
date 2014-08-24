#!/usr/bin/env python

import getopt
import sys
import cgi
import json
import ConfigParser
import kyotocabinet
import sqlite3
import os
import re

def usage():
    '''Function describing the script usage
    '''
    print "Script to get the database info for the policies"
    print "Usage: getPolicyData.py"
    print "Options:"
    print "help=help                 Prints this help"
    print ""

def getData(config):
    '''Function to return the policies from the database
    '''
    dpmAdmin = False

    # Get the username from the env
    username = ''
    if (config.has_option("HTMLENV", "user")):
        username = config.get("HTMLENV", "user")
    else:
        username = os.environ["REMOTE_USER"]
    
    # Get the communities for the user from the database
    conn = sqlite3.connect(config.get("DATABASE", "profile_name"))
    cur = conn.cursor()
    
    # If the user is a DPM admin then we need to be able to see all policies
    cur.execute('''select roles.role_id from user_community, user, roles
        where user.name = ? and user.user_id = user_community.user_id and
        roles.name = 'dpm admin' and 
        roles.role_id = user_community.role_id''',
        (username,))
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
        communities.append(ares[0])

    # Read the configs and get database keys
    visible_keys = [x.strip() for x in config.get("DATABASE", "default_visible").split(',')]

    # Keys to skip
    skip_keys = [x.strip() for x in config.get("DATABASE", "skip_keys").split(',')]
    sections = ["POLICY_SCHEMA", "DATASETS_SCHEMA", "ACTIONS_SCHEMA",
            "TARGETS_SCHEMA"]
    columns = []
    for section in sections:
        for option in config.options(section):
            val = config.get(section, option)
            if (val in skip_keys):
                continue
            if (val in visible_keys):
                columns.append((val, "true"))
            else:
                columns.append((val, "false"))

    # Open the database
    db = kyotocabinet.DB()
    dbfile = config.get("DATABASE", "name").strip()
    if (not db.open(dbfile, 
        kyotocabinet.DB.OWRITER | kyotocabinet.DB.OCREATE)):
        sys.stderr.write("open error: " + str(db.error()))

    data = []
    last_idx = db.get(config.get("DATABASE", "last_index"))
    if (last_idx is not None):
        last_index = int(last_idx)
    else:
        last_index = -1

    for idx in range(0, last_index+1):
        col_names = []
        col_multi = []
        dvals = []
        community_key = ''
        
        # Setup the column names
        for acol in columns:
            if ("policy_community" in acol):
                community_key = "%s_%s" % (acol[0], idx)
            if ("collection_persistentIdentifier" in acol[0]):
                col_multi.append("%s_[0-9]+_%s" % (acol[0], idx))
            else:
                col_names.append("%s_%s" % (acol[0], idx))
       
        # Get the keys from the database for the multi-elements
        mcolls = []
        for mcol in col_multi:
            tcol = db.match_regex(mcol)
            tcol.sort(key=lambda x: int(x.split('_')[-2]))
            mcolls = mcolls + tcol
        # Get the data from the database
        vals = db.get_bulk(col_names)
        mvals = db.get_bulk(mcolls)
        
        # Check if the user belongs to the policy community
        # if not skip the policy
        if (vals.has_key(community_key)):
            if (vals[community_key] not in communities):
                continue
       
        # Loop over the columns and store the values
        for cid in range(0, len(columns)):
            pat = re.compile('%s_[0-9]+_{0,1}[0-9]*' % columns[cid][0])
            for key in vals.keys():
                if (pat.match(key)):
                    dvals.append((vals[key], columns[cid][1]))
                    break
            # Loop over the columns with multivalues and concatenate
            # the results
            multiVal = False
            multiStr = ""
            for key in mvals.keys():
                if (pat.match(key)):
                    multiVal = True
                    if (len(multiStr) == 0):
                        multiStr = mvals[key]
                    else:
                        multiStr = "%s, %s" % (multiStr, mvals[key])
            if (multiVal):
                dvals.append((multiStr, columns[cid][1]))
        
        data.append(dvals)
        
    print json.dumps(data)

if __name__ == '__main__':
    cfgfile = "./config/policy_schema.cfg"
    
    fields = cgi.FieldStorage()

    if (fields.has_key("help")):
        usage()
        sys.exit()

    # Read the configs
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)

    print "Content-Type: application/json charset=utf-8"
    print ""
 
    getData(config)

