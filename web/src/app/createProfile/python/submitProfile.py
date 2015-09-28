#!/usr/bin/env python
import sqlite3
import ConfigParser
import os 
import sys
import cgi
import time
import json
import csv
import smtplib

def getAdmin(config):
    '''Function to load the DPM admin users
    '''
    dpm_admins = []
    fh = file(config.get("DPM_ADMIN", "admin_file"), "r")
    csv_obj = csv.reader(fh)
    for dpm_admin in csv_obj:
        dpm_obj = {}
        dpm_obj['name'] = dpm_admin[0].strip()
        dpm_obj['username'] = dpm_admin[1].strip()
        dpm_obj['email'] = dpm_admin[2].strip()
        dpm_admins.append(dpm_obj)
    fh.close()
    return dpm_admins

def submitRequest(config):
    '''Function to post the profile request to the database
    '''
    dataVals = json.load(sys.stdin)
    username = ''
    # Currently, until we get the AAI working we need to usea
    # a dummy setting for the HTMLENV variable and take the
    # value from the dataVals
    if (config.has_option("HTMLENV", "user")):
        # username = config.get("HTMLENV", "user")
        username = dataVals["username"].strip()
    else:
        username = os.environ["REMOTE_USER"]
    
    if (username.strip() != dataVals["username"].strip()):
        print "Error: username mismatch!"
        print "Exiting"
        sys.exit(1)

    smtpObj = smtplib.SMTP("localhost")
    
    email_from = 'noreply@dmpadmin.localhost'
    email_msg = "From: %s \n" % email_from + "To: %s \n" + \
            "Subject: Request for Access to the Data Policy Manager \n" +\
            "User '%s' (request id %s) has requested '%s' access to " +\
            "the Data Policy Manager for the community '%s'.\n"

    reqRes = {}
    dbfile = config.get("DATABASE", "profile_name")
    conn = sqlite3.connect(dbfile)

    cur = conn.cursor()
    for comm in dataVals["communities"]:
        # Check the same user for that community doesn't already exist.
        cur.execute('''select user_comm_id from user_community,
                community, user where user.email = ? and user.user_id =
                user_community.user_id and community.name = ? and
                community.community_id = user_community.community_id''',
                (dataVals["email"].lower().strip(), 
                    comm["name"].lower().strip())
                )

        result = cur.fetchone()
        if (result != None):
            print "roleExists"
        else:
            # Store the request and email the DPM admin
            uid = 0
            dpm_id = -1
            dpm_date_id = 0
            next_user_comm = 0
            # Do we have this user in the database, if so return
            # the UID otherwise store with the next id
            # We will only ever have one user with these details
            cur.execute('''select user_id from user where email = ? and
                    firstname = ? and lastname = ? and name = ?''',
                    (dataVals["email"].lower().strip(), 
                        dataVals["firstname"].lower().strip(),
                        dataVals["lastname"].lower().strip(),
                        dataVals["username"].lower().strip()))
            res = cur.fetchall()
            if (len(res) == 0):
                cur.execute("select max(user_id) from user")
                u_id = cur.fetchone()
                if (u_id is not None and u_id[0] is not None):
                    uid = int(u_id[0]) + 1
                cur.execute('''insert into user (user_id, name, firstname, 
                    lastname, email)  values(?,?,?,?,?)''',
                    (uid, dataVals["username"].strip(), 
                        dataVals["firstname"].lower().strip(), 
                        dataVals["lastname"].lower().strip(),
                        dataVals["email"].lower().strip()))
            else:
                uid = res[0][0]
            
            # Get the last date entry and store the submit time
            cur.execute('''select max(dpm_date_id) from dpm_date''')
            res = cur.fetchone()
            if (res is not None and res[0] is not None):
                dpm_date_id = int(res[0]) + 1
            cur.execute('''insert into dpm_date (dpm_date_id, submit_time)
                values (?, ?)''', (dpm_date_id, int(time.time())))

            # Get the selected community id the rows must exist so 
            # no need to check
            cur.execute('''select community_id from community 
                where name = ?''', (comm["name"].lower().strip(),))
            comm_id = cur.fetchone()[0]

            # Get the selected role id the rows must exist so no need
            # to check
            cur.execute('''select role_id from roles where name = ?''',
                    (dataVals["role"].lower().strip(),))
            role_id = cur.fetchone()[0] 

            # Store the pending URL until the user has been approved
            cur.execute('''select dpm_id from dpm_page where 
                name = 'pending' ''')
            res = cur.fetchall()
            dpm_id = res[0][0]

            # Get the last used community id
            cur.execute('''select max(user_comm_id) from user_community''');
            res = cur.fetchone()
            if (res is not None and res[0] is not None):
                next_user_comm = int(res[0]) + 1
            cur.execute('''insert into user_community (user_comm_id,
            user_id, community_id, dpm_id, dpm_date_id, role_id, 
            status_id) values (?,?,?,?,?,?,?)''',
            (next_user_comm, uid, comm_id, dpm_id, dpm_date_id, role_id, 1))
            
            conn.commit()

            # Email the DPM admin ( we need get the admins from the
            # config database)
            #
            admins = getAdmin(config)
            if (len(admins) == 0):
                admin_email = admins[0]["email"]
            else:
                emails = []
                for admin in admins:
                    if (admin["email"] not in emails):
                        emails.append(admin["email"])
                admin_email = ",".join(emails)
                email_from = emails

            msg = email_msg % (admin_email, dataVals["username"].strip(),
                    next_user_comm, dataVals["role"], comm["name"])
            
            try:
                smtpObj.sendmail(email_from, emails, msg)
            except smtplib.SMTPException:
                print "There has been a problem sending email"

if __name__ == '__main__':
    print "Content-Type: text/html"
    print ""
    cfgfile = "./config/policy.cfg"
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    submitRequest(config)
