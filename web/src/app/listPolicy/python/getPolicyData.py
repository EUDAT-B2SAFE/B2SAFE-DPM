#!/usr/bin/env python

import sys
import json
import ConfigParser
import sqlite3
import csv
import os
import re
import requests
import xml.etree.ElementTree


def usage():
    '''Function describing the script usage
    '''
    print "Script to get the database info for the policies"
    print "Usage: getPolicyData.py"
    print "Options:"
    print "help=help                 Prints this help"
    print ""


def get_admins(config):
    '''Function to load the DPM admin username
    '''
    dpm_admins = []
    file_handle = file(config.get("DPM_ADMIN", "admin_file"), "r")
    csv_obj = csv.reader(file_handle)
    for dpm_admin in csv_obj:
        username = dpm_admin[1].strip()
        dpm_admins.append(username)
    file_handle.close()
    return dpm_admins


def match_multi(expr, item):
    '''Match the expression'''
    res = re.match(expr, item)
    return res is not None


def get_user(config):
    '''Get the user from the environment'''
    username = ''
    if config.get("AUTHENTICATION", "type") == "AAI":
        username = os.environ["REMOTE_USER"]
    elif config.get("AUTHENTICATION", "type") == "STANDALONE":
        if config.has_option("HTMLENV", "user"):
            username = config.get("HTMLENV", "user")
    return username


def get_communities(config, username):
    '''Get the communities from the database. If the user is an
    admin return all the communities'''

    dpm_admin = False
    # Get the communities for the user from the database
    conn = sqlite3.connect(config.get("DATABASE", "profile_name"))
    cur = conn.cursor()

    # If the user is a DPM admin then we need to be able to see all policies
    admins = get_admins(config)
    if username in admins:
        dpm_admin = True

    res = []
    if dpm_admin:
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


def get_columns(config):
    '''Get the columns to display'''

    columns = []
    # Read the configs and get database keys
    visible_keys = [x.strip() for x in
                    config.get("DATABASE", "default_visible").split(',')]

    # Keys to skip
    skip_keys = [x.strip() for x in config.get("DATABASE",
                                               "skip_keys").split(',')]
    skip_keys = skip_keys + ["policy_id", "policy_md5", "policy_ctime",
                             "policy_community", "action_type",
                             "action_trigger_action", "policy_removed",
                             "action_trigger_type", "src_identifier",
                             "src_type", "src_hostname", "src_resource",
                             "tgt_identifier", "tgt_type", "tgt_hostname",
                             "tgt_resource"]

    sections = ["POLICY_SCHEMA", "ACTIONS_SCHEMA", "SOURCES_SCHEMA",
                "TARGETS_SCHEMA"]
    columns = []
    for section in sections:
        for option in config.options(section):
            val = config.get(section, option)
            if val in skip_keys:
                continue
            if val in visible_keys:
                columns.append((val, "true"))
            else:
                columns.append((val, "false"))
    return columns


def get_last_index(cursor):
    '''Return the index of the last policy stored in the database'''

    last_index = None
    last_idx = None
    cursor.execute("select value from policies where key = 'last_index'")
    result = cursor.fetchone()
    if result is not None:
        if len(result) > 0:
            last_idx = result[0]

    if last_idx is not None:
        last_index = int(last_idx)
    else:
        last_index = 0
    return last_index


def get_mcolls(cursor, in_array):
    '''Get the collections with multiple values
    '''
    mcolls = []
    # print 'in get_mcolls ', in_array
    for mcol in in_array:
        cursor.execute('''select key from policies where key regexp ?''',
                       (mcol,))
        tcol = [x[0] for x in cursor.fetchall()]
        tcol.sort(key=lambda x: int(x.split('_')[-2]))
        mcolls = mcolls + tcol
    return mcolls


def get_databases(base_url, config):
    '''Return a dictionary of available databases'''

    response = requests.get(base_url,
                            auth=(config.get("XMLDATABASE", "user"),
                                  config.get("XMLDATABASE", "pass")))
    xml_databases = {}
    if response.status_code == 200:
        xml_response =\
            xml.etree.ElementTree.ElementTree(
                xml.etree.ElementTree.fromstring(response.text))

        for xml_node in xml_response.getiterator():
            if "database" in xml_node.tag:
                if (len(xml_node.text.strip()) > 0 and xml_node.text.strip()
                        not in xml_databases.values()
                        and "policy_" in xml_node.text):
                    community = xml_node.text.strip().split("_")[-1]
                    xml_databases[community] = xml_node.text.strip()
    else:
        print "Problem querying the database: ", response.status_code
        print response.text
        sys.exit(response.status_code)

    return xml_databases


def get_data(config):
    '''Function to return the policies from the database
    '''

    # Get the username from the env
    username = get_user(config)

    # Get the communities from the Database
    communities = get_communities(config, username)

    # Get the columns to display
    columns = get_columns(config)

    data = []
    last_index = 0

    # Get the list of policies from the database
    basex_url = config.get("XMLDATABASE", "root_name")
    databases = get_databases(basex_url, config)
    xml_files = []
    for community in communities:
        if community in databases:
            url = basex_url.strip() + "/%s" % databases[community]
            response = requests.get(url,
                                    auth=(config.get("XMLDATABASE", "user"),
                                          config.get("XMLDATABASE", "pass")))
            if response.status_code == 200:
                xml_response =\
                    xml.etree.ElementTree.ElementTree(
                        xml.etree.ElementTree.fromstring(response.text))

                for xml_node in xml_response.getiterator():
                    if "resource" in xml_node.tag:
                        if xml_node.text.strip() not in xml_files:
                            xml_files.append((url, xml_node.text.strip()))
            else:
                print "Problem querying the database: ", response.status_code
                print response.text
                sys.exit(response.status_code)

    # Loop over the policies and get the atributes for the policies
    attributes = {"name": "", "uniqueid": "", "author": "", "version": ""}
    for policy_url, policy in xml_files:
        attributes["url"] = policy_url
        for attribute in attributes.keys():
            if attribute == "url":
                continue
            query = policy_url + "/%s" % policy + "?query=//*/@%s" % attribute
            response = requests.get(query,
                                    auth=(config.get("XMLDATABASE", "user"),
                                          config.get("XMLDATABASE", "pass")))
            if response.status_code == 200:
                attrib_name = "%s=" % attribute
                attributes[attribute] =\
                    response.text.split(attrib_name)[1].strip('"')
            else:
                print "Problem querying the database: ", response.status_code
                print response.text
                sys.exit(response.status_code)

        data.append([[attributes["name"], "true"],
                    [attributes["version"], "true"],
                    [attributes["author"], "true"],
                    [attributes["uniqueid"], "true"],
                    [attributes["url"], "false"]])

    for idx in range(0, last_index+1):
        col_names = []
        src_multi = []
        tgt_multi = []
        dvals = []
        community_key = ''

        # Setup the column names
        # Get the index of the timestamp - we will need this to sort on
        # later
        acount = 0
        time_idx = -1
        for acol in columns:
            if "policy_ctime" in acol:
                time_idx = acount
            acount += 1
            if "policy_community" in acol:
                community_key = "%s_%s" % (acol[0], idx)
            if "src_" in acol[0]:
                src_multi.append("\\b%s_[0-9]+_%s\\b" % (acol[0], idx))
            elif "tgt_" in acol[0]:
                tgt_multi.append("\\b%s_[0-9]+_%s\\b" % (acol[0], idx))
            else:
                col_names.append("%s_%s" % (acol[0], idx))

        # print "src_multi ", src_multi
        # print "tgt_multi ", tgt_multi
        # print "col_names ", col_names

        # Get the keys from the database for the multi-elements
        # mcolls = []
        # conn.create_function("regexp", 2, match_multi)
        # cur = conn.cursor()
        # mcolls = get_mcolls(cur, src_multi)
        # mcolls = mcolls + get_mcolls(cur, tgt_multi)

        # Get the data from the database
        # vals = {}
        # for col_name in col_names:
            # print "coll_name ", col_name
        #    cur.execute("select value from policies where key = ?",
        #                (col_name,))
        #    result = cur.fetchall()
            # print "result ", result
        #    vals[col_name] = result[0][0]
        # mvals = {}
        # for mcoll in mcolls:
        #    cur.execute("select value from policies where key = ?",
        #                (mcoll,))
        #    mvals[mcoll] = cur.fetchall()[0][0]

        # print "vals ", vals
        # print "mvals ", mvals

        # Check if the user belongs to the policy community
        # if not skip the policy
        # if community_key in vals:
        #    if vals[community_key] not in communities:
        #        continue

        # Loop over the columns and store the values
        # print "columns ", columns
        # for cid in range(0, len(columns)):
            # print "column ", columns[cid]
        #    pat = re.compile('%s_[0-9]+_{0,1}[0-9]*' % columns[cid][0])
        #    for key in vals.keys():
        #        if pat.match(key):
        #            dvals.append((vals[key], columns[cid][1]))
        #            break
            # Loop over the columns with multivalues and concatenate
            # the results
        #    multiple_values = False
        #    multi_string = ""
        #    sub_dict = {}
        #    for akey in mvals.keys():
        #        if pat.match(akey):
        #            sub_dict[akey] = mvals[akey]

        #    if len(sub_dict) > 0:
        #        multiple_values = True
                # print 'sub_dict ', sub_dict
        #        tkeys = sub_dict.keys()
                # print 'tkeys ', tkeys
        #        tkeys.sort(key=lambda x: int(x.split('_')[-2]))
        #        for key in tkeys:
        #            # print 'key ', key
        #            # print 'mvals ', mvals[key]
        #            if len(multi_string) == 0:
        #                if mvals[key] is not None:
        #                    multi_string = mvals[key]
        #            else:
        #                if mvals[key] is not None:
        #                    multi_string = "%s, %s" %\
        #                        (multi_string, mvals[key])
        #                else:
        #                    multi_string = "%s, " % (multi_string)
        #    if multiple_values:
        #        dvals.append((multi_string, columns[cid][1]))

        # data.append(dvals)

    # Sort the list according to timestamp
    # data.sort(key=lambda x: x[time_idx][0], reverse=True)
    print json.dumps(data)


if __name__ == '__main__':
    CFG_FILE = "./config/policy.cfg"

    # Read the configs
    POLICY_CONFIG = ConfigParser.ConfigParser()
    POLICY_CONFIG.read(CFG_FILE)

    print "Content-Type: application/json charset=utf-8"
    print ""

    get_data(POLICY_CONFIG)
