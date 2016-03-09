#!/usr/bin/env python

__author__ = 'Claudio Cacciari, Cineca, c.cacciari@cineca.it'

import json
import urllib2
import urllib
import time
import logging
from ConfigLoader import ConfigLoader

class ServerConnector:

    def __init__(self, config, test=False, loggerParentName=None, debug=False):

        if loggerParentName: loggerName = loggerParentName + ".ServerConnector"
        else: loggerName = "ServerConnector"
        self.logger = logging.getLogger(loggerName)

        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self.test = test
        self.debug = debug

        #load properties from configuration
        self.config = ConfigLoader(config)
        username = self.config.SectionMap('DpmServer')['username']
        password = self.config.SectionMap('DpmServer')['password']
        server = self.config.SectionMap('DpmServer')['hostname']

        #Prepare server connection
        authinfo = urllib2.HTTPPasswordMgrWithDefaultRealm()
        authinfo.add_password(None, server, username, password)
        handler = urllib2.HTTPBasicAuthHandler(authinfo)
        self.myopener = urllib2.build_opener(handler)


    def updateStatus(self, policyId, state):

        self.logger.info('uploading the policy status')
        url = '%s://%s:%s%s' % \
              (self.config.SectionMap('DpmServer')['scheme'],
               self.config.SectionMap('DpmServer')['hostname'],
               self.config.SectionMap('DpmServer')['port'],
               self.config.SectionMap('DpmServer')['uploadpath'])

        #Get the current UNIX timestamp
        timestamp = time.time()

        # Upload information
        opened = urllib2.install_opener(self.myopener)
        data = [{"identifier": policyId,
                                 "state": state,
                                 "timestamp": "%s" % timestamp,
                                 "hostname":
                                     self.config.SectionMap('Center')['id']}]
        self.logger.debug('url:' + url + ', data: %s' % data)
        req = urllib2.Request(url=url, data=json.dumps(data),
                              headers={'Content-Type': 'application/json'})
        response = urllib2.urlopen(req).read()
        self.logger.debug('response is %s ' % response)
        return response


    def listPolicies(self, begin_date=None, end_date=None):

        url = '%s://%s:%s%s?community=%s&site=%s' % \
                 (self.config.SectionMap('DpmServer')['scheme'],
                  self.config.SectionMap('DpmServer')['hostname'],
                  self.config.SectionMap('DpmServer')['port'],
                  self.config.SectionMap('DpmServer')['path'],
                  self.config.SectionMap('Community')['id'],
                  self.config.SectionMap('Center')['id'])

        #apply parameters
        if not begin_date is None:
            url += '&begin_date=%s' % begin_date
        if not end_date is None:
            url += '&end_date=%s' % end_date

        self.logger.info('Listing policies [%s]' % url)

        opened = urllib2.install_opener(self.myopener)
        response = urllib2.urlopen(url)
        json_data = response.read()

        if json_data is None:
            jsonDict = None
            self.logger.info('No response found')
        else:
            jsonDict = json.loads(json_data)
            self.logger.info('Found %d policies' % (len(jsonDict)))

        return jsonDict
