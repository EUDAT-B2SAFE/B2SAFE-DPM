#!/usr/bin/env python

__author__ = 'Willem Elbers (MPI-TLA) <willem.elbers@mpi.nl> \
              Claudio Cacciari (Cineca) <c.cacciari@cineca.it>'

import sys
import argparse
import urllib2
import json
import logging
import logging.handlers 
import os
import glob
from crontab import CronTab
from croniter import croniter
from datetime import datetime
from datetime import date
from PolicyParser import PolicyParser
from PolicyRunner import PolicyRunner
from ConfigLoader import ConfigLoader
from ServerConnector import ServerConnector

logger = logging.getLogger('PolicyManager')

def parseOverHttp(args):
    """
    Query the DPM server to fetch a list of policies to execute
    """
    debug = args.verbose
    config = ConfigLoader(args.config)
    setLoggingSystem(config, debug)
    logger.info('Getting the policies via HTTP')
    queryDpm(args, config)

def parseFromFile(args):
    """
    Parse a local policy file to execute
    """
    test = args.test
    debug = args.verbose
    policypath = args.path
    schemapath = args.schemapath
    config = ConfigLoader(args.config)
    setLoggingSystem(config, debug)
    logger.info('Getting the policies via file %s', policypath)
    mapFilename = config.SectionMap('AccountMapping')['file']
    usermap = loadUserMap(mapFilename)  
    pParser = PolicyParser(None, test, 'PolicyManager', debug)
    xmlSchemaDoc = pParser.parseXmlSchema(None, schemapath)
    pParser.parseFromFile(policypath, xmlSchemaDoc)
    runPolicy(pParser.policy, usermap, test, 'PolicyManager', debug)

def loadUserMap(mapFilename):
    """
    Load the file of account mapping into a dictionary
    """
    logger.info('Loading the account mapping file: ' + mapFilename)
    try:
        with open(mapFilename, "r") as jsonFile:
            try:
                usermap = json.load(jsonFile)
            except (ValueError) as ve:
                logger.exception('the file ' + mapFilename + ' is not a valid json.')
                sys.exit(1)
    except (IOError, OSError) as e:
        logger.exception('the file ' + mapFilename + ' is not readable.')
        sys.exit(1)

    return usermap

def cleanScheduledPolicies(args):
    """
    Remove expired (or all) policies from crontab
    """
    debug = args.verbose
    config = ConfigLoader(args.config)
    setLoggingSystem(config, debug)
    logger.info('Start to remove old policies')
    cron = CronTab(user=True)
    jobList = []
    for job in cron:
        logger.debug('checking job command: %s', job.command)
        if job.command.startswith("export clientUserName") \
        and 'irule' in job.command:
            if (args.all):
                jobList.append(job)
            else:
                logger.debug('checking if the job is expired')
                schedule = job.schedule()
                datetime = schedule.get_next()
                if datetime.year > (date.today()).year:
                    logger.debug('removing the expired job')
                    jobList.append(job)

    for job in jobList:
        logger.info('removing the job ' + job.comment)
        cron.remove(job)
        # remove rule files from the local file system
        path = os.path.join(os.path.dirname(sys.path[0]), 'rules')
        rulePath = path + '/replicate.' + job.comment + '.r'
        logger.debug('Removing the file: ' + rulePath)
        try:
            os.remove(rulePath)
            logger.debug('File removed')
        except OSError, e:
            logger.exception('Impossible to remove the file')

    cron.write_to_user(user=True)
    logger.info('Policies removed')

def runPolicy(policy, usermap, test, loggerName, debug):

    runner = PolicyRunner(usermap, test, loggerName, debug)
    runner.runPolicy(policy)

def queryDpm(args, config, begin_date=None, end_date=None):

    #load properties from configuration
    username = config.SectionMap('DpmServer')['username']
    password = config.SectionMap('DpmServer')['password']
    server = config.SectionMap('DpmServer')['hostname']
    url = '%s://%s%s?community_id=%s&site=%s' % \
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
    logger.info('Listing policies [%s]' % url)
    authinfo = urllib2.HTTPPasswordMgrWithDefaultRealm()
    authinfo.add_password(None, server, username, password)
    handler = urllib2.HTTPBasicAuthHandler(authinfo)
    myopener = urllib2.build_opener(handler)
    opened = urllib2.install_opener(myopener)
    response = urllib2.urlopen(url)

    json_data = response.read()

    if json_data is None:
        logger.info('No response found')
    else:
        _json = json.loads(json_data)
        logger.info('Found %d policies' % (len(_json)))
        for entry in _json:
            url = str(entry[0])
            ts = entry[1]
            checksum_value = str(entry[2])
            checksum_algo = str(entry[3])

            if not url.endswith('.html'):
                logger.info('Processing policy: %s [%s, %s, %s]', url, ts, 
                            checksum_value, checksum_algo)
                pParser = PolicyParser(None, args.test, 'PolicyManager', args.verbose)
                xmlSchemaDoc = pParser.parseXmlSchema(args.schemaurl, args.schemapath)
                pParser.parseFromUrl(url, xmlSchemaDoc, checksum_algo, checksum_value)
                if not pParser.policy is None:
                    mapFilename = config.SectionMap('AccountMapping')['file']
                    usermap = loadUserMap(mapFilename)
                    runPolicy(pParser.policy, usermap, args.test, 'PolicyManager', args.verbose)
            else:
                logger.error('invalid policy location [%s]', url)

def updatePolicyStatus(args):
    """
    Update the status of all the policies in the central DB
    """
    
    debug = args.verbose
    config = ConfigLoader(args.config)
    setLoggingSystem(config, debug)
    logger.info('Start to update the status of the policies') 
    loggerName = 'PolicyManager'
    conn = ServerConnector(args.config, args.test, loggerName, debug)
    policies = conn.listPolicies()
    if policies is not None:
        for entry in policies:
            url = str(entry[0])
            ts = entry[1]
            checksum_value = str(entry[2])
            checksum_algo = str(entry[3])

            if not url.endswith('.html'):
                logger.info('Processing policy: %s [%s, %s, %s]', url, ts,
                            checksum_value, checksum_algo)
                pParser = PolicyParser(None, args.test, 'PolicyManager', debug)
                xmlSchemaDoc = pParser.parseXmlSchema(args.schemaurl, args.schemapath)
                pParser.parseFromUrl(url, xmlSchemaDoc, checksum_algo, checksum_value)
                if not pParser.policy is None:
                    id = pParser.policy.policyId
                    state = getPolicyStatus(id, debug)
                    conn.updateStatus(id, state)
            else:
                logger.error('invalid policy location [%s]', url)

def getPolicyStatus(id, debug):
    """
    Get the status of a policy [QUEUED, RUNNING, DONE, FAILED]
    """
 
    rulePath = os.path.join(os.path.dirname(sys.path[0]), 'rules')
    ruleFiles = glob.glob(rulePath +'/replicate.' + id + '*')
    resPath = os.path.join(os.path.dirname(sys.path[0]), 'output')
    resFiles = glob.glob(resPath +'/response.' + id + '*')
    if ruleFiles is not None and len(ruleFiles) > 0:
        status = 'QUEUED'
        if resFiles is not None and len(resFiles) > 0:
            status = 'DONE'
    else:
        status = 'FAILED'
        if resFiles is not None and len(resFiles) > 0:
            status = 'DONE'

    return status


def setLoggingSystem(config, debug):
    """
    Initialize the logging system
    """

    logfilepath = config.SectionMap('Logging')['logfile']
    loglevel = config.SectionMap('Logging')['loglevel']
    ll = {'INFO': logging.INFO, 'DEBUG': logging.DEBUG, \
          'ERROR': logging.ERROR, 'WARNING': logging.WARNING}
    logger.setLevel(ll[loglevel])
    if (debug): 
        logger.setLevel(logging.DEBUG)
    rfh = logging.handlers.RotatingFileHandler(logfilepath, 
                                               maxBytes=6000000,
                                               backupCount=9)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: '
                                + '[%(funcName)s] %(message)s')
    rfh.setFormatter(formatter)
    logger.addHandler(rfh)


def main():
    argp = argparse.ArgumentParser(description="EUDAT Data Policy Manager (DPM) client")
    argp.add_argument('-T', '--type', choices=['periodic', 'hook', 'cli'], required=True,
                        help='Specify if this invokation is triggered periodic or via an irods hook')
    argp.add_argument('-t', '--test', action='store_true', required=False, 
                        help='Test the DPM client (does not trigger an actual replication)')
    argp.add_argument('-v', '--verbose', action='store_true', required=False, 
                        help='Run the DPM client in verbose mode')
    argp.add_argument('-c', '--config', required=True, help='Path to config.ini')
    group = argp.add_mutually_exclusive_group(required=True)
    group.add_argument('-su', '--schemaurl', help='The policy schema URL', nargs=1)
    group.add_argument('-sp', '--schemapath', help='Path to the policy schema file', nargs=1)
    
    subparsers = argp.add_subparsers(help='sub-command help')    
    parser_url = subparsers.add_parser('http', help='Fetch policy over http')
    parser_url.set_defaults(func=parseOverHttp)

    parser_file = subparsers.add_parser('file', help='Fetch policy from a file')
    parser_file.add_argument('-p', '--path', required=True, help='Path to the policy file')
    parser_file.set_defaults(func=parseFromFile)

    parser_clean = subparsers.add_parser('clean', help='Clean the expired policies from crontab')
    parser_clean.add_argument('-a', '--all', action='store_true', help='clean all the policies')
    parser_clean.set_defaults(func=cleanScheduledPolicies)

    parser_update = subparsers.add_parser('update', help='Update policy status in the central DB')
    parser_update.set_defaults(func=updatePolicyStatus)

    args = argp.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
