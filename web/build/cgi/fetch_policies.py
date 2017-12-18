#!/usr/bin/env python
# Fetch the policies from the database
import os
import cgi
import sys
import json
import requests
import ConfigParser
import xml.etree.ElementTree


def get_policies(config, cummunity):
    remote_user_str = "persistentid"
    remote_user = ""
    policies = []
    if remote_user_str in os.environ:
        remote_user = os.environ[remote_user_str]
    else:
        if config.get("AUTHENTICATION", "type") == "STANDALONE":
            remote_user = config.get("HTMLENV", "user")

    policy_url = "%s_%s" % (config.get("XMLDATABASE", "name"), community) +\
        "?query=//*[local-name()='policy'][@author='%s']" % remote_user
    response = requests.get(policy_url,
                            auth=(config.get("XMLDATABASE", "user"),
                                  config.get("XMLDATABASE", "pass")))

    if response.status_code == 200:
        response = "<policies>\n" + response.text + "</policies>\n"
        xml_policies = \
            xml.etree.ElementTree.ElementTree(
                xml.etree.ElementTree.fromstring(response))
        xml_files = []
        namespaces = config.get("XML_NAMESPACE", "namespacedef").split()
        ns = {}
        for namespace in namespaces:
            key, value = namespace.split("=")
            ns[key] = value.strip('"')
        for xml_node in xml_policies.getiterator():
            if xml_node.tag == "{%s}policy" % ns["xmlns:tns"]:
                policy = {}
                policy["uniqueid"] = xml_node.get("uniqueid")
            if xml_node.tag == "{%s}targets" % ns["xmlns:tns"]:
                for target in xml_node.findall("{%s}target" % ns["xmlns:tns"]):
                    for atgt in target.getiterator():
                        if atgt.tag == "{%s}site" % ns["xmlns:irodsns"]:
                            policy["type"] = "collection"
                            policy["irodssite"] = atgt.text
                        elif atgt.tag == "{%s}path" % ns["xmlns:irodsns"]:
                            policy["irodspath"] = atgt.text
                        elif atgt.tag == "{%s}persistentIdentifier" %\
                                ns["xmlns:tns"]:
                            policy["persistentIdentifier"] = atgt.text
                            policy["type"] = "pid"
                policies.append(policy)

    else:
        print "Problem fetching the policy from the database: ",\
            response.status_code
        print response.text
        sys.exit(response.status_code)

    print "Content-Type: application/json charset=utf-8"
    print ""
    print json.dumps(policies)


if __name__ == '__main__':
    cfgfile = "./config/policy.cfg"
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    fields = cgi.FieldStorage()
    community = fields['community'].value
    get_policies(config, community)
