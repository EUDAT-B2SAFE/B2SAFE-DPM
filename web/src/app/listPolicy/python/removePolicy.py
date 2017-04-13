#!/usr/bin/env python
import json
import sys
import ConfigParser
import xml.etree.ElementTree
import time
import md5
import requests


def removePol(config):
    '''Function to remove the policy
    '''

    # Read the input
    data = {}
    data = json.load(sys.stdin)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    ckval = md5.md5(data["policy"])

    # Create the XML document
    nsurl = "http://eudat.eu/2016/policy-status"
    root = xml.etree.ElementTree.Element("ns0:policy",
                                         attrib={"xmlns:ns0": nsurl,
                                                 "uniqueid": data["uuid"]})
    name = xml.etree.ElementTree.SubElement(root, "ns0:name")
    name.text = data["name"]
    version = xml.etree.ElementTree.SubElement(root, "ns0:version")
    version.text = data["version"]
    checksum = xml.etree.ElementTree.SubElement(root, "ns0:checksum",
                                                attrib={"method": "MD5"})
    checksum.text = ckval.hexdigest()
    status = xml.etree.ElementTree.SubElement(root, "ns0:status")
    overall = xml.etree.ElementTree.SubElement(status, "ns0:overall")
    overall.text = "REJECTED"
    details = xml.etree.ElementTree.SubElement(status, "ns0:details")
    timestamp = xml.etree.ElementTree.SubElement(root, "ns0:timestamp")
    timestamp.text = now

    policy_status = xml.etree.ElementTree.tostring(root)
    policy_name = "status_%s.xml" % data["uuid"]
    status_url = "%s_%s/%s" % (config.get("XMLDATABASE", "status_name"),
                               data["community"], policy_name)

    resp = requests.put(status_url, data=policy_status,
                        auth=(config.get("XMLDATABASE", "user"),
                              config.get("XMLDATABASE", "pass")))
    if resp.status_code != 201:
        print "Problem storing the status in the XML database: ",\
            resp.status_code
        print resp.text
        sys.exit(-100)


if __name__ == '__main__':
    cfgfile = 'config/policy.cfg'
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    print "Content-Type: html/text"
    print ""
    removePol(config)
