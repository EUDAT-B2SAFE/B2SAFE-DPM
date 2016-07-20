#!/usr/bin/env python

__author__ = 'Willem Elbers (MPI-TLA) <willem.elbers@mpi.nl> \
              Claudio Cacciari (Cineca) <c.cacciari@cineca.it>'

import sys
import argparse
import requests
import json
import logging
import logging.handlers
import os
import glob
from crontab import CronTab
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
            if args.all:
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
    # load properties from configuration
    with open(config.SectionMap('DpmServer')['tokenfile'], 'r') as fin:
        token_map = json.loads(fin.read())
        fin.close()
    username = token_map['token']
    password = token_map['pword']
    # TODO: we need to replace this URL with a URL for the baseX database.
    # this should be easy to do. The center is the hostname. We need to
    # remove the check for the checksum and we need to update the url for
    # the begindate and enddate.
    url = '%s://%s:%s%s' % (config.SectionMap('DpmServer')['scheme'],
                            config.SectionMap('DpmServer')['hostname'],
                            config.SectionMap('DpmServer')['port'],
                            config.SectionMap('DpmServer')['path'])

    start_time = 0
    end_time = 1000000000000000000
    if begin_date is not None:
        start_time = begin_date
    if end_date is not None:
        end_time = end_date

    post_data = '''<rest:query xmlns:rest="http://basex.org/rest">
                      <rest:text>
                         let $results :=
                         collection("policy")//*:policy[matches(@community,
                                                        "%s")]
                         for $policy in $results
                         where $policy//*:site[matches(text(), "%s")]
                         and $policy[@created > %s]
                         and not($policy[@created > %s])
                         let $policies := string-join(("%s", db:path($policy)),
                                                       "/")
                         return $policies
                      </rest:text>
                 </rest:query>''' % (config.SectionMap('Community')['id'],
                                     config.SectionMap('Center')['id'],
                                     start_time, end_time, url)

    # start interaction with DPM server
    logger.info('Getting policies [%s]' % url)
    response = requests.post(url, data=post_data, 
                             auth=(username, password), verify=False)

    print "response is ", response.text
    policy_files = response.text.split("\n")

    if policy_files is None:
        logger.info('No response found')
    else:
        logger.info('Found %d policies' % (len(policy_files)))
        for entry in policy_files:
            url = entry

            if not url.endswith('.html'):
                logger.info('Processing policy: %s', url)
                pParser = PolicyParser(None, args.test, 'PolicyManager',
                                       args.verbose)
                xmlSchemaDoc = pParser.parseXmlSchema(args.schemaurl,
                                                      args.schemapath)
                pParser.parseFromUrl(url, username, password, xmlSchemaDoc)
                if pParser.policy is not None:
                    mapFilename = config.SectionMap('AccountMapping')['file']
                    usermap = loadUserMap(mapFilename)
                    runPolicy(pParser.policy, usermap, args.test,
                              'PolicyManager', args.verbose)
            else:
                logger.error('invalid policy location [%s]', url)


def updatePolicyStatus(args):
    """
    Update the status of all the policies in the central DB
    """
    username = ''
    password = ''
    debug = args.verbose
    config = ConfigLoader(args.config)
    setLoggingSystem(config, debug)
    logger.info('Start to update the status of the policies')
    loggerName = 'PolicyManager'
    conn = ServerConnector(args.config, args.test, loggerName, debug)
    with open(config.SectionMap('DpmServer')['tokenfile'], 'r') as fin:
        json_input = json.loads(fin.read())
        username = json_input['token']
        fin.close()
    if (args.id):
        state = getPolicyStatus(args.id, debug)
        conn.updateStatus(args.id, state)
    else:
        policies = conn.listPolicies()
        if policies is not None:
            for entry in policies:
                logger.debug('entry %s' % type(entry))
                url = str(entry['identifier'])
                ts = int(entry['ctime'])
                checksum_value = str(entry['checksum'])
                checksum_algo = str(entry['checksum_type'])

                if not url.endswith('.html'):
                    logger.info('Processing policy: %s [%s, %s, %s]', url, ts,
                                checksum_value, checksum_algo)
                    pParser = PolicyParser(None, args.test, 'PolicyManager',
                                           debug)
                    xmlSchemaDoc = pParser.parseXmlSchema(args.schemaurl,
                                                          args.schemapath)
                    pParser.parseFromUrl(url, username, password, xmlSchemaDoc,
                                         checksum_algo, checksum_value)
                    if pParser.policy is not None:
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
    ruleFiles = glob.glob(rulePath + '/replicate.' + id + '*')
    resPath = os.path.join(os.path.dirname(sys.path[0]), 'output')
    resFiles = glob.glob(resPath + '/response.' + id + '*')
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
    ll = {'INFO': logging.INFO, 'DEBUG': logging.DEBUG,
          'ERROR': logging.ERROR, 'WARNING': logging.WARNING}
    logger.setLevel(ll[loglevel])
    if (debug):
        logger.setLevel(logging.DEBUG)
    rfh = logging.handlers.RotatingFileHandler(logfilepath,
                                               maxBytes=6000000,
                                               backupCount=9)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: ' +
                                  '[%(funcName)s] %(message)s')
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
    parser_update.add_argument('-i', '--id', help='id of the policy')
    parser_update.set_defaults(func=updatePolicyStatus)

    args = argp.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
