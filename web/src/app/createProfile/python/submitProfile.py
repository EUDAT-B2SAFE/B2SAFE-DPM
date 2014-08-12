#!/usr/bin/env python
import sqlite3
import ConfigParser
import os 
import sys
import cgi
import time
import json
import smtplib

def submitRequest(config):
    '''Function to post the profile request to the database
    '''
    dpm_admin = "DPM Admin"
    smtpObj = smtplib.SMTP("localhost")
    
    email_from = 'noreply@dmpadmin.localhost'
    email_msg = "From: %s \n" % email_from + "To: %s \n" + \
            "Subject: Request for Access to the Data Policy Manager \n" +\
            "User '%s' has requested (request id %s) '%s' access to" +\
            "the Data Policy Manager for the community '%s'.\n"

    reqRes = {}
    dataVals = json.load(sys.stdin)
    dbfile = config.get("DATABASE", "profile_name")
    conn = sqlite3.connect(dbfile)

    cur = conn.cursor()
    for comm in dataVals["communities"]:
        # Check the user for that community and that role doesn't already exist.
        cur.execute('''select user_comm_id from user_community, roles,
                community, user where user.email = ? and user.user_id =
                user_community.user_id and community.name = ? and
                community.community_id = user_community.community_id and
                roles.name = ? and 
                roles.role_id = user_community.role_id''',
                (dataVals["email"], comm["name"], dataVals["role"])
                )

        result = cur.fetchone()
        if (result != None):
            reqRes["roleExists"] = True
        else:
            # Store the request and email the DPM admin
            
            # Get the last user id and store the user info
            uid = 0
            dpm_date_id = 0
            next_user_comm = 0
            cur.execute('''select user_id from user where email = ?''',
                    (dataVals["email"],))
            u_id = cur.fetchone()
            if (u_id is not None and u_id[0] is not None):
                uid = int(u_id[0]) + 1
            cur.execute('''insert into user (user_id, firstname, lastname,
                    email)  values(?,?,?,?)''',
                    (uid, dataVals["firstname"], dataVals["lastname"],
                        dataVals["email"]))
            
            # Get the last date entry and store the submit time
            cur.execute('''select max(dpm_date_id) from dpm_date''')
            res = cur.fetchone()
            if (res is not None and res[0] is not None):
                print "dpm res ", res
                dpm_date_id = int(res[0]) + 1
            cur.execute('''insert into dpm_date (dpm_date_id, submit_time)
                values (?, ?)''', (dpm_date_id, int(time.time())))

            # Get the selected community id the rows must exist so 
            # no need to check
            cur.execute('''select community_id from community 
                where name = ?''', (comm["name"],))
            comm_id = cur.fetchone()[0]

            # Get the selected role id the rows must exist so no need
            # to check
            cur.execute('''select role_id from roles where name = ?''',
                    (dataVals["role"],))
            role_id = cur.fetchone()[0] 

            # Get the last used community id
            cur.execute('''select max(user_comm_id) from user_community''');
            res = cur.fetchone()
            if (res is not None and res[0] is not None):
                next_user_comm = int(res[0]) + 1
            cur.execute('''insert into user_community (user_comm_id,
            user_id, community_id, dpm_id, dpm_date_id, role_id, 
            status_id) values (?,?,?,?,?,?,?)''',
            (next_user_comm, uid, comm_id, 0, dpm_date_id, role_id, 1))
            
            conn.commit()

            # Email the DPM admin ( we need to read the database for
            # the dpm admin
            #
            cur = conn.cursor()
            cur.execute('''select user.email from user, user_community, 
                roles where user_community.role_id = roles.role_id and
                roles.name = ? and 
                user.user_id = user_community.user_id''',
                (dpm_admin,))
            res = cur.fetchone()
            if (res is not None and res[0] is not None):
                admin_email = res[0]
                msg = email_msg % (admin_email, 
                        dataVals["username"].strip(),
                        next_user_comm,
                        dataVals["role"], comm["name"])
                try:
                    smtpObj.sendmail(email_from, admin_email, msg)
                except smtplib.SMTPException:
                    print "There has been a problem sending email"


if __name__ == '__main__':
    print "Content-Type: text/htm"
    print ""
    cfgfile = "./config/policy_schema.cfg"
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    submitRequest(config)
