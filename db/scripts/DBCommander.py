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
from ConfigLoader import ConfigLoader
from ServerConnector import ServerConnector

# enabling logging
logger = logging.getLogger('DBCommander')
polNs = 'http://eudat.eu/2013/policy'
staNs = 'http://eudat.eu/2016/policy-status'


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
    st_pre = config.SectionMap('DpmServer')['status_prefix']
    loggerName = 'DBCommander'
    logger.info('Start to update the status of the policies')
    # update the status related to policies
    conn = ServerConnector(args.config, args.test, loggerName, debug)

    policies = conn.listPolicies()
    if policies is not None:
        for url in policies:
            logger.info('Search status of policy: ' + url)
            # get the policy id from the DB
            policyId = conn.getDocumentByUrl(url, '//*:policy/@uniqueid/data()')
            states = conn.getStates(policyId)
            if states is None:
                print 'Status of policy {} not found'.format(policyId)
            else:
                community_name = (url.rsplit('/', 2)[-2]).split('_',2)[2]
                # get the status doc from the DB
                dbname = st_pre + community_name
                response = conn.updateStatus(policyId, states, dbname)
                print 'Status of policy {}, update response:'.format(policyId, 
                                                                     response)
    else:
        print 'No policies to update'


def addPolicyStatus(args, mylogger=None):
    """ Check if a status document exist for each policy 
        and, if not, it creates a new one.

    @type  args:       list of objects
    @param args:       The list of input parameters
                       considered to search for policies 
    @type logger:      loggin.logger object
    @param logger:     the logger
    """
    debug = args.verbose
    config = ConfigLoader(args.config)
    st_pre = config.SectionMap('DpmServer')['status_prefix']
    if mylogger is None:
        logger = setLoggingSystem(config, debug)
    else:
        logger = mylogger

    logger.info('Start to list the policies')
    conn = ServerConnector(args.config, args.test, "DBCommander", debug)

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
            logger.debug('Checking status for policy with URL: ' + url)
            community_name = (url.rsplit('/', 2)[-2]).split('_',2)[2]
            uniqueid = conn.getDocumentByUrl(url, "//*:policy/@uniqueid/data()")
            # get the status doc from the DB
            dbname = st_pre + community_name
            status, doc = conn.getStatus(uniqueid, dbname)
            if status is None:
                logger.debug('Status doc not found, creating a new one')
                response = conn.createStatus(uniqueid, 'NEW', dbname)
                print 'Added new status for policy {}, response: {}'.format(
                                                                     uniqueid,
                                                                     response)
            else:
                logger.debug('Status doc already available')
                print ('Status already available, nothing to add for policy {}'
                      ).format(uniqueid)
    else:
        print 'Policies not found'
    
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
    logfilepath = config.SectionMap('Logs')['logfile']
    loglevel = config.SectionMap('Logs')['loglevel']
    ll = {'INFO': logging.INFO, 'DEBUG': logging.DEBUG,
          'ERROR': logging.ERROR, 'WARNING': logging.WARNING}
    logger.setLevel(ll[loglevel])
    if debug:
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
    argp = argparse.ArgumentParser(
                           description="EUDAT Data Policy Manager DBCommander")
    argp.add_argument('-t', '--test', action='store_true', required=False,
                        help='Test the DBCommander')
    argp.add_argument('-v', '--verbose', action='store_true', required=False,
                        help='Run in verbose mode')
    argp.add_argument('-c', '--config', required=True, help='Path to confiuration')

    subparsers = argp.add_subparsers(help='sub-command help', dest='subcmd')

    parser_update = subparsers.add_parser('update', 
                                          help='Update policy status in the DB')
    parser_update.set_defaults(func=updatePolicyStatus)

    parser_list = subparsers.add_parser('add', 
                              help='create the status doc for the new policies')
    parser_list.add_argument('-f', '--filter', help='filter the policies')
    parser_list.add_argument('-st', '--start', 
                             help='filter the policies based on this start date'
                                 +' (format: day-month-year hour:minute)')   
    parser_list.add_argument('-en', '--end', 
                             help='filter the policies based on this end date'
                                 +' (format: day-month-year hour:minute)')
    parser_list.set_defaults(func=addPolicyStatus)    

    args = argp.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
