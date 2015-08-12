#!/usr/bin/env python

__author__ = 'Willem Elbers, MPI-TLA, willem.elbers@mpi.nl'

import argparse
import urllib2
import json
from PolicyParser import PolicyParser
from PolicyRunner import PolicyRunner
from ConfigLoader import ConfigLoader

def parseOverHttp(args):
    """
    Query the DPM server to fetch a list of policies to execute
    """
    debug = args.verbose
    if debug:
        print 'parseOverHttp()'

    queryDpm(args)

def parseFromFile(args):
    """
    Parse a local policy file to execute
    """
    test = args.test
    debug = args.verbose
    policypath = args.path
    schemapath = args.schemapath

    if debug:
        print 'parseFromFile(policypath=%s,schemapath=%s,test=%s,debug=%s)' % (policypath,schemapath,test,debug)

    pParser = PolicyParser(None, test, debug)
    xmlSchemaDoc = pParser.parseXmlSchema(None, schemapath)
    pParser.parseFromFile(policypath, xmlSchemaDoc)
    runPolicy(pParser.policy, test, debug)


def runPolicy(policy, test, debug):
    runner = PolicyRunner(test, debug)
    runner.runPolicy(policy)

def queryDpm(args, begin_date=None, end_date=None):
    #load properties from configuration
    config = ConfigLoader(args.config)
    username = config.SectionMap('DpmServer')['username']
    password = config.SectionMap('DpmServer')['password']
    server = config.SectionMap('DpmServer')['hostname']
    url = '%s://%s%s?community_id=%s&center_id=%s' % \
          (config.SectionMap('DpmServer')['scheme'],
           config.SectionMap('DpmServer')['hostname'],
           config.SectionMap('DpmServer')['path'],
           config.SectionMap('Community')['id'],
           config.SectionMap('Center')['id'])

    #apply parameters
    if not begin_date is None:
        url += '&begin_date=%s' % begin_date
    if not end_date is None:
        url += '&end_date=%s' % end_date

    #start interaction with DPM server
    print 'Listing policies [%s]' % url
    authinfo = urllib2.HTTPPasswordMgrWithDefaultRealm()
    authinfo.add_password(None, server, username, password)
    handler = urllib2.HTTPBasicAuthHandler(authinfo)
    myopener = urllib2.build_opener(handler)
    opened = urllib2.install_opener(myopener)
    response = urllib2.urlopen(url)

    json_data = response.read()

    if json_data is None:
        print 'No response found'
    else:
        _json = json.loads(json_data)
        print 'Found %d policies' % (len(_json))
        for entry in _json:
            url = str(entry[0])
            ts = entry[1]
            checksum_value = str(entry[2])
            checksum_algo = str(entry[3])

            if not url.endswith('.html'):
                print '****************************************'
                print 'Processing policy: %s [%s, %s, %s]' % (url, ts, checksum_value, checksum_algo)

                pParser = PolicyParser(None, args.test, args.verbose)
                xmlSchemaDoc = pParser.parseXmlSchema(args.schemaurl, args.schemapath)
                pParser.parseFromUrl(url, xmlSchemaDoc, checksum_algo, checksum_value)
                if not pParser.policy is None:
                    runPolicy(pParser.policy, args.test, args.verbose)
            else:
                print 'invalid policy location [%s]' % url
        print '****************************************\n'


def main():
    argp = argparse.ArgumentParser(description="EUDAT Data Policy Manager (DPM) client")
    argp.add_argument('-T', '--type', choices=['periodic', 'hook', 'cli'], required=True,
                        help='Specify if this invokation is triggered periodic or via an irods hook')
    argp.add_argument('-t', '--test', action='store_true', required=False, 
                        help='Test the DPM client (does not trigger an actual replication)')
    argp.add_argument('-v', '--verbose', action='store_true', required=False, 
                        help='Run the DPM client in verbose mode')
    group = argp.add_mutually_exclusive_group(required=True)
    group.add_argument('-su', '--schemaurl', help='The policy schema URL', nargs=1)
    group.add_argument('-sp', '--schemapath', help='Path to the policy schema file', nargs=1)
    
    subparsers = argp.add_subparsers(help='sub-command help')    
    parser_url = subparsers.add_parser('http', help='Fetch policy over http')
    parser_url.add_argument('-c', '--config', required=True, help='Path to config.ini')
    parser_url.set_defaults(func=parseOverHttp)

    parser_file = subparsers.add_parser('file', help='Fetch policy from a file')
    parser_file.add_argument('-p', '--path', required=True, help='Path to the policy file')
    parser_file.set_defaults(func=parseFromFile)

    args = argp.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()