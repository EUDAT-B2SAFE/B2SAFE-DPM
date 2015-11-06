#!/usr/bin/env python
import cgi
import getopt
import sys
import json
import calendar
import time
import hashlib
import os
import sqlite3
import ConfigParser


def usage():
    '''Function describing the script usage
    '''
    print "Script to query the policy repository"
    print "Usage: querypolicy.py?community_id=<community>&site=<site>\ "
    print "       &begin_date=<date>&end_date=<date>"
    print ""
    print "Returns a JSON array consisting of: url_to_policy,"
    print " policy_ctime, policy_checksum, checksum_type"
    print ""
    print "One of the following arguments must be supplied:"
    print ""
    print "community_id=<communityid>  The identifier for the community."
    print ""
    print "site=<site>                 The site where the policy will be implemented."
    print "begin_date=<date>           The lower limit for the creation date."
    print "                            for the policy."
    print "end_date=<date>             The upper limit for the creation date."
    print ""
    print "Options:"
    print ""
    print "deactivated=true            Only show deactivated policies. In this"
    print "                            case only the uuid and md5 are returned"
    print ""


class PolicyQuery():
    '''Filter the policies
    '''
    def __init__(self, config, btime=-1, etime=-1, comid='', site=''):
        self.btime = btime
        self.etime = etime
        self.comid = comid
        self.site = site
        self.deactivated = False
        self.policy_key = config.get("POLICY_SCHEMA", "object")
        self.comm_str = config.get("POLICY_SCHEMA", "community")
        self.site_str = config.get("TARGETS_SCHEMA", "site").strip()
        self.ctime_str = config.get("POLICY_SCHEMA", "ctime").strip()
        self.remove_str = config.get("POLICY_SCHEMA", "removed").strip()
        self.ids = []
        self.removed_ids = []
        self.config = config

    def get(self, key):
        '''Get the value corresponding to the key'''
        result = None
        # Open the database
        dbfile = self.config.get("DATABASE", "name").strip()
        if (not os.path.isfile(dbfile)):
            sys.write.error("Unable to open the database %s" % dbfile)
            sys.exit(-100)

        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        cur.execute("select value from policies where key = ?", (key,))
        result = cur.fetchone()
        if (len(result) > 0):
            result = result[0]
        return result

    def _get_ids(self, results, cur):
        '''Filter the ids according to the deleted key'''
        for row in results:
            p_id = row[0].split("_")[-1]
            remove_str = "%s_%s" % (self.remove_str, p_id)
            cur.execute("select value from policies where key =?",
                        (remove_str,))
            val = cur.fetchone()
            if (val[0] == "true"):
                self.removed_ids.append(p_id)
            else:
                self.ids.append(p_id)

    def query(self):
        '''Method to filter the results according to the date
        or the site or the community
        '''

        # Open the database
        dbfile = self.config.get("DATABASE", "name").strip()
        if (not os.path.isfile(dbfile)):
            sys.write.error("Unable to open the database %s" % dbfile)
            sys.exit(-100)

        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()

        if (self.btime > 0 and self.etime == -1):
            ctime = "%s%%" % self.ctime_str
            cur.execute('''select key from policies where value > ?
                    and key like ?''', (self.btime, ctime))
            results = cur.fetchall()
            self._get_ids(results, cur)

        if (self.etime > 0 and self.btime == -1):
            ctime = "%s%%" % self.ctime_str
            cur.execute('''select key from policies where value < ?
                and key like ?''', (self.etime, ctime))
            results = cur.fetchall()
            self._get_ids(results, cur)

        if (len(self.comid) > 0):
            comid = "%s%%" % self.comm_str
            cur.execute('''select key from policies where value = ?
                    and key like ?''', (self.comid, comid))
            results = cur.fetchall()
            self._get_ids(results, cur)

        if (len(self.site) > 0):
            site = "%s%%" % self.site_str
            cur.execute('''select key from policies where value = ?
                and key like ?''', (self.site, site))
            results = cur.fetchall()
            self._get_ids(results, cur)


def transformDate(b_date, e_date):
    '''Function to transform the date into a unix timestamp in GMT
    '''
    sb_date = -1
    se_date = -1
    if (len(b_date) > 0):
        sb_date = calendar.timegm(time.strptime(b_date, "%Y-%m-%d"))
    if (len(e_date) > 0):
        se_date = calendar.timegm(time.strptime(e_date, "%Y-%m-%d"))
    return (sb_date, se_date)


def getPoliciesFromDB(config, community_id, site, b_date, e_date, deactivated):
    '''Function to query and retreive the policies from the
    key-value store
    '''
    sb_date, se_date = transformDate(b_date, e_date)

    # Loop over the database and get the ids
    policy_obj = PolicyQuery(config, sb_date, se_date, community_id, site)
    policy_obj.query()

    # Now loop over the policy ids and extract the md5, and create time
    # skip the removed policies
    policies = []
    if (not deactivated):
        for aid in policy_obj.ids:
            if (aid in policy_obj.removed_ids):
                continue
            ctime_key = "%s_%s" % (config.get("POLICY_SCHEMA",
                                              "ctime").strip(), aid)
            md5_key = "%s_%s" % (config.get("POLICY_SCHEMA", "md5").strip(),
                                 aid)
            policy_key = "%s_%s" % (config.get("POLICY_SCHEMA", "object").strip(),
                                    aid)
            policy_string = "%s=%s" % (config.get("DATABASE",
                                       "fetch_string").strip(), policy_key)
            policies.append([policy_string, policy_obj.get(ctime_key),
                             policy_obj.get(md5_key), "md5"])
    else:
        for aid in policy_obj.removed_ids:
            md5_key = "%s_%s" % (config.get("POLICY_SCHEMA", "md5").strip(), aid)
            uuid_key = "%s_%s" % (config.get("POLICY_SCHEMA", "uniqueid").strip(),
                                  aid)
            policies.append([policy_obj.get(uuid_key),
                             policy_obj.get(md5_key), "md5"])

    # Return the policies
    return policies


def runQuery():
    '''Function to query the policy files
    '''
    # get the database configs
    config = ConfigParser.ConfigParser()
    config.read("config/policy.cfg")

    community_id_key = "community_id"
    b_date_key = "begin_date"
    e_date_key = "end_date"
    site_key = "site"
    help_key = "help"
    deactivated_key = "deactivated"
    deactivated = False

    print "Content-Type: application/json; charset=utf-8"
    print ""

    formData = cgi.FieldStorage()

    # Get the community manager ID, site and date from the string
    keys = formData.keys()

    if (help_key in formData):
        usage()
        sys.exit(0)

    # Check we have keys we recognise
    if ((community_id_key not in keys) and (b_date_key not in keys)
            and (e_date_key not in keys)
            and (site_key not in keys) and help_key not in keys):
        print "Error: no recognised search paramaters supplied"
        print "recognised parameters are: 'community_id', 'site', 'begin_date', 'end_date'"
        print "Run with the help option (add '?help=help') to see the help"
        sys.exit(1)

    community_id = formData.getvalue(community_id_key, "")
    site = formData.getvalue(site_key, "")

    if (formData.getvalue(deactivated_key, "") == "true"):
        deactivated = True

    # If the date is supplied check the format. We expect YYYY-MM-DD
    b_date = formData.getvalue(b_date_key, "")
    if (len(b_date) > 0):
        try:
            time.strptime(b_date, "%Y-%m-%d")
        except ValueError:
            print "Format of the date should be YYYY-MM-DD"
            sys.exit(2)
        except:
            raise

    # If the date is supplied check the format. We expect YYYY-MM-DD
    e_date = formData.getvalue(e_date_key, "")
    if (len(e_date) > 0):
        try:
            time.strptime(e_date, "%Y-%m-%d")
        except ValueError:
            print "Format of the date should be YYYY-MM-DD"
            sys.exit(2)
        except:
            raise

    # Get the policy files subject to the search criteria
    policies = getPoliciesFromDB(config, community_id, site, b_date, e_date,
                                 deactivated)
    print json.JSONEncoder().encode(policies)

if __name__ == '__main__':
    verbose = 0
    opts, args = getopt.getopt(sys.argv[1:], 'hv', ['help', 'verbose'])
    for opt, val in opts:
        if (opt == '-h' or opt == '--help'):
            usage()
            sys.exit(0)
        if (opt == '-v' or opt == '--verbose'):
            verbose = 1

    runQuery()
