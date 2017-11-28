#! /usr/bin/env python
"""
Module to query the basex database and get the status information
"""

import ConfigParser
import xml.etree.ElementTree
import json
import os
import sys
import csv
import sqlite3
import requests


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
                        and "status_" in xml_node.text):
                    community = xml_node.text.strip().split("_")[-1]
                    xml_databases[community] = xml_node.text.strip()
    else:
        print "Problem querying the database: ", response.status_code
        print response.text
        sys.exit(response.status_code)

    return xml_databases


def query_db(config):
    '''Query the database and return the list of json objects'''

    tags = {"{http://eudat.eu/2016/policy-status}timestamp": "log_timestamp",
            "{http://eudat.eu/2016/policy-status}status": "log_state",
            "{http://eudat.eu/2016/policy-status}overall": "log_state_overall",
            "{http://eudat.eu/2016/policy-status}name": "policy_name",
            "{http://eudat.eu/2016/policy-status}version": "policy_version",
            "policy": "{http://eudat.eu/2016/policy-status}policy"}

    username = get_user(config)
    communities = get_communities(config, username)

    status_list = []
    basex_url = config.get("XMLDATABASE", "root_name")
    databases = get_databases(basex_url, config)

    for community in communities:
        if community in databases:
            url = basex_url.strip() + "/%s" % databases[community]
            response = requests.get(url,
                                    auth=(config.get("XMLDATABASE", "user"),
                                          config.get("XMLDATABASE", "pass")))

            if response.status_code == 200:
                response_string = \
                    xml.etree.ElementTree.fromstring(response.text)
                xml_response = \
                    xml.etree.ElementTree.ElementTree(response_string)

                xml_files = []
                for xml_node in xml_response.getiterator():
                    if (xml_node.text is not None
                            and len(xml_node.text.strip()) > 0):
                        xml_files.append(xml_node.text.strip())

                for policy_status in xml_files:
                    url_query = "%s/%s?query=//*[local-name()='policy']" % \
                            (url, policy_status)
                    response = \
                        requests.get(url_query,
                                     auth=(config.get("XMLDATABASE", "user"),
                                           config.get("XMLDATABASE", "pass")))
                    if response.status_code == 200:
                        response_string = \
                            xml.etree.ElementTree.fromstring(response.text)
                        status_obj = {}
                        if response_string.tag == tags["policy"]:
                            status_obj["policy_uniqueid"] = \
                                    response_string.attrib.get("uniqueid")
                        for an_elem in response_string.getchildren():
                            tag_name = tags.get(an_elem.tag)
                            if tag_name is not None:
                                if tag_name in tags and tags[tag_name] == "log_state":
                                    children = an_elem.getchildren()
                                    for achild in children:
                                        if tags[achild.tag_name] == "log_state_overall":
                                            status_obj[tag_name] = achild.text.strip()
                                else:
                                    status_obj[tag_name] = an_elem.text.strip()
                        status_list.append(status_obj)
    return status_list


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


def get_user(config):
    '''Get the user from the environment'''
    username = ''
    if config.get("AUTHENTICATION", "type") == "AAI":
        username = os.environ["persistentid"]
    elif config.get("AUTHENTICATION", "type") == "STANDALONE":
        if config.has_option("HTMLENV", "user"):
            username = config.get("HTMLENV", "user")
    return username


def get_status(config):
    '''Return the status information for the policies'''
    status_obj = {}
    status_cols = [config.get("LOG_SCHEMA", "name"),
                   config.get("LOG_SCHEMA", "version"),
                   config.get("LOG_SCHEMA", "uniqueid"),
                   config.get("LOG_SCHEMA", "state"),
                   config.get("LOG_SCHEMA", "timestamp")]

    status_list = query_db(config)
    status_obj["columns"] = status_cols
    status_obj["data"] = status_list
    print json.dumps(status_obj)


if __name__ == '__main__':
    CFG_FILE = './config/policy.cfg'

    # Read the configs
    POLICY_CONFIG = ConfigParser.ConfigParser()
    POLICY_CONFIG.read(CFG_FILE)

    print "Content-Type: application/json charset=utf-8"
    print ""

    get_status(POLICY_CONFIG)
