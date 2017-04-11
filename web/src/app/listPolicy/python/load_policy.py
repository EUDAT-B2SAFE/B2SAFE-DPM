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
    for child in node.iter():
        if "target" in child.tag and "targets" not in child.tag:
            target = {"organisation": {"name": "EUDAT"},
                      "system": {"name": "iRODS"}, "resource": {"name": ""},
                      "hostname": {"name": ""}}
            key_id = child.attrib["id"]
            for cchild in child.iter():
                if "site" in cchild.tag:
                    target["hostname"] = {"name": cchild.text}
                if "path" in cchild.tag:
                    target["identifier"] = {"name": cchild.text}
                    target["type"] = {"name": "collection"}
                if "persistentIdentifier" in cchild.tag:
                    target["identifier"] = {"name": cchild.text}
                    target["type"] = {"name": "pid"}
            targets[key_id] = target

    keys = [int(x) for x in targets.keys()]
    keys.sort()
    for akey in keys:
        target_list.append(targets["%s" % akey])
    return target_list


def fill_action(node, policy):
    '''Return the parameters for the action'''
    for child in node.iter():
        if "action" in child.tag:
            for cchild in child.iter():
                if "type" in cchild.tag:
                    policy["type"] = {"name": cchild.text}
                if "trigger" in cchild.tag:
                    for ccchild in cchild.iter():
                        if "runonce" in ccchild.tag:
                            policy["trigger"] = {"name": "immediately"}
                            policy["trigger_period"] = {"name": ""}
                            policy["trigger_date"] = {"name": ""}
                            policy["dateString"] = ""
                        elif "time" in ccchild.tag:
                            try:
                                ttime = time.strptime(ccchild.text,
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
                                                            ccchild.text}
                                trigger_date = ""
                                if ccchild.text == "* * * * * *":
                                    trigger_date = "minute"
                                if ccchild.text == "0 * * * * *":
                                    trigger_date = "hourly"
                                if ccchild.text == "0 0 * * * *":
                                    trigger_date = "daily"
                                if ccchild.text == "0 0 * * 0 *":
                                    trigger_date = "weekly"
                                if ccchild.text == "0 0 1 * * *":
                                    trigger_date = "monthly"
                                if ccchild.text == "0 0 1 1 * *":
                                    trigger_date = "yearly"
                                policy["trigger_date"] = {"name": trigger_date}
                                policy["dateString"] = ""
    return policy


def fill_sources(node):
    '''Return the parameters for the sources'''
    sources = {}
    source_list = []
    for child in node.iter():
        if "collection" in child.tag:
            source = {"organisation": {"name": "EUDAT"},
                      "system": {"name": "iRODS"}, "resource": {"name": ""},
                      "hostname": {"name": ""}}
            key_id = child.attrib["id"]
            for cchild in child.iter():
                if "site" in cchild.tag:
                    source["hostname"] = {"name": cchild.text}
                if "path" in cchild.tag:
                    source["identifier"] = {"name": cchild.text}
                    source["type"] = {"name": "collection"}
                if "persistentIdentifier" in cchild.tag:
                    source["identifier"] = {"name": cchild.text}
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

    # Read the configs
    config = ConfigParser.ConfigParser()
    config.read(cfg_file)

    load_policy(config, uuid, url)
