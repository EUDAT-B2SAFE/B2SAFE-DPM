__author__ = 'Willem Elbers (MPI-TLA) <willem.elbers@mpi.nl>, \
              Claudio Cacciari (Cineca) <c.cacciari@cineca.it>'
import json
import hashlib
import logging
import logging.handlers
from lxml import etree
import urllib2
from ReplicationPolicy import *


"""
 PolicyParser Class
 Class which manages the parsing of all the policy elements
"""
class PolicyParser():

    def __init__(self, type='', test=False, loggerParentName=None, debug=False):

        if loggerParentName: loggerName = loggerParentName + ".PolicyParser"
        else: loggerName = "PolicyParser"
        self.logger = logging.getLogger(loggerName)
        self.loggerName = loggerName

        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self.type = type
        self.test = test
        self.debug = debug
        self.dpmNS = '{http://eudat.eu/2013/policy}'
        self.policy = None

    def parseXmlSchemaFromUrl(self, url):

        self.logger.debug('Parsing xml schema from url ' + url)

        response = urllib2.urlopen(url)
        xmlData = response.read()
        schemaDoc = etree.fromstring(xmlData)
        response.close()
        return schemaDoc

    def parseXmlSchema(self, schemaurl, schemapath):

        if schemaurl:
            self.logger.debug('xml schema URL: ' + schemaurl[0])
            xmlSchemaDoc = self.parseXmlSchemaFromUrl(schemaurl[0])
        elif schemapath:
            self.logger.debug('xml schema path: ' + schemapath[0])
            xmlSchemaDoc = etree.parse(schemapath[0])
        else:
            self.logger.debug('xml schema is None')
            xmlSchemaDoc = None
        return xmlSchemaDoc

    def parseFromText(self, xmlData, xmlSchemaDoc):
        """
        Create an xml document from text input
        """

        self.logger.debug('Parsing xml doc from text')
        xmlschema = etree.XMLSchema(xmlSchemaDoc)
        root = etree.fromstring(xmlData)
        if not xmlschema(root):
            self.logger.error(xmlschema.error_log.last_error)
            errorMessage = xmlschema.error_log.last_error.message
            if errorMessage.startswith("Element '{http://eudat.eu/2013/policy}time'"):
                self.timeErrorManager(root, xmlschema)
            else:
                exit()
        self.parse(root)

    def parseFromFile(self, file, xmlSchemaDoc):
        """
        Create an xml document from file input
        """

        self.logger.debug('Parsing xml doc from file ' + file)
        xmlschema = etree.XMLSchema(xmlSchemaDoc)
        tree = etree.parse(file)
        root = tree.getroot()
        if not xmlschema(root):
            self.logger.error(xmlschema.error_log.last_error)
            errorMessage = xmlschema.error_log.last_error.message
            if errorMessage.startswith("Element '{http://eudat.eu/2013/policy}time'"):
                self.timeErrorManager(root, xmlschema)
            else:
                exit()
        self.parse(root)

    def parseFromUrl(self, url, username, password, xmlSchemaDoc,
                     checksum_algo=None, checksum_value=None):
        """
        Create an xml document from url input
        """

        self.logger.debug('Getting xml doc from url ' + url)

        authinfo = urllib2.HTTPPasswordMgrWithDefaultRealm()
        authinfo.add_password(None, url, username, password)
        handler = urllib2.HTTPBasicAuthHandler(authinfo)
        myopener = urllib2.build_opener(handler)
        urllib2.install_opener(myopener)
        response = urllib2.urlopen(url)
        response_data = response.read()
        data = json.loads(response_data)
        xmlData = data["policy"]

        self.logger.debug("xmlData is %s" % xmlData)

        #Decide if checksum verification is needed and if yes, compute the checksum for the downloaded policy
        checksumVerificationNeeded = not checksum_algo == None
        checksumVerified = False
        if checksumVerificationNeeded:
            self.logger.debug('Checksum computation: '),
            checksumVerification = False
            if checksum_algo == 'md5':
                self.logger.debug('md5')
                newChecksumValue = hashlib.md5(xmlData).hexdigest()
                checksumVerified = newChecksumValue == checksum_value
                self.logger.debug('checksum computed %s read %s' % \
                  (newChecksumValue, checksum_value))

        #Parse the policy if checksum verification is needed
        self.logger.debug('Checksum verification: ')
        if checksumVerificationNeeded and checksumVerified:
            self.logger.debug('passed')
            self.parseFromText(xmlData, xmlSchemaDoc)
        elif not checksumVerificationNeeded:
            self.logger.debug('disabled')
            self.parseFromText(xmlData, xmlSchemaDoc)
        else:
            self.logger.error('failed')

        response.close()

    def parse(self, policy):
        """
        Parse the policy
        """

        if policy == None or not policy.tag == self.dpmNS+'policy':
            self.logger.error('Failed to find policy element')
        else:
            self.policy = ReplicationPolicy(policy, self.dpmNS, self.loggerName,
                                            self.debug)
            self.policy.parse()

    def timeErrorManager(self, root, xmlschema):
        """
        Manage the extra year field in the time element
        """

        self.logger.debug('trying to fix year extra field in time element')
        timeElemList = root.xpath('//b:time',
                                 namespaces={'b':'http://eudat.eu/2013/policy'})
        for timeElem in timeElemList:
            self.logger.debug('Element: ' + etree.tostring(timeElem))
            if len(timeElem.text.split()) < 6:
                self.logger.debug('Adding missing field year')
                timeElem.text = timeElem.text + ' *'
                if not xmlschema(root):
                    self.logger.error(xmlschema.error_log.last_error)
                    exit()
            else:
                self.logger.debug('Impossible to fix the error')
                exit()
