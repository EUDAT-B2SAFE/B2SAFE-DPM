#! /usr/bin/env python
"""
Module to query the basex database and get the status information
"""

import ConfigParser
import xml.etree.ElementTree
import json
import requests


def query_db(config):
    '''Query the database and return the list of json objects'''

    tags = {"{http://eudat.eu/2016/policy-status}timestamp": "log_timestamp",
            "{http://eudat.eu/2016/policy-status}status": "log_state",
            "{http://eudat.eu/2016/policy-status}name": "policy_name",
            "{http://eudat.eu/2016/policy-status}version": "policy_version",
            "policy": "{http://eudat.eu/2016/policy-status}policy"}

    url = config.get("XMLDATABASE", "status_name")
    response = requests.get(url, auth=(config.get("XMLDATABASE", "user"),
                                       config.get("XMLDATABASE", "pass")))
    status_list = []

    if response.status_code == 200:
        response_string = xml.etree.ElementTree.fromstring(response.text)
        xml_response = xml.etree.ElementTree.ElementTree(response_string)

        xml_files = []
        for xml_node in xml_response.getiterator():
            if len(xml_node.text.strip()) > 0:
                xml_files.append(xml_node.text.strip())

        for policy_status in xml_files:
            url_query = \
                    "%s/%s?query=//*[local-name()='policy']" % \
                    (url, policy_status)
            response = requests.get(url_query,
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
                        status_obj[tag_name] = an_elem.text.strip()
                status_list.append(status_obj)
    return status_list


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
