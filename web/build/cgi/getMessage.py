#!/usr/bin/env python
import ConfigParser
import json
import sys


def getMessage(config):
    '''Function to get the base email message
    '''
    print 'Content-Type: application/json charset=utf-8'
    print ''

    msg_base = ''
    msg_subject_base = ''
    msg = ''
    subject = ''
    vals = json.load(sys.stdin)
    if (vals["approval"] == "approve"):
        msg_base = file(config.get("EMAIL", "accept_body"), 'r').read()
        msg_subject_base = file(config.get("EMAIL", "accept_subject"), 'r').read()
        msg = msg_base % (vals["role"], vals["community"])
        subject = msg_subject_base % (vals["community"], vals["role"])

    elif (vals["approval"] == "decline"):
        msg_base = file(config.get("EMAIL", "reject_body"), 'r').read()
        msg_subject_base = file(config.get("EMAIL", "reject_subject"), 'r').read()
        msg = msg_base % (vals["role"], vals["community"])
        subject = msg_subject_base % (vals["community"], vals["role"])

    elif (vals["approval"] == "close"):
        msg_base = file(config.get("EMAIL", "close_body"), 'r').read()
        msg_subject_base = file(config.get("EMAIL", "close_subject"), 'r').read()
        msg = msg_base % (vals["role"], vals["community"])
        subject = msg_subject_base % (vals["role"], vals["community"])

    email = {}
    email["msg"] = msg
    email["subject"] = subject
    print json.dumps(email)

if __name__ == '__main__':
    cfgfile = './config/policy.cfg'
    config = ConfigParser.ConfigParser()
    config.read(cfgfile)
    getMessage(config)
