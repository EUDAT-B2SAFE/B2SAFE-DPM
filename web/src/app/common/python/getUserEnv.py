#!/usr/bin/env python
import cgi
import os
import sys
import ConfigParser

def getUEnv():
    '''Function to get the user environment variable
    '''
    username = ''
    if (os.environ.has_key('REMOTE_USER')):
        username = os.environ['REMOTE_USER']
    else:
        # Just for testing put a dummy username in case the REMOTE_USER
        # env variable doesn't exist
        cfgfile = './config/policy_schema.cfg'
        config = ConfigParser.ConfigParser()
        config.read(cfgfile)
        username = config.get("HTMLENV", "user").strip()

    print 'Content-Type: text/html'
    print ''
    print username

if __name__ == '__main__':
    getUEnv()
