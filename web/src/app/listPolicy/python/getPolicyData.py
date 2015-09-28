#!/usr/bin/env python

import getopt
import sys
import cgi
import json
import ConfigParser
import sqlite3
import csv
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

def getAdmins(config):
    '''Function to load the DPM admin username
    '''
    dpm_admins = []
    fh = file(config.get("DPM_ADMIN", "admin_file"), "r")
    csv_obj = csv.reader(fh)
    for dpm_admin in csv_obj:
        username = dpm_admin[1].strip()
        dpm_admins.append(username)
    fh.close()
    return dpm_admins

def match_multi(expr, item):
    '''Match the expression'''
    res = re.match(expr, item)
    return res is not None

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
    admins = getAdmins(config)
    if (username in admins):
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

    # Open the database (first time around it's not really an error the db
    # doesn't exist)
    dbfile = config.get("DATABASE", "name").strip()
    if (not os.path.isfile(dbfile)):
        sys.stderr.write("Warning: Database %s does not exist\n" % dbfile)
        sys.exit(-100)

    conn = sqlite3.connect(dbfile)
    cur = conn.cursor()

    data = []
    last_idx = None

    cur.execute("select value from policies where key = 'last_index'")
    result = cur.fetchone()
    if (result != None and len(result) > 0):
        last_idx = result[0]

    if (last_idx is not None):
        last_index = int(last_idx)
    else:
        last_index = 0
    
    # print "last_index is ", last_index
    for idx in range(0, last_index+1):
        col_names = []
        col_multi = []
        dvals = []
        community_key = ''
        
        # Setup the column names
        # Get the index of the timestamp - we will need this to sort on
        # later
        acount = 0
        time_idx = -1
        for acol in columns:
            if ("policy_ctime" in acol):
                time_idx = acount
            acount += 1
            if ("policy_community" in acol):
                community_key = "%s_%s" % (acol[0], idx)
            if ("collection_persistentIdentifier" in acol[0]):
                col_multi.append("%s_[0-9]+_%s" % (acol[0], idx))
            else:
                col_names.append("%s_%s" % (acol[0], idx))

        #print "col_multi ", col_multi
        #print "col_names ", col_names
        
        # Get the keys from the database for the multi-elements
        mcolls = []
        conn.create_function("regexp", 2, match_multi)
        cursor = conn.cursor()
        for mcol in col_multi:
            cur.execute('''select key from policies where 
                key regexp ?''', (mcol,))
            tcol = [x[0] for x in cur.fetchall()]
            tcol.sort(key=lambda x: int(x.split('_')[-2]))
            mcolls = mcolls + tcol
        # Get the data from the database
        vals = {}
        for col_name in col_names:
            cur.execute("select value from policies where key = ?", 
                    (col_name,))
            vals[col_name] = cur.fetchall()[0][0]
        mvals = {}
        for mcoll in mcolls:
            cur.execute("select value from policies where key = ?", 
                    (mcoll,))
            mvals[mcoll] = cur.fetchall()[0][0]

        #print "vals ", vals
        #print "mvals ", mvals

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
        
    # Sort the list according to timestamp
    data.sort(key=lambda x: x[time_idx][0], reverse=True)
    print json.dumps(data)

if __name__ == '__main__':
    cfgfile = "./config/policy.cfg"
    
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

