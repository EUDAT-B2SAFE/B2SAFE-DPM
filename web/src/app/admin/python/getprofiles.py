#!/usr/bin/env python
import ConfigParser
import sqlite3
import os
import json

def fetch_cm(conn, username, status_options, keys):
    '''Function to fetch the rows visible to a community manager
    '''
    data = {}
    data["cols"] = keys

    # First pick up which communities the user is registered to
    # then get the requests for those communities
    cur = conn.cursor()
    cur.execute('''select community.name from user_community, community,
        status, user where user.user_id = user_community.user_id and
        user_community.community_id = community.community_id and
        user_community.status_id = status.status_id and
        user.name = ? and status.status = ?''', (username, "approved"))
    communities = cur.fetchall()

    data["rows"] = []

    for acommunity in communities:
        cur.execute('''select user_community.user_comm_id, user.lastname, 
            user.firstname, user.name, user.email, roles.name, 
            community.name, dpm_date.submit_time, status.status 
            from user, community, user_community, dpm_date, roles, status
            where user.user_id = user_community.user_id
            and dpm_date.dpm_date_id = user_community.dpm_date_id and
            roles.role_id = user_community.role_id and 
            community.community_id = user_community.community_id and
            status.status_id = user_community.status_id and
            community.name = ?''', (acommunity[0],))
        results = cur.fetchall()
        
        for result in results:
            datum = {}
            db_name = ''
            for count in range(0, len(result)):
                # save the user we don't want to allow the user to delete
                # themselves from the dpm
                if (count == 3):
                    db_name = result[count]
                # Deal with the status here
                if (count == 8):
                    if (username != db_name):
                        datum["status_options"] = status_options[result[count]]
                    else:
                        datum["status_options"] = []
                
                res = {}
                res["name"] = result[count]
                if (datum.has_key("values")):
                    datum["values"].append(res)
                else:
                    datum["values"] = [res]
            data["rows"].append(datum)

    print json.dumps(data)

def fetch_all(conn, username, status_options, keys):
    '''Method to fetch all rows from the
    database
    '''
    cur = conn.cursor()
    cur.execute('''select user_community.user_comm_id, user.lastname, 
            user.firstname, user.name, user.email, roles.name, 
            community.name, dpm_date.submit_time, status.status 
            from user, community, user_community, dpm_date, roles, status
            where user.user_id = user_community.user_id
            and dpm_date.dpm_date_id = user_community.dpm_date_id and
            roles.role_id = user_community.role_id and 
            community.community_id = user_community.community_id and
            status.status_id = user_community.status_id''')
    results = cur.fetchall()
    data = {}
    data["cols"] = keys
    data["rows"] = []
    for result in results:
        datum = {}
        for count in range(0, len(result)):
            res = {}
            # save the user we don't want to allow the user to delete
            # themselves from the dpm
            if (count == 3):
                db_name = result[count]
 
            # Deal with the status here
            if (count == 8):
                if (db_name != username):
                    datum["status_options"] = status_options[result[count]]
                else:
                    datum["status_options"] = []

            res["name"] = result[count]
            if (datum.has_key("values")):
                datum["values"].append(res)
            else:
                datum["values"] = [res]
        data["rows"].append(datum)

    print json.dumps(data)

def getProfiles(config):
    '''Function to get the profiles from the database
    '''
    if (config.has_option("HTMLENV", "user")):
        username = config.get("HTMLENV", "user").strip()
    else:
        username = os.environ["REMOTE_USER"].strip()
    
    # Define the options for the status and the table column keys
    status_options= {"approved": ["decline", "close"], 
        "closed": ["approve"], "pending": ["approve", "decline"],
        "declined": ["approve"]}

    keys = ["uid", "lastname", "firstname", "username", "email", "role",
            "community", "submittime", "status"]

    # What type of user are we?
    conn = sqlite3.connect(config.get("DATABASE", "profile_name"))
    cur = conn.cursor()
    cur.execute('''select roles.name from roles, user_community, user,
        status where user.name = ? 
        and user.user_id = user_community.user_id
        and roles.role_id = user_community.role_id and 
        user_community.status_id = status.status_id and
        status.status = 'approved' ''',
        (username,))
    roles = cur.fetchall()
    conn.commit()
    dpm_admin = False
    cm_admin = False
    for arole in roles:
        if ("dpm admin" == arole[0]):
            dpm_admin = True
            break
    if (not dpm_admin):
        for arole in roles:
            if ("community admin" == arole[0]):
                cm_admin = True
                break
    
    if (dpm_admin):
        fetch_all(conn, username, status_options, keys)
    elif (cm_admin):
        fetch_cm(conn, username, status_options, keys)

if __name__ == '__main__':
    cfgfile = './config/policy_schema.cfg'
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    print "Content-Type: application/json charset=utf-8"
    print ""
    getProfiles(config)
