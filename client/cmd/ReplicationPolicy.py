__authors__ = 'Willem Elbers (MPI-TLA) <willem.elbers@mpi.nl>, \
               Claudio Cacciari (Cineca) <c.cacciari@cineca.it>'

import logging
import logging.handlers
from lxml import etree
from Policy import Policy

"""
 ReplicationPolicy Class
 see https://github.com/EUDAT-B2SAFE/B2SAFE-DPM/tree/master/schema
"""
class ReplicationPolicy(Policy):

    def __init__(self, element, ns, loggerParentName=None, debug=False):

        if loggerParentName: loggerName = loggerParentName + ".ReplicationPolicy"
        else: loggerName = "ReplicationPolicy"
        self.logger = logging.getLogger(loggerName)
        self.loggerName = loggerName

        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        self.debug = debug

        Policy.__init__(self, element, ns, loggerName, debug)
        self.dataset = None
        self.actions = []

    def toString(self):

        str = 'Policy:'
        str += Policy.toString(self);
        if self.dataset is not None:
            str += self.dataset.toString('\t')
        str += '\tActions:\n'
        for action in self.actions:
            str += action.toString('\t\t')
        return str

    def parse(self):

        Policy.parse(self)
        self.parseDataSets(self.root.findall(self.ns+'dataset'))
        self.parseActions(self.root.findall(self.ns+'actions'))

    def parseDataSets(self, datasets):

        self.logger.debug('Parsing the policy datasets')
        if datasets == None:
            print('No datasets found')
        else:
            for dataset in datasets:
                self.dataset = Dataset(dataset, self.ns, self.loggerName, self.debug)

    def parseActions(self, actions):

        self.logger.debug('Parsing the policy actions')
        if actions == None:
            print('No actions found')
        elif not len(actions) == 1:
            print('Expected one <actions> element instead of '+str(len(actions)))
        else:
            for action in actions[0].findall(self.ns+'action'):
                self.actions.append(Action(action, self.ns))


"""
 Dataset Class
 Parses the list of data sets
"""
class Dataset():

    def __init__(self, element, ns, loggerParentName=None, debug=False):

        if loggerParentName: loggerName = loggerParentName + ".Dataset"
        else: loggerName = "Dataset"
        self.logger = logging.getLogger(loggerName)

        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self.logger.debug('Parsing the data set')
        self.collections = []
        for collectionElement in element.findall(ns+'collection'):
            self.collections.append(Collection(collectionElement, ns, loggerName, debug))

    def toString(self, prefix=''):

        str = '%sCollections:\n' % (prefix)
        for collection in self.collections:
            str += '%s\t%s\n' % (prefix, collection.toString())
        return str


"""
 Collection Class
 Parses a single collection location
"""
class Collection():

    def __init__(self, element, ns, loggerParentName=None, debug=False):

        if loggerParentName: loggerName = loggerParentName + ".Collection"
        else: loggerName = "Collection"
        self.logger = logging.getLogger(loggerName)

        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self.id = element.get('id').strip()
        self.logger.debug('Got collection id: ' + self.id)
        #process persistent identifier
        pid = element.findall(ns+'persistentIdentifier')
        if pid:
            self.type = pid[0].get('type').strip()
            self.value = pid[0].text.strip()
            self.logger.debug('Got pid type %s and value %s', self.type,
                                                              self.value)
        #process location
        location = element.findall(ns+'location')
        if location:
            self.type = 'object path'
            loc = Location(element, ns, loggerName, debug)
            self.value = loc.location.path
            self.locTriplet = '[%s, %s, %s]' % (loc.location.site,
                                                loc.location.path,
                                                loc.location.resource)
            self.logger.debug('Got path %s', self.locTriplet)

    def toString(self):

        str = '%s [%s] %s' % (self.type, self.id, self.value)
        return str

"""
 Class parsing and defining all action properties
"""
class Action():

    def __init__(self, element, ns, loggerParentName=None, debug=False):
        """Initialize the class"""

        if loggerParentName: loggerName = loggerParentName + ".Action"
        else: loggerName = "Action"
        self.logger = logging.getLogger(loggerName)

        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self.targets = []
        self.sources = []

        self.name = element.get('name')
        if self.name is not None:
            self.name = self.name.strip()

        self.type = element.findall(ns+'type')[0].text
        if self.type is not None:
            self.type = self.type.strip()

        self.trigger = None
        if len(element.findall(ns+'trigger/'+ns+'action')) > 0:
            self.trigger = element.findall(ns+'trigger/'+ns+'action')[0].text.strip()
            self.triggerType = 'action'
        elif len(element.findall(ns+'trigger/'+ns+'time')) > 0:
            self.trigger = element.findall(ns+'trigger/'+ns+'time')[0].text.strip()
            self.triggerType = 'time'
        elif len(element.findall(ns+'trigger/'+ns+'runonce')) > 0:
            self.triggerType = 'runonce'
        else:
            logger.error('Unkown trigger')

        #Process sources
        for source in element.findall(ns+'sources/'+ns+'source'):
            pids = source.findall(ns+'persistentIdentifier')
            if pids is not None and len(pids) > 0:
                self.sources.append(PersistentIdentifier(source, ns, loggerName, 
                                                         debug))
            else:
                self.sources.append(Location(source, ns, loggerName, debug))

        #Process targets
        for target in element.findall(ns+'targets/'+ns+'target'):
            self.targets.append(Location(target, ns, loggerName, debug))

        self.logger.debug('Got ' + self.toString())

    def toString(self, prefix='\t'):

        str = '%sAction: %s [%s] running %s\n' % (prefix, self.name, self.type, self.trigger)
        str += '%s\tSources:\n' % (prefix)
        for source in self.sources:
            if isinstance(source, Location):
                str += '%s\t\tlocation [%s, %s, %s]\n' % (prefix, 
                                                          source.location.site, 
                                                          source.location.path, 
                                                          source.location.resource)
            if isinstance(source, PersistentIdentifier):
                str += '%s\t\tpid [%s, %s]\n' % (prefix, source.type, source.value)
        str += '%s\tTargets:\n' % (prefix)
        for target in self.targets:
            if isinstance(target, Location):
                str += '%s\t\tlocation [%s, %s, %s]\n' % (prefix, 
                                                          target.location.site, 
                                                          target.location.path, 
                                                          target.location.resource)
            if isinstance(target, PersistentIdentifier):
                str += '%s\t\tpid [%s, %s]\n' % (prefix, target.type, target.value) 
            
        return str;


"""
 Class parsing the persistent iddentifier element
"""
class PersistentIdentifier():

    def __init__(self, element, ns, loggerParentName=None, debug=False):

        if loggerParentName: loggerName = loggerParentName + ".PersitentIdentifier"
        else: loggerName = "PersitentIdentifier"
        self.logger = logging.getLogger(loggerName)
        self.loggerName = loggerName
        self.debug = debug

        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self.id = element.get('id')
        if self.id is not None:
            self.logger.debug('Got PID id: ' + self.id)
        #process persistent identifier
        pid = element.findall(ns+'persistentIdentifier')
        if pid:
            self.type = pid[0].get('type').strip()
            self.value = pid[0].text.strip()
            self.logger.debug('Got pid type %s and value %s', self.type, 
                                                              self.value)


"""
 Class parsing the location element
"""
class Location():

    def __init__(self, element, ns, loggerParentName=None, debug=False):

        if loggerParentName: loggerName = loggerParentName + ".Location"
        else: loggerName = "Location"
        self.logger = logging.getLogger(loggerName)
        self.loggerName = loggerName
        self.debug = debug

        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self.id = element.get('id')
        if self.id is not None:
            self.logger.debug('Got Location id: ' + self.id)
        for location in element.findall(ns+'location'):
            self.location = self.parseLocationType(location)
            self.type = self.location.type
            self.value = self.location.path


    def parseLocationType(self, location):

        type = location.get('{http://www.w3.org/2001/XMLSchema-instance}type')
        self.logger.debug('location type: ' + type)
        if type == 'irodsns:coordinates':
            return IrodsLocation(location, self.loggerName, self.debug)
        else:
            self.logger.error('Unkown location type')
            return None


"""
 Class parsing the specific iRODS location properties
"""
class IrodsLocation:

    def __init__(self, element, loggerParentName=None, debug=False):

        if loggerParentName: loggerName = loggerParentName + ".IrodsLocation"
        else: loggerName = "IrodsLocation"
        self.logger = logging.getLogger(loggerName)

        if debug:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        self.type = 'irods'
        self.dpmIrodsns = '{http://eudat.eu/2013/iRODS-policy}'
        self.site = element.findall(self.dpmIrodsns+'site')[0].text.strip()
        if not element.findall(self.dpmIrodsns+'path')[0].text == None:
            self.path = element.findall(self.dpmIrodsns+'path')[0].text.strip()
        else:
            self.path = ''
        resElements = element.findall(self.dpmIrodsns+'resource')
        if resElements == None or len(resElements) <= 0:
            self.resource = ''
        else:
            if resElements[0].text is None:
                self.resource = ''
            else:
                self.resource = resElements[0].text.strip()

        self.logger.debug('Got iRODS path %s and resource %s', self.path,
                                                               self.resource)
