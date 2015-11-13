import logging
import logging.handlers

"""
 Policy Class
 It parses the header of the xml policy document
"""

class Policy():


    def __init__(self, element, ns, loggerParentName=None, debug=False):
        """Policy class initializer"""

        if loggerParentName: loggerName = loggerParentName + ".Policy"
        else: loggerName = "Policy"
        self.logger = logging.getLogger(loggerName)

        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self.root = element
        self.ns = ns
        self.name = None
        self.version = None
        self.author = None
        self.policyId = None


    def parse(self):

        self.logger.debug('Parsing the policy document')
        self.name = self.root.get('name')
        self.version = self.root.get('version')
        self.author = self.root.get('author')
        self.policyId = self.root.get('uniqueid')
        self.logger.debug('Got name: %s, version: %s, author: %s, uniqueid: %s',
                          self.name, self.version, self.author, self.policyId)


    def toString(self, prefix='\t'):

        return '%sName: %s\n%sVersion:%s\n%sAuthor: %s\n%sID:%s\n' % (prefix, \
               self.name, prefix,self.version, prefix, self.author, prefix, \
               self.policyId)

