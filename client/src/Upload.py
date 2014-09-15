#!/usr/bin/env python

__author__ = 'Willem Elbers, MPI-TLA, willem.elbers@mpi.nl'

import argparse
import urllib2
import urllib
import time
from ConfigLoader import ConfigParser

def upload(args):
    #load properties from configuration
    config = ConfigParser(args.config)
    username = config.SectionMap('DpmServer')['username']
    password = config.SectionMap('DpmServer')['password']
    server = config.SectionMap('DpmServer')['hostname']
    url = '%s://%s%s?community_id=%s&center_id=%s' % \
          (config.SectionMap('DpmServer')['scheme'],
           config.SectionMap('DpmServer')['hostname'],
           config.SectionMap('DpmServer')['uploadpath'])

    #Extract the policy id and the policy execution status from the policy name
    state = fetchPolicyState(args.destination)
    policyId = fetchPolicyState(args.destination)
    #Get the current UNIX timestamp
    timestamp = time.time()

    #Prepare server connection
    authinfo = urllib2.HTTPPasswordMgrWithDefaultRealm()
    authinfo.add_password(None, server, username, password)
    handler = urllib2.HTTPBasicAuthHandler(authinfo)
    myopener = urllib2.build_opener(handler)
    opened = urllib2.install_opener(myopener)

    # Upload information
    data = urllib.urlencode({'id': policyId, 'state': state, 'timestamp': timestamp, 'center': config.SectionMap('Center')['id'], 'community': config.SectionMap('Community')['id']})
    print 'url: %s, data: %s' % (args.url, data)
    req = urllib2.Request(url=url, data=data)
    response = urllib2.urlopen(req).read()
    print response

def fetchPolicyState(destination):
    segments = destination.split('.')
    if segments[-1].lower() == 'replicate':
        return 'RUNNING'
    elif segments[-1].lower() == 'success':
        return 'FINISHED'
    else:
        return 'FAILED'

def fetchPolicyId(destination):
    segments = destination.split('.')
    return segments[0]


def main():
    argp = argparse.ArgumentParser(description="EUDAT Data Policy Manager data upload script")
    argp.add_argument('-c', '--config', required=True, help='Path to config.ini')
    argp.add_argument('-s', '--source', required=False, help='Object before rename')
    argp.add_argument('-d', '--destination', required=False, help='Object after rename')

    args = argp.parse_args()
    upload(args)

if __name__ == '__main__':
    main()
