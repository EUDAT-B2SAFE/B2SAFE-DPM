#! /usr/bin/env python
"""
Load the XML policy into a JSON object
"""

import sys
import json
import time
import cgi
import ConfigParser
import requests
import xml.etree.ElementTree


def fill_targets(node):
    '''Return the parameters for the targets'''
    targets = {}
    target_list = []
    for child in node:
        if "actions" in child.tag:
            for cchild in child:
                if "action" in child.tag:
                    for ccchild in cchild:
                        if "targets" in ccchild.tag:
                            for cccchild in ccchild:
                                if "target" in cccchild.tag:
                                    target = {"organisation": {"name": "EUDAT"},
                                              "system": {"name": "iRODS"},
                                              "resource": {"name": ""},
                                              "hostname": {"name": ""}}
                                    key_id = cccchild.attrib["id"]
                                    for ccccchild in cccchild:
                                        if "location" in ccccchild.tag:
                                            for cccccchild in ccccchild:
                                                if "site" in cccccchild.tag:
                                                    target["hostname"] = {"name": cccccchild.text}
                                                if "path" in cccccchild.tag:
                                                    target["identifier"] = {"name": cccccchild.text}
                                                    target["type"] = {"name": "collection"}
                                                if "persistentIdentifier" in cccccchild.tag:
                                                    target["identifier"] = {"name": cccccchild.text}
                                                    target["type"] = {"name": "pid"}
                                    targets[key_id] = target

    keys = [int(x) for x in targets.keys()]
    keys.sort()
    for akey in keys:
        target_list.append(targets["%s" % akey])
    return target_list


def fill_action(node, policy):
    '''Return the parameters for the action'''
    for child in node:
        if "actions" in child.tag:
            for cchild in child:
                if "action" in cchild.tag:
                    for ccchild in cchild:
                        if "type" in ccchild.tag:
                            policy["type"] = {"name": ccchild.text}
                        if "trigger" in ccchild.tag:
                            for cccchild in ccchild:
                                if "runonce" in cccchild.tag:
                                    policy["trigger"] = {"name": "immediately"}
                                    policy["trigger_period"] = {"name": ""}
                                    policy["trigger_date"] = {"name": ""}
                                    policy["dateString"] = ""
                                elif "time" in cccchild.tag:
                                    try:
                                        ttime = time.strptime(cccchild.text,
                                                              "%M %H %d %m * %Y")
                                        date_string = time.strftime("%Y-%M-%dT%H:%MZ",
                                                                    ttime)
                                        policy["trigger"] = {"name": "date/time"}
                                        policy["trigger_period"] = {"name": ""}
                                        policy["trigger_date"] = {"name": "date"}
                                        policy["dateString"] = date_string
                                    except ValueError:
                                        policy["trigger"] = {"name": "date/time"}
                                        policy["trigger_period"] = {"name":
                                                                    cccchild.text}
                                        trigger_date = ""
                                        if cccchild.text == "* * * * * *":
                                            trigger_date = "minute"
                                        if cccchild.text == "0 * * * * *":
                                            trigger_date = "hourly"
                                        if cccchild.text == "0 0 * * * *":
                                            trigger_date = "daily"
                                        if cccchild.text == "0 0 * * 0 *":
                                            trigger_date = "weekly"
                                        if cccchild.text == "0 0 1 * * *":
                                            trigger_date = "monthly"
                                        if cccchild.text == "0 0 1 1 * *":
                                            trigger_date = "yearly"
                                        policy["trigger_date"] = {"name": trigger_date}
                                        policy["dateString"] = ""
    return policy


def fill_sources(node):
    '''Return the parameters for the sources'''
    sources = {}
    source_list = []
    for child in node:
        if "dataset" in child.tag:
            for cchild in child:
                if "collection" in cchild.tag:
                    source = {"organisation": {"name": "EUDAT"},
                              "system": {"name": "iRODS"},
                              "resource": {"name": ""},
                              "hostname": {"name": ""}}
                    key_id = cchild.attrib["id"]
                    for ccchild in cchild:
                        if "location" in ccchild.tag:
                            for cccchild in ccchild:
                                if "site" in cccchild.tag:
                                    source["hostname"] = {"name": cccchild.text}
                                if "path" in cccchild.tag:
                                    source["identifier"] = {"name": cccchild.text}
                                    source["type"] = {"name": "collection"}
                                if "persistentIdentifier" in cccchild.tag:
                                    source["identifier"] = {"name": cccchild.text}
                                    source["type"] = {"name": "pid"}
                    sources[key_id] = source

    keys = [int(x) for x in sources.keys()]
    keys.sort()
    for akey in keys:
        source_list.append(sources["%s" % akey])
    return source_list


def fill_policy_params(node):
    '''Return the policy paramters in the JSON object'''
    params = {}
    params["author"] = node.attrib["author"]
    params["name"] = node.attrib["name"]
    params["uuid"] = node.attrib["uniqueid"]
    params["version"] = node.attrib["version"]
    params["community"] = node.attrib["community"]
    return params


def load_policy(cfg, uuid, url):
    '''Read the XML policy from the database and load into a JSON object'''
    json_policy = {}
    xml_policy = ''

    # Create the URL for the policy xml file
    policy_url = url + "/policy_%s.xml" % (uuid)
    response = requests.get(policy_url,
                            auth=(cfg.get("XMLDATABASE", "user"),
                                  cfg.get("XMLDATABASE", "pass")))

    if response.status_code == 200:
        xml_policy = response.text
    else:
        print "Problem fetching the policy from the database: ",\
            response.status_code
        print response.text
        sys.exit(response.status_code)

    if len(xml_policy) > 0:
        root_node = xml.etree.ElementTree.fromstring(xml_policy)
        json_policy = fill_policy_params(root_node)
        sources = fill_sources(root_node)
        json_policy["sources"] = sources
        targets = fill_targets(root_node)
        json_policy["targets"] = targets
        json_policy = fill_action(root_node, json_policy)

    print "Content-Type: application/json charset=utf-8"
    print ""
    print json.dumps(json_policy)


if __name__ == '__main__':

    cfg_file = "./config/policy.cfg"
    fields = cgi.FieldStorage()

    uuid = fields["uuid"].value
    url = fields["policyURL"].value
    # uuid = "26b4e27c-7237-4380-a398-22c4ecf6dba3"
    # url = "http://localhost:8984/rest/policy_community_clarin"
    # Read the configs

    # Read the configs
    config = ConfigParser.ConfigParser()
    config.read(cfg_file)

    load_policy(config, uuid, url)
