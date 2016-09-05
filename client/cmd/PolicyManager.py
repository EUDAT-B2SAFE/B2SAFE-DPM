#!/usr/bin/env python

__author__ = 'Willem Elbers (MPI-TLA) <willem.elbers@mpi.nl>, \
              Claudio Cacciari (Cineca) <c.cacciari@cineca.it>, \
              Adil Hasan (SIGMA) <adilhasan2@gmail.com>'

import sys
import argparse
import requests
import json
import logging
import logging.handlers
import os
import glob
import xmltodict
import time

from crontab import CronTab
from datetime import datetime
from datetime import date
from PolicyParser import PolicyParser
from PolicyRunner import PolicyRunner
from ConfigLoader import ConfigLoader
from ServerConnector import ServerConnector

# TODO define a proper Policy Manager class

# eabling logging
logger = logging.getLogger('PolicyManager')
polNs = 'http://eudat.eu/2013/policy'
staNs = 'http://eudat.eu/2016/policy-status'

def parseOverHttp(args):
    """
    Query the DPM server to fetch a list of policies to execute
   
    @type  args: list of objects
    @param args: list of input arguments
    """
    debug = args.verbose
    config = ConfigLoader(args.config)
    setLoggingSystem(config, debug)
    logger.info('Getting the policies via HTTP')
    # download the policies from the DB and execute the related B2SAFE workflow
    queryDpm(args, config)

def parseFromFile(args):
    """
    Parse a local policy file to execute
    
    @type  args: list of objects
    @param args: list of input arguments
    """
    test = args.test
    debug = args.verbose
    policypath = args.path
    config = ConfigLoader(args.config)
    setLoggingSystem(config, debug)
    # get the policy schema path
    schemapath = config.SectionMap('Schemas')['policies']
    logger.info('Getting the policy schema via file %s', policypath)
    # get the user account mapping
    mapFilename = config.SectionMap('AccountMapping')['file']
    usermap = loadUserMap(mapFilename)
    # load the policy schema
    pParser = PolicyParser(None, test, 'PolicyManager', debug)
    xmlSchemaDoc = pParser.parseXmlSchema(None, [schemapath])
    # load the policy doc and validate it
    pParser.parseFromFile(policypath, xmlSchemaDoc)
    # execute the policy as a B2SAFE workflow
    runPolicy(pParser.policy, usermap, test, 'PolicyManager', debug)


def loadUserMap(mapFilename):
    """
    Load the file of account mapping into a dictionary
       
    @type  mapFilename: string
    @param mapFilename: A file path to the json user mapping configuration
    @rtype:             dictionary
    @return:            A dictionary containing EUDAT global username as keys
                        and local B2SAFE username as values
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

    @type  args: list of objects
    @param args: The list of input parameters
    """
    debug = args.verbose
    config = ConfigLoader(args.config)
    setLoggingSystem(config, debug)
    logger.info('Start to remove old policies')
    cron = CronTab(user=True)
    jobList = []
    for job in cron:
        logger.debug('checking job command: %s', job.command)
        # find the scheduled cron jobs based on iRODS icommand keywords
        if job.command.startswith("export clientUserName") \
                and 'irule' in job.command:
            if args.all:
                # add all the scheduled cron jobs to the remove list
                jobList.append(job)
            else:
                # add only the expired cron jobs to the remove list
                logger.debug('checking if the job is expired')
                schedule = job.schedule()
                # get the date of the next expected execution of the job
                datetime = schedule.get_next()
                # the expiration is decided based on the year only
                if datetime.year > (date.today()).year:
                    logger.debug('removing the expired job')
                    jobList.append(job)

    for job in jobList:
        logger.info('removing the job ' + job.comment)
        # remove the job
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
    # commit the change to the cron scheduler
    cron.write_to_user(user=True)
    logger.info('Policies removed')


def runPolicy(policy, usermap, test, loggerName, debug):
    """
    Schedule the policy to be enforced

    @type  policy:     policy object
    @param policy:     The policy to be scheduled
    @type  usermap:    dictionary
    @param usermap:    A dictionary containing EUDAT global username as keys
                       and local B2SAFE username as values
    @type  test:       boolean
    @param test:       If True, the code is executed without performing real 
                       operations
    @type  loggerName: string
    @param loggerName: The name of the logger
    @type  debug:      boolean
    @param debug:      If True the debug is enabled
    """
    runner = PolicyRunner(usermap, test, loggerName, debug)
    runner.runPolicy(policy)


def queryDpm(args, config):
    """ Download the policies from the DB and execute the related B2SAFE workflow

    @type  args:       list of objects
    @param args:       The list of input parameters
    @type  config:     ConfigLoader object
    @param config:     It contains the configuration parameters
    """
    debug = args.verbose
    # manage the checksum verification
    chk_veri = False
    chk_verify = config.SectionMap('Integrity')['checksum_verify']
    if chk_verify.lower() == 'true':
        chk_veri = True
    # load the policy schema path/url
    policySchemaUrl = None
    policySchema = config.SectionMap('Schemas')['policies']
    if policySchema.startswith('http://'):
        policySchemaUrl = policySchema
    # get the list of policies matching the input criteria
    conn = ServerConnector(args.config, args.test, "PolicyManager", debug)
    policy_files = getInfoPolicies(args,logger)
    if policy_files is not None:
        for url in policy_files:
            logger.info('Processing policy: %s', url)
            # load the XML policy schema
            pParser = PolicyParser(None, args.test, 'PolicyManager', debug)
            policySchemaDoc = pParser.parseXmlSchema([policySchemaUrl], 
                                                     [policySchema])
            if chk_veri:
                # get the id from the policy on the DB
                policyId = conn.getDocumentByUrl(url, '//*:policy/@uniqueid/data()')
                # get the status doc from the DB for the checksum
                status, doc = conn.getStatus(policyId)
                # parse the policy and validate against schema and checksum
                pParser.parseFromUrl(url, policySchemaDoc, conn, 
                        status[staNs+':policy'][staNs+':checksum']['@method'],
                        status[staNs+':policy'][staNs+':checksum']['#text'])
            else:
                # parse the policy and validate against schema
                pParser.parseFromUrl(url, policySchemaDoc, conn)
            if pParser.policy is not None:
                # load user mapping
                mapFilename = config.SectionMap('AccountMapping')['file']
                usermap = loadUserMap(mapFilename)
                # schedule the policy
                runPolicy(pParser.policy, usermap, args.test, 'PolicyManager',
                          debug)


def updatePolicyStatus(args):
    """
    Update the status of all the policies in the central DB

    @type  args: list of objects
    @param args: The list of input parameters
    @rtype:      string
    @return:     The response of the update operation on the DB  
    """
    response = None
    debug = args.verbose
    config = ConfigLoader(args.config)
    setLoggingSystem(config, debug)
    logger.info('Start to update the status of the policies')
    loggerName = 'PolicyManager'
    # update the status related to policies
    conn = ServerConnector(args.config, args.test, loggerName, debug)
    if (args.id):
        # get the local status of a policy based on the id
        state = getPolicyStatus(args.id, debug)
        # update the status doc on the DB
        response = conn.updateStatus(args.id, state)
    else:
        # get the list of the policies to be updated
        policies = conn.listPolicies()
        if policies is not None:
            for url in policies:
                logger.info('Processing policy: %s', url)
                # get the policy id from the DB
                policyId = conn.getDocumentByUrl(url, '//*:policy/@uniqueid/data()')
                if policyId is not None:
                    # get the local status of a policy based on the id
                    state = getPolicyStatus(policyId, debug)
                    # update the status doc on the DB
                    response = conn.updateStatus(policyId, state)
                else:
                    logger.info('policy id not found')

    return response


def getPolicyStatus(id, debug):
    """
    Get the status of the enforcement of a policy

    @type  id:    string
    @param id:    The policy id
    @type  debug: boolean
    @param debug: If True the debug is enabled    
    @rtype:       string
    @return:      The status of the enforcement of the policy:
                  [QUEUED | RUNNING | DONE | FAILED]
    """
    # define the paths where to find the irods rules and the related output
    rulePath = os.path.join(os.path.dirname(sys.path[0]), 'rules')
    ruleFiles = glob.glob(rulePath + '/replicate.' + id + '*')
    resPath = os.path.join(os.path.dirname(sys.path[0]), 'output')
    resFiles = glob.glob(resPath + '/response.' + id + '*')
    if ruleFiles is not None and len(ruleFiles) > 0:
        # the policy has been translated to a rule, but not executed
        status = 'QUEUED'
        if resFiles is not None and len(resFiles) > 0:
            # the rule has been executed, but it is still scheduled
            status = 'RUNNING'
    else:
        # the policy is not currently translated to a rule
        status = 'FAILED'
        if resFiles is not None and len(resFiles) > 0:
            # the rule has been executed and it is not scheduled
            status = 'DONE'

    return status


def getInfoPolicies(args, mylogger=None):
    """ Download the policies from the DB and execute the related B2SAFE workflow

    @type  args:       list of objects
    @param args:       The list of input parameters
                       considered to search for policies 
    @type logger:      loggin.logger object
    @param logger:     the logger
    """
    debug = args.verbose
    config = ConfigLoader(args.config)
    if mylogger is None:
        logger = setLoggingSystem(config, debug)
    else:
        logger = mylogger
    logger.info('Start to list the policies')
    conn = ServerConnector(args.config, args.test, "PolicyManager", debug)
    # if a policy id is provided the whole policy doc is shown
    if args.subcmd == 'list' and args.id:
        logger.debug('Policy with id [{}] is downloaded'.format(args.id))
        polDict, polDoc = conn.getPolicy(args.id)
        print polDoc
        return None
    attributes = {}
    # loading the default from config
    if len(config.SectionMap('PolicyFilters')) > 0:
        logger.debug('Loading the filter parameters from the config file')
        for par in config.SectionMap('PolicyFilters'):
            attributes[par] = config.SectionMap('PolicyFilters')[par]
    # loading the filter parameters from the input
    if args.filter:
        logger.debug('Loading the filter parameters from the input')
        pairs = args.filter.split(',')
        for pair in pairs:
            try:
                key, value = pair.split(':')
            except:
                print 'wrong value [{}] as a filter'.format(str(pair))
                sys.exit(1)
            attributes[key] = value
    # filter policies according to input time interval
    if args.start is not None:
        sdate = datetime.strptime(args.start, "%d-%m-%Y %H:%M")
        start = int(time.mktime(sdate.timetuple()))
        policies = conn.listPolicies(attributes, start)
        if args.end is not None:
            edate = datetime.strptime(args.end, "%d-%m-%Y %H:%M")
            end = int(time.mktime(edate.timetuple()))
            policies = conn.listPolicies(attributes, start, end)
    elif args.end is not None:
        edate = datetime.strptime(args.end, "%d-%m-%Y %H:%M")
        end = int(time.mktime(edate.timetuple()))
        policies = conn.listPolicies(attributes, 0, end)
    else:
        policies = conn.listPolicies(attributes)
    # listing of the policies matching the criteria of the dict "attributes"
    if policies is not None:
        for url in policies:
            print url
            if args.subcmd == 'list'and args.ext:
                # listing policies with extended attributes
                xmldoc = conn.getDocumentByUrl(url)
                pol = xmltodict.parse(xmldoc, process_namespaces=True)
                for key in pol[polNs+':policy']:
                    if isinstance(key, basestring) and key.startswith('@'):
                        print '{} = {}'.format(key[1:], 
                                               pol[polNs+':policy'][key])
                # get the status doc from the DB
                status, doc = conn.getStatus(pol[polNs+':policy']['@uniqueid'])
                if status is None:
                    print 'status = '
                    print 'checksum = '
                else:
                    print 'status = {}'.format(
                           status[staNs+':policy'][staNs+':status'])
                    print 'checksum = {}'.format(
                           status[staNs+':policy'][staNs+':checksum']['#text'])
            print '{: ^40}'.format('')
    else:
        print 'Nothing found'
    
    return policies


def setLoggingSystem(config, debug):
    """
    Initialize the logging system

    @type  config: ConfigLoader object
    @param config: It contains the configuration parameters
    @type  debug:  boolean
    @param debug:  If True the debug is enabled
    """
    # set the logger configuration
    logfilepath = config.SectionMap('Logging')['logfile']
    loglevel = config.SectionMap('Logging')['loglevel']
    ll = {'INFO': logging.INFO, 'DEBUG': logging.DEBUG,
          'ERROR': logging.ERROR, 'WARNING': logging.WARNING}
    logger.setLevel(ll[loglevel])
    if (debug):
        logger.setLevel(logging.DEBUG)
#TODO make the rotation parameters part of the configuration file
    # log to a file with rotation enabled
    rfh = logging.handlers.RotatingFileHandler(logfilepath,
                                               maxBytes=6000000,
                                               backupCount=9)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: ' +
                                  '[%(funcName)s] %(message)s')
    rfh.setFormatter(formatter)
    logger.addHandler(rfh)
    return logger


def main():
    argp = argparse.ArgumentParser(description="EUDAT Data Policy Manager cli")
    argp.add_argument('-t', '--test', action='store_true', required=False,
                        help='Test the DPM client (does not trigger an actual' 
                            +' replication)')
    argp.add_argument('-v', '--verbose', action='store_true', required=False,
                        help='Run the DPM client in verbose mode')
    argp.add_argument('-c', '--config', required=True, help='Path to config.ini')

    subparsers = argp.add_subparsers(help='sub-command help', dest='subcmd')
    parser_url = subparsers.add_parser('http', help='Fetch policy over http')
    parser_url.add_argument('-f', '--filter', help='filter the policies')
    parser_url.add_argument('-st', '--start',
                            help='filter the policies based on this start date'
                                +' (format: day-month-year hour:minute)')
    parser_url.add_argument('-en', '--end',
                            help='filter the policies based on this end date'
                                +' (format: day-month-year hour:minute)')    
    parser_url.set_defaults(func=parseOverHttp)

    parser_file = subparsers.add_parser('file', help='Fetch policy from a file')
    parser_file.add_argument('-p', '--path', required=True, 
                             help='Path to the policy file')
    parser_file.set_defaults(func=parseFromFile)

    parser_clean = subparsers.add_parser('clean', 
                                         help='Remove the expired policies from'
                                             +' crontab')
    parser_clean.add_argument('-a', '--all', action='store_true', 
                              help='Remove all the policies')
    parser_clean.set_defaults(func=cleanScheduledPolicies)

    parser_update = subparsers.add_parser('update', 
                                          help='Update policy status in the DB')
    parser_update.add_argument('-i', '--id', help='id of the policy')
    parser_update.set_defaults(func=updatePolicyStatus)

    parser_list = subparsers.add_parser('list', 
                                        help='list policies in the central DB')
    parser_list.add_argument('-i', '--id', help='id of the policy')
    parser_list.add_argument('-e', '--ext', action='store_true', 
                             help='extended set of information')
    parser_list.add_argument('-f', '--filter', help='filter the policies')
    parser_list.add_argument('-st', '--start', 
                             help='filter the policies based on this start date'
                                 +' (format: day-month-year hour:minute)')   
    parser_list.add_argument('-en', '--end', 
                             help='filter the policies based on this end date'
                                 +' (format: day-month-year hour:minute)')
    parser_list.set_defaults(func=getInfoPolicies)    

    args = argp.parse_args()
    if args.subcmd == 'list' and args.id and (args.ext or args.filter):
        print "-i and -e|-f are mutually exclusive ..."
        sys.exit(2)
    args.func(args)

if __name__ == '__main__':
    main()
