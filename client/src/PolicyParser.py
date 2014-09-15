import urllib2
from lxml import etree
from ReplicationPolicy import *
import hashlib

class PolicyParser():

    def __init__(self, type='', test=False, debug=False):
        self.type = type
        self.test = test
        self.debug = debug
        self.dpmNS = '{http://eudat.eu/2013/policy}'
        self.policy = None

    def parseXmlSchemaFromUrl(self, url):
        response = urllib2.urlopen(url)
        xmlData = response.read()
        schemaDoc = etree.fromstring(xmlData)
        response.close()
        return schemaDoc

    def parseXmlSchema(self, schemaurl, schemapath):
        if schemaurl:
            #if self.debug: print('schema URL: '+schemaurl[0])
            xmlSchemaDoc = self.parseXmlSchemaFromUrl(schemaurl[0])
        elif schemapath:
            #if self.debug: print('schema path: '+schemapath[0])
            xmlSchemaDoc = etree.parse(schemapath[0])
        else:
            xmlSchemaDoc = None
        return xmlSchemaDoc

    def parseFromText(self, xmlData, xmlSchemaDoc):
        """
        Create an xml document from text input
        """
        xmlschema = etree.XMLSchema(xmlSchemaDoc)
        root = etree.fromstring(xmlData)
        if not xmlschema(root):
            print (xmlschema.error_log).last_error
            exit()
        self.parse(root)

    def parseFromFile(self, file, xmlSchemaDoc):
        """
        Create an xml document from file input
        """
        xmlschema = etree.XMLSchema(xmlSchemaDoc)
        tree = etree.parse(file)
        if not xmlschema(tree):
            print (xmlschema.error_log).last_error
            exit()
        root = tree.getroot()
        self.parse(root)

    def parseFromUrl(self, url, xmlSchemaDoc, checksum_algo=None, checksum_value=None):
        """
        Create an xml document from url input
        """
        response = urllib2.urlopen(url)
        xmlData = response.read()
#        xmlData += 'incorrect'

        #Decide if checksum verification is needed and if yes, compute the checksum for the downloaded policy
        checksumVerificationNeeded = not checksum_algo == None
        checksumVerified = False
        if checksumVerificationNeeded:
            print('Checksum computation: '),
            checksumVerification = False
            if checksum_algo == 'md5':
                print 'md5'
                newChecksumValue = hashlib.md5(xmlData).hexdigest()
                checksumVerified = newChecksumValue == checksum_value

        #Parse the policy if checksum verification is needed
        print('Checksum verification: '),
        if checksumVerificationNeeded and checksumVerified:
            print 'passed'
            self.parseFromText(xmlData, xmlSchemaDoc)
        elif not checksumVerificationNeeded:
            print 'disabled'
            self.parseFromText(xmlData, xmlSchemaDoc)
        else:
            print 'failed'

        response.close()

    def parse(self, policy):
        """
        Parse the policy
        """
        if policy == None or not policy.tag == self.dpmNS+'policy':
            print('Failed to find policy element')
        else:
            self.policy = ReplicationPolicy(policy, self.dpmNS)
            self.policy.parse()
